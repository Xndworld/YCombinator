#!/usr/bin/env python3
"""
Red Bull Basement 2026 — Gerador de Respostas para Edital
==========================================================

Lê os top 50 do ranking geral (banco_geral_ranking.csv) e gera, para cada
startup, as respostas prontas para o formulário oficial do Red Bull Basement
2026, campo a campo, exportando uma planilha CSV completa.

Saída: redbull_basement_top50.csv

Uso:
    python redbull_basement_generator.py
    python redbull_basement_generator.py --top 10
    python redbull_basement_generator.py --ranking banco_geral_ranking.csv
    python redbull_basement_generator.py --model claude-haiku-4-5-20251001
"""

import csv
import json
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ============================================================================
# CONSTANTES
# ============================================================================

DEFAULT_RANKING_FILE = "banco_geral_ranking.csv"
DEFAULT_OUTPUT_FILE  = "redbull_basement_top50.csv"
CHECKPOINT_FILE      = "redbull_basement_checkpoint.json"
DEFAULT_MODEL        = "claude-sonnet-4-6"
DEFAULT_TOP_N        = 50

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

# ============================================================================
# PROMPT PRINCIPAL
# ============================================================================

SYSTEM_PROMPT = """Você é um especialista em editais de inovação para startups.
Sua missão é ler o documento de apresentação de uma startup e transformá-lo em
respostas prontas para preencher o formulário oficial do Red Bull Basement 2026,
campo a campo, na ordem exata do formulário.

Use linguagem direta, jovem e impactante. Sem bullets. Texto corrido.
Respeite rigorosamente os limites de caracteres indicados.
Retorne APENAS JSON válido, sem texto antes ou depois."""

def build_user_prompt(problema: str, descricao: str, desenvolvimento: str) -> str:
    return f"""Cole o documento da sua startup abaixo:
================================================
NOME DO PROBLEMA: {problema}

DESCRIÇÃO: {descricao}

DESENVOLVIMENTO / OPORTUNIDADE: {desenvolvimento}
================================================

Gere as respostas para cada campo na ordem abaixo e retorne como JSON com
exatamente estas chaves. Respeite os limites de caracteres:

{{
  "campo_1_ideia": "<até 250 chars — O QUÊ é a solução, PARA QUEM serve e QUAL é o diferencial>",
  "campo_2_publico": "<até 400 chars — Perfil do usuário, contexto, dor principal e por que a solução é para eles>",
  "campo_3_problemas": "<até 400 chars — 2-3 problemas concretos com escala e urgência>",
  "campo_4_como_funciona": "<até 400 chars — Funcionamento prático, tecnologia usada, resultado concreto>",
  "campo_5a_nome_startup": "<até 4 palavras — nome memorável e contemporâneo>",
  "campo_5b_resumo_card": "<até 150 chars — versão ultra-resumida do campo 1>",
  "campo_5c_publico_card": "<até 400 chars — versão revisada do campo 2, ainda mais direta>",
  "campo_5d_problema_card": "<até 400 chars — versão revisada do campo 3, mantenha urgência>",
  "campo_5e_solucao_card": "<até 400 chars — versão revisada do campo 4, fácil de entender em 5 segundos>",
  "pitch_60_segundos": "<~130 palavras — roteiro de pitch falado estruturado em 5 blocos: [0-10s] GANCHO, [10-22s] PROBLEMA, [22-35s] SOLUÇÃO, [35-47s] TRAÇÃO, [47-60s] CHAMADA FINAL. Tom: confiante, humano, apaixonado>"
}}

REGRAS CRÍTICAS:
- campo_1_ideia: máximo 250 caracteres
- campo_2_publico: máximo 400 caracteres
- campo_3_problemas: máximo 400 caracteres
- campo_4_como_funciona: máximo 400 caracteres
- campo_5a_nome_startup: máximo 4 palavras
- campo_5b_resumo_card: máximo 150 caracteres
- campo_5c_publico_card: máximo 400 caracteres
- campo_5d_problema_card: máximo 400 caracteres
- campo_5e_solucao_card: máximo 400 caracteres
- pitch_60_segundos: aproximadamente 130 palavras
- A solução DEVE mencionar uso de IA ou tecnologia
- O problema DEVE ter senso de urgência e escala
- Linguagem jovem, direta, sem excesso de termos técnicos
- Retorne APENAS JSON válido"""


# ============================================================================
# GERAÇÃO VIA API
# ============================================================================

def gerar_respostas(
    client: "anthropic.Anthropic",
    ranking: int,
    problema: str,
    descricao: str,
    desenvolvimento: str,
    model: str = DEFAULT_MODEL,
    max_retries: int = 3,
) -> dict:
    """Chama a API Claude para gerar as respostas do formulário."""
    prompt = build_user_prompt(problema, descricao, desenvolvimento)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()

            # Remove possíveis blocos markdown ```json ... ```
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            data = json.loads(raw)

            # Enforce limits (truncate silently if over)
            limits = {
                "campo_1_ideia": 250,
                "campo_2_publico": 400,
                "campo_3_problemas": 400,
                "campo_4_como_funciona": 400,
                "campo_5b_resumo_card": 150,
                "campo_5c_publico_card": 400,
                "campo_5d_problema_card": 400,
                "campo_5e_solucao_card": 400,
            }
            for key, limit in limits.items():
                if key in data and len(data[key]) > limit:
                    data[key] = data[key][:limit]

            return data

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"    [!] Tentativa {attempt}/{max_retries} falhou (parse): {e}")
        except Exception as e:
            print(f"    [!] Tentativa {attempt}/{max_retries} falhou (api): {e}")
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"    Aguardando {wait}s antes de tentar novamente...")
                time.sleep(wait)

    # Fallback: retorna dicionário vazio marcado como erro
    return {k: "ERRO_GERACAO" for k in [
        "campo_1_ideia", "campo_2_publico", "campo_3_problemas",
        "campo_4_como_funciona", "campo_5a_nome_startup", "campo_5b_resumo_card",
        "campo_5c_publico_card", "campo_5d_problema_card", "campo_5e_solucao_card",
        "pitch_60_segundos",
    ]}


# ============================================================================
# CHECKPOINT
# ============================================================================

def load_checkpoint(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================================
# LEITURA DO RANKING
# ============================================================================

def ler_top_n(ranking_file: str, top_n: int) -> list[dict]:
    """Lê os top N registros do CSV de ranking."""
    rows = []
    with open(ranking_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Ordenar por ranking (coluna numérica)
    rows.sort(key=lambda r: int(r.get("ranking", 9999)))
    return rows[:top_n]


# ============================================================================
# EXPORTAÇÃO CSV
# ============================================================================

def salvar_csv(output_file: str, resultados: list[dict]):
    """Salva os resultados no CSV de saída."""
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(resultados)
    print(f"\n[✓] Planilha salva em: {output_file}  ({len(resultados)} startups)")


# ============================================================================
# MODO OFFLINE (sem API key) — preenche template vazio
# ============================================================================

def gerar_template_vazio(ranking: int, problema: str) -> dict:
    """Retorna linha com placeholders para preenchimento manual."""
    return {
        "ranking": ranking,
        "nome_problema": problema,
        "campo_1_ideia": "[PREENCHER — até 250 chars: O QUÊ, PARA QUEM, DIFERENCIAL]",
        "campo_2_publico": "[PREENCHER — até 400 chars: perfil, contexto, dor, por que essa solução]",
        "campo_3_problemas": "[PREENCHER — até 400 chars: 2-3 problemas concretos com escala e urgência]",
        "campo_4_como_funciona": "[PREENCHER — até 400 chars: funcionamento, tecnologia, resultado concreto]",
        "campo_5a_nome_startup": "[PREENCHER — até 4 palavras]",
        "campo_5b_resumo_card": "[PREENCHER — até 150 chars]",
        "campo_5c_publico_card": "[PREENCHER — até 400 chars]",
        "campo_5d_problema_card": "[PREENCHER — até 400 chars]",
        "campo_5e_solucao_card": "[PREENCHER — até 400 chars]",
        "pitch_60_segundos": "[PREENCHER — ~130 palavras: GANCHO / PROBLEMA / SOLUÇÃO / TRAÇÃO / CHAMADA FINAL]",
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Gera planilha de respostas do edital Red Bull Basement 2026 para os top 50 do ranking."
    )
    parser.add_argument(
        "--ranking", default=DEFAULT_RANKING_FILE,
        help=f"CSV de ranking (padrão: {DEFAULT_RANKING_FILE})"
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT_FILE,
        help=f"CSV de saída (padrão: {DEFAULT_OUTPUT_FILE})"
    )
    parser.add_argument(
        "--top", type=int, default=DEFAULT_TOP_N,
        help=f"Quantas startups processar (padrão: {DEFAULT_TOP_N})"
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Modelo Claude (padrão: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--template-only", action="store_true",
        help="Gerar planilha só com templates/placeholders, sem chamar a API"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Delay em segundos entre chamadas de API (padrão: 0.5)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  RED BULL BASEMENT 2026 — Gerador de Respostas")
    print("=" * 60)

    # Verificar arquivo de ranking
    if not os.path.exists(args.ranking):
        print(f"[ERRO] Arquivo de ranking não encontrado: {args.ranking}")
        sys.exit(1)

    # Ler top N
    top_startups = ler_top_n(args.ranking, args.top)
    print(f"[+] {len(top_startups)} startups carregadas do ranking")

    # Determinar modo de execução
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    use_api = HAS_ANTHROPIC and api_key and not args.template_only

    if args.template_only:
        print("[+] Modo: template-only (sem API)")
    elif not HAS_ANTHROPIC:
        print("[!] Biblioteca 'anthropic' não instalada. Gerando templates vazios.")
        print("    Para instalar: pip install anthropic")
        use_api = False
    elif not api_key:
        print("[!] ANTHROPIC_API_KEY não configurada. Gerando templates vazios.")
        print("    Configure com: export ANTHROPIC_API_KEY=sua_chave")
        use_api = False
    else:
        print(f"[+] Modo: API Claude ({args.model})")

    # Carregar checkpoint
    checkpoint = load_checkpoint(CHECKPOINT_FILE)
    client = None
    if use_api:
        client = anthropic.Anthropic(api_key=api_key)

    resultados = []
    novos = 0

    for i, row in enumerate(top_startups):
        ranking_num = int(row.get("ranking", i + 1))
        problema    = row.get("problema", "").strip()
        descricao   = row.get("descricao", "").strip()
        desenvolvimento = row.get("desenvolvimento", "").strip()

        checkpoint_key = str(ranking_num)
        prefixo = f"[{i+1}/{len(top_startups)}] #{ranking_num}"

        # Se já foi processado e salvo no checkpoint, reutilizar
        if checkpoint_key in checkpoint:
            print(f"{prefixo} (cache) {problema[:60]}...")
            resultado = checkpoint[checkpoint_key]
        else:
            print(f"{prefixo} Processando: {problema[:60]}...")

            if use_api:
                campos = gerar_respostas(
                    client, ranking_num, problema, descricao, desenvolvimento,
                    model=args.model
                )
            else:
                campos = gerar_template_vazio(ranking_num, problema)

            resultado = {
                "ranking": ranking_num,
                "nome_problema": problema,
                **campos,
            }

            # Salvar no checkpoint
            checkpoint[checkpoint_key] = resultado
            save_checkpoint(CHECKPOINT_FILE, checkpoint)
            novos += 1

            if use_api and args.delay > 0:
                time.sleep(args.delay)

        resultados.append(resultado)

    # Ordenar por ranking antes de salvar
    resultados.sort(key=lambda r: int(r.get("ranking", 9999)))

    salvar_csv(args.output, resultados)

    print(f"[+] Novos processados via API: {novos}")
    print(f"[+] Reaproveitados do cache:   {len(resultados) - novos}")
    if os.path.exists(CHECKPOINT_FILE):
        print(f"[+] Checkpoint salvo em: {CHECKPOINT_FILE}")
    print("\nColunas na planilha:")
    for col in OUTPUT_COLUMNS:
        print(f"   • {col}")
    print("\nConcluído!")


if __name__ == "__main__":
    main()
