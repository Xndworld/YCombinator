#!/usr/bin/env python3
"""
Bars Judge Agent - Avaliador de 500 Temas/Problemas de Startup
==============================================================

Agente que avalia ~500 problemas/oportunidades usando o framework de avaliação
baseado em Y Combinator, Lean Startup, Peter Thiel, Reid Hoffman e outros.

Modos de operação:
    --mode api       : Usa a API do Claude para avaliar (mais preciso, requer ANTHROPIC_API_KEY)
    --mode heuristic : Usa análise textual heurística (rápido, sem API)

Uso:
    # Modo heurístico (sem API key necessária)
    python bars_judge_agent.py --mode heuristic

    # Modo API (requer API key)
    export ANTHROPIC_API_KEY="sua-chave-aqui"
    python bars_judge_agent.py --mode api

    # Executar com limite de problemas (para teste)
    python bars_judge_agent.py --mode heuristic --limit 10

    # Retomar execução anterior (usa checkpoint)
    python bars_judge_agent.py --mode api --resume

Saída:
    - avaliacao_500_temas_ranking.csv (CSV unificado com todas as pontuações e ranking)
    - checkpoint_avaliacao.json (checkpoint para retomada)
"""

import csv
import json
import math
import os
import re
import sys
import time
import argparse
import glob as glob_module
from pathlib import Path
from typing import Optional

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ============================================================================
# FRAMEWORK DE AVALIAÇÃO
# ============================================================================

FRAMEWORK = {
    "1_dor_comportamento": {
        "nome": "Natureza da Dor e Comportamento",
        "criterios": [
            {"id": "dor_financeira", "nome": "Intensidade da dor financeira", "peso": 5,
             "descricao": "O problema causa perda direta de dinheiro? (Michael Seibel: as melhores dores afetam a receita)"},
            {"id": "gambiarras", "nome": "Existência de Gambiarras/Workarounds", "peso": 5,
             "descricao": "Os usuários já usam planilhas, WhatsApp ou processos manuais para tentar resolver? (Steve Blank: prova definitiva de demanda)"},
            {"id": "frequencia", "nome": "Frequência do problema", "peso": 5,
             "descricao": "Acontece várias vezes ao dia/semana? (YC: alta frequência constrói o hábito)"},
            {"id": "urgencia", "nome": "Urgência percebida", "peso": 4,
             "descricao": "O usuário sabe que tem o problema e está ativamente buscando solução? (Eric Ries: não eduque o mercado no início)"},
            {"id": "dor_tempo", "nome": "Intensidade da dor de tempo", "peso": 4,
             "descricao": "Causa desperdício massivo de horas produtivas?"},
            {"id": "risco", "nome": "Risco atrelado ao problema", "peso": 4,
             "descricao": "Gera multas, processos, acidentes ou churn para quem sofre?"},
            {"id": "frustracao", "nome": "Nível de frustração/Fricção", "peso": 4,
             "descricao": "O quão estressante é lidar com o processo atual?"},
            {"id": "consequencia_erro", "nome": "Consequência do erro", "peso": 4,
             "descricao": "Falhar nesse processo custa o emprego ou a empresa do usuário?"},
            {"id": "observabilidade", "nome": "Observabilidade do comportamento", "peso": 3,
             "descricao": "Dá para ver o usuário sofrendo com isso, ou é algo puramente mental/subjetivo? (Lean Startup)"},
            {"id": "clareza_persona", "nome": "Clareza de quem sofre", "peso": 3,
             "descricao": "É possível descrever a persona exata que sofre a dor extrema? (Persona de Steve Blank)"},
        ]
    },
    "2_mercado_escala": {
        "nome": "Tamanho de Mercado e Potencial de Escala",
        "criterios": [
            {"id": "tam", "nome": "Tamanho de Mercado Total - TAM", "peso": 5,
             "descricao": "O tema afeta um mercado que movimenta bilhões globalmente ou bilhões de reais localmente?"},
            {"id": "crescimento", "nome": "Crescimento do Mercado", "peso": 5,
             "descricao": "O mercado está expandindo ano a ano? (Sam Altman: prefira um mercado pequeno crescendo rápido do que um grande estagnado)"},
            {"id": "monopolio_local", "nome": "Capacidade de ser um monopólio local/nicho", "peso": 4,
             "descricao": "Dá para dominar um sub-nicho antes de expandir? (Peter Thiel: Zero to One)"},
            {"id": "amplitude", "nome": "Amplitude demográfica", "peso": 3,
             "descricao": "Afeta grandes massas ou a maioria das empresas de um setor?"},
            {"id": "escala_nao_linear", "nome": "Escalabilidade não-linear", "peso": 4,
             "descricao": "A solução teórica para este tema exigirá custo marginal zero? (ex: software vs. serviço braçal). (Reid Hoffman)"},
            {"id": "ticket", "nome": "Tamanho do ticket natural", "peso": 3,
             "descricao": "O tema sugere contratos de alto valor (Enterprise) ou alto volume (B2C)?"},
            {"id": "expansao", "nome": "Potencial de expansão de produto", "peso": 3,
             "descricao": "O problema abre portas para resolver problemas adjacentes no futuro?"},
            {"id": "penetracao_digital", "nome": "Penetração digital do setor", "peso": 3,
             "descricao": "O mercado-alvo já usa tecnologia básica ou ainda é 100% analógico e resistente?"},
            {"id": "internacionalizacao", "nome": "Capacidade de internacionalização", "peso": 2,
             "descricao": "É um problema global ou restrito à cultura local?"},
            {"id": "dep_infraestrutura", "nome": "Dependência de infraestrutura física", "peso": 2,
             "descricao": "Resolver isso exige construir fábricas ou logística complexa? (Pesos invertidos: mais dependência = menor nota)"},
        ]
    },
    "3_timing": {
        "nome": "Timing e Why Now",
        "criterios": [
            {"id": "timing_tech", "nome": "Timing Tecnológico", "peso": 5,
             "descricao": "Novas tecnologias (ex: LLMs, novas APIs) tornaram viável resolver isso agora?"},
            {"id": "timing_regulatorio", "nome": "Timing Regulatório", "peso": 5,
             "descricao": "Leis novas (ex: Open Finance, regulação climática, LGPD) forçam o mercado a adotar soluções?"},
            {"id": "mudanca_comportamental", "nome": "Mudança Comportamental/Demográfica", "peso": 4,
             "descricao": "O tema surfa uma onda social inevitável (ex: Geração Z no trabalho, envelhecimento populacional)?"},
            {"id": "pressao_macro", "nome": "Pressão Macroeconômica", "peso": 4,
             "descricao": "Crises, inflação ou juros altos tornam a resolução deste problema inadiável por economia de custo?"},
            {"id": "janela", "nome": "Janela de Oportunidade", "peso": 4,
             "descricao": "O mercado está começando a acordar para isso, mas os gigantes ainda são lentos? (Marc Andreessen)"},
        ]
    },
    "4_validacao_lean": {
        "nome": "Validação e Execução Lean",
        "criterios": [
            {"id": "acesso_usuarios", "nome": "Acesso aos Usuários", "peso": 5,
             "descricao": "Os empreendedores conseguem encontrar e falar com quem tem o problema facilmente? (Ash Maurya: Canais no Lean Canvas)"},
            {"id": "velocidade_validacao", "nome": "Velocidade de Validação", "peso": 5,
             "descricao": "É possível testar o interesse no tema em semanas com entrevistas ou landing pages?"},
            {"id": "facilidade_mvp", "nome": "Facilidade de criar o MVP", "peso": 4,
             "descricao": "A primeira versão da solução pode ser feita em no-code ou serviço manual (Concierge MVP)? (Eric Ries)"},
            {"id": "mudanca_habito", "nome": "Necessidade de mudança de hábito", "peso": 4,
             "descricao": "O usuário precisa mudar drasticamente como vive para adotar a solução futura? (Nota alta se NÃO precisa)"},
            {"id": "dados_disponiveis", "nome": "Densidade de dados disponíveis", "peso": 3,
             "descricao": "Já existem dados de mercado, relatórios ou APIs disponíveis para construir em cima?"},
            {"id": "aha_moment", "nome": "Tempo de adoção / Aha Moment", "peso": 3,
             "descricao": "Dá para entregar valor nos primeiros minutos de uso?"},
            {"id": "multiplos_lados", "nome": "Dependência de múltiplos lados", "peso": 3,
             "descricao": "O tema exige criar um marketplace complexo logo no dia 1 (problema do ovo e da galinha)?"},
            {"id": "feedback", "nome": "Visibilidade de feedback", "peso": 3,
             "descricao": "A startup saberá rapidamente se falhou ao tentar resolver o problema?"},
        ]
    },
    "5_monetizacao": {
        "nome": "Monetização e Viabilidade de Negócio",
        "criterios": [
            {"id": "wtp", "nome": "Disposição a Pagar / WTP", "peso": 5,
             "descricao": "Os clientes têm capacidade financeira e histórico de pagar para resolver dores similares? (Marty Cagan: Value Risk)"},
            {"id": "clareza_pagador", "nome": "Clareza de quem paga", "peso": 5,
             "descricao": "O usuário final é o pagador, ou depende de publicidade/terceiros? (Sempre priorize quando quem sofre a dor é quem paga)"},
            {"id": "orcamento", "nome": "Orçamento pré-existente", "peso": 4,
             "descricao": "As empresas já têm um budget alocado onde essa solução pode entrar (ex: verba de marketing, segurança)?"},
            {"id": "ciclo_vendas", "nome": "Ciclo de Vendas B2B", "peso": 3,
             "descricao": "O tema sugere vendas que demoram 1 mês (ótimo) ou 18 meses (péssimo para startups iniciantes)?"},
            {"id": "recorrencia", "nome": "Frequência de monetização", "peso": 3,
             "descricao": "Permite modelo de receita recorrente (SaaS/Assinatura)?"},
            {"id": "poder_preco", "nome": "Poder de precificação", "peso": 3,
             "descricao": "O problema é tão grave que a startup poderá ditar o preço (inelasticidade)?"},
            {"id": "cac", "nome": "Custo de Aquisição (CAC) projetado", "peso": 3,
             "descricao": "O tema possui canais orgânicos, virais ou baratos para atrair clientes?"},
        ]
    },
    "6_defensibilidade": {
        "nome": "Defensibilidade e Competição",
        "criterios": [
            {"id": "ausencia_monopolios", "nome": "Ausência de monopólios estabelecidos", "peso": 4,
             "descricao": "O tema já foi resolvido por Google, Microsoft ou um gigante local muito amado? (Peter Thiel: fuja da concorrência extrema)"},
            {"id": "efeito_rede", "nome": "Potencial de Efeito de Rede", "peso": 4,
             "descricao": "Quanto mais pessoas tiverem o problema resolvido, melhor a solução fica para todos? (Helmer: Network Economies)"},
            {"id": "switching_cost", "nome": "Switching Cost futuro", "peso": 4,
             "descricao": "Quem adotar a solução terá muita dificuldade de trocar de fornecedor depois? (Helmer: Switching Costs)"},
            {"id": "dados_proprietarios", "nome": "Acúmulo de Dados Proprietários", "peso": 3,
             "descricao": "A startup vai criar uma base de dados que ninguém mais tem? (Cornered Resource)"},
            {"id": "diferenciacao_10x", "nome": "Diferenciação percebida (10x melhor)", "peso": 3,
             "descricao": "A dor atual é tão mal resolvida que fazer o básico bem feito já parece revolução? (Peter Thiel)"},
            {"id": "fragmentacao", "nome": "Fragmentação da Concorrência", "peso": 2,
             "descricao": "Existem vários players pequenos e ruins (bom sinal) ou um dominando 80% (mau sinal)?"},
        ]
    },
    "7_riscos_fatais": {
        "nome": "Riscos Fatais (Red Flags)",
        "criterios": [
            {"id": "tarpit", "nome": "Risco de Tarpit Idea", "peso": 5,
             "descricao": "Parece uma ideia brilhante, mas centenas já tentaram e morreram pelo mesmo motivo estrutural de aquisição/retenção? (Nota alta = BAIXO risco de tarpit, ou seja, NÃO é armadilha)"},
            {"id": "risco_legal", "nome": "Risco Legal/Regulatório letal", "peso": 4,
             "descricao": "Testar o problema pode dar cadeia ou multas milionárias? (Nota alta = BAIXO risco legal)"},
            {"id": "platform_risk", "nome": "Dependência Crítica de Parceiro (Platform Risk)", "peso": 4,
             "descricao": "O tema depende 100% de uma mudança de API do Facebook, Apple ou Google? (Nota alta = BAIXA dependência)"},
            {"id": "alinhamento_ods", "nome": "Alinhamento com ODS/Banca/Edital", "peso": 3,
             "descricao": "O tema converge com os ODS (Objetivos de Desenvolvimento Sustentável) e o foco em clima/demografia no Brasil exigidos pelos financiadores?"},
        ]
    },
}

# ============================================================================
# PROMPT DO AVALIADOR
# ============================================================================

SYSTEM_PROMPT = """Você é um avaliador especializado em startups e inovação, com profundo conhecimento dos frameworks de:
- Y Combinator (Paul Graham, Michael Seibel)
- Customer Development (Steve Blank)
- Lean Startup (Eric Ries, Ash Maurya)
- Zero to One (Peter Thiel)
- Blitzscaling (Reid Hoffman)
- 7 Powers (Hamilton Helmer)
- Marty Cagan (Product Management)
- Sequoia Capital / Sam Altman (Venture Capital)
- Bill Gross / Marc Andreessen (Timing)

Sua tarefa é avaliar problemas/oportunidades de startup em uma escala de 1 a 10 para cada critério fornecido.

REGRAS DE PONTUAÇÃO:
- 1-2: Muito fraco / Quase inexistente
- 3-4: Fraco / Abaixo da média
- 5-6: Moderado / Na média
- 7-8: Forte / Acima da média
- 9-10: Excepcional / Máximo possível

Para critérios na categoria "Riscos Fatais":
- Nota ALTA (8-10) = o problema TEM BAIXO RISCO (positivo)
- Nota BAIXA (1-3) = o problema TEM ALTO RISCO (negativo/red flag)

Seja rigoroso e diferenciador. Evite dar notas médias (5-6) para tudo.
Considere o contexto de 2026, com as tecnologias e regulações atuais.
Avalie com base no potencial para uma startup early-stage no Brasil e/ou globalmente."""


def build_evaluation_prompt(problema: str, descricao: str, desenvolvimento: str) -> str:
    """Constrói o prompt de avaliação para um problema específico."""

    criterios_text = ""
    for cat_key, cat_data in FRAMEWORK.items():
        criterios_text += f"\n### {cat_data['nome']}\n"
        for c in cat_data["criterios"]:
            criterios_text += f"- **{c['id']}** (Peso {c['peso']}): {c['nome']} — {c['descricao']}\n"

    return f"""Avalie o seguinte problema/oportunidade de startup:

**PROBLEMA:** {problema}

**DESCRIÇÃO GERAL:** {descricao}

**DESENVOLVIMENTO/OPORTUNIDADE:** {desenvolvimento}

---

Avalie CADA critério abaixo com uma nota de 1 a 10. Responda EXCLUSIVAMENTE no formato JSON abaixo, sem texto adicional.

CRITÉRIOS:
{criterios_text}

Responda SOMENTE com o JSON abaixo (sem markdown, sem ```json, sem texto antes ou depois):
{{
  "dor_financeira": <nota>,
  "gambiarras": <nota>,
  "frequencia": <nota>,
  "urgencia": <nota>,
  "dor_tempo": <nota>,
  "risco": <nota>,
  "frustracao": <nota>,
  "consequencia_erro": <nota>,
  "observabilidade": <nota>,
  "clareza_persona": <nota>,
  "tam": <nota>,
  "crescimento": <nota>,
  "monopolio_local": <nota>,
  "amplitude": <nota>,
  "escala_nao_linear": <nota>,
  "ticket": <nota>,
  "expansao": <nota>,
  "penetracao_digital": <nota>,
  "internacionalizacao": <nota>,
  "dep_infraestrutura": <nota>,
  "timing_tech": <nota>,
  "timing_regulatorio": <nota>,
  "mudanca_comportamental": <nota>,
  "pressao_macro": <nota>,
  "janela": <nota>,
  "acesso_usuarios": <nota>,
  "velocidade_validacao": <nota>,
  "facilidade_mvp": <nota>,
  "mudanca_habito": <nota>,
  "dados_disponiveis": <nota>,
  "aha_moment": <nota>,
  "multiplos_lados": <nota>,
  "feedback": <nota>,
  "wtp": <nota>,
  "clareza_pagador": <nota>,
  "orcamento": <nota>,
  "ciclo_vendas": <nota>,
  "recorrencia": <nota>,
  "poder_preco": <nota>,
  "cac": <nota>,
  "ausencia_monopolios": <nota>,
  "efeito_rede": <nota>,
  "switching_cost": <nota>,
  "dados_proprietarios": <nota>,
  "diferenciacao_10x": <nota>,
  "fragmentacao": <nota>,
  "tarpit": <nota>,
  "risco_legal": <nota>,
  "platform_risk": <nota>,
  "alinhamento_ods": <nota>
}}"""


# ============================================================================
# FUNÇÕES DE CÁLCULO
# ============================================================================

def calcular_pontuacoes(notas: dict) -> dict:
    """Calcula pontuações ponderadas por categoria e total."""
    resultado = {}
    total_geral = 0
    max_total = 0

    for cat_key, cat_data in FRAMEWORK.items():
        subtotal = 0
        max_cat = 0
        for criterio in cat_data["criterios"]:
            cid = criterio["id"]
            peso = criterio["peso"]
            nota = notas.get(cid, 5)
            subtotal += nota * peso
            max_cat += 10 * peso
        resultado[f"subtotal_{cat_key}"] = subtotal
        resultado[f"max_{cat_key}"] = max_cat
        resultado[f"pct_{cat_key}"] = round((subtotal / max_cat) * 100, 1) if max_cat > 0 else 0
        total_geral += subtotal
        max_total += max_cat

    resultado["total_geral"] = total_geral
    resultado["max_total"] = max_total
    resultado["pct_total"] = round((total_geral / max_total) * 100, 1) if max_total > 0 else 0

    return resultado


# ============================================================================
# LEITURA DOS CSVs
# ============================================================================

def carregar_problemas(diretorio: str) -> list[dict]:
    """Carrega todos os problemas dos CSVs no diretório."""
    problemas = []
    arquivos_csv = sorted(glob_module.glob(os.path.join(diretorio, "*.csv")))

    if not arquivos_csv:
        print(f"ERRO: Nenhum arquivo CSV encontrado em {diretorio}")
        sys.exit(1)

    for arquivo in arquivos_csv:
        nome_arquivo = os.path.basename(arquivo)
        print(f"  Carregando: {nome_arquivo}")

        # Tentar diferentes encodings
        for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
            try:
                with open(arquivo, "r", encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    count = 0
                    for row in reader:
                        problema = row.get("Problema", "").strip().strip('"')
                        descricao = row.get("Descrição Geral", row.get("Descri\u00e7\u00e3o Geral", "")).strip().strip('"')
                        desenvolvimento = row.get("Desenvolvimento", "").strip().strip('"')

                        if problema:
                            problemas.append({
                                "arquivo_fonte": nome_arquivo,
                                "problema": problema,
                                "descricao": descricao,
                                "desenvolvimento": desenvolvimento,
                            })
                            count += 1
                    print(f"    -> {count} problemas carregados")
                    break
            except (UnicodeDecodeError, KeyError):
                continue

    print(f"\nTotal de problemas carregados: {len(problemas)}")
    return problemas


# ============================================================================
# AVALIAÇÃO VIA API
# ============================================================================

def avaliar_problema(client: anthropic.Anthropic, problema: dict, model: str,
                     max_retries: int = 3) -> Optional[dict]:
    """Avalia um único problema usando a API do Claude."""
    prompt = build_evaluation_prompt(
        problema["problema"],
        problema["descricao"],
        problema["desenvolvimento"],
    )

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            texto = response.content[0].text.strip()

            # Limpar possíveis marcadores de código
            if texto.startswith("```"):
                texto = texto.split("\n", 1)[1] if "\n" in texto else texto[3:]
            if texto.endswith("```"):
                texto = texto[:-3]
            texto = texto.strip()

            notas = json.loads(texto)

            # Validar que todas as notas estão entre 1 e 10
            for key, val in notas.items():
                if not isinstance(val, (int, float)) or val < 1 or val > 10:
                    notas[key] = max(1, min(10, int(val) if isinstance(val, (int, float)) else 5))

            return notas

        except json.JSONDecodeError as e:
            print(f"    [Tentativa {attempt + 1}] Erro ao parsear JSON: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except anthropic.RateLimitError:
            wait_time = 2 ** (attempt + 2)
            print(f"    [Rate limit] Aguardando {wait_time}s...")
            time.sleep(wait_time)
        except anthropic.APIError as e:
            print(f"    [Tentativa {attempt + 1}] Erro de API: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    return None


# ============================================================================
# AVALIAÇÃO HEURÍSTICA (SEM API)
# ============================================================================

# Mapeamento de palavras-chave para cada critério com seus sinais (+/-) e pesos
KEYWORD_RULES = {
    "dor_financeira": {
        "positivo": [
            "custo", "perda", "receita", "bilhões", "milhões", "falência", "prejuízo",
            "economia", "faturamento", "lucro", "financeiro", "dinheiro", "capital",
            "investimento", "encarecer", "inflação", "preço", "tarif", "orçament",
            "deficit", "gasto", "despesa", "verba", "patrimônio", "pobreza",
            "valor", "mercado", "contrato", "pagamento",
        ],
        "negativo": ["emocional", "psicológico", "subjetivo", "cultural", "estético"],
        "base": 5,
    },
    "gambiarras": {
        "positivo": [
            "manual", "planilha", "whatsapp", "processo manual", "analógico",
            "improviso", "gambiarra", "artesanal", "burocracia", "papel",
            "ineficiente", "obsolet", "legado", "antigo", "precário",
            "informal", "fragmentad", "desorganizad", "workaround",
        ],
        "negativo": ["automatizado", "digital nativo", "já resolvido"],
        "base": 5,
    },
    "frequencia": {
        "positivo": [
            "diário", "diariamente", "semanal", "constante", "crônico", "recorrente",
            "frequente", "contínuo", "permanente", "repetitivo", "rotina", "cotidian",
            "todo dia", "toda semana", "ciclo", "periódico", "sistêmico",
        ],
        "negativo": ["raro", "eventual", "esporádico", "pontual", "uma vez"],
        "base": 5,
    },
    "urgencia": {
        "positivo": [
            "urgente", "crítico", "emergência", "inadiável", "imediato", "agudo",
            "pressão", "colapso", "crise", "risco iminente", "inevitável",
            "forçar", "obrigar", "necessário", "essencial", "vital",
        ],
        "negativo": ["longo prazo", "gradual", "lento", "futuro distante"],
        "base": 5,
    },
    "dor_tempo": {
        "positivo": [
            "horas", "demora", "lento", "burocracia", "espera", "atraso",
            "ciclo longo", "anos", "meses", "produtividade", "tempo",
            "desperdiç", "trava", "bloquei", "paralis", "fila",
            "licenciamento", "aprovação",
        ],
        "negativo": ["rápido", "instantâneo", "ágil", "automático"],
        "base": 5,
    },
    "risco": {
        "positivo": [
            "multa", "processo", "acidente", "morte", "colapso", "cadeia",
            "regulatório", "legal", "compliance", "sanção", "penalidade",
            "risco", "perigo", "segurança", "fatal", "mortalidade",
            "judicializaç", "litígio", "responsa",
        ],
        "negativo": ["seguro", "estável", "controlado", "baixo risco"],
        "base": 5,
    },
    "frustracao": {
        "positivo": [
            "frustrant", "estressant", "humilhant", "sofrimento", "dor",
            "tensão", "conflito", "insatisfaç", "irritant", "desgast",
            "exaust", "burnout", "ansiedade", "angústia", "trauma",
            "abandono", "exclusão", "discrimin",
        ],
        "negativo": ["satisfeito", "confortável", "tranquilo"],
        "base": 5,
    },
    "consequencia_erro": {
        "positivo": [
            "fatal", "catastróf", "irreversível", "destruição", "perda total",
            "morte", "colapso", "apagão", "falência", "desastre",
            "acidente", "contaminação", "epidemia", "pandemia",
            "guerra", "fome", "seca", "inundação",
        ],
        "negativo": ["reversível", "menor", "insignificante", "tolerável"],
        "base": 5,
    },
    "observabilidade": {
        "positivo": [
            "visível", "evidente", "manifesto", "palpável", "concreto",
            "mensurável", "dados", "estatística", "número", "relatório",
            "indicador", "métrica", "registro", "foto", "vídeo",
            "físico", "infraestrutura", "equipamento",
        ],
        "negativo": ["subjetivo", "mental", "invisível", "oculto", "tácito", "intangível"],
        "base": 6,
    },
    "clareza_persona": {
        "positivo": [
            "idoso", "agricultor", "PME", "startup", "médico", "engenheiro",
            "operário", "motorista", "entregador", "professor", "enfermeiro",
            "produtor rural", "minerador", "pescador", "empreendedor",
            "cuidador", "gestor", "trabalhador", "freelancer", "autônomo",
            "paciente", "consumidor", "estudante", "aposentado",
            "empresa", "indústria", "hospital", "escola", "governo",
        ],
        "negativo": ["todos", "genérico", "qualquer pessoa", "sociedade em geral"],
        "base": 6,
    },
    "tam": {
        "positivo": [
            "bilhões", "trilhões", "milhões", "global", "mundial",
            "setor inteiro", "indústria", "cadeia global", "mercado",
            "economia", "PIB", "exportação", "importação", "commodit",
            "energia", "saúde", "agro", "mineração", "financeiro",
            "transporte", "logística", "construção", "telecomunicações",
        ],
        "negativo": ["nicho pequeno", "restrito", "micro", "local apenas"],
        "base": 6,
    },
    "crescimento": {
        "positivo": [
            "crescente", "expansão", "acelerando", "emergente", "boom",
            "exponencial", "dobra", "triplicar", "aumento", "demanda",
            "transição", "descarbonização", "eletrificação", "digitalização",
            "envelhecimento", "urbanização", "migração",
        ],
        "negativo": ["estagnado", "declínio", "saturado", "maduro", "encolhendo"],
        "base": 6,
    },
    "monopolio_local": {
        "positivo": [
            "nicho", "específico", "vertical", "especializado", "segmento",
            "sub-mercado", "regional", "local", "setor", "dominar",
        ],
        "negativo": ["genérico", "horizontal", "amplo demais", "commodity"],
        "base": 6,
    },
    "amplitude": {
        "positivo": [
            "massa", "todos", "universal", "setor inteiro", "milhões",
            "população", "maioria", "grande porte", "abrangente",
            "demográfico", "urbanização", "massivo",
        ],
        "negativo": ["poucos", "nicho minúsculo", "elite", "exclusivo"],
        "base": 5,
    },
    "escala_nao_linear": {
        "positivo": [
            "software", "plataforma", "digital", "SaaS", "API", "algoritmo",
            "IA", "automação", "cloud", "app", "dados", "modelo", "LLM",
            "escalável", "marginal zero", "replicável",
        ],
        "negativo": [
            "braçal", "físico", "logística complexa", "fábrica", "construção",
            "hardware", "manufatura", "presencial", "in loco",
        ],
        "base": 5,
    },
    "ticket": {
        "positivo": [
            "enterprise", "B2B", "contrato", "premium", "alto valor",
            "corporativo", "industrial", "infraestrutura", "governo",
            "bilhões", "milhões", "investimento pesado",
        ],
        "negativo": ["gratuito", "free", "baixo valor", "centavos"],
        "base": 6,
    },
    "expansao": {
        "positivo": [
            "adjacente", "plataforma", "ecossistema", "expandir", "integrar",
            "complementar", "cadeia", "end-to-end", "horizontal",
            "vertical", "diversificar", "portfólio",
        ],
        "negativo": ["único", "isolado", "singular", "one-trick"],
        "base": 6,
    },
    "penetracao_digital": {
        "positivo": [
            "digital", "app", "software", "online", "cloud", "internet",
            "conectado", "smartphone", "computador", "API", "dados",
        ],
        "negativo": [
            "analógico", "manual", "papel", "offline", "resistente a tecnologia",
            "comunidade isolada", "sem internet", "rural remoto",
        ],
        "base": 5,
    },
    "internacionalizacao": {
        "positivo": [
            "global", "mundial", "internacional", "universal", "cross-border",
            "multilateral", "multipais", "export",
        ],
        "negativo": [
            "local", "Brasil", "regional", "cultural", "idioma",
            "legislação local", "IBAMA", "SUS", "Cerrado", "Amazônia",
        ],
        "base": 5,
    },
    "dep_infraestrutura": {  # NOTA INVERTIDA: mais dependência = nota menor
        "positivo": [  # Palavras que indicam POUCA dependência (nota alta)
            "software", "digital", "plataforma", "app", "cloud",
            "remoto", "virtual", "SaaS", "API",
        ],
        "negativo": [  # Palavras que indicam MUITA dependência (nota baixa)
            "fábrica", "logística", "construção", "hardware", "infraestrutura",
            "físico", "mineração", "refino", "transporte", "estrada",
            "ferrovia", "cabo", "usina", "embarcação", "navio",
            "instalação", "planta industrial",
        ],
        "base": 5,
    },
    "timing_tech": {
        "positivo": [
            "IA", "LLM", "inteligência artificial", "machine learning",
            "blockchain", "API", "drone", "IoT", "sensor", "genômica",
            "AR", "realidade aumentada", "VR", "5G", "edge computing",
            "computação quântica", "robótica", "automação", "GPT",
            "generativ", "deep learning", "computer vision", "NLP",
            "satélite", "LIDAR", "3D", "impressão 3D", "biometria",
        ],
        "negativo": ["analógico", "mecânico", "manual", "artesanal"],
        "base": 5,
    },
    "timing_regulatorio": {
        "positivo": [
            "regulação", "lei", "LGPD", "licenciamento", "compliance",
            "norma", "ISO", "Open Finance", "Open Banking", "GDPR",
            "ESG", "carbono", "emissões", "regulament", "legislação",
            "ODS", "Paris", "COP", "tributação", "fiscal", "sanção",
        ],
        "negativo": ["desregulado", "livre", "sem regulação"],
        "base": 5,
    },
    "mudanca_comportamental": {
        "positivo": [
            "Geração Z", "envelhecimento", "silver", "idoso", "demográfico",
            "Gen Z", "millennial", "boomer", "aposentadoria", "longevidade",
            "urbanização", "migração", "digital native", "remoto",
            "home office", "híbrido", "gig economy", "freelancer",
            "sustentabilidade", "vegano", "consciente",
        ],
        "negativo": ["estável", "imutável", "tradicional consolidado"],
        "base": 6,
    },
    "pressao_macro": {
        "positivo": [
            "crise", "inflação", "juros", "escassez", "custo",
            "recessão", "guerra", "geopolítica", "tarifas", "sanções",
            "clima", "aquecimento", "seca", "inundação", "desastre",
            "pandemia", "pobreza", "desigualdade",
        ],
        "negativo": ["estabilidade", "prosperidade", "abundância"],
        "base": 6,
    },
    "janela": {
        "positivo": [
            "emergente", "novo", "início", "despertar", "pioneiro",
            "poucos players", "inexplorado", "greenfield", "ninguém resolve",
            "ausência de soluções", "vácuo", "lacuna", "gap",
        ],
        "negativo": ["saturado", "dominado", "maduro", "consolidado"],
        "base": 6,
    },
    "acesso_usuarios": {
        "positivo": [
            "empresa", "LinkedIn", "associação", "sindicato", "comunidade",
            "feira", "evento", "rede", "fórum", "grupo", "online",
            "B2B", "concentrado", "fácil acesso",
        ],
        "negativo": [
            "difícil acesso", "disperso", "remoto", "isolado",
            "governo", "militar", "classificado",
        ],
        "base": 6,
    },
    "velocidade_validacao": {
        "positivo": [
            "landing page", "entrevista", "pesquisa", "protótipo rápido",
            "no-code", "teste", "MVP", "concierge", "piloto",
            "software", "digital", "online",
        ],
        "negativo": [
            "hardware", "regulação", "certificação", "anos",
            "fábrica", "infraestrutura pesada", "clínico",
        ],
        "base": 5,
    },
    "facilidade_mvp": {
        "positivo": [
            "no-code", "software", "plataforma", "concierge", "serviço manual",
            "consultoria", "planilha", "bot", "automação simples",
            "MVP", "protótipo", "app", "site",
        ],
        "negativo": [
            "hardware", "fábrica", "certificação médica", "regulação pesada",
            "infraestrutura", "construção", "manufatura", "dispositivo",
            "satélite", "embarcação", "navio", "usina",
        ],
        "base": 5,
    },
    "mudanca_habito": {  # NOTA ALTA = NÃO precisa mudar hábito
        "positivo": [  # Palavras que indicam NÃO precisa mudar (nota alta)
            "transparente", "automático", "invisível", "background",
            "plug-and-play", "integrado", "sem esforço", "mesmo workflow",
        ],
        "negativo": [  # Palavras que indicam PRECISA mudar (nota baixa)
            "mudar comportamento", "nova forma", "adotar", "aprender",
            "treinar", "paradigma", "transformação cultural", "resistência",
        ],
        "base": 6,
    },
    "dados_disponiveis": {
        "positivo": [
            "dados", "API", "relatório", "público", "aberto", "open data",
            "estatística", "censo", "pesquisa", "satélite", "sensor",
            "monitoramento", "base de dados", "dataset",
        ],
        "negativo": ["sem dados", "escasso", "proprietário fechado", "inexistente"],
        "base": 5,
    },
    "aha_moment": {
        "positivo": [
            "instantâneo", "rápido", "imediato", "primeiro uso", "visível",
            "resultado tangível", "economia imediata", "alerta", "dashboard",
        ],
        "negativo": [
            "longo prazo", "gradual", "meses para ver resultado",
            "complexo de entender", "abstrato",
        ],
        "base": 5,
    },
    "multiplos_lados": {  # NOTA ALTA = NÃO depende de múltiplos lados
        "positivo": [  # Palavras que indicam simplicidade
            "B2B direto", "vendedor-comprador", "single-sided",
            "ferramenta", "SaaS", "unilateral",
        ],
        "negativo": [  # Palavras que indicam marketplace/multi-sided
            "marketplace", "dois lados", "plataforma bilateral",
            "oferta e demanda", "ovo e galinha", "rede",
        ],
        "base": 6,
    },
    "feedback": {
        "positivo": [
            "mensurável", "métricas", "KPI", "resultado visível",
            "feedback rápido", "teste A/B", "conversão", "engajamento",
            "churn", "NPS", "satisfação",
        ],
        "negativo": ["difícil medir", "subjetivo", "longo prazo", "intangível"],
        "base": 6,
    },
    "wtp": {
        "positivo": [
            "pagar", "investir", "comprar", "orçamento", "verba",
            "contratar", "licença", "assinatura", "premium",
            "B2B", "enterprise", "corporativo", "industrial",
            "seguro", "compliance", "obrigatório",
        ],
        "negativo": [
            "gratuito", "sem dinheiro", "pobreza", "subsistência",
            "governo paga", "filantropia", "ONG",
        ],
        "base": 5,
    },
    "clareza_pagador": {
        "positivo": [
            "B2B", "empresa paga", "pagador direto", "quem sofre paga",
            "corporativo", "industrial", "contrato", "cliente",
        ],
        "negativo": [
            "publicidade", "gratuito", "governo", "terceiro paga",
            "subsídio", "doação", "fundação", "ONG",
        ],
        "base": 6,
    },
    "orcamento": {
        "positivo": [
            "orçamento", "verba", "budget", "alocação", "investimento",
            "capex", "opex", "TI", "marketing", "segurança",
            "compliance", "departamento", "procurement",
        ],
        "negativo": ["sem verba", "novo gasto", "inexistente", "corte"],
        "base": 5,
    },
    "ciclo_vendas": {  # NOTA ALTA = ciclo curto
        "positivo": [
            "self-service", "online", "SaaS", "assinatura", "imediato",
            "teste grátis", "freemium", "PME", "rápido",
        ],
        "negativo": [
            "enterprise longo", "compliance pesado", "licitação",
            "governo", "anos", "comitê", "board",
        ],
        "base": 5,
    },
    "recorrencia": {
        "positivo": [
            "SaaS", "assinatura", "recorrente", "mensal", "anual",
            "plataforma", "monitoramento", "contínuo", "manutenção",
            "serviço", "renovação",
        ],
        "negativo": [
            "one-time", "projeto único", "pontual", "consultoria",
            "instalação única",
        ],
        "base": 6,
    },
    "poder_preco": {
        "positivo": [
            "inelástico", "essencial", "vital", "insubstituível",
            "regulatório", "obrigatório", "compliance", "segurança",
            "vida ou morte", "sem alternativa", "monopol",
        ],
        "negativo": [
            "commodity", "preço baixo", "concorrência de preço",
            "sensível a preço", "genérico",
        ],
        "base": 5,
    },
    "cac": {
        "positivo": [
            "orgânico", "viral", "boca-a-boca", "comunidade", "SEO",
            "content marketing", "referral", "efeito rede",
            "evento", "associação", "conferência",
        ],
        "negativo": [
            "caro adquirir", "pago", "cold call", "outbound pesado",
            "TV", "mídia cara",
        ],
        "base": 5,
    },
    "ausencia_monopolios": {
        "positivo": [
            "fragmentado", "ninguém resolve", "ausência", "vácuo",
            "inexplorado", "greenfield", "poucos players",
            "artesanal", "disperso", "desorganizado",
        ],
        "negativo": [
            "Google", "Microsoft", "Amazon", "Apple", "Facebook",
            "Meta", "dominante", "monopólio", "oligopólio",
            "gigante", "incumbente forte",
        ],
        "base": 7,
    },
    "efeito_rede": {
        "positivo": [
            "rede", "comunidade", "marketplace", "plataforma",
            "colaborativo", "compartilhado", "mais usuários",
            "efeito de rede", "network", "viral",
        ],
        "negativo": ["isolado", "individual", "single-user", "standalone"],
        "base": 5,
    },
    "switching_cost": {
        "positivo": [
            "integrado", "embarcado", "workflow", "dados proprietários",
            "migração difícil", "lock-in", "customizado", "treino",
            "certificação", "conformidade",
        ],
        "negativo": ["fácil trocar", "commodity", "plug-and-play", "genérico"],
        "base": 5,
    },
    "dados_proprietarios": {
        "positivo": [
            "dados únicos", "base exclusiva", "dados que ninguém tem",
            "proprietário", "acúmulo", "histórico", "treinamento",
            "modelo próprio", "dataset", "benchmark", "corpus",
        ],
        "negativo": ["dados públicos", "open source", "commoditizado"],
        "base": 5,
    },
    "diferenciacao_10x": {
        "positivo": [
            "revolução", "disruptivo", "10x", "transformador", "mal resolvido",
            "ninguém faz bem", "precário", "inadequado", "obsoleto",
            "arcaico", "abandono", "negligenciado", "invisível",
        ],
        "negativo": ["já bom", "satisfatório", "funcional", "bem servido"],
        "base": 6,
    },
    "fragmentacao": {
        "positivo": [
            "fragmentado", "vários players", "artesanal", "disperso",
            "pequenos", "regionais", "sem líder", "caótico",
        ],
        "negativo": ["concentrado", "monopol", "oligopólio", "um dominante"],
        "base": 6,
    },
    "tarpit": {  # NOTA ALTA = BAIXO risco de tarpit (NÃO é armadilha)
        "positivo": [  # Palavras que indicam NÃO é tarpit
            "B2B", "enterprise", "infraestrutura", "regulação",
            "industrial", "especializado", "técnico", "profissional",
            "compliance", "deep tech", "hardware",
        ],
        "negativo": [  # Palavras que indicam PODE SER tarpit
            "rede social", "app de", "marketplace genérico", "discovery",
            "consumidor final", "lazer", "entretenimento", "lifestyle",
            "dating", "podcast", "influencer", "social media",
        ],
        "base": 6,
    },
    "risco_legal": {  # NOTA ALTA = BAIXO risco legal
        "positivo": [  # Palavras que indicam BAIXO risco legal
            "software", "consultoria", "educação", "informação",
            "dados públicos", "marketplace", "SaaS",
        ],
        "negativo": [  # Palavras que indicam ALTO risco legal
            "saúde", "fintech", "regulado", "médico", "farmacêutico",
            "financeiro", "clínico", "drogas", "cadeia", "multa",
            "licenciamento", "autorização", "ANVISA", "BACEN", "CVM",
            "mineração", "energia", "nuclear",
        ],
        "base": 6,
    },
    "platform_risk": {  # NOTA ALTA = BAIXA dependência de plataforma
        "positivo": [  # Palavras que indicam independência
            "independente", "próprio", "open source", "standalone",
            "infraestrutura própria", "hardware", "físico",
        ],
        "negativo": [  # Palavras que indicam dependência
            "API", "Facebook", "Google", "Apple", "Instagram", "WhatsApp",
            "plataforma de terceiro", "app store", "play store",
            "algoritmo de terceiro", "dependência",
        ],
        "base": 7,
    },
    "alinhamento_ods": {
        "positivo": [
            "sustentável", "clima", "social", "igualdade", "pobreza",
            "saúde", "educação", "ODS", "ESG", "inclusão", "diversidade",
            "ambiental", "descarbonização", "água", "energia limpa",
            "fome", "saneamento", "resiliência", "biodiversidade",
            "reciclagem", "circular", "renovável", "transição justa",
        ],
        "negativo": ["luxo exclusivo", "armas", "tabaco", "fóssil puro"],
        "base": 5,
    },
}

# Classificadores de domínio com perfis de ajuste
DOMAIN_PROFILES = {
    "energia": {
        "keywords": ["energia", "elétric", "solar", "eólica", "bateria", "grid", "rede elétrica",
                      "usina", "transmissão", "distribuição", "apagão", "blackout", "carregamento",
                      "EV", "veículo elétrico", "transformador", "geração"],
        "adjustments": {"tam": 2, "crescimento": 2, "pressao_macro": 1, "risco": 1,
                        "alinhamento_ods": 2, "dep_infraestrutura": -2, "facilidade_mvp": -2},
    },
    "ia_tech": {
        "keywords": ["IA", "inteligência artificial", "LLM", "machine learning", "algoritm",
                      "generativ", "GPT", "modelo", "deep learning", "NLP", "alucinação",
                      "viés algorítmico", "dados sintéticos", "automação", "agente"],
        "adjustments": {"timing_tech": 3, "escala_nao_linear": 2, "facilidade_mvp": 1,
                        "crescimento": 2, "janela": 1, "tarpit": -1},
    },
    "saude": {
        "keywords": ["saúde", "médic", "hospital", "farmacêutic", "paciente", "clínic",
                      "droga", "GLP-1", "genômic", "terapia", "SUS", "cirurgia",
                      "diagnóstic", "doença"],
        "adjustments": {"tam": 2, "risco": 2, "risco_legal": -2, "facilidade_mvp": -2,
                        "poder_preco": 2, "alinhamento_ods": 2, "wtp": 1},
    },
    "agro": {
        "keywords": ["agro", "agricultur", "produt rural", "irrigação", "fazend", "soja",
                      "milho", "pecuária", "safra", "colheita", "rural", "seguro agrícola",
                      "crédito rural"],
        "adjustments": {"tam": 2, "dor_financeira": 1, "alinhamento_ods": 2,
                        "penetracao_digital": -1, "dep_infraestrutura": -1},
    },
    "fintech": {
        "keywords": ["fintech", "crédito", "financeiro", "banco", "pagamento", "seguro",
                      "cripto", "blockchain", "tokeniz", "open finance", "open banking"],
        "adjustments": {"tam": 2, "escala_nao_linear": 2, "risco_legal": -2,
                        "recorrencia": 2, "crescimento": 1, "wtp": 1},
    },
    "clima": {
        "keywords": ["clima", "aquecimento", "seca", "inundação", "tempestade", "emissões",
                      "carbono", "descarbonização", "hídric", "água", "resiliência",
                      "desastre", "térmic"],
        "adjustments": {"alinhamento_ods": 3, "pressao_macro": 2, "timing_regulatorio": 2,
                        "urgencia": 1, "risco": 1, "tam": 1},
    },
    "silver_economy": {
        "keywords": ["idoso", "silver", "envelhecimento", "aposentad", "longevidade",
                      "cuidador", "geriátr", "prateado", "60+", "80+", "artrite",
                      "demência", "solidão"],
        "adjustments": {"mudanca_comportamental": 2, "crescimento": 2, "alinhamento_ods": 2,
                        "clareza_persona": 2, "diferenciacao_10x": 1, "penetracao_digital": -1},
    },
    "geopolitica": {
        "keywords": ["geopolít", "friendshoring", "nearshoring", "cadeia global",
                      "tarifa", "sanção", "blocos", "China", "EUA", "mineral estratégico",
                      "chokepoint", "soberania"],
        "adjustments": {"tam": 2, "pressao_macro": 2, "janela": 1,
                        "acesso_usuarios": -1, "facilidade_mvp": -2},
    },
    "govtech_regtech": {
        "keywords": ["govtech", "regtech", "licenciamento", "burocracia", "governo",
                      "compliance", "regulação", "IBAMA", "ambiental", "licitação"],
        "adjustments": {"dor_tempo": 2, "timing_regulatorio": 2, "ciclo_vendas": -2,
                        "risco_legal": -1, "diferenciacao_10x": 2},
    },
    "futuro_trabalho": {
        "keywords": ["trabalho", "emprego", "burnout", "freelancer", "gig economy",
                      "remoto", "híbrido", "recrutamento", "talento", "skill",
                      "upskilling", "júnior", "sênior", "Geração Z"],
        "adjustments": {"mudanca_comportamental": 2, "frequencia": 1, "clareza_persona": 1,
                        "escala_nao_linear": 1, "amplitude": 1},
    },
    "mineracao": {
        "keywords": ["mineração", "mineral", "lítio", "cobalto", "terras raras",
                      "refino", "extração", "mina", "cobre", "urânio"],
        "adjustments": {"tam": 2, "dep_infraestrutura": -3, "facilidade_mvp": -3,
                        "risco_legal": -2, "pressao_macro": 2, "ticket": 2},
    },
}


def _count_keyword_matches(text: str, keywords: list[str]) -> int:
    """Conta quantas keywords aparecem no texto (case-insensitive, partial match)."""
    text_lower = text.lower()
    count = 0
    for kw in keywords:
        if kw.lower() in text_lower:
            count += 1
    return count


def _detect_domains(text: str) -> list[str]:
    """Detecta quais domínios se aplicam ao texto."""
    text_lower = text.lower()
    domains = []
    for domain, profile in DOMAIN_PROFILES.items():
        matches = sum(1 for kw in profile["keywords"] if kw.lower() in text_lower)
        if matches >= 2:
            domains.append(domain)
    return domains


def avaliar_problema_heuristico(problema: dict) -> dict:
    """Avalia um problema usando análise heurística de keywords."""
    # Concatenar todo o texto para análise
    texto = f"{problema['problema']} {problema['descricao']} {problema['desenvolvimento']}"

    notas = {}

    # Pontuar cada critério baseado em keywords
    for criterio_id, rules in KEYWORD_RULES.items():
        base = rules["base"]
        pos_matches = _count_keyword_matches(texto, rules["positivo"])
        neg_matches = _count_keyword_matches(texto, rules["negativo"])

        # Calcular ajuste: cada match positivo +0.5, cada negativo -0.7
        ajuste = (pos_matches * 0.5) - (neg_matches * 0.7)

        # Aplicar ajuste com diminishing returns (logarítmico)
        if ajuste > 0:
            ajuste = min(ajuste, 2 + math.log1p(ajuste))
        elif ajuste < 0:
            ajuste = max(ajuste, -(2 + math.log1p(abs(ajuste))))

        nota = base + ajuste

        # Clampar entre 1 e 10
        notas[criterio_id] = max(1, min(10, round(nota)))

    # Aplicar ajustes de domínio
    domains = _detect_domains(texto)
    for domain in domains:
        adjustments = DOMAIN_PROFILES[domain].get("adjustments", {})
        for criterio_id, adj in adjustments.items():
            if criterio_id in notas:
                notas[criterio_id] = max(1, min(10, notas[criterio_id] + adj))

    # Ajustes especiais baseados em comprimento e riqueza do texto
    text_len = len(texto)
    if text_len > 500:
        notas["observabilidade"] = min(10, notas.get("observabilidade", 5) + 1)
        notas["clareza_persona"] = min(10, notas.get("clareza_persona", 5) + 1)

    # Verificar se há "Oportunidade:" explícita no texto (indica boa estruturação)
    if "oportunidade:" in texto.lower():
        notas["janela"] = min(10, notas.get("janela", 5) + 1)
        notas["diferenciacao_10x"] = min(10, notas.get("diferenciacao_10x", 5) + 1)

    return notas


# ============================================================================
# CHECKPOINT / RETOMADA
# ============================================================================

CHECKPOINT_FILE = "checkpoint_avaliacao.json"


def salvar_checkpoint(resultados: list[dict], diretorio: str):
    """Salva checkpoint para retomada."""
    path = os.path.join(diretorio, CHECKPOINT_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)


def carregar_checkpoint(diretorio: str) -> list[dict]:
    """Carrega checkpoint existente."""
    path = os.path.join(diretorio, CHECKPOINT_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ============================================================================
# GERAÇÃO DO CSV FINAL
# ============================================================================

def gerar_csv_final(resultados: list[dict], diretorio: str) -> str:
    """Gera o CSV final unificado com todas as pontuações e ranking."""

    # Ordenar por total_geral (decrescente)
    resultados_ordenados = sorted(resultados, key=lambda x: x.get("total_geral", 0), reverse=True)

    # Atribuir ranking
    for i, r in enumerate(resultados_ordenados, 1):
        r["ranking"] = i

    # Definir colunas do CSV
    colunas = [
        "ranking",
        "problema",
        "descricao",
        "desenvolvimento",
        "arquivo_fonte",
    ]

    # Adicionar colunas de notas individuais por categoria
    for cat_key, cat_data in FRAMEWORK.items():
        for criterio in cat_data["criterios"]:
            colunas.append(f"nota_{criterio['id']}")
            colunas.append(f"ponderada_{criterio['id']}")

    # Adicionar subtotais de categoria
    for cat_key, cat_data in FRAMEWORK.items():
        colunas.append(f"subtotal_{cat_key}")
        colunas.append(f"pct_{cat_key}")

    # Adicionar total geral
    colunas.extend(["total_geral", "max_total", "pct_total"])

    # Montar as linhas
    linhas = []
    for r in resultados_ordenados:
        linha = {
            "ranking": r["ranking"],
            "problema": r["problema"],
            "descricao": r.get("descricao", ""),
            "desenvolvimento": r.get("desenvolvimento", ""),
            "arquivo_fonte": r.get("arquivo_fonte", ""),
        }

        # Notas individuais
        notas = r.get("notas", {})
        for cat_key, cat_data in FRAMEWORK.items():
            for criterio in cat_data["criterios"]:
                cid = criterio["id"]
                nota = notas.get(cid, 0)
                linha[f"nota_{cid}"] = nota
                linha[f"ponderada_{cid}"] = nota * criterio["peso"]

        # Subtotais
        for cat_key in FRAMEWORK:
            linha[f"subtotal_{cat_key}"] = r.get(f"subtotal_{cat_key}", 0)
            linha[f"pct_{cat_key}"] = r.get(f"pct_{cat_key}", 0)

        linha["total_geral"] = r.get("total_geral", 0)
        linha["max_total"] = r.get("max_total", 0)
        linha["pct_total"] = r.get("pct_total", 0)

        linhas.append(linha)

    # Escrever CSV
    output_path = os.path.join(diretorio, "avaliacao_500_temas_ranking.csv")
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas, quoting=csv.QUOTE_ALL)

        # Header com nomes legíveis
        header_names = {
            "ranking": "Ranking",
            "problema": "Problema",
            "descricao": "Descrição Geral",
            "desenvolvimento": "Desenvolvimento",
            "arquivo_fonte": "Arquivo Fonte",
            "total_geral": "Total Geral",
            "max_total": "Máximo Possível",
            "pct_total": "% Total",
        }

        # Adicionar headers das notas
        for cat_key, cat_data in FRAMEWORK.items():
            header_names[f"subtotal_{cat_key}"] = f"Subtotal {cat_data['nome']}"
            header_names[f"pct_{cat_key}"] = f"% {cat_data['nome']}"
            for criterio in cat_data["criterios"]:
                cid = criterio["id"]
                header_names[f"nota_{cid}"] = f"Nota {criterio['nome']}"
                header_names[f"ponderada_{cid}"] = f"Pond. {criterio['nome']} (x{criterio['peso']})"

        # Escrever header legível como primeira linha de comentário, e depois os dados
        writer.writeheader()
        for linha in linhas:
            writer.writerow(linha)

    print(f"\nCSV gerado: {output_path}")
    print(f"Total de problemas avaliados: {len(linhas)}")

    # Imprimir Top 20
    print("\n" + "=" * 80)
    print("TOP 20 PROBLEMAS/OPORTUNIDADES")
    print("=" * 80)
    for r in resultados_ordenados[:20]:
        pct = r.get("pct_total", 0)
        total = r.get("total_geral", 0)
        print(f"  #{r['ranking']:>3d} | {pct:>5.1f}% | {total:>4d} pts | {r['problema'][:70]}")

    print("\n" + "=" * 80)
    print("BOTTOM 10 (PIORES AVALIADOS)")
    print("=" * 80)
    for r in resultados_ordenados[-10:]:
        pct = r.get("pct_total", 0)
        total = r.get("total_geral", 0)
        print(f"  #{r['ranking']:>3d} | {pct:>5.1f}% | {total:>4d} pts | {r['problema'][:70]}")

    # Estatísticas por categoria
    print("\n" + "=" * 80)
    print("MÉDIA POR CATEGORIA")
    print("=" * 80)
    for cat_key, cat_data in FRAMEWORK.items():
        pcts = [r.get(f"pct_{cat_key}", 0) for r in resultados_ordenados]
        media = sum(pcts) / len(pcts) if pcts else 0
        print(f"  {cat_data['nome']:<45s} | Média: {media:>5.1f}%")

    return output_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Bars Judge Agent - Avaliador de 500 Temas de Startup"
    )
    parser.add_argument(
        "--mode", type=str, default="heuristic", choices=["api", "heuristic"],
        help="Modo de avaliação: 'api' (usa Claude API) ou 'heuristic' (análise textual local, default)"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Limitar número de problemas a avaliar (0 = todos)"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Retomar avaliação anterior a partir do checkpoint"
    )
    parser.add_argument(
        "--model", type=str, default="claude-sonnet-4-20250514",
        help="Modelo Claude a usar no modo API (default: claude-sonnet-4-20250514)"
    )
    parser.add_argument(
        "--dir", type=str, default=".",
        help="Diretório com os arquivos CSV (default: diretório atual)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=10,
        help="Salvar checkpoint a cada N avaliações (default: 10)"
    )
    args = parser.parse_args()

    diretorio = os.path.abspath(args.dir)

    print("=" * 80)
    print("BARS JUDGE AGENT - Avaliador de Temas de Startup")
    print("=" * 80)
    print(f"Diretório: {diretorio}")
    print(f"Modo: {args.mode.upper()}")
    if args.mode == "api":
        print(f"Modelo: {args.model}")
    print(f"Limite: {'Todos' if args.limit == 0 else args.limit}")
    print(f"Retomar: {'Sim' if args.resume else 'Não'}")
    print()

    # Configurar cliente API se necessário
    client = None
    if args.mode == "api":
        if not HAS_ANTHROPIC:
            print("ERRO: Pacote 'anthropic' não instalado.")
            print("Execute: pip install anthropic")
            sys.exit(1)
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERRO: Variável de ambiente ANTHROPIC_API_KEY não configurada.")
            print("Execute: export ANTHROPIC_API_KEY='sua-chave-aqui'")
            print("Ou use --mode heuristic para avaliação sem API.")
            sys.exit(1)
        client = anthropic.Anthropic(api_key=api_key)

    # Carregar problemas
    print("Carregando problemas dos CSVs...")
    problemas = carregar_problemas(diretorio)

    if args.limit > 0:
        problemas = problemas[:args.limit]
        print(f"Limitado a {args.limit} problemas.")

    # Carregar checkpoint se retomando
    resultados = []
    problemas_avaliados = set()
    if args.resume:
        resultados = carregar_checkpoint(diretorio)
        problemas_avaliados = {r["problema"] for r in resultados}
        print(f"Checkpoint carregado: {len(resultados)} problemas já avaliados.")

    # Avaliar problemas
    total = len(problemas)
    pendentes = [p for p in problemas if p["problema"] not in problemas_avaliados]
    print(f"\nProblemas pendentes: {len(pendentes)} de {total}")
    print("-" * 80)

    for i, problema in enumerate(pendentes, 1):
        idx_global = len(resultados) + 1
        print(f"[{idx_global}/{total}] Avaliando: {problema['problema'][:60]}...")

        if args.mode == "api":
            notas = avaliar_problema(client, problema, args.model)
        else:
            notas = avaliar_problema_heuristico(problema)

        if notas is None:
            print(f"  FALHA ao avaliar. Pulando...")
            continue

        # Calcular pontuações
        pontuacoes = calcular_pontuacoes(notas)

        resultado = {
            "problema": problema["problema"],
            "descricao": problema["descricao"],
            "desenvolvimento": problema["desenvolvimento"],
            "arquivo_fonte": problema["arquivo_fonte"],
            "notas": notas,
            **pontuacoes,
        }

        resultados.append(resultado)

        # Exibir resumo compacto
        if i % 50 == 0 or i == len(pendentes):
            print(f"  ... {idx_global} avaliados | Último: {pontuacoes['total_geral']}/{pontuacoes['max_total']} "
                  f"({pontuacoes['pct_total']}%)")

        # Checkpoint periódico
        if idx_global % args.batch_size == 0:
            salvar_checkpoint(resultados, diretorio)

        # Rate limiting apenas para modo API
        if args.mode == "api":
            time.sleep(0.5)

    # Salvar checkpoint final
    salvar_checkpoint(resultados, diretorio)
    print(f"\nCheckpoint final salvo: {len(resultados)} avaliações.")

    # Gerar CSV final
    if resultados:
        output_path = gerar_csv_final(resultados, diretorio)
        print(f"\nProcesso concluído! Arquivo: {output_path}")
    else:
        print("\nNenhum resultado para gerar CSV.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
