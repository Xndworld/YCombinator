"""
Societal Problem Agent - Orquestrador Principal

Agente especializado em:
1. Pesquisar e entender problemas societais
2. Avaliar através de framework de 7 categorias e 55+ critérios ponderados
3. Conectar aspectos da sociedade aos impactos nos mercados
4. Gerar artigos analíticos para cada problema
5. Rankear e exportar resultados em CSV unitário

Baseado nas metodologias de:
- Y Combinator (Paul Graham / Michael Seibel)
- Customer Development (Steve Blank)
- Lean Startup (Eric Ries / Ash Maurya)
- Venture Capital (Sequoia Capital / Sam Altman)
- Blitzscaling (Reid Hoffman)
- Zero to One (Peter Thiel)
- 7 Powers (Hamilton Helmer)
- Idealab (Bill Gross) / Marc Andreessen
- Inspired (Marty Cagan)
"""

import os
import time
import json
from datetime import datetime
from typing import Optional, Callable

from .config import (
    SCORING_FRAMEWORK,
    TOTAL_CRITERIA,
    MAX_POSSIBLE_SCORE,
    get_all_criteria,
    get_category_names,
)
from .scoring import ScoringEngine, ProblemScore
from .article_writer import ArticleWriter
from .csv_handler import CSVHandler


class SocietalProblemAgent:
    """
    Agente principal que orquestra todo o pipeline de análise.

    Pipeline:
    1. Carrega problemas dos CSVs
    2. Avalia cada problema com o framework completo
    3. Gera artigos analíticos
    4. Rankeia todos os problemas
    5. Exporta CSV unitário final
    """

    def __init__(
        self,
        base_dir: str = ".",
        llm_evaluator: Optional[Callable] = None,
        llm_writer: Optional[Callable] = None,
        verbose: bool = True,
    ):
        """
        Args:
            base_dir: Diretório base onde estão os CSVs de entrada.
            llm_evaluator: Função LLM para avaliação de critérios.
                          Assinatura: (prompt: str) -> str
            llm_writer: Função LLM para geração de artigos.
                       Assinatura: (prompt: str) -> str
            verbose: Se True, imprime progresso detalhado.
        """
        self.base_dir = base_dir
        self.verbose = verbose

        self.scoring_engine = ScoringEngine(llm_evaluator=llm_evaluator)
        self.article_writer = ArticleWriter(llm_writer=llm_writer)
        self.csv_handler = CSVHandler(base_dir=base_dir)

        self.problemas = []
        self.scores = []
        self.stats = {
            "total_problemas": 0,
            "total_criterios_por_problema": TOTAL_CRITERIA,
            "pontuacao_maxima_possivel": MAX_POSSIBLE_SCORE,
            "tempo_inicio": None,
            "tempo_fim": None,
            "tempo_total_segundos": 0,
        }

    def log(self, msg: str):
        """Log condicional."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {msg}")

    def carregar_problemas(self, arquivos: Optional[list] = None) -> int:
        """
        Etapa 1: Carrega problemas dos CSVs.

        Returns:
            Número de problemas carregados.
        """
        self.log("=" * 60)
        self.log("ETAPA 1: CARREGANDO PROBLEMAS")
        self.log("=" * 60)

        self.problemas = self.csv_handler.carregar_problemas(arquivos)
        self.stats["total_problemas"] = len(self.problemas)

        self.log(f"Problemas carregados: {len(self.problemas)}")
        self.log(f"Critérios por problema: {TOTAL_CRITERIA}")
        self.log(f"Total de avaliações a realizar: {len(self.problemas) * TOTAL_CRITERIA}")

        return len(self.problemas)

    def avaliar_todos(self, limite: Optional[int] = None) -> list:
        """
        Etapa 2: Avalia todos os problemas contra o framework.

        Args:
            limite: Se definido, avalia apenas os primeiros N problemas.

        Returns:
            Lista de ProblemScore.
        """
        self.log("=" * 60)
        self.log("ETAPA 2: AVALIANDO PROBLEMAS")
        self.log("=" * 60)

        self.stats["tempo_inicio"] = time.time()

        problemas_a_avaliar = self.problemas[:limite] if limite else self.problemas
        total = len(problemas_a_avaliar)

        self.scores = []
        for i, problema in enumerate(problemas_a_avaliar, 1):
            self.log(f"Avaliando [{i}/{total}]: {problema.get('Problema', 'N/A')[:60]}...")

            score = self.scoring_engine.avaliar_problema(problema, problema_id=i)
            self.scores.append(score)

            if i % 50 == 0:
                self.log(f"  Progresso: {i}/{total} ({i/total*100:.1f}%)")

        self.log(f"Avaliação concluída: {len(self.scores)} problemas avaliados")
        return self.scores

    def rankear(self) -> list:
        """
        Etapa 3: Rankeia os problemas por pontuação total.

        Returns:
            Lista de ProblemScore rankeados.
        """
        self.log("=" * 60)
        self.log("ETAPA 3: RANKEANDO PROBLEMAS")
        self.log("=" * 60)

        self.scores = self.scoring_engine.rankear_problemas(self.scores)

        # Imprime top 10
        self.log("\nTOP 10 PROBLEMAS:")
        self.log("-" * 80)
        for score in self.scores[:10]:
            self.log(
                f"  #{score.ranking:3d} | {score.pontuacao_total:6.0f}/{score.pontuacao_maxima:.0f} "
                f"({score.percentual:5.1f}%) | {score.problema_titulo[:55]}"
            )

        return self.scores

    def gerar_artigos(self, limite: Optional[int] = None) -> int:
        """
        Etapa 4: Gera artigos para os problemas avaliados.

        Args:
            limite: Se definido, gera artigos apenas para os top N.

        Returns:
            Número de artigos gerados.
        """
        self.log("=" * 60)
        self.log("ETAPA 4: GERANDO ARTIGOS")
        self.log("=" * 60)

        scores_para_artigo = self.scores[:limite] if limite else self.scores
        total = len(scores_para_artigo)
        total_problemas = len(self.scores)

        for i, score in enumerate(scores_para_artigo, 1):
            self.log(f"Gerando artigo [{i}/{total}]: {score.problema_titulo[:50]}...")
            artigo = self.article_writer.gerar_artigo(score, total_problemas)
            score.artigo = artigo

        self.log(f"Artigos gerados: {total}")
        return total

    def exportar(self, output_filename: str = "ranking_final.csv") -> dict:
        """
        Etapa 5: Exporta CSV unitário final.

        Returns:
            Dicionário com caminhos dos arquivos gerados.
        """
        self.log("=" * 60)
        self.log("ETAPA 5: EXPORTANDO RESULTADOS")
        self.log("=" * 60)

        # CSV completo
        csv_completo = self.csv_handler.exportar_csv_completo(
            self.scores, output_filename
        )

        # CSV resumo
        csv_resumo = self.csv_handler.exportar_resumo(
            self.scores, "ranking_resumo.csv"
        )

        # Exportar artigos individuais
        artigos_dir = os.path.join(self.base_dir, "artigos")
        os.makedirs(artigos_dir, exist_ok=True)

        artigos_exportados = 0
        for score in self.scores:
            if score.artigo:
                # Sanitiza o nome do arquivo
                safe_name = "".join(
                    c if c.isalnum() or c in (" ", "-", "_") else "_"
                    for c in score.problema_titulo[:80]
                ).strip()
                filename = f"{score.ranking:03d}_{safe_name}.md"
                filepath = os.path.join(artigos_dir, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(score.artigo)
                artigos_exportados += 1

        self.stats["tempo_fim"] = time.time()
        self.stats["tempo_total_segundos"] = (
            self.stats["tempo_fim"] - self.stats["tempo_inicio"]
            if self.stats["tempo_inicio"]
            else 0
        )

        self.log(f"\nArquivos gerados:")
        self.log(f"  CSV Completo: {csv_completo}")
        self.log(f"  CSV Resumo: {csv_resumo}")
        self.log(f"  Artigos: {artigos_exportados} em {artigos_dir}/")

        return {
            "csv_completo": csv_completo,
            "csv_resumo": csv_resumo,
            "artigos_dir": artigos_dir,
            "artigos_exportados": artigos_exportados,
        }

    def executar_pipeline_completo(
        self,
        arquivos: Optional[list] = None,
        limite_avaliacao: Optional[int] = None,
        limite_artigos: Optional[int] = None,
        output_filename: str = "ranking_final.csv",
    ) -> dict:
        """
        Executa o pipeline completo de análise.

        Args:
            arquivos: Lista de CSVs para carregar (None = automático).
            limite_avaliacao: Limitar número de problemas avaliados.
            limite_artigos: Limitar número de artigos gerados.
            output_filename: Nome do CSV final.

        Returns:
            Dicionário com resultados e estatísticas.
        """
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║   SOCIETAL PROBLEM AGENT - Pipeline de Análise          ║")
        self.log("║   Framework: YC + Lean + VC + Estratégia Competitiva    ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log("")

        # Etapa 1: Carregar
        n_problemas = self.carregar_problemas(arquivos)
        if n_problemas == 0:
            self.log("[ERRO] Nenhum problema carregado. Verifique os CSVs.")
            return {"erro": "Nenhum problema carregado"}

        # Etapa 2: Avaliar
        self.avaliar_todos(limite=limite_avaliacao)

        # Etapa 3: Rankear
        self.rankear()

        # Etapa 4: Gerar artigos
        self.gerar_artigos(limite=limite_artigos)

        # Etapa 5: Exportar
        resultados = self.exportar(output_filename)

        # Estatísticas finais
        self._imprimir_estatisticas()

        return {
            "status": "sucesso",
            "problemas_carregados": n_problemas,
            "problemas_avaliados": len(self.scores),
            "artigos_gerados": resultados["artigos_exportados"],
            "arquivos": resultados,
            "stats": self.stats,
            "top_10": [
                {
                    "ranking": s.ranking,
                    "titulo": s.problema_titulo,
                    "pontuacao": s.pontuacao_total,
                    "percentual": s.percentual,
                }
                for s in self.scores[:10]
            ],
        }

    def _imprimir_estatisticas(self):
        """Imprime estatísticas finais da execução."""
        self.log("")
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║                 ESTATÍSTICAS FINAIS                     ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log(f"  Problemas analisados: {len(self.scores)}")
        self.log(f"  Critérios por problema: {TOTAL_CRITERIA}")
        self.log(f"  Total de avaliações: {len(self.scores) * TOTAL_CRITERIA}")
        self.log(f"  Pontuação máxima possível: {MAX_POSSIBLE_SCORE}")

        if self.scores:
            melhor = self.scores[0]
            pior = self.scores[-1]
            media = sum(s.percentual for s in self.scores) / len(self.scores)

            self.log(f"\n  Melhor: #{melhor.ranking} {melhor.problema_titulo[:40]}... ({melhor.percentual:.1f}%)")
            self.log(f"  Pior:   #{pior.ranking} {pior.problema_titulo[:40]}... ({pior.percentual:.1f}%)")
            self.log(f"  Média:  {media:.1f}%")

        tempo = self.stats.get("tempo_total_segundos", 0)
        self.log(f"\n  Tempo total: {tempo:.1f}s")

    def obter_analise_problema(self, ranking_position: int) -> Optional[str]:
        """Retorna a análise formatada de um problema pelo ranking."""
        for score in self.scores:
            if score.ranking == ranking_position:
                return self.scoring_engine.formatar_pontuacao(score)
        return None

    def obter_artigo(self, ranking_position: int) -> Optional[str]:
        """Retorna o artigo de um problema pelo ranking."""
        for score in self.scores:
            if score.ranking == ranking_position:
                return score.artigo
        return None

    def resumo_categorias(self) -> dict:
        """Retorna um resumo das médias por categoria entre todos os problemas."""
        if not self.scores:
            return {}

        resumo = {}
        cat_names = get_category_names()

        for cat_key, cat_nome in cat_names.items():
            percentuais = []
            for score in self.scores:
                if cat_key in score.categorias:
                    percentuais.append(score.categorias[cat_key].percentual)

            if percentuais:
                resumo[cat_nome] = {
                    "media": sum(percentuais) / len(percentuais),
                    "max": max(percentuais),
                    "min": min(percentuais),
                    "problemas_avaliados": len(percentuais),
                }

        return resumo

    def info(self) -> str:
        """Retorna informações sobre o framework de avaliação."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║        SOCIETAL PROBLEM AGENT - Framework v1.0              ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║                                                            ║",
            "║  Agente especializado em análise de problemas societais     ║",
            "║  e oportunidades de negócio.                                ║",
            "║                                                            ║",
            "║  Capacidades:                                               ║",
            "║  - Pesquisar e entender problemas da sociedade              ║",
            "║  - Avaliar com framework de 7 categorias / 55+ critérios   ║",
            "║  - Conectar impactos societais aos mercados                 ║",
            "║  - Gerar artigos analíticos aprofundados                    ║",
            "║  - Rankear e exportar em CSV unitário                       ║",
            "║                                                            ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  CATEGORIAS DE AVALIAÇÃO                                    ║",
            "╠══════════════════════════════════════════════════════════════╣",
        ]

        total_criterios = 0
        for cat_key, category in SCORING_FRAMEWORK.items():
            n_crits = len(category["criterios"])
            total_criterios += n_crits
            peso_total = sum(c["peso"] for c in category["criterios"].values())
            lines.append(f"║  {category['nome'][:50]:<50} ║")
            lines.append(f"║    Critérios: {n_crits} | Peso total: {peso_total:<23} ║")
            lines.append(f"║    Escola: {category['escola_base'][:45]:<45}  ║")
            lines.append("║                                                            ║")

        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append(f"║  Total: {total_criterios} critérios | Pontuação máx: {MAX_POSSIBLE_SCORE:<14}   ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(lines)
