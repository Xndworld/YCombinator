"""
RBB Judge Agent — Orquestrador Principal

Pipeline de avaliação de startups para o Red Bull Basement (RBB):
  1. Carrega artigos .md de um diretório ou lista de arquivos
  2. Avalia cada artigo contra os 5 pilares do framework RBB
  3. Rankeia por score_total (0-100)
  4. Exporta CSV de ranking, CSV de resumo e JSON completo

Performance com LLM: 1 call por artigo (avaliação holística JSON).
Performance sem LLM: instantâneo (heurística de keywords).
"""

import os
import time
from datetime import datetime
from typing import Optional, Callable

from .config import (
    SCORING_FRAMEWORK,
    MAX_POSSIBLE_SCORE,
    THRESHOLD_APROVADO,
    THRESHOLD_OBSERVACAO,
)
from .scoring import RBBScoringEngine, RBBScore
from .article_handler import ArticleHandler


class RBBJudgeAgent:
    """
    Agente principal que orquestra o pipeline de avaliação RBB.

    Uso:
        agent = RBBJudgeAgent(base_dir=".", llm_evaluator=minha_func_llm)
        resultado = agent.executar_pipeline(diretorio_artigos="artigos/")
    """

    def __init__(
        self,
        base_dir: str = ".",
        llm_evaluator: Optional[Callable] = None,
        verbose: bool = True,
    ):
        """
        Args:
            base_dir: Diretório base para saída dos arquivos.
            llm_evaluator: Função (system: str, user: str) -> str que chama o LLM.
                           Se None, usa heurística de keywords.
            verbose: Se True, imprime progresso detalhado.
        """
        self.base_dir = base_dir
        self.verbose = verbose

        self.scoring_engine = RBBScoringEngine(llm_evaluator=llm_evaluator)
        self.article_handler = ArticleHandler(base_dir=base_dir)

        self.artigos = []
        self.scores = []
        self.stats = {
            "total_artigos": 0,
            "avaliados_com_llm": llm_evaluator is not None,
            "tempo_inicio": None,
            "tempo_fim": None,
            "tempo_total_segundos": 0,
            "distribuicao_status": {},
            "distribuicao_classes": {},
        }

    def log(self, msg: str):
        """Log condicional com timestamp."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {msg}")

    # ========================================================================
    # ETAPAS DO PIPELINE
    # ========================================================================

    def carregar_artigos(
        self,
        caminhos: Optional[list] = None,
        diretorio: Optional[str] = None,
    ) -> int:
        """
        Etapa 1: Carrega artigos .md.

        Args:
            caminhos: Lista de caminhos de arquivos. Tem precedência sobre diretorio.
            diretorio: Diretório para descoberta automática de .md.

        Returns:
            Número de artigos carregados.
        """
        self.log("=" * 60)
        self.log("ETAPA 1: CARREGANDO ARTIGOS")
        self.log("=" * 60)

        self.artigos = self.article_handler.carregar_artigos(
            caminhos=caminhos,
            diretorio=diretorio,
        )
        self.stats["total_artigos"] = len(self.artigos)

        modo = "LLM (1 call/artigo)" if self.stats["avaliados_com_llm"] else "Heurístico (keywords)"
        self.log(f"Artigos carregados: {len(self.artigos)}")
        self.log(f"Modo de avaliação: {modo}")
        self.log(f"Framework: 5 Pilares RBB | Score máximo: {MAX_POSSIBLE_SCORE}")

        return len(self.artigos)

    def avaliar_todos(self, limite: Optional[int] = None) -> list:
        """
        Etapa 2: Avalia todos os artigos carregados.

        Args:
            limite: Se definido, avalia apenas os primeiros N artigos.

        Returns:
            Lista de RBBScore.
        """
        self.log("=" * 60)
        self.log("ETAPA 2: AVALIANDO ARTIGOS")
        self.log("=" * 60)

        self.stats["tempo_inicio"] = time.time()
        artigos_a_avaliar = self.artigos[:limite] if limite else self.artigos
        total = len(artigos_a_avaliar)

        self.scores = []
        for i, artigo in enumerate(artigos_a_avaliar, 1):
            titulo_curto = artigo.get("titulo", "N/A")[:55]
            self.log(f"Avaliando [{i}/{total}]: {titulo_curto}...")

            score = self.scoring_engine.avaliar_artigo(artigo, artigo_id=i)
            self.scores.append(score)

            self.log(
                f"  → Score: {score.score_total}/{MAX_POSSIBLE_SCORE} "
                f"({score.percentual:.1f}%) [{score.classificacao}] {score.status_ranqueamento}"
            )

            # Pausa entre chamadas LLM para respeitar rate limits
            if self.stats["avaliados_com_llm"] and i < total:
                time.sleep(0.5)

            if i % 10 == 0:
                self.log(f"  Progresso: {i}/{total} ({i / total * 100:.1f}%)")

        self.log(f"Avaliação concluída: {len(self.scores)} artigos avaliados.")
        return self.scores

    def rankear(self) -> list:
        """
        Etapa 3: Rankeia artigos por score_total.

        Returns:
            Lista de RBBScore ordenada por ranking.
        """
        self.log("=" * 60)
        self.log("ETAPA 3: RANKEANDO PROJETOS")
        self.log("=" * 60)

        self.scores = self.scoring_engine.rankear_artigos(self.scores)

        # Calcula distribuições
        status_dist = {}
        classe_dist = {}
        for s in self.scores:
            status_dist[s.status_ranqueamento] = status_dist.get(s.status_ranqueamento, 0) + 1
            classe_dist[s.classificacao] = classe_dist.get(s.classificacao, 0) + 1

        self.stats["distribuicao_status"] = status_dist
        self.stats["distribuicao_classes"] = classe_dist

        # Top 10
        self.log("\nTOP 10 PROJETOS RBB:")
        self.log("-" * 80)
        for score in self.scores[:10]:
            self.log(
                f"  #{score.ranking:3d} [{score.classificacao}] "
                f"{score.score_total:3d}/{MAX_POSSIBLE_SCORE} "
                f"({score.percentual:5.1f}%) | {score.nome_projeto[:50]}"
            )

        self.log(f"\nDistribuição por status: {status_dist}")
        self.log(f"Distribuição por classe: {classe_dist}")

        return self.scores

    def exportar(
        self,
        output_ranking: str = "rbb_ranking.csv",
        output_resumo: str = "rbb_resumo.csv",
        output_json: str = "rbb_avaliacao.json",
        exportar_json_individual: bool = False,
    ) -> dict:
        """
        Etapa 4: Exporta resultados.

        Args:
            output_ranking: Nome do CSV de ranking completo.
            output_resumo: Nome do CSV de resumo.
            output_json: Nome do JSON completo.
            exportar_json_individual: Se True, gera JSON individual por projeto.

        Returns:
            Dicionário com caminhos dos arquivos gerados.
        """
        self.log("=" * 60)
        self.log("ETAPA 4: EXPORTANDO RESULTADOS")
        self.log("=" * 60)

        csv_ranking = self.article_handler.exportar_ranking_csv(self.scores, output_ranking)
        csv_resumo = self.article_handler.exportar_resumo_csv(self.scores, output_resumo)
        json_path = self.article_handler.exportar_json(self.scores, output_json)

        arquivos_gerados = {
            "csv_ranking": csv_ranking,
            "csv_resumo": csv_resumo,
            "json_completo": json_path,
        }

        if exportar_json_individual:
            json_dir = os.path.join(self.base_dir, "rbb_avaliacoes_individuais")
            os.makedirs(json_dir, exist_ok=True)
            json_individuais = []
            for score in self.scores:
                path = self.article_handler.exportar_json_individual(score, json_dir)
                json_individuais.append(path)
            arquivos_gerados["json_individuais"] = json_individuais
            self.log(f"  JSONs individuais: {json_dir}/ ({len(json_individuais)} arquivos)")

        self.stats["tempo_fim"] = time.time()
        self.stats["tempo_total_segundos"] = (
            self.stats["tempo_fim"] - self.stats["tempo_inicio"]
            if self.stats["tempo_inicio"]
            else 0
        )

        self.log(f"\nArquivos gerados:")
        self.log(f"  CSV Ranking: {csv_ranking}")
        self.log(f"  CSV Resumo:  {csv_resumo}")
        self.log(f"  JSON Dados:  {json_path}")

        return arquivos_gerados

    def executar_pipeline(
        self,
        caminhos: Optional[list] = None,
        diretorio: Optional[str] = None,
        limite: Optional[int] = None,
        output_ranking: str = "rbb_ranking.csv",
        output_resumo: str = "rbb_resumo.csv",
        output_json: str = "rbb_avaliacao.json",
        exportar_json_individual: bool = False,
    ) -> dict:
        """
        Executa o pipeline completo: carrega → avalia → rankeia → exporta.

        Args:
            caminhos: Lista de arquivos .md (prioridade sobre diretorio).
            diretorio: Diretório com artigos .md para avaliação.
            limite: Limitar número de artigos avaliados.
            output_ranking: CSV com ranking completo.
            output_resumo: CSV com resumo.
            output_json: JSON com todas as avaliações.
            exportar_json_individual: Se True, gera JSON por projeto.

        Returns:
            Dicionário com status, estatísticas e top_10.
        """
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║    RBB JUDGE AGENT — Red Bull Basement Evaluator        ║")
        self.log("║    Framework: 5 Pilares | Foco: Impacto Social/IA       ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log("")

        # Etapa 1: Carregar
        n_artigos = self.carregar_artigos(caminhos=caminhos, diretorio=diretorio)
        if n_artigos == 0:
            self.log("[ERRO] Nenhum artigo carregado. Verifique o diretório ou os caminhos.")
            return {"erro": "Nenhum artigo carregado"}

        # Etapa 2: Avaliar
        self.avaliar_todos(limite=limite)

        # Etapa 3: Rankear
        self.rankear()

        # Etapa 4: Exportar
        arquivos = self.exportar(
            output_ranking=output_ranking,
            output_resumo=output_resumo,
            output_json=output_json,
            exportar_json_individual=exportar_json_individual,
        )

        # Estatísticas finais
        self._imprimir_estatisticas()

        return {
            "status": "sucesso",
            "artigos_carregados": n_artigos,
            "artigos_avaliados": len(self.scores),
            "arquivos": arquivos,
            "stats": {
                k: v for k, v in self.stats.items()
                if k not in ("tempo_inicio", "tempo_fim")
            },
            "top_10": [
                {
                    "ranking": s.ranking,
                    "classificacao": s.classificacao,
                    "status": s.status_ranqueamento,
                    "nome_projeto": s.nome_projeto,
                    "arquivo": s.arquivo,
                    "score_total": s.score_total,
                    "percentual": round(s.percentual, 1),
                    "areas": s.areas_interesse_relacionadas,
                }
                for s in self.scores[:10]
            ],
        }

    # ========================================================================
    # UTILITÁRIOS
    # ========================================================================

    def avaliar_artigo_unico(self, caminho: str) -> Optional[RBBScore]:
        """
        Avalia um único artigo e retorna o RBBScore.

        Útil para avaliação pontual de um projeto específico.
        """
        artigo = self.article_handler._ler_artigo(caminho)
        if not artigo:
            return None

        score = self.scoring_engine.avaliar_artigo(artigo, artigo_id=1)
        score.ranking = 1

        if self.verbose:
            print(self.scoring_engine.formatar_score(score))

        return score

    def obter_analise(self, ranking_position: int) -> Optional[str]:
        """Retorna análise formatada de um projeto pelo ranking."""
        for score in self.scores:
            if score.ranking == ranking_position:
                return self.scoring_engine.formatar_score(score)
        return None

    def info(self) -> str:
        """Retorna informações sobre o framework RBB."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║        RBB JUDGE AGENT — Framework v1.0                     ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║                                                              ║",
            "║  Agente avaliador especialista em inovação de impacto       ║",
            "║  Treinado para a banca do Red Bull Basement (RBB).          ║",
            "║  Foco: Impacto Social/Ambiental + IA + Storytelling         ║",
            "║                                                              ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  OS 5 PILARES DE AVALIAÇÃO                                   ║",
            "╠══════════════════════════════════════════════════════════════╣",
        ]

        for pilar_key, pilar in SCORING_FRAMEWORK.items():
            n_criterios = len(pilar["criterios"])
            peso = pilar["peso_maximo"]
            pct = pilar["peso_percentual"]
            lines.append(f"║  {pilar['nome'][:52]:<52} ║")
            lines.append(f"║    Peso: {peso} pts ({pct}) | {n_criterios} critérios{' ' * (27 - len(str(peso)) - len(pct) - len(str(n_criterios)))}║")
            lines.append("║                                                              ║")

        lines.extend([
            "╠══════════════════════════════════════════════════════════════╣",
            f"║  Score Máximo: {MAX_POSSIBLE_SCORE} pts | Status: Aprovado(≥80) Obs(60-79) Rep(<60) ║",
            "║  Classificação: S+(≥90%) S(≥80%) A(≥70%) B(≥60%) C(≥50%)  ║",
            "╚══════════════════════════════════════════════════════════════╝",
        ])

        return "\n".join(lines)

    def _imprimir_estatisticas(self):
        """Imprime estatísticas finais do pipeline."""
        self.log("")
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║            ESTATÍSTICAS FINAIS RBB JUDGE                ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log(f"  Artigos avaliados: {len(self.scores)}")

        modo = "LLM (1 call/artigo)" if self.stats["avaliados_com_llm"] else "Heurístico"
        self.log(f"  Modo: {modo}")

        if self.stats["avaliados_com_llm"]:
            self.log(f"  Total LLM calls: {len(self.scores)} (1 por artigo)")

        status_dist = self.stats.get("distribuicao_status", {})
        self.log(f"\n  Por Status:")
        for status, count in sorted(status_dist.items()):
            bar = "█" * min(count, 40)
            self.log(f"    [{status:<18}] {bar} {count}")

        classe_dist = self.stats.get("distribuicao_classes", {})
        self.log(f"\n  Por Classe:")
        for cls in ["S+", "S", "A", "B", "C", "D", "F"]:
            count = classe_dist.get(cls, 0)
            if count > 0:
                bar = "█" * min(count, 40)
                self.log(f"    [{cls}] {bar} {count}")

        if self.scores:
            melhor = self.scores[0]
            pior = self.scores[-1]
            media = sum(s.score_total for s in self.scores) / len(self.scores)

            self.log(f"\n  Melhor:  #{melhor.ranking} [{melhor.classificacao}] "
                     f"{melhor.nome_projeto[:40]}... ({melhor.score_total}/{MAX_POSSIBLE_SCORE})")
            self.log(f"  Pior:    #{pior.ranking} [{pior.classificacao}] "
                     f"{pior.nome_projeto[:40]}... ({pior.score_total}/{MAX_POSSIBLE_SCORE})")
            self.log(f"  Média:   {media:.1f}/{MAX_POSSIBLE_SCORE} ({media:.1f}%)")

        tempo = self.stats.get("tempo_total_segundos", 0)
        self.log(f"\n  Tempo total: {tempo:.1f}s")
