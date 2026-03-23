import os
import requests
import random
import re
import time

# --- CONFIGURAÇÕES GERAIS ---
TEXT_MODEL = "gemini-3.1-flash-lite-preview"


def _clean_output(text: str, max_chars: int = 240) -> str:
    """Safety net: cuts at the last complete sentence within the limit."""
    text = text.strip()
    for ch in ('"', "'", "`"):
        if text.startswith(ch) and text.endswith(ch):
            text = text[1:-1].strip()
            break
    if len(text) <= max_chars:
        return text
    candidates = []
    for m in re.finditer(r"[.!?](?=\s|$)", text):
        end = m.end()
        if end <= max_chars:
            candidates.append(end)
    if candidates:
        return text[:candidates[-1]].strip()
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars // 2:
        return truncated[:last_space].strip() + "."
    return truncated.strip()


def gemini_gerar_tweet(prompt, retries=2):
    """Gera o texto denso e cínico para o Intel Report."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment!")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 600,
            "temperature": 0.92
        }
    }
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=25)
            r.raise_for_status()
            text = r.json()['candidates'][0]['content']['parts'][0]['text']
            return _clean_output(text)
        except Exception as e:
            if attempt < retries:
                time.sleep(3)
                continue
            return f"System error: Node disconnected. {str(e)}"


def _char_limit_instruction(max_chars: int = 240) -> str:
    """Returns the counting instruction appended to every prompt."""
    return (
        f"HARD LIMIT: {max_chars} characters maximum. "
        f"Before outputting, count your characters. "
        f"If the text exceeds {max_chars} chars, rewrite it shorter. "
        f"Write exactly 2 complete sentences. Each must end with a period. "
        f"Output ONLY the final text. No preamble, no explanation."
    )


def resumir_em_gemini(titulos):
    """Gera o Intel Report com isolamento de dados e layout variado."""
    noticias = [n.strip() for n in titulos.split('-') if len(n.strip()) > 8]

    if len(noticias) < 3:
        return "Insufficient data stream for full analysis."

    random.shuffle(noticias)

    n = len(noticias)
    set1 = noticias[:max(1, n // 3)]
    set2 = noticias[n // 3:(2 * n) // 3]
    set3 = noticias[(2 * n) // 3:]

    limit = _char_limit_instruction()

    # --- Chamadas para o Gemini ---
    post_1 = gemini_gerar_tweet(
        f"You are a cynical ex-Goldman quant. No hashtags/emojis. "
        f"Analyze ONLY: {set1}. Find the institutional trap. "
        f"DO NOT summarize the headlines — extract the subtext and implication. "
        f"IMPORTANT: find the single hidden thread connecting ALL these headlines. "
        f"Do not treat each headline separately — synthesize them into one unified insight. "
        f"Start with a verb or number. "
        f"FORBIDDEN words: liquidity, bullish, bearish, DYOR. "
        f"{limit}"
    ).strip()

    post_2 = gemini_gerar_tweet(
        f"You are a protocol archaeologist. No hashtags/emojis. "
        f"Analyze ONLY: {set2}. Interpret what the infrastructure reveals and hides. "
        f"DO NOT summarize the headlines — extract the subtext and implication. "
        f"IMPORTANT: find the single hidden thread connecting ALL these headlines. "
        f"Do not treat each headline separately — synthesize them into one unified insight. "
        f"FORBIDDEN words: liquidity, liquidation, exit. "
        f"{limit}"
    ).strip()

    post_3 = gemini_gerar_tweet(
        f"You are a sovereign risk analyst. No hashtags/emojis. "
        f"Analyze ONLY: {set3}. Connect to macro power dynamics. "
        f"DO NOT summarize the headlines — extract the subtext and implication. "
        f"IMPORTANT: find the single hidden thread connecting ALL these headlines. "
        f"Do not treat each headline separately — synthesize them into one unified insight. "
        f"FORBIDDEN words: liquidity, liquidation, institutional. "
        f"Your second sentence MUST end with: 'Logic dictates 42.' "
        f"{limit}"
    ).strip()

    post_4 = gemini_gerar_tweet(
        f"You are a literary curator for people who lost faith in financial systems but not in language. "
        f"Choose the single most resonant quote from this verified list that fits the SUBTEXT of: {noticias[:3]}. "
        f"VERIFIED QUOTES (use ONLY these, word for word): "
        f"1. \'One must imagine Sisyphus happy.\' — Camus "
        f"2. \'It is not the strongest of the species that survives, but the most adaptable.\' — Darwin "
        f"3. \'The most courageous act is still to think for yourself. Aloud.\' — Coco Chanel "
        f"4. \'In a time of deceit, telling the truth is a revolutionary act.\' — Orwell "
        f"5. \'God is dead. God remains dead. And we have killed him.\' — Nietzsche "
        f"6. \'I am not afraid of storms, for I am learning how to sail my ship.\' — Alcott "
        f"7. \'The only way to deal with an unfree world is to become so absolutely free that your very existence is an act of rebellion.\' — Camus "
        f"8. \'To live is to suffer, to survive is to find some meaning in the suffering.\' — Nietzsche "
        f"9. \'I have not failed. I\'ve just found 10,000 ways that won\'t work.\' — Edison "
        f"10. \'He who has a why to live can bear almost any how.\' — Nietzsche "
        f"11. \'The show must go on, but the actors have forgotten their lines.\' — Cioran "
        f"12. \'I am tired of being a human being.\' — Bukowski "
        f"13. \'In the beginning was the Word, and the Word was with God... and the Word was a lie.\' — Cioran "
        f"14. \'There is but one truly serious philosophical problem, and that is suicide.\' — Camus "
        f"15. \'What is done out of love always takes place beyond good and evil.\' — Nietzsche "
        f"16. \'The gods too are fond of a joke.\' — Aristotle "
        f"17. \'Man is the only animal that must be encouraged to live.\' — Nietzsche "
        f"18. \'You can ignore reality, but you cannot ignore the consequences of ignoring reality.\' — Rand "
        f"19. \'The distinguishing mark of man is the hand, the instrument with which he does all his mischief.\' — Orwell "
        f"20. \'It was a bright cold day in April, and the clocks were striking thirteen.\' — Orwell "
        f"Pick the one that feels inevitable given the headlines. "
        f"Format exactly: \'Quote text\' — Author. "
        f"Max 200 chars. No intro, no emojis. Output ONLY the formatted quote."
    ).strip()

    # --- UI / Formatação ---
    headers = [
        "🔥 @crypto42alpha — INTEL REPORT",
        "📡 @crypto42alpha — SIGNAL DETECTED",
        "📊 @crypto42alpha — MACRO DECODING",
        "🧿 @crypto42alpha — THE 42 PROTOCOL",
        "⚡ @crypto42alpha — DISPATCH",
    ]

    bullets_set = [
        ("I", "II", "III", "IV"),
        ("01", "02", "03", "04"),
        ("[TAPE]", "[PLUMBING]", "[DECODING]", "[ECHO]"),
        ("● ALPHA", "● INFRA", "● MACRO", "● VOX"),
        ("▸ SIGNAL", "▸ STRUCTURE", "▸ POWER", "▸ RESONANCE"),
    ]

    header = random.choice(headers)
    b1, b2, b3, b4 = random.choice(bullets_set)

    return (
        f"{header}\n\n"
        f"{b1}:\n{post_1}\n\n"
        f"{b2}:\n{post_2}\n\n"
        f"{b3}:\n{post_3}\n\n"
        f"{b4}:\n{post_4}"
    )
