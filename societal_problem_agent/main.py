#!/usr/bin/env python3
"""
Societal Problem Agent - Ponto de Entrada Principal

Uso:
    python -m societal_problem_agent.main [opções]

Exemplos:
    # Execução completa (todos os problemas)
    python -m societal_problem_agent.main

    # Apenas os primeiros 10 problemas (teste rápido)
    python -m societal_problem_agent.main --limite 10

    # Com LLM via API (requer ANTHROPIC_API_KEY)
    python -m societal_problem_agent.main --usar-llm

    # Apenas mostrar informações do framework
    python -m societal_problem_agent.main --info

    # Especificar diretório e arquivo de saída
    python -m societal_problem_agent.main --dir /path/to/csvs --output resultado.csv
"""

import argparse
import os
import sys


def criar_llm_evaluator(api_key: str, model: str = "claude-sonnet-4-20250514"):
    """Cria uma função de avaliação usando a API da Anthropic."""
    try:
        import anthropic
    except ImportError:
        print("[ERRO] Pacote 'anthropic' não instalado. Execute: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    def evaluator(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    return evaluator


def criar_llm_writer(api_key: str, model: str = "claude-sonnet-4-20250514"):
    """Cria uma função de escrita de artigos usando a API da Anthropic."""
    try:
        import anthropic
    except ImportError:
        print("[ERRO] Pacote 'anthropic' não instalado. Execute: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    def writer(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    return writer


def main():
    parser = argparse.ArgumentParser(
        description="Societal Problem Agent - Análise de Problemas Societais",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                          # Execução completa
  %(prog)s --limite 10              # Apenas 10 problemas
  %(prog)s --info                   # Info do framework
  %(prog)s --usar-llm              # Usar LLM para avaliação
  %(prog)s --dir ../dados          # Diretório customizado
        """
    )

    parser.add_argument(
        "--dir",
        default=".",
        help="Diretório base com os CSVs de entrada (default: diretório atual)"
    )
    parser.add_argument(
        "--output",
        default="ranking_final.csv",
        help="Nome do arquivo CSV de saída (default: ranking_final.csv)"
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Limitar número de problemas a avaliar"
    )
    parser.add_argument(
        "--limite-artigos",
        type=int,
        default=None,
        help="Limitar número de artigos a gerar (default: todos)"
    )
    parser.add_argument(
        "--usar-llm",
        action="store_true",
        help="Usar LLM (Anthropic API) para avaliação e artigos"
    )
    parser.add_argument(
        "--modelo",
        default="claude-sonnet-4-20250514",
        help="Modelo da Anthropic a usar (default: claude-sonnet-4-20250514)"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar informações do framework e sair"
    )
    parser.add_argument(
        "--silencioso",
        action="store_true",
        help="Modo silencioso (sem output de progresso)"
    )
    parser.add_argument(
        "--arquivos",
        nargs="+",
        default=None,
        help="Lista específica de CSVs para carregar"
    )

    args = parser.parse_args()

    # Import aqui para evitar import circular
    from .agent import SocietalProblemAgent

    # Modo info
    if args.info:
        agent = SocietalProblemAgent(base_dir=args.dir, verbose=True)
        print(agent.info())
        return

    # Configura LLM se solicitado
    llm_evaluator = None
    llm_writer = None

    if args.usar_llm:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[ERRO] ANTHROPIC_API_KEY não definida no ambiente.")
            print("  Export a variável: export ANTHROPIC_API_KEY='sua-chave'")
            sys.exit(1)

        print(f"[INFO] Usando LLM: {args.modelo}")
        llm_evaluator = criar_llm_evaluator(api_key, args.modelo)
        llm_writer = criar_llm_writer(api_key, args.modelo)

    # Cria e executa o agente
    agent = SocietalProblemAgent(
        base_dir=args.dir,
        llm_evaluator=llm_evaluator,
        llm_writer=llm_writer,
        verbose=not args.silencioso,
    )

    resultado = agent.executar_pipeline_completo(
        arquivos=args.arquivos,
        limite_avaliacao=args.limite,
        limite_artigos=args.limite_artigos,
        output_filename=args.output,
    )

    # Imprime resultado final
    if resultado.get("status") == "sucesso":
        print("\n" + "=" * 60)
        print("EXECUÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 60)
        print(f"  Problemas analisados: {resultado['problemas_avaliados']}")
        print(f"  Artigos gerados: {resultado['artigos_gerados']}")
        print(f"  CSV Principal: {resultado['arquivos']['csv_completo']}")
        print(f"  CSV Resumo: {resultado['arquivos']['csv_resumo']}")
        print(f"  Artigos em: {resultado['arquivos']['artigos_dir']}")
        print()
        print("TOP 10:")
        for item in resultado.get("top_10", []):
            print(f"  #{item['ranking']:3d} ({item['percentual']:5.1f}%) {item['titulo'][:55]}")
    else:
        print(f"\n[ERRO] {resultado.get('erro', 'Erro desconhecido')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
