import os
import requests
import random
import time
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURAÇÕES GERAIS ---
# Model fallback chain — tries each in order until one works
MODEL_FALLBACK_CHAIN = [
    "gemini-1.5-flash",        # stable, widely available
    "gemini-1.5-flash-8b",     # lighter, higher quota
    "gemini-2.0-flash-lite",   # may be restricted on free tier
]

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
MAX_OUTPUT_TOKENS = 320

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
        "structure": "Open with a cold numerical or structural observation. Build to a philosophical provocation. End with a sentence that reframes everything above it.",
        "forbidden": ["liquidity", "bullish", "bearish", "DYOR"],
    },
    {
        "name": "the_archaeologist",
        "role": (
            "You are a protocol archaeologist. You don't read price — you read "
            "infrastructure as sediment. Every deployment, bridge, and upgrade "
            "is a fossil that reveals what power wanted to be permanent."
        ),
        "structure": "Start with what the infrastructure *reveals* (not describes). Layer in what it *hides*. Close with what that silence means for those paying attention.",
        "forbidden": ["liquidity", "liquidation", "exit", "pump"],
    },
    {
        "name": "the_sovereign",
        "role": (
            "You are a sovereign risk analyst who stopped working for governments "
            "when you realized protocol-states were more honest about their coercion. "
            "You think in decades, speak in paradoxes."
        ),
        "structure": "Frame the news as a move in a longer geopolitical or monetary chess game. Identify who benefits from the narrative, not the event. End with an unsettling implication.",
        "forbidden": ["liquidity", "liquidation", "institutional", "moon"],
    },
    {
        "name": "the_nihilist_trader",
        "role": (
            "You are a DeFi-native who has watched three full cycles. You have no "
            "ideology left — only pattern recognition and a dark sense of humor "
            "about the recursion of human greed dressed as innovation."
        ),
        "structure": "Open with the pattern you've seen before. Name exactly how this iteration differs (even slightly). Close with what that difference actually costs someone.",
        "forbidden": ["revolutionary", "unprecedented", "paradigm shift", "alpha"],
    },
]


def _pick_persona() -> dict:
    return random.choice(PERSONAS)


def _build_single_prompt(news_set: list, persona: dict, extra_instruction: str = "") -> str:
    forbidden_str = ", ".join(persona["forbidden"])
    return (
        f"{persona['role']}\n\n"
        f"STRUCTURE TO FOLLOW: {persona['structure']}\n\n"
        f"ANALYZE ONLY THESE HEADLINES: {news_set}\n\n"
        f"RULES:\n"
        f"- Max 270 characters\n"
        f"- No hashtags, no emojis, no bullet points\n"
        f"- No generic finance commentary — every sentence must earn its place\n"
        f"- FORBIDDEN WORDS: {forbidden_str}\n"
        f"- Write for someone who has read Taleb, traded through a crash, and "
        f"distrusts anyone still using the word 'ecosystem'\n"
        f"{extra_instruction}\n"
        f"Output ONLY the post text. Nothing else."
    )


def _build_echo_prompt(sample: list) -> str:
    return (
        f"You are a literary curator for people who have lost faith in financial systems "
        f"but not in language.\n\n"
        f"SELECT one quote from: Nietzsche, Cioran, Borges, Kafka, Bukowski, Camus, "
        f"Dostoevsky, or Orwell.\n\n"
        f"The quote must resonate with the SUBTEXT of these headlines — not the surface: {sample}\n\n"
        f"RULES:\n"
        f"- The quote must feel inevitable, not decorative\n"
        f"- Must be in English\n"
        f"- Format exactly: 'Quote text' — Author\n"
        f"- Max 200 chars\n"
        f"- No intro, no commentary, no emojis\n"
        f"Output ONLY the formatted quote."
    )


def _build_prompts(set1: list, set2: list, set3: list, sample: list) -> dict:
    return {
        "tape": _build_single_prompt(set1, _pick_persona()),
        "plumbing": _build_single_prompt(set2, _pick_persona()),
        "decoding": _build_single_prompt(
            set3,
            _pick_persona(),
            extra_instruction="End your post with exactly: 'Logic dictates 42.'"
        ),
        "echo": _build_echo_prompt(sample),
    }


# ---------------------------------------------------------------------------
# API CALL — with model fallback chain + Retry-After support
# ---------------------------------------------------------------------------
def _parse_retry_after(error_msg: str) -> float:
    """Extracts retry delay in seconds from Gemini's error message."""
    match = re.search(r"retry in ([0-9.]+)s", error_msg)
    if match:
        return float(match.group(1))
    return 0.0


def _call_model(prompt: str, model: str) -> str | None:
    """
    Makes a single attempt against one model.
    Returns text on success.
    Returns None if quota/rate-limited (caller should try next model).
    Raises on hard errors (4xx non-429, malformed response).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "temperature": 0.92,
        },
    }

    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    logger.info("Model %s — HTTP %s", model, r.status_code)

    if r.ok:
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    # Parse error body
    try:
        error_body = r.json()
        error_msg = error_body.get("error", {}).get("message", r.text[:300])
    except Exception:
        error_msg = r.text[:300]

    if r.status_code == 429:
        retry_after = _parse_retry_after(error_msg)
        logger.warning("Model %s quota/rate-limited. Retry-After: %.1fs", model, retry_after)
        return None  # signal to try next model

    # Other 4xx = hard error, no point retrying
    raise RuntimeError(f"HTTP {r.status_code} — {error_msg}")


def gemini_gerar_tweet(prompt: str) -> str:
    """
    Tries each model in MODEL_FALLBACK_CHAIN.
    Falls back to the next model on 429.
    Retries with exponential backoff on connection/timeout errors.
    """
    for model in MODEL_FALLBACK_CHAIN:
        for attempt in range(MAX_RETRIES + 1):
            try:
                result = _call_model(prompt, model)
                if result is not None:
                    return result
                # 429 on this model — skip to next model immediately
                break

            except (KeyError, IndexError):
                logger.error("Malformed response from model %s", model)
                return "System error: Malformed response from node."

            except RuntimeError as e:
                # Hard 4xx error
                logger.error("Hard error on model %s: %s", model, e)
                return f"System error: {e}"

            except requests.exceptions.Timeout:
                logger.warning("Timeout — model %s attempt %d/%d", model, attempt + 1, MAX_RETRIES + 1)

            except requests.exceptions.RequestException as e:
                logger.warning("Request error — model %s attempt %d/%d: %s", model, attempt + 1, MAX_RETRIES + 1, e)

            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                logger.info("Retrying model %s in %ds...", model, wait)
                time.sleep(wait)

    return "System error: All models exhausted. Check your Gemini quota at https://ai.dev/rate-limit"


# ---------------------------------------------------------------------------
# PARSING / SPLITTING
# ---------------------------------------------------------------------------
def _parse_noticias(titulos: str) -> list[str]:
    return [n.strip() for n in titulos.split("-") if len(n.strip()) > 8]


def _split_sets(noticias: list) -> tuple[list, list, list]:
    n = len(noticias)
    return (
        noticias[: max(1, n // 3)],
        noticias[n // 3 : (2 * n) // 3],
        noticias[(2 * n) // 3 :],
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
                results[key] = f"Signal lost on {key.upper()} channel."

    header = random.choice(HEADERS)
    b1, b2, b3, b4 = random.choice(BULLET_SETS)

    return (
        f"{header}\n\n"
        f"{b1}:\n{results.get('tape', '')}\n\n"
        f"{b2}:\n{results.get('plumbing', '')}\n\n"
        f"{b3}:\n{results.get('decoding', '')}\n\n"
        f"{b4}:\n{results.get('echo', '')}"
    )
