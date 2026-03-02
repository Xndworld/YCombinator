"""
Idea Ranking Agent - Orquestrador Principal

Pipeline de avaliação de ideias/soluções em 4 etapas:
  1. Carrega ideias do CSV banco
  2. Avalia cada ideia (kill filter + 5 categorias)
  3. Rankeia por pontuação final
  4. Exporta CSVs com ranking e classificação

Performance: 6 chamadas LLM por ideia (1 kill filter + 5 categorias)
vs. 22 chamadas se avaliasse cada critério individualmente.
"""

import json
import os
import time
from datetime import datetime
from typing import Optional, Callable

from .config import (
    SCORING_FRAMEWORK,
    MAX_POSSIBLE_SCORE,
    KILL_FILTER_PENALTY,
    get_category_names,
)
from .scoring import IdeaScoringEngine, IdeaScore
from .csv_handler import IdeaCSVHandler


class IdeaRankingAgent:
    """
    Agente principal que orquestra o pipeline de avaliação de ideias.

    Uso:
        agent = IdeaRankingAgent(base_dir=".", llm_evaluator=minha_func_llm)
        resultado = agent.executar_pipeline("banco_ideias.csv")
    """

    def __init__(
        self,
        base_dir: str = ".",
        llm_evaluator: Optional[Callable] = None,
        verbose: bool = True,
    ):
        """
        Args:
            base_dir: Diretório base para I/O.
            llm_evaluator: Função (prompt: str) -> str para avaliação via LLM.
                          Se None, usa heurística de keywords.
            verbose: Se True, imprime progresso.
        """
        self.base_dir = base_dir
        self.verbose = verbose

        self.scoring_engine = IdeaScoringEngine(llm_evaluator=llm_evaluator)
        self.csv_handler = IdeaCSVHandler(base_dir=base_dir)

        self.ideias = []
        self.scores = []
        self.stats = {
            "total_ideias": 0,
            "total_categorias": len(SCORING_FRAMEWORK),
            "pontuacao_maxima": MAX_POSSIBLE_SCORE,
            "tempo_inicio": None,
            "tempo_fim": None,
            "tempo_total_segundos": 0,
            "kill_filter_falhas": 0,
            "distribuicao_tiers": {},
        }

    def log(self, msg: str):
        """Log condicional."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {msg}")

    def carregar_ideias(self, arquivos: Optional[list] = None) -> int:
        """
        Etapa 1: Carrega ideias dos CSVs.

        Returns:
            Número de ideias carregadas.
        """
        self.log("=" * 60)
        self.log("ETAPA 1: CARREGANDO IDEIAS")
        self.log("=" * 60)

        self.ideias = self.csv_handler.carregar_ideias(arquivos)
        self.stats["total_ideias"] = len(self.ideias)

        self.log(f"Ideias carregadas: {len(self.ideias)}")
        self.log(f"Categorias de avaliação: {len(SCORING_FRAMEWORK)}")
        self.log(f"Calls por ideia: 6 (1 kill filter + 5 categorias)")

        return len(self.ideias)

    def avaliar_todas(self, limite: Optional[int] = None) -> list:
        """
        Etapa 2: Avalia todas as ideias (kill filter + scorecard).

        Args:
            limite: Se definido, avalia apenas as primeiras N ideias.

        Returns:
            Lista de IdeaScore.
        """
        self.log("=" * 60)
        self.log("ETAPA 2: AVALIANDO IDEIAS")
        self.log("=" * 60)

        self.stats["tempo_inicio"] = time.time()

        ideias_a_avaliar = self.ideias[:limite] if limite else self.ideias
        total = len(ideias_a_avaliar)

        self.scores = []
        for i, ideia in enumerate(ideias_a_avaliar, 1):
            titulo = ideia.get("Ideia", "N/A")[:55]
            self.log(f"Avaliando [{i}/{total}]: {titulo}...")

            score = self.scoring_engine.avaliar_ideia(ideia, ideia_id=i)
            self.scores.append(score)

            # Log kill filter
            if not score.kill_filter.passou:
                self.log(f"  ⚠ Kill Filter FALHOU: {', '.join(score.kill_filter.falhas)}")
                self.stats["kill_filter_falhas"] += 1

            if i % 25 == 0:
                self.log(f"  Progresso: {i}/{total} ({i / total * 100:.1f}%)")

        self.log(f"Avaliação concluída: {len(self.scores)} ideias avaliadas")
        self.log(f"Kill Filter falhas: {self.stats['kill_filter_falhas']}/{total}")

        return self.scores

    def rankear(self) -> list:
        """
        Etapa 3: Rankeia ideias por pontuação final.

        Returns:
            Lista de IdeaScore rankeados.
        """
        self.log("=" * 60)
        self.log("ETAPA 3: RANKEANDO IDEIAS")
        self.log("=" * 60)

        self.scores = self.scoring_engine.rankear_ideias(self.scores)

        # Calcula distribuição de tiers
        tiers = {}
        for s in self.scores:
            tiers[s.classificacao] = tiers.get(s.classificacao, 0) + 1
        self.stats["distribuicao_tiers"] = tiers

        # Top 10
        self.log("\nTOP 10 IDEIAS:")
        self.log("-" * 80)
        for score in self.scores[:10]:
            flag = " ⚠" if score.rebaixada else ""
            self.log(
                f"  #{score.ranking:3d} [{score.classificacao}] "
                f"{score.pontuacao_final:5.0f}/{score.pontuacao_maxima:.0f} "
                f"({score.percentual:5.1f}%) | {score.ideia_titulo[:50]}{flag}"
            )

        self.log(f"\nDistribuição de tiers: {tiers}")

        return self.scores

    def exportar(
        self,
        output_ranking: str = "ideias_ranking.csv",
        output_resumo: str = "ideias_resumo.csv",
    ) -> dict:
        """
        Etapa 4: Exporta CSVs com ranking e resumo.

        Returns:
            Dicionário com caminhos dos arquivos gerados.
        """
        self.log("=" * 60)
        self.log("ETAPA 4: EXPORTANDO RESULTADOS")
        self.log("=" * 60)

        csv_ranking = self.csv_handler.exportar_ranking(self.scores, output_ranking)
        csv_resumo = self.csv_handler.exportar_resumo(self.scores, output_resumo)

        # Exportar JSON com dados completos
        json_path = os.path.join(self.base_dir, "ideias_avaliacao.json")
        self._exportar_json(json_path)

        self.stats["tempo_fim"] = time.time()
        self.stats["tempo_total_segundos"] = (
            self.stats["tempo_fim"] - self.stats["tempo_inicio"]
            if self.stats["tempo_inicio"]
            else 0
        )

        self.log(f"\nArquivos gerados:")
        self.log(f"  CSV Ranking:  {csv_ranking}")
        self.log(f"  CSV Resumo:   {csv_resumo}")
        self.log(f"  JSON Dados:   {json_path}")

        return {
            "csv_ranking": csv_ranking,
            "csv_resumo": csv_resumo,
            "json_dados": json_path,
        }

    def executar_pipeline(
        self,
        arquivos: Optional[list] = None,
        limite: Optional[int] = None,
        output_ranking: str = "ideias_ranking.csv",
        output_resumo: str = "ideias_resumo.csv",
    ) -> dict:
        """
        Executa o pipeline completo de avaliação.

        Args:
            arquivos: Lista de CSVs de ideias (None = auto-discover).
            limite: Limitar número de ideias avaliadas.
            output_ranking: Nome do CSV de ranking completo.
            output_resumo: Nome do CSV de resumo.

        Returns:
            Dicionário com resultados e estatísticas.
        """
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║    IDEA RANKING AGENT - Pipeline de Avaliação           ║")
        self.log("║    Framework: YC Scorecard (5 Categorias + Kill Filter) ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log("")

        # Etapa 1: Carregar
        n_ideias = self.carregar_ideias(arquivos)
        if n_ideias == 0:
            self.log("[ERRO] Nenhuma ideia carregada. Verifique os CSVs.")
            return {"erro": "Nenhuma ideia carregada"}

        # Etapa 2: Avaliar
        self.avaliar_todas(limite=limite)

        # Etapa 3: Rankear
        self.rankear()

        # Etapa 4: Exportar
        resultados = self.exportar(output_ranking, output_resumo)

        # Estatísticas finais
        self._imprimir_estatisticas()

        return {
            "status": "sucesso",
            "ideias_carregadas": n_ideias,
            "ideias_avaliadas": len(self.scores),
            "arquivos": resultados,
            "stats": self.stats,
            "top_10": [
                {
                    "ranking": s.ranking,
                    "classificacao": s.classificacao,
                    "titulo": s.ideia_titulo,
                    "pontuacao": s.pontuacao_final,
                    "percentual": s.percentual,
                    "rebaixada": s.rebaixada,
                }
                for s in self.scores[:10]
            ],
        }

    def _exportar_json(self, filepath: str):
        """Exporta dados completos em JSON."""
        dados = {
            "meta": {
                "versao": "1.0.0",
                "data": datetime.now().isoformat(),
                "framework": "YC Idea Ranking (5 Categorias + Kill Filter)",
                "total_ideias": len(self.scores),
                "pontuacao_maxima": MAX_POSSIBLE_SCORE,
                "penalidade_kill_filter": f"{int((1 - KILL_FILTER_PENALTY) * 100)}%",
            },
            "stats": {
                k: v for k, v in self.stats.items()
                if k not in ("tempo_inicio", "tempo_fim")
            },
            "ideias": [],
        }

        for s in self.scores:
            ideia_data = {
                "ranking": s.ranking,
                "classificacao": s.classificacao,
                "ideia": s.ideia_titulo,
                "descricao": s.ideia_descricao,
                "problema": s.problema,
                "origem": s.origem,
                "kill_filter": {
                    "status": "passou" if s.kill_filter.passou else "falhou",
                    "mvp_semanas": s.kill_filter.mvp_semanas,
                    "margem_tech": s.kill_filter.margem_tech,
                    "distribuicao_escalavel": s.kill_filter.distribuicao_escalavel,
                    "falhas": s.kill_filter.falhas,
                },
                "categorias": {
                    cat_key: {
                        "nome": cr.categoria_nome,
                        "nota": cr.nota,
                        "peso": cr.peso_total,
                        "ponderada": cr.pontuacao_ponderada,
                        "percentual": cr.percentual,
                        "razao": cr.razao,
                    }
                    for cat_key, cr in s.categorias.items()
                },
                "pontuacao_bruta": s.pontuacao_bruta,
                "pontuacao_final": s.pontuacao_final,
                "pontuacao_maxima": s.pontuacao_maxima,
                "percentual": s.percentual,
                "rebaixada": s.rebaixada,
            }
            dados["ideias"].append(ideia_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def _imprimir_estatisticas(self):
        """Imprime estatísticas finais."""
        self.log("")
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║                 ESTATÍSTICAS FINAIS                     ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log(f"  Ideias avaliadas: {len(self.scores)}")
        self.log(f"  Calls por ideia: 6 (1 kill filter + 5 categorias)")
        self.log(f"  Total de calls: {len(self.scores) * 6}")
        self.log(f"  Pontuação máxima: {MAX_POSSIBLE_SCORE}")

        kf = self.stats.get("kill_filter_falhas", 0)
        self.log(f"  Kill Filter falhas: {kf} ({kf / len(self.scores) * 100:.1f}%)" if self.scores else "")

        tiers = self.stats.get("distribuicao_tiers", {})
        self.log(f"\n  Distribuição de Tiers:")
        for tier in ["S", "A", "B", "C", "D", "F"]:
            count = tiers.get(tier, 0)
            if count > 0:
                bar = "█" * min(count, 50)
                self.log(f"    [{tier}] {bar} {count}")

        if self.scores:
            melhor = self.scores[0]
            pior = self.scores[-1]
            media = sum(s.percentual for s in self.scores) / len(self.scores)

            self.log(f"\n  Melhor: #{melhor.ranking} [{melhor.classificacao}] "
                     f"{melhor.ideia_titulo[:40]}... ({melhor.percentual:.1f}%)")
            self.log(f"  Pior:   #{pior.ranking} [{pior.classificacao}] "
                     f"{pior.ideia_titulo[:40]}... ({pior.percentual:.1f}%)")
            self.log(f"  Média:  {media:.1f}%")

        tempo = self.stats.get("tempo_total_segundos", 0)
        self.log(f"\n  Tempo total: {tempo:.1f}s")

    def obter_analise(self, ranking_position: int) -> Optional[str]:
        """Retorna a análise formatada de uma ideia pelo ranking."""
        for score in self.scores:
            if score.ranking == ranking_position:
                return self.scoring_engine.formatar_pontuacao(score)
        return None

    def info(self) -> str:
        """Retorna informações sobre o framework de avaliação."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║        IDEA RANKING AGENT - Framework v1.0                  ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║                                                            ║",
            "║  Agente de avaliação de ideias/soluções de startup          ║",
            "║  Julga e rankeia ideias do brainstorm/problem solving.      ║",
            "║                                                            ║",
            "║  Etapas:                                                    ║",
            "║  1. Kill Filter (3 perguntas matadoras)                     ║",
            "║  2. Scorecard de 5 categorias (nota holística)             ║",
            "║  3. Ranking com classificação S/A/B/C/D/F                  ║",
            "║                                                            ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  KILL FILTER                                                ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  1. MVP em semanas (não meses/anos)?                       ║",
            "║  2. Margem de tecnologia (não agência)?                    ║",
            "║  3. Distribuição escalável (não porta a porta)?            ║",
            f"║  Threshold: nota <= 4 em qualquer = penalização de "
            f"{int((1 - KILL_FILTER_PENALTY) * 100)}%     ║",
            "║                                                            ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  CATEGORIAS DE AVALIAÇÃO                                    ║",
            "╠══════════════════════════════════════════════════════════════╣",
        ]

        for cat_key, cat in SCORING_FRAMEWORK.items():
            n_crits = len(cat["criterios"])
            lines.append(f"║  {cat['nome'][:50]:<50} ║")
            lines.append(
                f"║    Critérios: {n_crits} | Peso total: {cat['peso_total']}"
                f"{' ' * (27 - len(str(n_crits)) - len(str(cat['peso_total'])))}║"
            )
            lines.append("║                                                            ║")

        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append(
            f"║  Total: 22 critérios em 5 categorias | "
            f"Pontuação máx: {MAX_POSSIBLE_SCORE}    ║"
        )
        lines.append("║  Classificação: S (≥80%) A (≥65%) B (≥50%) C (≥35%) D/F    ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(lines)
