"""
Manipulador de CSV para Ideias

Responsável por:
- Carregar ideias de CSVs (banco de ideias do brainstorm/problem solving)
- Exportar CSV rankeado com pontuações
- Exportar resumo compacto para classificação rápida

Colunas esperadas no CSV de entrada:
  Ideia, Descrição, Problema, Origem (opcional), Desenvolvimento (opcional)
"""

import csv
import os
from typing import Optional

from .config import SCORING_FRAMEWORK, MAX_POSSIBLE_SCORE, KILL_FILTER
from .scoring import IdeaScore


class IdeaCSVHandler:
    """Gerencia importação e exportação de dados CSV de ideias."""

    # Mapeamentos de nomes de colunas aceitos
    COLUMN_ALIASES = {
        "Ideia": ["Ideia", "ideia", "Idea", "idea", "Nome", "nome", "Titulo", "titulo", "Título"],
        "Descrição": ["Descrição", "descricao", "Descricao", "Descrição da Ideia", "Description", "description"],
        "Problema": ["Problema", "problema", "Problem", "problem", "Problema que resolve"],
        "Origem": ["Origem", "origem", "Origin", "origin", "Fonte", "fonte", "Source"],
        "Desenvolvimento": ["Desenvolvimento", "desenvolvimento", "Development", "Detalhes", "detalhes"],
    }

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir

    def carregar_ideias(self, arquivos: Optional[list] = None) -> list:
        """
        Carrega ideias de arquivos CSV.

        Args:
            arquivos: Lista de caminhos de CSV. Se None, busca automaticamente.

        Returns:
            Lista de dicionários normalizados com dados das ideias.
        """
        if arquivos is None:
            arquivos = self._descobrir_csvs()

        ideias = []
        titulos_vistos = set()

        for arquivo in arquivos:
            filepath = arquivo if os.path.isabs(arquivo) else os.path.join(self.base_dir, arquivo)
            if not os.path.exists(filepath):
                print(f"[AVISO] Arquivo não encontrado: {filepath}")
                continue

            novas = self._ler_csv(filepath)
            for ideia in novas:
                titulo = ideia.get("Ideia", "").strip()
                if titulo and titulo not in titulos_vistos:
                    titulos_vistos.add(titulo)
                    ideias.append(ideia)

        print(f"[INFO] Total de ideias únicas carregadas: {len(ideias)}")
        return ideias

    def _descobrir_csvs(self) -> list:
        """Descobre CSVs de ideias no diretório base."""
        csvs = []
        for f in sorted(os.listdir(self.base_dir)):
            if f.endswith(".csv") and ("ideia" in f.lower() or "idea" in f.lower()):
                csvs.append(f)
        return csvs

    def _ler_csv(self, filepath: str) -> list:
        """Lê um CSV e retorna lista de dicionários normalizados."""
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
            print(f"[ERRO] Não foi possível ler {filepath}")
            return []

        reader = csv.DictReader(content.splitlines())
        ideias = []

        for row in reader:
            # Limpa BOM e espaços dos nomes de colunas
            cleaned = {}
            for key, value in row.items():
                if key is None:
                    continue
                clean_key = key.strip().replace("\ufeff", "")
                cleaned[clean_key] = value.strip() if value else ""

            # Normaliza para nomes padrão
            normalizado = self._normalizar_colunas(cleaned)
            if normalizado.get("Ideia"):
                ideias.append(normalizado)

        print(f"[INFO] Carregadas {len(ideias)} ideias de {os.path.basename(filepath)}")
        return ideias

    def _normalizar_colunas(self, row: dict) -> dict:
        """Mapeia variações de nomes de colunas para nomes padrão."""
        normalizado = {}
        for campo_padrao, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in row:
                    normalizado[campo_padrao] = row[alias]
                    break
            if campo_padrao not in normalizado:
                normalizado[campo_padrao] = ""
        return normalizado

    def exportar_ranking(self, scores: list, output_filename: str = "ideias_ranking.csv") -> str:
        """
        Exporta CSV completo com ranking e todas as pontuações.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)

        headers = self._build_headers()

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for score in scores:
                row = self._build_row(score)
                writer.writerow(row)

        print(f"[INFO] Ranking exportado: {output_path} ({len(scores)} ideias)")
        return output_path

    def exportar_resumo(self, scores: list, output_filename: str = "ideias_resumo.csv") -> str:
        """
        Exporta CSV resumido para classificação rápida.

        Returns:
            Caminho do arquivo gerado.
        """
        output_path = os.path.join(self.base_dir, output_filename)

        headers = [
            "Ranking", "Classificação", "Ideia", "Problema", "Origem",
            "Kill Filter", "KF MVP", "KF Margem", "KF Distrib",
        ]
        for cat_key, cat in SCORING_FRAMEWORK.items():
            headers.append(f"{cat['nome']} (Nota)")
            headers.append(f"{cat['nome']} (%)")

        headers.extend([
            "Pontuação Bruta", "Pontuação Final",
            "Pontuação Máxima", "Percentual (%)", "Rebaixada",
        ])

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for s in scores:
                row = [
                    s.ranking,
                    s.classificacao,
                    s.ideia_titulo,
                    s.problema,
                    s.origem,
                    "PASSOU" if s.kill_filter.passou else "FALHOU",
                    s.kill_filter.mvp_semanas,
                    s.kill_filter.margem_tech,
                    s.kill_filter.distribuicao_escalavel,
                ]
                for cat_key in SCORING_FRAMEWORK:
                    if cat_key in s.categorias:
                        c = s.categorias[cat_key]
                        row.append(c.nota)
                        row.append(f"{c.percentual:.1f}")
                    else:
                        row.extend(["", ""])

                row.extend([
                    f"{s.pontuacao_bruta:.1f}",
                    f"{s.pontuacao_final:.1f}",
                    f"{s.pontuacao_maxima:.1f}",
                    f"{s.percentual:.1f}",
                    "Sim" if s.rebaixada else "Não",
                ])
                writer.writerow(row)

        print(f"[INFO] Resumo exportado: {output_path}")
        return output_path

    def _build_headers(self) -> list:
        """Constrói headers do CSV completo."""
        headers = [
            "Ranking",
            "Classificação",
            "ID",
            "Ideia",
            "Descrição",
            "Problema",
            "Origem",
            # Kill Filter
            "Kill Filter Status",
            "KF - MVP Semanas",
            "KF - Margem Tech",
            "KF - Distribuição Escalável",
            "KF - Falhas",
        ]

        # Categorias
        for cat_key, cat in SCORING_FRAMEWORK.items():
            headers.append(f"{cat['nome']} - Nota")
            headers.append(f"{cat['nome']} - Ponderada")
            headers.append(f"{cat['nome']} - Máximo")
            headers.append(f"{cat['nome']} - Percentual (%)")
            headers.append(f"{cat['nome']} - Razão")

        headers.extend([
            "Pontuação Bruta",
            "Pontuação Final",
            "Pontuação Máxima",
            "Percentual Total (%)",
            "Rebaixada",
        ])

        return headers

    def _build_row(self, s: IdeaScore) -> list:
        """Constrói uma linha do CSV completo."""
        row = [
            s.ranking,
            s.classificacao,
            s.ideia_id,
            s.ideia_titulo,
            s.ideia_descricao,
            s.problema,
            s.origem,
            # Kill Filter
            "PASSOU" if s.kill_filter.passou else "FALHOU",
            s.kill_filter.mvp_semanas,
            s.kill_filter.margem_tech,
            s.kill_filter.distribuicao_escalavel,
            "; ".join(s.kill_filter.falhas) if s.kill_filter.falhas else "",
        ]

        # Categorias
        for cat_key in SCORING_FRAMEWORK:
            if cat_key in s.categorias:
                c = s.categorias[cat_key]
                row.append(c.nota)
                row.append(f"{c.pontuacao_ponderada:.1f}")
                row.append(f"{c.pontuacao_maxima:.1f}")
                row.append(f"{c.percentual:.1f}")
                row.append(c.razao)
            else:
                row.extend(["", "", "", "", ""])

        row.extend([
            f"{s.pontuacao_bruta:.1f}",
            f"{s.pontuacao_final:.1f}",
            f"{s.pontuacao_maxima:.1f}",
            f"{s.percentual:.1f}",
            "Sim" if s.rebaixada else "Não",
        ])

        return row
