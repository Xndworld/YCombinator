"""
Manipulador de Artigos — RBB Judge Agent

Responsável por:
  - Descobrir e ler artigos Markdown (*.md) de diretórios
  - Extrair título e conteúdo de cada artigo
  - Exportar ranking CSV e JSON com resultados da avaliação RBB

Colunas do CSV de saída:
  Ranking, Classificação, Status, Score Total, Projeto, Arquivo,
  Áreas RBB, ODS, Pilar 1 nota, ..., Pilar 5 nota,
  Pontos Fortes, Riscos, Recomendação
"""

import csv
import json
import os
import re
from datetime import datetime
from typing import Optional

from .config import SCORING_FRAMEWORK, MAX_POSSIBLE_SCORE
from .scoring import RBBScore


class ArticleHandler:
    """Gerencia leitura de artigos e exportação de resultados RBB."""

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir

    # ========================================================================
    # LEITURA DE ARTIGOS
    # ========================================================================

    def descobrir_artigos(self, diretorio: Optional[str] = None) -> list:
        """
        Descobre arquivos .md em um diretório.

        Args:
            diretorio: Caminho do diretório. Se None, usa self.base_dir.

        Returns:
            Lista de caminhos absolutos de arquivos .md, ordenados.
        """
        alvo = diretorio or self.base_dir
        if not os.path.isdir(alvo):
            print(f"[AVISO] Diretório não encontrado: {alvo}")
            return []

        arquivos = sorted([
            os.path.join(alvo, f)
            for f in os.listdir(alvo)
            if f.endswith(".md")
        ])
        return arquivos

    def carregar_artigos(self, caminhos: Optional[list] = None, diretorio: Optional[str] = None) -> list:
        """
        Carrega artigos de uma lista de caminhos ou de um diretório.

        Args:
            caminhos: Lista de caminhos de arquivos .md. Tem precedência sobre diretorio.
            diretorio: Diretório para descoberta automática.

        Returns:
            Lista de dicionários: {'arquivo', 'titulo', 'conteudo'}.
        """
        if caminhos:
            arquivos = caminhos
        else:
            arquivos = self.descobrir_artigos(diretorio)

        artigos = []
        for caminho in arquivos:
            artigo = self._ler_artigo(caminho)
            if artigo:
                artigos.append(artigo)

        print(f"[INFO] {len(artigos)} artigos carregados.")
        return artigos

    def _ler_artigo(self, caminho: str) -> Optional[dict]:
        """Lê um arquivo .md e extrai título e conteúdo."""
        if not os.path.exists(caminho):
            print(f"[AVISO] Arquivo não encontrado: {caminho}")
            return None

        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
        conteudo = None

        for enc in encodings:
            try:
                with open(caminho, "r", encoding=enc) as f:
                    conteudo = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if conteudo is None:
            print(f"[ERRO] Não foi possível ler: {caminho}")
            return None

        titulo = self._extrair_titulo(conteudo, caminho)

        return {
            "arquivo": os.path.basename(caminho),
            "caminho": caminho,
            "titulo": titulo,
            "conteudo": conteudo,
        }

    def _extrair_titulo(self, conteudo: str, caminho: str) -> str:
        """Extrai o título do artigo do conteúdo Markdown."""
        # Tenta H1
        match = re.search(r"^#\s+(.+)$", conteudo, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Tenta H2 seguido de texto (alguns artigos começam assim)
        match = re.search(r"^##\s+(.+)$", conteudo, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback: nome do arquivo sem extensão e sem numeração
        nome = os.path.basename(caminho).replace(".md", "")
        # Remove prefixo numérico (ex: "001_")
        nome = re.sub(r"^\d+_", "", nome)
        return nome.strip()

    # ========================================================================
    # EXPORTAÇÃO
    # ========================================================================

    def exportar_ranking_csv(self, scores: list, output_filename: str = "rbb_ranking.csv") -> str:
        """
        Exporta CSV completo com ranking e pontuações detalhadas.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)
        headers = self._build_csv_headers()

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)
            for score in scores:
                writer.writerow(self._build_csv_row(score))

        print(f"[INFO] Ranking CSV exportado: {output_path} ({len(scores)} projetos)")
        return output_path

    def exportar_resumo_csv(self, scores: list, output_filename: str = "rbb_resumo.csv") -> str:
        """
        Exporta CSV resumido para visão rápida.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)

        headers = [
            "Ranking", "Classe", "Status",
            "Score Total", "Score %",
            "Projeto", "Arquivo",
            "Áreas RBB",
            "P1 Impacto (0-35)", "P2 Tecnologia (0-20)",
            "P3 Storytelling (0-25)", "P4 Viabilidade (0-10)",
            "P5 Equipe (0-10)",
        ]

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for s in scores:
                row = [
                    s.ranking,
                    s.classificacao,
                    s.status_ranqueamento,
                    s.score_total,
                    f"{s.percentual:.1f}%",
                    s.nome_projeto,
                    s.arquivo,
                    "; ".join(s.areas_interesse_relacionadas),
                ]
                for pilar_key in SCORING_FRAMEWORK:
                    if pilar_key in s.pilares:
                        row.append(s.pilares[pilar_key].nota)
                    else:
                        row.append("")
                writer.writerow(row)

        print(f"[INFO] Resumo CSV exportado: {output_path}")
        return output_path

    def exportar_json(self, scores: list, output_filename: str = "rbb_avaliacao.json") -> str:
        """
        Exporta JSON completo com todas as avaliações para banco de dados de ranqueamento.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)

        dados = {
            "meta": {
                "versao": "1.0.0",
                "data": datetime.now().isoformat(),
                "framework": "RBB Judge Agent — Red Bull Basement Scorecard (5 Pilares)",
                "total_projetos": len(scores),
                "score_maximo": MAX_POSSIBLE_SCORE,
                "thresholds": {
                    "aprovado": "score >= 80",
                    "em_observacao": "60 <= score < 80",
                    "reprovado": "score < 60",
                },
            },
            "projetos": [],
        }

        for s in scores:
            projeto = {
                "ranking": s.ranking,
                "classificacao": s.classificacao,
                "status_ranqueamento": s.status_ranqueamento,
                "arquivo": s.arquivo,
                "nome_projeto": s.nome_projeto,
                "resumo_avaliador": s.resumo_avaliador,
                "areas_interesse_relacionadas": s.areas_interesse_relacionadas,
                "ods_relacionados": s.ods_relacionados,
                "score_total": s.score_total,
                "score_percentual": round(s.percentual, 1),
                "pontuacoes": {
                    pilar_key: {
                        "nome": p.pilar_nome,
                        "nota": p.nota,
                        "peso_maximo": p.peso_maximo,
                        "percentual": round(p.percentual, 1),
                        "justificativa": p.justificativa,
                    }
                    for pilar_key, p in s.pilares.items()
                },
                "parecer_banca": {
                    "pontos_fortes": s.pontos_fortes,
                    "pontos_fracos_riscos": s.pontos_fracos_riscos,
                    "recomendacao_acao": s.recomendacao_acao,
                    "status_ranqueamento": s.status_ranqueamento,
                },
            }

            # Inclui JSON bruto do LLM se disponível
            if s.json_raw:
                projeto["json_llm_raw"] = s.json_raw

            dados["projetos"].append(projeto)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        print(f"[INFO] JSON completo exportado: {output_path}")
        return output_path

    def exportar_json_individual(self, score: RBBScore, output_dir: Optional[str] = None) -> str:
        """
        Exporta o JSON de avaliação de um único projeto (formato do metaprompt).

        Returns:
            Caminho do arquivo gerado.
        """
        alvo = output_dir or self.base_dir
        os.makedirs(alvo, exist_ok=True)

        nome_arquivo = re.sub(r"[^\w\-]", "_", score.nome_projeto)[:50]
        output_path = os.path.join(alvo, f"rbb_{nome_arquivo}.json")

        # Formato exatamente conforme o schema do metaprompt
        dados = {
            "nome_projeto": score.nome_projeto,
            "resumo_avaliador": score.resumo_avaliador,
            "areas_interesse_relacionadas": score.areas_interesse_relacionadas,
            "ods_relacionados": score.ods_relacionados,
            "score_total": score.score_total,
            "pontuacoes": {},
            "parecer_banca": {
                "pontos_fortes": score.pontos_fortes,
                "pontos_fracos_riscos": score.pontos_fracos_riscos,
                "recomendacao_acao": score.recomendacao_acao,
                "status_ranqueamento": score.status_ranqueamento,
            },
        }

        for pilar_key, p in score.pilares.items():
            dados["pontuacoes"][pilar_key] = {
                "nota": p.nota,
                "justificativa": p.justificativa,
            }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

        return output_path

    # ========================================================================
    # HELPERS INTERNOS
    # ========================================================================

    def _build_csv_headers(self) -> list:
        headers = [
            "Ranking", "Classificação", "Status Ranqueamento",
            "Score Total", "Score (%)",
            "Nome do Projeto", "Arquivo",
            "Áreas de Interesse", "ODS Relacionados",
        ]
        for pilar_key, pilar_config in SCORING_FRAMEWORK.items():
            nome = pilar_config["nome"]
            max_pts = pilar_config["peso_maximo"]
            headers.append(f"{nome} — Nota (0-{max_pts})")
            headers.append(f"{nome} — % do Pilar")
            headers.append(f"{nome} — Justificativa")

        headers.extend([
            "Pontos Fortes",
            "Riscos / Pontos Fracos",
            "Recomendação da Banca",
        ])
        return headers

    def _build_csv_row(self, s: RBBScore) -> list:
        row = [
            s.ranking,
            s.classificacao,
            s.status_ranqueamento,
            s.score_total,
            f"{s.percentual:.1f}",
            s.nome_projeto,
            s.arquivo,
            "; ".join(s.areas_interesse_relacionadas),
            "; ".join(s.ods_relacionados),
        ]

        for pilar_key in SCORING_FRAMEWORK:
            if pilar_key in s.pilares:
                p = s.pilares[pilar_key]
                row.append(p.nota)
                row.append(f"{p.percentual:.1f}")
                row.append(p.justificativa)
            else:
                row.extend(["", "", ""])

        row.append("; ".join(s.pontos_fortes))
        row.append("; ".join(s.pontos_fracos_riscos))
        row.append(s.recomendacao_acao)

        return row
