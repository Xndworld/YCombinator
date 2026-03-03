#!/usr/bin/env python3
"""
Idea Ranking Agent - Ponto de Entrada Principal

Uso:
    python -m idea_ranking_agent [opções]

Exemplos:
    # Avaliar ideias de um CSV específico
    python -m idea_ranking_agent --arquivos banco_ideias.csv

    # Avaliar com LLM (requer ANTHROPIC_API_KEY)
    python -m idea_ranking_agent --arquivos banco_ideias.csv --usar-llm

    # Limitar a 10 ideias (teste rápido)
    python -m idea_ranking_agent --arquivos banco_ideias.csv --limite 10

    # Auto-descobrir CSVs com "ideia" no nome
    python -m idea_ranking_agent

    # Ver informações do framework
    python -m idea_ranking_agent --info
"""

import argparse
import os
import sys


def criar_llm_evaluator(api_key: str, model: str = "claude-sonnet-4-20250514"):
    """Cria função de avaliação usando a API da Anthropic."""
    try:
        import anthropic
    except ImportError:
        print("[ERRO] Pacote 'anthropic' não instalado. Execute: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    def evaluator(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    return evaluator


def main():
    parser = argparse.ArgumentParser(
        description="Idea Ranking Agent - Avaliação e Ranking de Ideias de Startup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --arquivos banco_ideias.csv            # Avaliar CSV específico
  %(prog)s --arquivos banco_ideias.csv --usar-llm # Usar Claude para avaliação
  %(prog)s --limite 10                             # Teste rápido com 10 ideias
  %(prog)s --info                                  # Info do framework

CSV de entrada deve ter colunas: Ideia, Descrição, Problema
Colunas opcionais: Origem, Desenvolvimento
        """,
    )

    parser.add_argument(
        "--dir",
        default=".",
        help="Diretório base (default: diretório atual)",
    )
    parser.add_argument(
        "--arquivos",
        nargs="+",
        default=None,
        help="CSV(s) de ideias para avaliar",
    )
    parser.add_argument(
        "--output",
        default="ideias_ranking.csv",
        help="Nome do CSV de ranking (default: ideias_ranking.csv)",
    )
    parser.add_argument(
        "--output-resumo",
        default="ideias_resumo.csv",
        help="Nome do CSV de resumo (default: ideias_resumo.csv)",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Limitar número de ideias a avaliar",
    )
    parser.add_argument(
        "--usar-llm",
        action="store_true",
        help="Usar LLM (Anthropic API) para avaliação",
    )
    parser.add_argument(
        "--modelo",
        default="claude-sonnet-4-20250514",
        help="Modelo da Anthropic (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar informações do framework e sair",
    )
    parser.add_argument(
        "--silencioso",
        action="store_true",
        help="Modo silencioso",
    )
    parser.add_argument(
        "--ver",
        type=int,
        default=None,
        help="Ver análise detalhada da ideia no ranking N",
    )

    args = parser.parse_args()

    from .agent import IdeaRankingAgent

    # Modo info
    if args.info:
        agent = IdeaRankingAgent(base_dir=args.dir, verbose=True)
        print(agent.info())
        return

    # Configura LLM
    llm_evaluator = None
    if args.usar_llm:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[ERRO] ANTHROPIC_API_KEY não definida no ambiente.")
            print("  Export a variável: export ANTHROPIC_API_KEY='sua-chave'")
            sys.exit(1)

        print(f"[INFO] Usando LLM: {args.modelo}")
        llm_evaluator = criar_llm_evaluator(api_key, args.modelo)

    # Cria e executa o agente
    agent = IdeaRankingAgent(
        base_dir=args.dir,
        llm_evaluator=llm_evaluator,
        verbose=not args.silencioso,
    )

    resultado = agent.executar_pipeline(
        arquivos=args.arquivos,
        limite=args.limite,
        output_ranking=args.output,
        output_resumo=args.output_resumo,
    )

    # Resultado final
    if resultado.get("status") == "sucesso":
        print("\n" + "=" * 60)
        print("EXECUÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 60)
        print(f"  Ideias avaliadas: {resultado['ideias_avaliadas']}")
        print(f"  CSV Ranking: {resultado['arquivos']['csv_ranking']}")
        print(f"  CSV Resumo:  {resultado['arquivos']['csv_resumo']}")
        print(f"  JSON Dados:  {resultado['arquivos']['json_dados']}")
        print()
        print("TOP 10:")
        for item in resultado.get("top_10", []):
            flag = " ⚠REBAIXADA" if item["rebaixada"] else ""
            print(
                f"  #{item['ranking']:3d} [{item['classificacao']}] "
                f"({item['percentual']:5.1f}%) {item['titulo'][:50]}{flag}"
            )

        # Se --ver foi passado
        if args.ver:
            analise = agent.obter_analise(args.ver)
            if analise:
                print(f"\n{analise}")
            else:
                print(f"\n[AVISO] Ranking #{args.ver} não encontrado.")
    else:
        print(f"\n[ERRO] {resultado.get('erro', 'Erro desconhecido')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
