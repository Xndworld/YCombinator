#!/usr/bin/env python3
"""
RBB Judge Agent — Ponto de Entrada Principal

Avalia artigos de startup conforme os 5 pilares do Red Bull Basement
e gera ranking por impacto social, tecnologia e storytelling.

Uso:
    python -m rbb_judge_agent [opções]

Exemplos:
    # Avaliar todos os .md do diretório artigos/ (modo heurístico)
    python -m rbb_judge_agent --dir artigos/

    # Avaliar com LLM Claude (requer ANTHROPIC_API_KEY)
    python -m rbb_judge_agent --dir artigos/ --usar-llm

    # Avaliar arquivos específicos
    python -m rbb_judge_agent --arquivos projeto_a.md projeto_b.md --usar-llm

    # Avaliar um único artigo e imprimir análise detalhada
    python -m rbb_judge_agent --arquivo meu_projeto.md --usar-llm

    # Limitar a 5 artigos (teste rápido)
    python -m rbb_judge_agent --dir artigos/ --limite 5 --usar-llm

    # Ver informações do framework
    python -m rbb_judge_agent --info

    # Ver análise detalhada do projeto rankeado em #3
    python -m rbb_judge_agent --dir artigos/ --ver 3 --usar-llm
"""

import argparse
import os
import sys


def criar_llm_evaluator(api_key: str, model: str = "claude-sonnet-4-6"):
    """
    Cria função de avaliação usando a API da Anthropic.

    A função retornada aceita (system: str, user: str) -> str,
    compatível com o RBBScoringEngine.
    """
    try:
        import anthropic
    except ImportError:
        print("[ERRO] Pacote 'anthropic' não instalado.")
        print("  Execute: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    def evaluator(system: str, user: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text

    return evaluator


def main():
    parser = argparse.ArgumentParser(
        description="RBB Judge Agent — Avaliador de Startups para o Red Bull Basement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --dir artigos/                        # Avaliação heurística de todos os .md
  %(prog)s --dir artigos/ --usar-llm             # Avaliação via Claude
  %(prog)s --arquivo projeto.md --usar-llm       # Avaliar um único projeto
  %(prog)s --arquivos a.md b.md --usar-llm       # Avaliar arquivos específicos
  %(prog)s --dir artigos/ --limite 5             # Teste rápido com 5 artigos
  %(prog)s --info                                # Info do framework RBB
  %(prog)s --dir artigos/ --ver 1 --usar-llm     # Ver análise do #1 do ranking

Modos de avaliação:
  Heurístico (padrão): keyword matching instantâneo, sem API
  LLM (--usar-llm):    Claude avalia via API, 1 call por artigo, mais preciso
        """,
    )

    parser.add_argument(
        "--dir-saida",
        default=".",
        help="Diretório de saída para CSVs e JSONs (default: diretório atual)",
    )
    parser.add_argument(
        "--dir",
        default=None,
        help="Diretório com artigos .md para avaliar",
    )
    parser.add_argument(
        "--arquivo",
        default=None,
        help="Avaliar um único arquivo .md",
    )
    parser.add_argument(
        "--arquivos",
        nargs="+",
        default=None,
        help="Lista de arquivos .md para avaliar",
    )
    parser.add_argument(
        "--output",
        default="rbb_ranking.csv",
        help="Nome do CSV de ranking (default: rbb_ranking.csv)",
    )
    parser.add_argument(
        "--output-resumo",
        default="rbb_resumo.csv",
        help="Nome do CSV de resumo (default: rbb_resumo.csv)",
    )
    parser.add_argument(
        "--output-json",
        default="rbb_avaliacao.json",
        help="Nome do JSON completo (default: rbb_avaliacao.json)",
    )
    parser.add_argument(
        "--json-individual",
        action="store_true",
        help="Exportar JSON individual por projeto (em rbb_avaliacoes_individuais/)",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Limitar número de artigos a avaliar",
    )
    parser.add_argument(
        "--usar-llm",
        action="store_true",
        help="Usar LLM (Anthropic API) para avaliação precisa",
    )
    parser.add_argument(
        "--modelo",
        default="claude-sonnet-4-6",
        help="Modelo Anthropic (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar informações do framework RBB e sair",
    )
    parser.add_argument(
        "--silencioso",
        action="store_true",
        help="Modo silencioso (suprime logs de progresso)",
    )
    parser.add_argument(
        "--ver",
        type=int,
        default=None,
        help="Ver análise detalhada do projeto no ranking N",
    )

    args = parser.parse_args()

    from .agent import RBBJudgeAgent

    # Modo info
    if args.info:
        agent = RBBJudgeAgent(base_dir=args.dir_saida, verbose=True)
        print(agent.info())
        return

    # Configura LLM
    llm_evaluator = None
    if args.usar_llm:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[ERRO] ANTHROPIC_API_KEY não definida no ambiente.")
            print("  Configure com: export ANTHROPIC_API_KEY='sua-chave'")
            sys.exit(1)
        print(f"[INFO] Usando LLM: {args.modelo}")
        llm_evaluator = criar_llm_evaluator(api_key, args.modelo)

    # Cria agente
    agent = RBBJudgeAgent(
        base_dir=args.dir_saida,
        llm_evaluator=llm_evaluator,
        verbose=not args.silencioso,
    )

    # Modo arquivo único
    if args.arquivo:
        print(f"\n[INFO] Avaliando arquivo único: {args.arquivo}")
        score = agent.avaliar_artigo_unico(args.arquivo)
        if score:
            # Salva JSON individual
            json_path = agent.article_handler.exportar_json_individual(score, args.dir_saida)
            print(f"\n[INFO] JSON salvo em: {json_path}")
        return

    # Determina caminhos dos artigos
    caminhos = args.arquivos
    diretorio = args.dir

    if not caminhos and not diretorio:
        # Tenta diretório padrão "artigos/" no dir atual
        padrao = os.path.join(os.getcwd(), "artigos")
        if os.path.isdir(padrao):
            diretorio = padrao
            print(f"[INFO] Usando diretório padrão: {diretorio}")
        else:
            print("[ERRO] Informe --dir, --arquivo ou --arquivos.")
            print("  Use --help para ver opções disponíveis.")
            sys.exit(1)

    # Executa pipeline completo
    resultado = agent.executar_pipeline(
        caminhos=caminhos,
        diretorio=diretorio,
        limite=args.limite,
        output_ranking=args.output,
        output_resumo=args.output_resumo,
        output_json=args.output_json,
        exportar_json_individual=args.json_individual,
    )

    if resultado.get("status") == "sucesso":
        print("\n" + "=" * 60)
        print("EXECUÇÃO RBB JUDGE CONCLUÍDA")
        print("=" * 60)
        print(f"  Artigos avaliados: {resultado['artigos_avaliados']}")
        print(f"  CSV Ranking:  {resultado['arquivos']['csv_ranking']}")
        print(f"  CSV Resumo:   {resultado['arquivos']['csv_resumo']}")
        print(f"  JSON Dados:   {resultado['arquivos']['json_completo']}")
        print()
        print("TOP 10 PROJETOS RBB:")
        for item in resultado.get("top_10", []):
            areas = ", ".join(item["areas"][:2]) if item["areas"] else "N/A"
            print(
                f"  #{item['ranking']:3d} [{item['classificacao']}] "
                f"{item['score_total']:3d}/100 ({item['percentual']:5.1f}%) "
                f"| {item['nome_projeto'][:45]}"
            )
            print(f"       Status: {item['status']} | Áreas: {areas}")

        # Análise detalhada se --ver foi passado
        if args.ver:
            # Precisa recarregar os scores (eles estão no agente)
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
