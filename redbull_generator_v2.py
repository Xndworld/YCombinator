#!/usr/bin/env python3
"""
Red Bull Basement 2026 - Application Form Generator
Generates responses for top 50 startups from banco_geral_ranking.csv
"""

import csv
import json
import os
import sys
import time

import anthropic

# ── Config ────────────────────────────────────────────────────────────────────
CSV_INPUT = "/home/user/YCombinator/banco_geral_ranking.csv"
CHECKPOINT_FILE = "/home/user/YCombinator/redbull_basement_checkpoint.json"
CSV_OUTPUT = "/home/user/YCombinator/redbull_basement_top50.csv"
MODEL = "claude-haiku-4-5-20251001"

OUTPUT_COLUMNS = [
    "ranking",
    "nome_problema",
    "campo_1_ideia",
    "campo_2_publico",
    "campo_3_problemas",
    "campo_4_como_funciona",
    "campo_5a_nome_startup",
    "campo_5b_resumo_card",
    "campo_5c_publico_card",
    "campo_5d_problema_card",
    "campo_5e_solucao_card",
    "pitch_60_segundos",
]

CHAR_LIMITS = {
    "campo_1_ideia": 250,
    "campo_2_publico": 400,
    "campo_3_problemas": 400,
    "campo_4_como_funciona": 400,
    "campo_5a_nome_startup": 60,   # "up to 4 words" — generous char buffer
    "campo_5b_resumo_card": 150,
    "campo_5c_publico_card": 400,
    "campo_5d_problema_card": 400,
    "campo_5e_solucao_card": 400,
    "pitch_60_segundos": 1500,     # ~130 words, generous
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_api_client():
    """Return an Anthropic client using env var or OAuth token file."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        fd_str = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR")
        if fd_str:
            try:
                fd = int(fd_str)
                with os.fdopen(fd, "r") as fh:
                    api_key = fh.read().strip()
            except Exception as e:
                print(f"  [warn] Could not read OAuth token fd: {e}")
    if not api_key:
        raise RuntimeError("No API key found. Set ANTHROPIC_API_KEY.")
    return anthropic.Anthropic(api_key=api_key)


def truncate(text: str, limit: int) -> str:
    if isinstance(text, str) and len(text) > limit:
        return text[:limit]
    return text or ""


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Filter out entries that are still placeholders
        valid = {}
        for k, v in data.items():
            if isinstance(v.get("campo_1_ideia"), str) and v["campo_1_ideia"].startswith("[PREENCHER"):
                continue
            valid[str(k)] = v
        return valid
    return {}


def save_checkpoint(checkpoint: dict):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def read_top50():
    with open(CSV_INPUT, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    rows_sorted = sorted(rows, key=lambda x: int(x["ranking"]))
    return rows_sorted[:50]


def build_prompt(startup: dict) -> str:
    problema = startup.get("problema", "")
    descricao = startup.get("descricao", "")
    desenvolvimento = startup.get("desenvolvimento", "")

    return f"""Você vai gerar os campos de inscrição para o Red Bull Basement 2026 para a seguinte startup/problema:

PROBLEMA: {problema}

DESCRIÇÃO: {descricao}

DESENVOLVIMENTO/OPORTUNIDADE: {desenvolvimento}

Gere EXATAMENTE este JSON com as 10 chaves abaixo. Linguagem jovem, direta, impactante, em português brasileiro. Sem bullets, texto corrido.

{{
  "campo_1_ideia": "Até 250 chars — O QUÊ é a solução, PARA QUEM serve e QUAL é o diferencial.",
  "campo_2_publico": "Até 400 chars — Perfil do usuário, contexto de uso, dor principal, por que essa solução é para eles.",
  "campo_3_problemas": "Até 400 chars — 2 a 3 problemas concretos com escala e urgência, sem bullets.",
  "campo_4_como_funciona": "Até 400 chars — Como a solução funciona na prática, qual tecnologia de IA é usada, qual resultado concreto entrega.",
  "campo_5a_nome_startup": "Até 4 palavras — nome memorável e contemporâneo para a startup.",
  "campo_5b_resumo_card": "Até 150 chars — versão ultra-resumida do campo_1_ideia.",
  "campo_5c_publico_card": "Até 400 chars — versão revisada e mais impactante do campo_2_publico.",
  "campo_5d_problema_card": "Até 400 chars — versão revisada e mais impactante do campo_3_problemas.",
  "campo_5e_solucao_card": "Até 400 chars — versão revisada e mais impactante do campo_4_como_funciona.",
  "pitch_60_segundos": "Cerca de 130 palavras — roteiro de pitch falado com 5 blocos: [0-10s] GANCHO, [10-22s] PROBLEMA, [22-35s] SOLUÇÃO, [35-47s] TRAÇÃO, [47-60s] CHAMADA FINAL."
}}

Retorne APENAS o JSON válido, sem texto antes ou depois."""


def call_api(client: anthropic.Anthropic, startup: dict) -> dict:
    """Call Claude API and return parsed JSON response."""
    user_prompt = build_prompt(startup)

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="Você é especialista em editais de inovação. Gere respostas para o Red Bull Basement 2026. Linguagem jovem, direta. Retorne APENAS JSON válido.",
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = message.content[0].text.strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first line (```json or ```) and last line (```)
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        content = "\n".join(lines).strip()

    return json.loads(content)


def apply_limits(data: dict) -> dict:
    """Enforce character limits on all fields."""
    result = {}
    for field, limit in CHAR_LIMITS.items():
        val = data.get(field, "")
        result[field] = truncate(val, limit)
    return result


def save_csv(checkpoint: dict):
    """Save final CSV from checkpoint data."""
    rows = sorted(checkpoint.values(), key=lambda x: int(x.get("ranking", 0)))

    with open(CSV_OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=== Red Bull Basement 2026 Generator ===\n")

    # Load data
    top50 = read_top50()
    print(f"Loaded {len(top50)} startups from CSV")

    # Load checkpoint (only valid/complete entries)
    checkpoint = load_checkpoint()
    print(f"Found {len(checkpoint)} valid entries in checkpoint\n")

    # Init API client
    client = get_api_client()
    print(f"API client initialized\n")

    # Process each startup
    for i, startup in enumerate(top50, 1):
        ranking = str(startup["ranking"])
        nome_problema = startup.get("problema", "")[:100]

        if ranking in checkpoint:
            print(f"[{i:02d}/50] Ranking {ranking} — already done, skipping")
            continue

        print(f"[{i:02d}/50] Ranking {ranking} — {nome_problema[:60]}...")

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                raw = call_api(client, startup)
                fields = apply_limits(raw)

                entry = {
                    "ranking": int(ranking),
                    "nome_problema": startup.get("problema", ""),
                    **fields,
                }

                checkpoint[ranking] = entry
                save_checkpoint(checkpoint)
                print(f"  ✓ Done (nome_startup: {fields.get('campo_5a_nome_startup', '?')})")
                break

            except json.JSONDecodeError as e:
                print(f"  [attempt {attempt}] JSON parse error: {e}")
                if attempt == retries:
                    print(f"  ✗ Failed after {retries} attempts — skipping")
            except Exception as e:
                print(f"  [attempt {attempt}] Error: {e}")
                if attempt == retries:
                    print(f"  ✗ Failed after {retries} attempts — skipping")
                else:
                    time.sleep(2 ** attempt)

        # Small delay to be nice to the API
        time.sleep(0.5)

    # Save CSV
    print("\n=== Saving CSV ===")
    row_count = save_csv(checkpoint)
    print(f"Saved {row_count} rows to {CSV_OUTPUT}")
    print("\nDone!")


if __name__ == "__main__":
    main()
