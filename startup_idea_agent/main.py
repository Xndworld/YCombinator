#!/usr/bin/env python3
"""
Startup Idea Agent - Ponto de Entrada Principal

Uso:
    python -m startup_idea_agent [opções]

Exemplos:
    # Execução completa a partir do banco de dados JSON
    python -m startup_idea_agent

    # Apenas os primeiros 5 problemas (teste rápido)
    python -m startup_idea_agent --limite 5

    # Com LLM via API (requer ANTHROPIC_API_KEY)
    python -m startup_idea_agent --usar-llm

    # A partir de CSVs em vez de JSON
    python -m startup_idea_agent --fonte csv

    # Apenas mostrar informações do framework
    python -m startup_idea_agent --info

    # Processar um único problema via argumento
    python -m startup_idea_agent --problema "Falta de acesso a crédito para PMEs"
"""

import argparse
import os
import sys


def criar_llm_function(api_key: str, model: str, max_tokens: int = 4096):
    """Cria uma função genérica de chamada LLM usando a API da Anthropic."""
    try:
        import anthropic
    except ImportError:
        print("[ERRO] Pacote 'anthropic' não instalado. Execute: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    def llm_call(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    return llm_call


def main():
    parser = argparse.ArgumentParser(
        description="Startup Idea Agent - Geração e Avaliação de Ideias de Startup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                              # Pipeline completo (JSON)
  %(prog)s --limite 5                   # Apenas 5 problemas
  %(prog)s --info                       # Info do framework
  %(prog)s --usar-llm                   # Usar LLM (Claude API)
  %(prog)s --fonte csv                  # Carregar de CSVs
  %(prog)s --problema "Descrição..."    # Problema único
        """,
    )

    parser.add_argument(
        "--dir",
        default=".",
        help="Diretório base do projeto (default: diretório atual)",
    )
    parser.add_argument(
        "--fonte",
        default="json",
        choices=["json", "csv"],
        help="Fonte dos problemas: 'json' (banco_geral_dados.json) ou 'csv' (default: json)",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Limitar número de problemas a processar",
    )
    parser.add_argument(
        "--limite-artigos",
        type=int,
        default=None,
        help="Limitar número de artigos a gerar (default: todos)",
    )
    parser.add_argument(
        "--output",
        default="ideias_startup",
        help="Diretório de saída para artigos e dados (default: ideias_startup)",
    )
    parser.add_argument(
        "--usar-llm",
        action="store_true",
        help="Usar LLM (Anthropic API) para geração, avaliação e artigos",
    )
    parser.add_argument(
        "--modelo",
        default="claude-sonnet-4-20250514",
        help="Modelo da Anthropic a usar (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--problema",
        type=str,
        default=None,
        help="Processar um único problema (texto livre)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar informações do framework e sair",
    )
    parser.add_argument(
        "--silencioso",
        action="store_true",
        help="Modo silencioso (sem output de progresso)",
    )
    parser.add_argument(
        "--arquivos",
        nargs="+",
        default=None,
        help="Lista específica de CSVs para carregar (quando --fonte csv)",
    )

    args = parser.parse_args()

    # Import aqui para evitar import circular
    from .agent import StartupIdeaAgent

    # Modo info
    if args.info:
        agent = StartupIdeaAgent(base_dir=args.dir, verbose=True)
        print(agent.info())
        return

    # Configura LLM se solicitado
    llm_generator = None
    llm_evaluator = None
    llm_writer = None

    if args.usar_llm:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[ERRO] ANTHROPIC_API_KEY não definida no ambiente.")
            print("  Export a variável: export ANTHROPIC_API_KEY='sua-chave'")
            sys.exit(1)

        print(f"[INFO] Usando LLM: {args.modelo}")
        llm_generator = criar_llm_function(api_key, args.modelo, max_tokens=2048)
        llm_evaluator = criar_llm_function(api_key, args.modelo, max_tokens=500)
        llm_writer = criar_llm_function(api_key, args.modelo, max_tokens=4096)

    # Cria o agente
    agent = StartupIdeaAgent(
        base_dir=args.dir,
        llm_generator=llm_generator,
        llm_evaluator=llm_evaluator,
        llm_writer=llm_writer,
        verbose=not args.silencioso,
    )

    # Modo problema único
    if args.problema:
        agent.carregar_problema_unico(
            {
                "Problema": args.problema,
                "Descrição Geral": args.problema,
                "Desenvolvimento": "",
            }
        )
        agent.gerar_ideias()
        agent.avaliar_ideias()
        agent.gerar_artigos()
        resultados = agent.exportar(args.output)

        if agent.idea_scores:
            print("\n" + "=" * 60)
            print("RESULTADO")
            print("=" * 60)
            score = agent.idea_scores[0]
            print(f"  Ideia: {score.ideia_nome or score.problema_titulo}")
            print(f"  Pontuação: {score.pontuacao_total:.0f}/{score.pontuacao_maxima:.0f} ({score.percentual:.1f}%)")
            print(f"\n  Artigo salvo em: {resultados['artigos_dir']}/")

            if score.artigo:
                print("\n" + "-" * 60)
                print(score.artigo)
        return

    # Pipeline completo
    resultado = agent.executar_pipeline_completo(
        fonte=args.fonte,
        arquivos_csv=args.arquivos,
        limite=args.limite,
        limite_artigos=args.limite_artigos,
        output_dir=args.output,
    )

    # Imprime resultado final
    if resultado.get("status") == "sucesso":
        print("\n" + "=" * 60)
        print("EXECUÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 60)
        print(f"  Problemas processados: {resultado['problemas_carregados']}")
        print(f"  Ideias geradas: {resultado['ideias_geradas']}")
        print(f"  Artigos gerados: {resultado['artigos_gerados']}")
        print(f"  Artigos em: {resultado['arquivos']['artigos_dir']}")
        print(f"  CSV Resumo: {resultado['arquivos']['csv_resumo']}")
        print(f"  JSON Completo: {resultado['arquivos']['json_completo']}")
        print()
        print("TOP 10 IDEIAS:")
        for item in resultado.get("top_10", []):
            print(
                f"  #{item['ranking']:3d} ({item['percentual']:5.1f}%) "
                f"{item['nome'][:55]}"
            )
    else:
        print(f"\n[ERRO] {resultado.get('erro', 'Erro desconhecido')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
