#!/usr/bin/env python3
"""
Agente de Brainstorm & Problem Solving
========================================

5 agentes especializados que geram 25 soluções cada por problema.
Todas as soluções são escritas diretamente no banco JSON centralizado
com métricas de classificação pré-computadas.

Cada agente aborda de um ângulo diferente:
    1. Tecnológico     - IA, software, automação, deep tech
    2. Modelo Negócio  - Marketplace, plataforma, SaaS, fintech
    3. Social          - Comunidade, comportamento, incentivos
    4. Regulatório     - Compliance, GovTech, certificação
    5. Infraestrutura  - Hardware, logística, supply chain

Economia de tokens:
    - Lê contexto compacto do banco (~200 tokens por problema)
    - Gera soluções estruturadas (JSON, não texto livre)
    - Salva diretamente em solucoes.json com hints de classificação
    - Top 100 mantido automaticamente pelo banco

Uso:
    python -m agentes.brainstorm.brainstorm_agent --problema P0001
    python -m agentes.brainstorm.brainstorm_agent --top 50
    python -m agentes.brainstorm.brainstorm_agent --problema P0001 --agente 3
"""

import json
import os
import sys
import argparse
import time

# Path setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "agentes"))

from banco_dados import BancoDados

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# Os 5 ângulos de brainstorm
ANGULOS = {
    1: {
        "nome": "Tecnológico",
        "foco": "IA, machine learning, automação, deep tech, software, IoT, blockchain",
        "prompt_extra": "Foque em soluções que usam tecnologia de ponta como diferencial. "
                       "Considere IA generativa, visão computacional, NLP, sensores, "
                       "edge computing, APIs, integrações. "
                       "A tecnologia deve ser o moat principal.",
    },
    2: {
        "nome": "Modelo de Negócio",
        "foco": "Marketplace, plataforma, SaaS, fintech, subscription, freemium, aggregator",
        "prompt_extra": "Foque em inovação de modelo de negócio. "
                       "Considere marketplaces, plataformas two-sided, "
                       "SaaS vertical, embedded finance, revenue sharing, "
                       "data monetization. O modelo deve criar lock-in.",
    },
    3: {
        "nome": "Social/Comportamental",
        "foco": "Comunidade, gamificação, incentivos, mudança de hábito, educação, rede social",
        "prompt_extra": "Foque em soluções que mudam comportamento ou criam comunidades. "
                       "Considere gamificação, incentivos sociais, peer pressure, "
                       "educação, nudges, programas de fidelidade. "
                       "O efeito de rede social deve ser o motor.",
    },
    4: {
        "nome": "Regulatório/Institucional",
        "foco": "GovTech, RegTech, compliance, certificação, standards, políticas públicas",
        "prompt_extra": "Foque em soluções que aproveitam ou criam estruturas regulatórias. "
                       "Considere compliance-as-a-service, certificações, "
                       "advocacy platforms, public-private partnerships. "
                       "A regulação deve ser vantagem, não barreira.",
    },
    5: {
        "nome": "Infraestrutura/Operacional",
        "foco": "Hardware, logística, supply chain, manufatura, energia, construção",
        "prompt_extra": "Foque em soluções de infraestrutura física ou operacional. "
                       "Considere logística last-mile, micro-fábricas, "
                       "infraestrutura descentralizada, shared infrastructure. "
                       "A escala operacional deve ser o diferencial.",
    },
}


PROMPT_BRAINSTORM = """Você é um especialista em criação de startups e problem solving.

PROBLEMA:
Título: {titulo}
Descrição: {descricao}
Desenvolvimento: {desenvolvimento}

CONTEXTO DO RANKING:
- Score do problema: {score_pct}%
- Pontos fortes: {pontos_fortes}
- Pontos fracos: {pontos_fracos}
- Tags: {tags}

ÂNGULO DE ABORDAGEM: {angulo_nome}
Foco: {angulo_foco}
{angulo_extra}

TAREFA:
Gere exatamente 5 soluções de startup para este problema, todas do ângulo "{angulo_nome}".

Para CADA solução, retorne um JSON com esta estrutura EXATA:
{{
  "titulo": "Nome da startup/solução (3-6 palavras)",
  "resumo": "Uma frase descrevendo a solução (max 30 palavras)",
  "proposta_valor": "O que resolve e para quem (max 40 palavras)",
  "mercado_alvo": "B2B|B2C|B2B2C|B2G - segmento específico",
  "modelo_receita": "SaaS|marketplace|transacional|subscription|freemium|licenciamento|outro",
  "diferencial": "O que torna esta solução 10x melhor que alternativas (max 30 palavras)",
  "metricas": {{
    "inovacao": N,
    "viabilidade": N,
    "tam_potencial": N,
    "diferenciacao": N,
    "velocidade_mvp": N,
    "defensibilidade": N
  }}
}}

Onde N é uma nota de 1 a 10.

CRITÉRIOS PARA AS MÉTRICAS:
- inovacao: Quão novo/diferente é? (1=existe igual, 10=nunca visto)
- viabilidade: Quão factível com tech atual? (1=ficção, 10=simples de construir)
- tam_potencial: Tamanho do mercado endereçável (1=nicho micro, 10=bilhões)
- diferenciacao: Quão difícil de copiar? (1=trivial, 10=impossível)
- velocidade_mvp: Tempo para MVP funcional (1=anos, 10=semanas)
- defensibilidade: Moat de longo prazo (1=nenhum, 10=fortress)

Retorne APENAS um array JSON com as 5 soluções. Sem texto extra."""


def gerar_solucoes_heuristico(contexto: dict, angulo_id: int) -> list:
    """
    Gera 5 soluções usando heurística quando não há LLM.
    Útil para teste e como fallback.
    """
    angulo = ANGULOS[angulo_id]
    titulo = contexto["titulo"]
    tags = contexto.get("tags", [])

    templates = {
        1: [  # Tecnológico
            ("Plataforma IA para {tag}", "SaaS", 7, 7, 7, 6, 7, 6),
            ("Sensor IoT de {tag}", "subscription", 6, 6, 6, 7, 5, 7),
            ("API de dados para {tag}", "SaaS", 6, 8, 6, 5, 8, 5),
            ("Automação ML de {tag}", "SaaS", 7, 6, 7, 6, 6, 6),
            ("Dashboard analytics {tag}", "SaaS", 5, 8, 5, 4, 8, 4),
        ],
        2: [  # Modelo de Negócio
            ("Marketplace de {tag}", "marketplace", 6, 7, 8, 5, 6, 7),
            ("SaaS vertical para {tag}", "SaaS", 5, 8, 6, 6, 7, 6),
            ("Plataforma B2B de {tag}", "subscription", 6, 7, 7, 5, 6, 5),
            ("Fintech para {tag}", "transacional", 7, 6, 8, 6, 5, 7),
            ("Agregador de {tag}", "freemium", 5, 7, 6, 4, 7, 5),
        ],
        3: [  # Social
            ("Comunidade de {tag}", "freemium", 6, 8, 6, 5, 8, 6),
            ("App gamificado de {tag}", "freemium", 7, 7, 5, 6, 7, 5),
            ("Rede de pares para {tag}", "marketplace", 6, 7, 5, 5, 6, 6),
            ("Programa incentivos {tag}", "subscription", 5, 7, 5, 4, 7, 5),
            ("Educação gamificada {tag}", "subscription", 6, 8, 6, 5, 7, 5),
        ],
        4: [  # Regulatório
            ("Compliance-as-service {tag}", "SaaS", 6, 7, 6, 7, 6, 7),
            ("Certificação digital {tag}", "licenciamento", 5, 6, 5, 7, 5, 7),
            ("GovTech para {tag}", "SaaS", 6, 6, 7, 6, 5, 7),
            ("RegTech monitor {tag}", "subscription", 5, 7, 5, 6, 6, 6),
            ("Advocacy platform {tag}", "freemium", 5, 6, 5, 5, 6, 5),
        ],
        5: [  # Infraestrutura
            ("Infra descentralizada {tag}", "subscription", 7, 5, 7, 7, 4, 8),
            ("Logística smart {tag}", "transacional", 6, 6, 7, 6, 5, 6),
            ("Micro-fábrica de {tag}", "licenciamento", 7, 5, 6, 8, 3, 8),
            ("Supply chain {tag}", "SaaS", 5, 7, 7, 5, 6, 6),
            ("Shared infra {tag}", "marketplace", 6, 6, 6, 5, 5, 6),
        ],
    }

    tag_principal = tags[0] if tags else titulo.split()[0].lower()
    solucoes = []

    for template in templates.get(angulo_id, templates[1]):
        nome, modelo, inov, viab, tam, dif, vel, defe = template
        solucoes.append({
            "titulo": nome.format(tag=tag_principal)[:60],
            "resumo": f"Solução {angulo['nome'].lower()} para {titulo[:40]}",
            "proposta_valor": f"Resolve {titulo[:30]} via abordagem {angulo['nome'].lower()}",
            "mercado_alvo": "B2B" if angulo_id in [1, 4, 5] else "B2C",
            "modelo_receita": modelo,
            "diferencial": f"Abordagem {angulo['nome'].lower()} única para o problema",
            "metricas": {
                "inovacao": inov,
                "viabilidade": viab,
                "tam_potencial": tam,
                "diferenciacao": dif,
                "velocidade_mvp": vel,
                "defensibilidade": defe,
            },
        })

    return solucoes


def gerar_solucoes_llm(client, contexto: dict, angulo_id: int,
                       model: str = "claude-sonnet-4-20250514") -> list:
    """Gera 5 soluções via API do Claude."""
    angulo = ANGULOS[angulo_id]

    prompt = PROMPT_BRAINSTORM.format(
        titulo=contexto["titulo"],
        descricao=contexto["descricao"],
        desenvolvimento=contexto["desenvolvimento"],
        score_pct=contexto["score_pct"],
        pontos_fortes=", ".join(contexto.get("pontos_fortes", [])),
        pontos_fracos=", ".join(contexto.get("pontos_fracos", [])),
        tags=", ".join(contexto.get("tags", [])),
        angulo_nome=angulo["nome"],
        angulo_foco=angulo["foco"],
        angulo_extra=angulo["prompt_extra"],
    )

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}],
    )

    texto = response.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1] if "\n" in texto else texto[3:]
    if texto.endswith("```"):
        texto = texto[:-3]

    return json.loads(texto.strip())


def processar_problema(problema_id: str, agentes: list = None,
                       mode: str = "heuristic", model: str = "claude-sonnet-4-20250514"):
    """
    Processa um problema: gera soluções com todos os agentes e salva no banco.

    Args:
        problema_id: ID do problema (ex: "P0001")
        agentes: Lista de IDs de agentes a usar (default: todos 1-5)
        mode: "heuristic" ou "api"
        model: Modelo Claude para modo API
    """
    banco = BancoDados()
    contexto = banco.contexto_para_brainstorm(problema_id)

    if not contexto:
        print(f"[ERRO] Problema {problema_id} não encontrado no banco.")
        return

    if agentes is None:
        agentes = [1, 2, 3, 4, 5]

    client = None
    if mode == "api":
        if not HAS_ANTHROPIC:
            print("[ERRO] anthropic não instalado. Use: pip install anthropic")
            return
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[ERRO] ANTHROPIC_API_KEY não definida.")
            return
        client = anthropic.Anthropic(api_key=api_key)

    print(f"\nBrainstorm: {contexto['titulo'][:60]}")
    print(f"  Score: {contexto['score_pct']}% | Tags: {', '.join(contexto['tags'][:5])}")
    print(f"  Pontos fortes: {', '.join(contexto['pontos_fortes'])}")
    print(f"  Pontos fracos: {', '.join(contexto['pontos_fracos'])}")

    total_solucoes = 0
    for agente_id in agentes:
        angulo = ANGULOS[agente_id]
        print(f"\n  Agente {agente_id} ({angulo['nome']})...")

        if mode == "api" and client:
            solucoes = gerar_solucoes_llm(client, contexto, agente_id, model)
        else:
            solucoes = gerar_solucoes_heuristico(contexto, agente_id)

        # Adiciona tipo do ângulo a cada solução
        for sol in solucoes:
            sol["tipo"] = angulo["nome"].lower()

        # Salva no banco central
        ids = banco.adicionar_solucoes(solucoes, problema_id, agente_id)
        print(f"    {len(ids)} soluções salvas: {ids[0]}..{ids[-1]}")
        total_solucoes += len(ids)

    # Mostra top 10 do ranking atual
    print(f"\n  Total: {total_solucoes} soluções geradas para {problema_id}")
    top = banco.obter_top_n_solucoes(10)
    if top:
        print(f"\n  TOP 10 SOLUÇÕES (ranking global):")
        for s in top:
            print(f"    #{s['ranking']} ({s['score']:.1f}) [{s['problema_id']}] {s['titulo'][:50]}")

    return total_solucoes


def main():
    parser = argparse.ArgumentParser(
        description="Brainstorm Agent - Gera soluções para problemas do banco",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--problema", type=str, help="ID do problema (ex: P0001)")
    parser.add_argument("--top", type=int, default=None,
                       help="Processar os top N problemas do ranking")
    parser.add_argument("--agente", type=int, default=None, choices=[1,2,3,4,5],
                       help="Usar apenas este agente (1-5)")
    parser.add_argument("--mode", default="heuristic", choices=["api", "heuristic"])
    parser.add_argument("--model", default="claude-sonnet-4-20250514")

    args = parser.parse_args()
    banco = BancoDados()

    agentes = [args.agente] if args.agente else None

    if args.problema:
        processar_problema(args.problema, agentes, args.mode, args.model)
    elif args.top:
        problemas = banco.obter_top_n_problemas(args.top)
        print(f"Processando top {len(problemas)} problemas...")
        for p in problemas:
            processar_problema(p["id"], agentes, args.mode, args.model)
    else:
        # Mostra resumo do banco
        stats = banco.stats()
        print("Banco de Dados:")
        print(f"  Problemas: {stats['problemas']}")
        print(f"  Soluções:  {stats['solucoes']}")
        print(f"\nUso:")
        print(f"  python -m agentes.brainstorm.brainstorm_agent --problema P0001")
        print(f"  python -m agentes.brainstorm.brainstorm_agent --top 50")
        print(f"  python -m agentes.brainstorm.brainstorm_agent --top 10 --mode api")


if __name__ == "__main__":
    main()
