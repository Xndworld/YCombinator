#!/usr/bin/env python3
"""
Agente Orquestrador - Pipeline Completo YCombinator
====================================================

Gerencia o fluxo completo do pipeline:

    ETAPA 1: Relatórios (dados/01_relatorios/)
        └─> Relatórios de mercado, tendências e análises macro
            Inputs: .md e .docx com análises de geopolítica, clima, IA, economia

    ETAPA 2: Análise Combinatória → Problemas (dados/02_problemas/)
        └─> Gera planilha de problemas a partir dos relatórios
            Output: CSVs com problemas rankeados em batches

    ETAPA 3: Ranking de Problemas (dados/03_ranking_problemas/)
        └─> Agente Classificador avalia e rankeia os problemas
            Agente: societal_problem_agent (classificador_problemas)
            Output: ranking_final.csv, banco_geral_ranking.csv

    ETAPA 4: Artigos de Problemas (dados/04_artigos_problemas/)
        └─> Top 50 problemas geram artigos detalhados
            Agente: article_writer (dentro do societal_problem_agent)
            Output: 50 artigos .md com análise profunda

    ETAPA 5: Brainstorm de Soluções (dados/05_brainstorm_solucoes/)
        └─> 5 agentes geram 25 soluções cada = 125 soluções por problema
            Agentes: brainstorm (5 instâncias)
            Output: soluções rankeadas em ranking_solucoes/

    ETAPA 6: Artigos de Startups (dados/06_artigos_startups/)
        └─> Top 100 soluções viram artigos de startup
            Output: artigos detalhados de oportunidade de negócio

    ETAPA 7: Bancas Avaliadoras (dados/07_bancas/)
        ├─> Banca RedBull (dados/07_bancas/redbull/)
        │   └─> Avalia startups, formata para processo/edital RedBull
        │       Agente: banca_redbull
        │       Output: processo/ com respostas formatadas
        │
        └─> Banca YCombinator (dados/07_bancas/ycombinator/)
            └─> Avalia startups, gera ranking para fase 2
                Agente: banca_ycombinator
                Output: ranking_fase2/

    [FUTURO] Protocolo de Atualização:
        └─> Novos insights entram no pipeline
            Se rankeado no top 50 → gera artigo + brainstorm
            Se solução no top 100 → gera artigo de startup → bancas

Uso:
    python -m agentes.orquestrador.orquestrador [comando]

Comandos:
    status      - Mostra status de cada etapa do pipeline
    run         - Executa o pipeline completo (etapas disponíveis)
    run --etapa N - Executa apenas a etapa N
    diagram     - Mostra o diagrama do pipeline
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Adiciona agentes/ ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from banco_dados import BancoDados

# Raiz do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Diretórios do pipeline
PIPELINE_DIRS = {
    1: ("01_relatorios", "Relatórios de Mercado"),
    2: ("02_problemas", "Análise Combinatória → Problemas"),
    3: ("03_ranking_problemas", "Ranking de Problemas"),
    4: ("04_artigos_problemas", "Artigos de Problemas (Top 50)"),
    5: ("05_brainstorm_solucoes", "Brainstorm de Soluções"),
    6: ("06_artigos_startups", "Artigos de Startups (Top 100)"),
    7: ("07_bancas", "Bancas Avaliadoras (RedBull + YCombinator)"),
}

# Agentes disponíveis e seu status
AGENTES = {
    "classificador_problemas": {
        "nome": "Classificador de Problemas",
        "modulo": "agentes.societal_problem_agent",
        "status": "implementado",
        "etapas": [3, 4],
    },
    "avaliador_batch": {
        "nome": "Avaliador Batch",
        "modulo": "agentes.bars_judge_agent",
        "status": "implementado",
        "etapas": [2, 3],
    },
    "brainstorm": {
        "nome": "Brainstorm & Problem Solving (5 agentes)",
        "modulo": "agentes.brainstorm.brainstorm_agent",
        "status": "implementado",
        "etapas": [5],
    },
    "banca_redbull": {
        "nome": "Banca RedBull",
        "modulo": "agentes.banca_redbull",
        "status": "placeholder",
        "etapas": [7],
    },
    "banca_ycombinator": {
        "nome": "Banca YCombinator",
        "modulo": "agentes.banca_ycombinator",
        "status": "placeholder",
        "etapas": [7],
    },
}


class Orquestrador:
    """Gerencia o pipeline completo do projeto YCombinator."""

    def __init__(self, project_root: str = PROJECT_ROOT):
        self.project_root = project_root
        self.dados_dir = os.path.join(project_root, "dados")

    def get_dir(self, etapa: int) -> str:
        """Retorna o diretório de uma etapa."""
        subdir = PIPELINE_DIRS[etapa][0]
        return os.path.join(self.dados_dir, subdir)

    def contar_arquivos(self, diretorio: str, extensao: str = None) -> int:
        """Conta arquivos em um diretório."""
        if not os.path.exists(diretorio):
            return 0
        total = 0
        for root, dirs, files in os.walk(diretorio):
            for f in files:
                if extensao is None or f.endswith(extensao):
                    total += 1
        return total

    def status_etapa(self, etapa: int) -> dict:
        """Retorna o status de uma etapa do pipeline."""
        dir_name, descricao = PIPELINE_DIRS[etapa]
        dir_path = os.path.join(self.dados_dir, dir_name)

        status = {
            "etapa": etapa,
            "nome": descricao,
            "diretorio": dir_path,
            "existe": os.path.exists(dir_path),
            "arquivos": {},
        }

        if status["existe"]:
            status["arquivos"] = {
                "csv": self.contar_arquivos(dir_path, ".csv"),
                "json": self.contar_arquivos(dir_path, ".json"),
                "md": self.contar_arquivos(dir_path, ".md"),
                "docx": self.contar_arquivos(dir_path, ".docx"),
                "total": self.contar_arquivos(dir_path),
            }

        # Determina status baseado no conteúdo
        total = status["arquivos"].get("total", 0)
        if total > 0:
            status["estado"] = "concluido"
        elif status["existe"]:
            status["estado"] = "vazio"
        else:
            status["estado"] = "pendente"

        return status

    def status_completo(self) -> list:
        """Retorna o status de todas as etapas."""
        return [self.status_etapa(i) for i in range(1, 8)]

    def imprimir_status(self):
        """Imprime o status formatado do pipeline."""
        print("\n" + "=" * 70)
        print("  PIPELINE YCOMBINATOR - STATUS")
        print("=" * 70)

        indicadores = {"concluido": "[OK]", "vazio": "[--]", "pendente": "[  ]"}

        for status in self.status_completo():
            ind = indicadores.get(status["estado"], "[??]")
            arqs = status["arquivos"]
            detalhe = ""
            if arqs.get("total", 0) > 0:
                partes = []
                for ext in ["csv", "json", "md", "docx"]:
                    if arqs.get(ext, 0) > 0:
                        partes.append(f"{arqs[ext]} {ext}")
                detalhe = f" ({', '.join(partes)})"

            print(f"  {ind} Etapa {status['etapa']}: {status['nome']}{detalhe}")

        # Status dos agentes
        print("\n" + "-" * 70)
        print("  AGENTES")
        print("-" * 70)

        for key, agente in AGENTES.items():
            icone = "[OK]" if agente["status"] == "implementado" else "[--]"
            etapas_str = ", ".join(str(e) for e in agente["etapas"])
            print(f"  {icone} {agente['nome']:<45} (Etapas: {etapas_str})")

        # Banco JSON centralizado
        print("\n" + "-" * 70)
        print("  BANCO JSON CENTRALIZADO (dados/banco/)")
        print("-" * 70)
        banco = BancoDados()
        stats = banco.stats()
        print(f"  Problemas:  {stats['problemas']}")
        print(f"  Soluções:   {stats['solucoes']}")
        print(f"  Startups:   {stats['startups']}")
        print(f"  Bancas:     {stats['avaliacoes_bancas']}")

        if stats['problemas'] > 0:
            top3 = banco.obter_top_n_problemas(3)
            print(f"\n  Top 3 problemas:")
            for p in top3:
                print(f"    #{p['ranking']} ({p['scores']['pct']}%) {p['titulo'][:50]}")

        if stats['solucoes'] > 0:
            top3_sol = banco.obter_top_n_solucoes(3)
            print(f"\n  Top 3 soluções:")
            for s in top3_sol:
                print(f"    #{s['ranking']} ({s['score']:.1f}) {s['titulo'][:50]}")

        print("=" * 70 + "\n")

    def imprimir_diagrama(self):
        """Imprime o diagrama visual do pipeline."""
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    PIPELINE YCOMBINATOR                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌─────────────────────┐                                            ║
║  │  01_RELATÓRIOS      │  Relatórios .md + .docx                    ║
║  │  (Input)            │  Geopolítica, Clima, IA, Economia          ║
║  └──────────┬──────────┘                                            ║
║             │                                                       ║
║             ▼                                                       ║
║  ┌─────────────────────┐                                            ║
║  │  02_PROBLEMAS       │  Análise combinatória dos relatórios       ║
║  │  (Batches + CSVs)   │  → Gera planilha de problemas              ║
║  └──────────┬──────────┘                                            ║
║             │                                                       ║
║             ▼  [Agente: Classificador de Problemas]                 ║
║  ┌─────────────────────┐                                            ║
║  │  03_RANKING         │  500 problemas rankeados                   ║
║  │  PROBLEMAS          │  7 categorias × 55+ critérios              ║
║  └──────────┬──────────┘                                            ║
║             │                                                       ║
║             ▼  Top 50 → [Agente: Article Writer]                    ║
║  ┌─────────────────────┐                                            ║
║  │  04_ARTIGOS         │  Artigos analíticos por problema           ║
║  │  PROBLEMAS          │  498 artigos gerados                       ║
║  └──────────┬──────────┘                                            ║
║             │                                                       ║
║             ▼  [5 Agentes de Brainstorm × 25 soluções]              ║
║  ┌─────────────────────┐                                            ║
║  │  05_BRAINSTORM      │  125 soluções por problema                 ║
║  │  SOLUÇÕES           │  Ranking de soluções                       ║
║  └──────────┬──────────┘                                            ║
║             │                                                       ║
║             ▼  Top 100 soluções                                     ║
║  ┌─────────────────────┐                                            ║
║  │  06_ARTIGOS         │  Artigos de oportunidade de startup        ║
║  │  STARTUPS           │  Desenvolvidos pelo time                   ║
║  └──────────┬──────────┘                                            ║
║             │                                                       ║
║             ▼                                                       ║
║  ┌─────────────────────────────────────────────┐                    ║
║  │  07_BANCAS AVALIADORAS                      │                    ║
║  │  ┌──────────────────┐ ┌──────────────────┐  │                    ║
║  │  │  REDBULL          │ │  YCOMBINATOR     │  │                    ║
║  │  │  → processo/      │ │  → ranking_fase2/│  │                    ║
║  │  │  Edital formatado │ │  Ranking p/ fase │  │                    ║
║  │  └──────────────────┘ └──────────────────┘  │                    ║
║  └─────────────────────────────────────────────┘                    ║
║                                                                     ║
║  ┌─────────────────────────────────────────────┐                    ║
║  │  [FUTURO] PROTOCOLO DE ATUALIZAÇÃO          │                    ║
║  │  Novo insight → Problema? → Top 50? →       │                    ║
║  │  Artigo + Brainstorm → Top 100? → Startup   │                    ║
║  └─────────────────────────────────────────────┘                    ║
║                                                                     ║
╚══════════════════════════════════════════════════════════════════════╝
""")

    def executar_etapa(self, etapa: int, **kwargs):
        """Executa uma etapa específica do pipeline."""
        print(f"\n>>> Executando Etapa {etapa}: {PIPELINE_DIRS[etapa][1]}")

        if etapa == 3:
            return self._executar_classificacao(**kwargs)
        elif etapa == 4:
            return self._executar_artigos_problemas(**kwargs)
        elif etapa == 5:
            return self._executar_brainstorm(**kwargs)
        else:
            print(f"[AVISO] Etapa {etapa} ainda não implementada.")
            return False

    def _executar_classificacao(self, limite=None, usar_llm=False, **kwargs):
        """Executa a classificação de problemas (Etapa 3)."""
        sys.path.insert(0, self.project_root)
        from agentes.societal_problem_agent.agent import SocietalProblemAgent

        agent = SocietalProblemAgent(
            base_dir=self.get_dir(2),
            output_dir=self.get_dir(3),
            artigos_dir=self.get_dir(4),
        )

        resultado = agent.executar_pipeline_completo(
            limite_avaliacao=limite,
            output_filename="ranking_final.csv",
        )

        return resultado.get("status") == "sucesso"

    def _executar_artigos_problemas(self, limite=50, **kwargs):
        """Executa a geração de artigos para top N problemas (Etapa 4)."""
        sys.path.insert(0, self.project_root)
        from agentes.societal_problem_agent.agent import SocietalProblemAgent

        agent = SocietalProblemAgent(
            base_dir=self.get_dir(2),
            output_dir=self.get_dir(3),
            artigos_dir=self.get_dir(4),
        )

        resultado = agent.executar_pipeline_completo(
            limite_artigos=limite,
            output_filename="ranking_final.csv",
        )

        return resultado.get("status") == "sucesso"

    def _executar_brainstorm(self, limite=50, mode="heuristic", **kwargs):
        """Executa brainstorm para os top N problemas (Etapa 5)."""
        from agentes.brainstorm.brainstorm_agent import processar_problema

        banco = BancoDados()
        problemas = banco.obter_top_n_problemas(limite)

        if not problemas:
            print("[ERRO] Nenhum problema no banco. Execute etapas 2-3 primeiro.")
            return False

        print(f"Gerando soluções para {len(problemas)} problemas...")
        total = 0
        for p in problemas:
            n = processar_problema(p["id"], mode=mode)
            total += (n or 0)

        print(f"\nBrainstorm concluído: {total} soluções geradas")
        top = banco.obter_top_n_solucoes(5)
        if top:
            print(f"\nTOP 5 soluções globais:")
            for s in top:
                print(f"  #{s['ranking']} ({s['score']:.1f}) {s['titulo'][:50]}")

        return True

    def executar_pipeline(self, etapa_inicio=1, etapa_fim=7, **kwargs):
        """Executa o pipeline da etapa_inicio até etapa_fim."""
        print("\n" + "=" * 70)
        print("  EXECUTANDO PIPELINE YCOMBINATOR")
        print("=" * 70)

        for etapa in range(etapa_inicio, etapa_fim + 1):
            status = self.status_etapa(etapa)

            if status["estado"] == "concluido" and etapa < etapa_inicio:
                print(f"  [SKIP] Etapa {etapa}: {status['nome']} (já concluída)")
                continue

            sucesso = self.executar_etapa(etapa, **kwargs)
            if not sucesso:
                print(f"\n[AVISO] Pipeline parou na Etapa {etapa}")
                break

        self.imprimir_status()


def main():
    parser = argparse.ArgumentParser(
        description="Orquestrador do Pipeline YCombinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    subparsers.add_parser("status", help="Mostrar status do pipeline")
    subparsers.add_parser("diagram", help="Mostrar diagrama do pipeline")

    p_run = subparsers.add_parser("run", help="Executar pipeline")
    p_run.add_argument("--etapa", type=int, default=None,
                       help="Executar apenas esta etapa")
    p_run.add_argument("--limite", type=int, default=None,
                       help="Limitar número de itens processados")

    args = parser.parse_args()

    orq = Orquestrador()

    if args.comando == "status":
        orq.imprimir_status()
    elif args.comando == "diagram":
        orq.imprimir_diagrama()
    elif args.comando == "run":
        if args.etapa:
            orq.executar_etapa(args.etapa, limite=args.limite)
        else:
            orq.executar_pipeline(limite=args.limite)
    else:
        parser.print_help()
        print("\nExemplo rápido:")
        print("  python -m agentes.orquestrador.orquestrador status")
        print("  python -m agentes.orquestrador.orquestrador diagram")
        print("  python -m agentes.orquestrador.orquestrador run --etapa 3")


if __name__ == "__main__":
    main()
