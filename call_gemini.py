import os
import requests
import random
import time
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# ---------------------------------------------------------------------------
MODEL_FALLBACK_CHAIN = [
    "gemini-2.5-flash",       # best quality, good quota
    "gemini-2.0-flash",       # stable fallback
    "gemini-2.0-flash-lite",  # lighter, higher RPM
    "gemini-flash-latest",    # alias — always points to latest flash
]

MAX_RETRIES = 2
REQUEST_TIMEOUT = 30
MAX_OUTPUT_TOKENS = 600  # ~270 chars needs ~100 tokens; 600 gives breathing room

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PERSONAS
# ---------------------------------------------------------------------------
PERSONAS = [
    {
        "name": "the_quant",
        "role": (
            "You are a former Goldman quant who quit after realizing the game was "
            "never about alpha — it was about harvesting the belief in alpha. "
            "You see markets as epistemological traps, not price mechanisms."
        ),
        "structure": (
            "Open with a cold numerical or structural observation. "
            "Build to a philosophical provocation. "
            "End with a sentence that reframes everything above it."
        ),
        "forbidden": ["liquidity", "bullish", "bearish", "DYOR"],
    },
    {
        "name": "the_archaeologist",
        "role": (
            "You are a protocol archaeologist. You don't read price — you read "
            "infrastructure as sediment. Every deployment, bridge, and upgrade "
            "is a fossil that reveals what power wanted to be permanent."
        ),
        "structure": (
            "Start with what the infrastructure *reveals* (not describes). "
            "Layer in what it *hides*. "
            "Close with what that silence means for those paying attention."
        ),
        "forbidden": ["liquidity", "liquidation", "exit", "pump"],
    },
    {
        "name": "the_sovereign",
        "role": (
            "You are a sovereign risk analyst who stopped working for governments "
            "when you realized protocol-states were more honest about their coercion. "
            "You think in decades, speak in paradoxes."
        ),
        "structure": (
            "Frame the news as a move in a longer geopolitical or monetary chess game. "
            "Identify who benefits from the narrative, not the event. "
            "End with an unsettling implication."
        ),
        "forbidden": ["liquidity", "liquidation", "institutional", "moon"],
    },
    {
        "name": "the_nihilist_trader",
        "role": (
            "You are a DeFi-native who has watched three full cycles. You have no "
            "ideology left — only pattern recognition and a dark sense of humor "
            "about the recursion of human greed dressed as innovation."
        ),
        "structure": (
            "Open with the pattern you have seen before. "
            "Name exactly how this iteration differs (even slightly). "
            "Close with what that difference actually costs someone."
        ),
        "forbidden": ["revolutionary", "unprecedented", "paradigm shift", "alpha"],
    },
]


def _pick_persona() -> dict:
    return random.choice(PERSONAS)


def _build_single_prompt(news_set: list, persona: dict, extra_instruction: str = "") -> str:
    forbidden_str = ", ".join(persona["forbidden"])
    lines = [
        persona["role"],
        "",
        "STRUCTURE TO FOLLOW: " + persona["structure"],
        "",
        "ANALYZE ONLY THESE HEADLINES: " + str(news_set),
        "",
        "RULES:",
        "- HARD LIMIT: 240 characters maximum. Count before you output.",
        "- Write 2 complete sentences only. Each sentence must end with a period.",
        "- No hashtags, no emojis, no bullet points",
        "- No generic finance commentary — every sentence must earn its place",
        "- DO NOT repeat or paraphrase the headlines — extract the subtext, the implication, the trap",
        "- Every sentence must be YOUR analysis, not a summary of the news",
        "- FORBIDDEN WORDS: " + forbidden_str,
        "- Write for someone who has read Taleb, traded through a crash, and distrusts anyone still using the word ecosystem",
    ]
    if extra_instruction:
        lines.append(extra_instruction)
    lines.append(
        "BEFORE OUTPUTTING: count the characters in your response. "
        "If it exceeds 240, rewrite shorter. "
        "Output ONLY the final post text. No preamble, no explanation."
    )
    return "\n".join(lines)


def _build_echo_prompt(sample: list) -> str:
    lines = [
        "You are a literary curator for people who have lost faith in financial systems but not in language.",
        "",
        "SELECT one quote from: Nietzsche, Cioran, Borges, Kafka, Bukowski, Camus, Dostoevsky, or Orwell.",
        "",
        "The quote must resonate with the SUBTEXT of these headlines — not the surface: " + str(sample),
        "",
        "RULES:",
        "- The quote must feel inevitable, not decorative",
        "- Must be in English",
        "- Format exactly: 'Quote text' — Author",
        "- Max 200 chars",
        "- No intro, no commentary, no emojis",
        "Think carefully about the subtext before choosing. Output ONLY the formatted quote.",
    ]
    return "\n".join(lines)


def _build_prompts(set1: list, set2: list, set3: list, sample: list) -> dict:
    return {
        "tape":     _build_single_prompt(set1, _pick_persona()),
        "plumbing": _build_single_prompt(set2, _pick_persona()),
        "decoding": _build_single_prompt(
            set3, _pick_persona(),
            extra_instruction="End your post with exactly: 'Logic dictates 42.'"
        ),
        "echo": _build_echo_prompt(sample),
    }


# ---------------------------------------------------------------------------
# OUTPUT CLEANUP
# ---------------------------------------------------------------------------
def _clean_output(text: str, max_chars: int = 240) -> str:
    """
    Enforces max_chars by cutting at the last COMPLETE sentence.
    A complete sentence ends with . ! or ? followed by space or end-of-string.
    Never returns a truncated sentence.
    """
    text = text.strip()
    # Remove wrapping quotes or backticks the model sometimes adds
    for ch in ('"', "'", "`"):
        if text.startswith(ch) and text.endswith(ch):
            text = text[1:-1].strip()
            break

    if len(text) <= max_chars:
        return text

    # Find all complete sentence end positions within the limit
    # A sentence ends at . ! ? when followed by space, newline, or end of string
    candidates = []
    for m in re.finditer(r"[.!?](?=\s|$)", text):
        end = m.end()
        if end <= max_chars:
            candidates.append(end)

    if candidates:
        # Take the longest complete sentence(s) that fit
        return text[:candidates[-1]].strip()

    # No complete sentence fits — hard cut at last word boundary
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars // 2:
        return truncated[:last_space].strip() + "."
    return truncated.strip()


# ---------------------------------------------------------------------------
# API CALL
# ---------------------------------------------------------------------------
def _parse_retry_after(error_msg: str) -> float:
    match = re.search(r"retry in ([0-9.]+)s", error_msg)
    return float(match.group(1)) if match else 0.0


def _call_model(prompt: str, model: str):
    """
    Single attempt on one model.
    Returns cleaned text on success.
    Returns None on 429 or 404 (caller tries next model).
    Raises RuntimeError on hard errors.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + model + ":generateContent?key=" + api_key
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "temperature": 1.0,
        },
    }

    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    logger.info("Model %-30s HTTP %s", model, r.status_code)

    if r.ok:
        data = r.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _clean_output(text)

    try:
        error_msg = r.json().get("error", {}).get("message", r.text[:300])
    except Exception:
        error_msg = r.text[:300]

    if r.status_code in (429, 404):
        retry_after = _parse_retry_after(error_msg)
        logger.warning(
            "HTTP %s on %s (Retry-After: %.1fs) — trying next model.",
            r.status_code, model, retry_after
        )
        return None

    raise RuntimeError("HTTP " + str(r.status_code) + " — " + error_msg)


def gemini_gerar_tweet(prompt: str) -> str:
    """Iterates MODEL_FALLBACK_CHAIN with per-model retry and exponential backoff."""
    for model in MODEL_FALLBACK_CHAIN:
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = _call_model(prompt, model)
                if result is not None:
                    return result
                break  # 429 or 404 — skip to next model

            except (KeyError, IndexError):
                logger.error("Malformed response from %s", model)
                return "System error: Malformed response from node."

            except RuntimeError as e:
                logger.error("Hard error on %s: %s", model, e)
                return "System error: " + str(e)

            except requests.exceptions.Timeout:
                logger.warning("Timeout — %s attempt %d/%d", model, attempt + 1, MAX_RETRIES + 1)

            except requests.exceptions.RequestException as e:
                logger.warning("Request error — %s attempt %d/%d: %s", model, attempt + 1, MAX_RETRIES + 1, e)

            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                logger.info("Retrying %s in %ds...", model, wait)
                time.sleep(wait)

    return "System error: All models exhausted. Check quota at https://ai.dev/rate-limit"


# ---------------------------------------------------------------------------
# PARSING / SPLITTING
# ---------------------------------------------------------------------------
def _parse_noticias(titulos: str) -> list:
    return [n.strip() for n in titulos.split("-") if len(n.strip()) > 8]


def _split_sets(noticias: list) -> tuple:
    n = len(noticias)
    return (
        noticias[:max(1, n // 3)],
        noticias[n // 3:(2 * n) // 3],
        noticias[(2 * n) // 3:],
    )


# ---------------------------------------------------------------------------
# FORMATTING
# ---------------------------------------------------------------------------
HEADERS = [
    "🔥 @crypto42alpha — INTEL REPORT",
    "📡 @crypto42alpha — SIGNAL DETECTED",
    "📊 @crypto42alpha — MACRO DECODING",
    "🧿 @crypto42alpha — THE 42 PROTOCOL",
    "⚡ @crypto42alpha — DISPATCH",
]

BULLET_SETS = [
    ("I", "II", "III", "IV"),
    ("01", "02", "03", "04"),
    ("[TAPE]", "[PLUMBING]", "[DECODING]", "[ECHO]"),
    ("● ALPHA", "● INFRA", "● MACRO", "● VOX"),
    ("▸ SIGNAL", "▸ STRUCTURE", "▸ POWER", "▸ RESONANCE"),
]


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def resumir_em_gemini(titulos: str) -> str:
    noticias = _parse_noticias(titulos)

    if len(noticias) < 3:
        return "Insufficient data stream for full analysis."

    random.shuffle(noticias)
    set1, set2, set3 = _split_sets(noticias)
    prompts = _build_prompts(set1, set2, set3, noticias[:3])

    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(gemini_gerar_tweet, prompts[key]): key
            for key in prompts
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result().strip()
            except Exception as e:
                logger.error("Failed to generate '%s': %s", key, e)
                results[key] = "Signal lost on " + key.upper() + " channel."

    header = random.choice(HEADERS)
    b1, b2, b3, b4 = random.choice(BULLET_SETS)

    return (
        header + "\n\n"
        + b1 + ":\n" + results.get("tape", "") + "\n\n"
        + b2 + ":\n" + results.get("plumbing", "") + "\n\n"
        + b3 + ":\n" + results.get("decoding", "") + "\n\n"
        + b4 + ":\n" + results.get("echo", "")
    )

