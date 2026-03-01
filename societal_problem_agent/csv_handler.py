"""
Manipulador de CSV

Responsável por:
- Carregar problemas de múltiplos arquivos CSV
- Exportar o CSV unitário final com todas as pontuações e rankings
"""

import csv
import os
from typing import Optional

from .config import SCORING_FRAMEWORK, get_max_possible_score
from .scoring import ProblemScore


class CSVHandler:
    """Gerencia importação e exportação de dados CSV."""

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir

    def carregar_problemas(self, arquivos: Optional[list] = None) -> list:
        """
        Carrega problemas de arquivos CSV.

        Args:
            arquivos: Lista de nomes de arquivos CSV. Se None, busca automaticamente.

        Returns:
            Lista de dicionários com os dados dos problemas.
        """
        if arquivos is None:
            arquivos = self._descobrir_csvs()

        problemas = []
        ids_vistos = set()

        for arquivo in arquivos:
            filepath = os.path.join(self.base_dir, arquivo)
            if not os.path.exists(filepath):
                print(f"[AVISO] Arquivo não encontrado: {filepath}")
                continue

            novos = self._ler_csv(filepath)
            for p in novos:
                # Dedup por titulo
                titulo = p.get("Problema", "").strip()
                if titulo and titulo not in ids_vistos:
                    ids_vistos.add(titulo)
                    problemas.append(p)

        print(f"[INFO] Total de problemas únicos carregados: {len(problemas)}")
        return problemas

    def _descobrir_csvs(self) -> list:
        """Descobre automaticamente arquivos CSV no diretório base."""
        csvs = []
        for f in sorted(os.listdir(self.base_dir)):
            if f.endswith(".csv") and not f.startswith("output_") and f != "ranking_final.csv":
                csvs.append(f)
        return csvs

    def _ler_csv(self, filepath: str) -> list:
        """Lê um arquivo CSV e retorna lista de dicionários."""
        problemas = []

        # Detecta encoding
        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
        content = None

        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if content is None:
            print(f"[ERRO] Não foi possível ler {filepath} com nenhum encoding")
            return []

        # Parse CSV
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            # Normaliza nomes de colunas (remove BOM e espaços)
            cleaned = {}
            for key, value in row.items():
                clean_key = key.strip().replace("\ufeff", "")
                cleaned[clean_key] = value.strip() if value else ""

            # Mapeia variações de nomes de colunas
            if "Descricao Geral" in cleaned and "Descrição Geral" not in cleaned:
                cleaned["Descrição Geral"] = cleaned["Descricao Geral"]

            if cleaned.get("Problema"):
                problemas.append(cleaned)

        print(f"[INFO] Carregados {len(problemas)} problemas de {os.path.basename(filepath)}")
        return problemas

    def exportar_csv_completo(self, scores: list, output_filename: str = "ranking_final.csv") -> str:
        """
        Exporta o CSV unitário final com todas as pontuações.

        Args:
            scores: Lista de ProblemScore já rankeados.
            output_filename: Nome do arquivo de saída.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)

        # Monta os headers
        headers = self._build_headers()

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for ps in scores:
                row = self._build_row(ps)
                writer.writerow(row)

        print(f"[INFO] CSV exportado: {output_path} ({len(scores)} problemas)")
        return output_path

    def _build_headers(self) -> list:
        """Constrói a lista de headers do CSV."""
        headers = [
            "Ranking",
            "ID",
            "Problema",
            "Descrição Geral",
            "Desenvolvimento",
            "Pontuação Total",
            "Pontuação Máxima",
            "Percentual Total (%)",
        ]

        # Headers por categoria
        for cat_key, category in SCORING_FRAMEWORK.items():
            cat_nome = category["nome"]
            headers.append(f"{cat_nome} - Pontuação")
            headers.append(f"{cat_nome} - Máximo")
            headers.append(f"{cat_nome} - Percentual (%)")

            # Headers por critério
            for crit_key, criterio in category["criterios"].items():
                headers.append(f"{criterio['nome']} (Peso {criterio['peso']}) - Nota")
                headers.append(f"{criterio['nome']} (Peso {criterio['peso']}) - Ponderada")
                headers.append(f"{criterio['nome']} (Peso {criterio['peso']}) - Justificativa")

        headers.append("Artigo Gerado")

        return headers

    def _build_row(self, ps: ProblemScore) -> list:
        """Constrói uma linha do CSV para um problema."""
        row = [
            ps.ranking,
            ps.problema_id,
            ps.problema_titulo,
            ps.problema_descricao,
            ps.problema_desenvolvimento,
            f"{ps.pontuacao_total:.1f}",
            f"{ps.pontuacao_maxima:.1f}",
            f"{ps.percentual:.1f}",
        ]

        # Dados por categoria
        for cat_key in SCORING_FRAMEWORK:
            if cat_key in ps.categorias:
                cat = ps.categorias[cat_key]
                row.append(f"{cat.pontuacao_obtida:.1f}")
                row.append(f"{cat.pontuacao_maxima:.1f}")
                row.append(f"{cat.percentual:.1f}")

                # Dados por critério
                crit_dict = {c.criterio_key: c for c in cat.criterios}
                for crit_key in SCORING_FRAMEWORK[cat_key]["criterios"]:
                    if crit_key in crit_dict:
                        c = crit_dict[crit_key]
                        row.append(c.nota)
                        row.append(f"{c.nota_ponderada:.1f}")
                        row.append(c.justificativa)
                    else:
                        row.extend(["", "", ""])
            else:
                # Categoria não avaliada
                cat_crits = len(SCORING_FRAMEWORK[cat_key]["criterios"])
                row.extend(["", "", ""])  # cat scores
                row.extend(["", "", ""] * cat_crits)  # crit scores

        # Artigo (truncado para CSV se muito longo)
        artigo = ps.artigo if ps.artigo else ""
        row.append(artigo)

        return row

    def exportar_resumo(self, scores: list, output_filename: str = "ranking_resumo.csv") -> str:
        """
        Exporta um CSV resumido com apenas ranking, scores por categoria e total.

        Args:
            scores: Lista de ProblemScore já rankeados.
            output_filename: Nome do arquivo de saída.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)

        headers = ["Ranking", "ID", "Problema", "Pontuação Total", "Percentual (%)"]
        for cat_key, category in SCORING_FRAMEWORK.items():
            headers.append(f"{category['nome']} (%)")

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for ps in scores:
                row = [
                    ps.ranking,
                    ps.problema_id,
                    ps.problema_titulo,
                    f"{ps.pontuacao_total:.1f}",
                    f"{ps.percentual:.1f}",
                ]
                for cat_key in SCORING_FRAMEWORK:
                    if cat_key in ps.categorias:
                        row.append(f"{ps.categorias[cat_key].percentual:.1f}")
                    else:
                        row.append("")
                writer.writerow(row)

        print(f"[INFO] Resumo exportado: {output_path}")
        return output_path
