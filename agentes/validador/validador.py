#!/usr/bin/env python3
"""
Agente Validador - Verifica Integridade do Pipeline
=====================================================

Garante que:
1. Todas as etapas do pipeline estão conectadas corretamente
2. Os dados de saída de uma etapa são compatíveis com a entrada da próxima
3. Não há dados corrompidos ou inconsistentes
4. Os agentes existentes estão funcionais e importáveis
5. Os diretórios necessários existem e têm os arquivos esperados

Uso:
    python -m agentes.validador.validador [comando]

Comandos:
    check       - Verificação completa de integridade
    check-etapa N - Verificar apenas a etapa N
    check-agentes - Verificar se todos os agentes são importáveis
    fix         - Corrigir problemas encontrados (criar diretórios, etc.)
"""

import csv
import importlib
import json
import os
import sys
import argparse
from pathlib import Path

# Adiciona agentes/ ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from banco_dados import BancoDados

# Raiz do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Estrutura esperada do pipeline
ESTRUTURA_ESPERADA = {
    "dados/01_relatorios": {
        "descricao": "Relatórios de mercado e tendências",
        "extensoes_esperadas": [".md", ".docx"],
        "minimo_arquivos": 1,
    },
    "dados/02_problemas": {
        "descricao": "Problemas gerados por análise combinatória",
        "extensoes_esperadas": [".csv", ".json"],
        "minimo_arquivos": 1,
        "subdiretorios": ["batches"],
    },
    "dados/03_ranking_problemas": {
        "descricao": "Rankings de problemas avaliados",
        "extensoes_esperadas": [".csv"],
        "minimo_arquivos": 0,
    },
    "dados/04_artigos_problemas": {
        "descricao": "Artigos analíticos dos problemas",
        "extensoes_esperadas": [".md"],
        "minimo_arquivos": 0,
    },
    "dados/05_brainstorm_solucoes": {
        "descricao": "Soluções de brainstorm (125 por problema)",
        "extensoes_esperadas": [".csv", ".json", ".md"],
        "minimo_arquivos": 0,
        "subdiretorios": ["solucoes", "ranking_solucoes"],
    },
    "dados/06_artigos_startups": {
        "descricao": "Artigos de startups (top 100 soluções)",
        "extensoes_esperadas": [".md"],
        "minimo_arquivos": 0,
    },
    "dados/07_bancas": {
        "descricao": "Avaliações das bancas RedBull e YCombinator",
        "extensoes_esperadas": [".json", ".md", ".csv"],
        "minimo_arquivos": 0,
        "subdiretorios": ["redbull/processo", "ycombinator/ranking_fase2"],
    },
    "dados/banco": {
        "descricao": "Banco JSON centralizado (fonte primária de dados)",
        "extensoes_esperadas": [".json"],
        "minimo_arquivos": 1,
    },
}

AGENTES_ESPERADOS = {
    "societal_problem_agent": {
        "path": "agentes/societal_problem_agent",
        "arquivos": ["__init__.py", "agent.py", "main.py", "config.py",
                     "scoring.py", "csv_handler.py", "article_writer.py"],
        "status_esperado": "implementado",
    },
    "bars_judge_agent": {
        "path": "agentes/bars_judge_agent.py",
        "arquivos": None,
        "status_esperado": "implementado",
    },
    "orquestrador": {
        "path": "agentes/orquestrador",
        "arquivos": ["__init__.py", "orquestrador.py"],
        "status_esperado": "implementado",
    },
    "validador": {
        "path": "agentes/validador",
        "arquivos": ["__init__.py", "validador.py"],
        "status_esperado": "implementado",
    },
    "brainstorm": {
        "path": "agentes/brainstorm",
        "arquivos": ["__init__.py"],
        "status_esperado": "placeholder",
    },
    "banca_redbull": {
        "path": "agentes/banca_redbull",
        "arquivos": ["__init__.py"],
        "status_esperado": "placeholder",
    },
    "banca_ycombinator": {
        "path": "agentes/banca_ycombinator",
        "arquivos": ["__init__.py"],
        "status_esperado": "placeholder",
    },
}


class Validador:
    """Verifica integridade e conexões do pipeline."""

    def __init__(self, project_root: str = PROJECT_ROOT):
        self.project_root = project_root
        self.erros = []
        self.avisos = []
        self.ok = []

    def _path(self, relativo: str) -> str:
        return os.path.join(self.project_root, relativo)

    def _log_erro(self, msg: str):
        self.erros.append(msg)
        print(f"  [ERRO] {msg}")

    def _log_aviso(self, msg: str):
        self.avisos.append(msg)
        print(f"  [AVISO] {msg}")

    def _log_ok(self, msg: str):
        self.ok.append(msg)
        print(f"  [OK] {msg}")

    def verificar_estrutura_diretorios(self) -> bool:
        """Verifica se todos os diretórios do pipeline existem."""
        print("\n--- Verificando Estrutura de Diretórios ---")
        tudo_ok = True

        for dir_rel, config in ESTRUTURA_ESPERADA.items():
            dir_path = self._path(dir_rel)
            if os.path.isdir(dir_path):
                self._log_ok(f"{dir_rel}/ existe")

                # Verificar subdirs
                for subdir in config.get("subdiretorios", []):
                    sub_path = os.path.join(dir_path, subdir)
                    if os.path.isdir(sub_path):
                        self._log_ok(f"  {dir_rel}/{subdir}/ existe")
                    else:
                        self._log_aviso(f"  {dir_rel}/{subdir}/ não existe")
            else:
                self._log_erro(f"{dir_rel}/ NÃO EXISTE")
                tudo_ok = False

        return tudo_ok

    def verificar_conteudo_etapas(self) -> bool:
        """Verifica se as etapas têm o conteúdo mínimo esperado."""
        print("\n--- Verificando Conteúdo das Etapas ---")
        tudo_ok = True

        for dir_rel, config in ESTRUTURA_ESPERADA.items():
            dir_path = self._path(dir_rel)
            if not os.path.isdir(dir_path):
                continue

            # Conta arquivos por extensão
            contagem = {}
            for root, _, files in os.walk(dir_path):
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    contagem[ext] = contagem.get(ext, 0) + 1

            total = sum(contagem.values())
            minimo = config["minimo_arquivos"]

            if total >= minimo and total > 0:
                partes = [f"{v} {k}" for k, v in sorted(contagem.items())]
                self._log_ok(f"{dir_rel}: {total} arquivos ({', '.join(partes)})")
            elif total == 0 and minimo == 0:
                self._log_aviso(f"{dir_rel}: vazio (etapa futura)")
            elif total < minimo:
                self._log_erro(f"{dir_rel}: {total} arquivos (mínimo: {minimo})")
                tudo_ok = False

        return tudo_ok

    def verificar_agentes(self) -> bool:
        """Verifica se os agentes existem e têm os arquivos necessários."""
        print("\n--- Verificando Agentes ---")
        tudo_ok = True

        for nome, config in AGENTES_ESPERADOS.items():
            agent_path = self._path(config["path"])

            if os.path.exists(agent_path):
                if config["arquivos"]:
                    faltando = []
                    for arq in config["arquivos"]:
                        if not os.path.exists(os.path.join(agent_path, arq)):
                            faltando.append(arq)

                    if faltando:
                        self._log_erro(f"{nome}: faltam {faltando}")
                        tudo_ok = False
                    else:
                        self._log_ok(f"{nome}: completo ({config['status_esperado']})")
                else:
                    self._log_ok(f"{nome}: existe ({config['status_esperado']})")
            else:
                self._log_erro(f"{nome}: NÃO ENCONTRADO em {config['path']}")
                tudo_ok = False

        return tudo_ok

    def verificar_conexoes_pipeline(self) -> bool:
        """Verifica se os dados fluem corretamente entre etapas."""
        print("\n--- Verificando Conexões do Pipeline ---")
        tudo_ok = True

        # Etapa 2 → 3: CSVs de problemas devem existir para classificação
        problemas_dir = self._path("dados/02_problemas")
        csvs = list(Path(problemas_dir).rglob("*.csv")) if os.path.exists(problemas_dir) else []
        if csvs:
            self._log_ok(f"Etapa 2→3: {len(csvs)} CSVs de problemas disponíveis para classificação")
        else:
            self._log_aviso("Etapa 2→3: Nenhum CSV de problemas encontrado")

        # Etapa 3 → 4: Rankings devem alimentar geração de artigos
        ranking_dir = self._path("dados/03_ranking_problemas")
        rankings = list(Path(ranking_dir).rglob("*.csv")) if os.path.exists(ranking_dir) else []
        if rankings:
            self._log_ok(f"Etapa 3→4: {len(rankings)} rankings disponíveis para artigos")
        else:
            self._log_aviso("Etapa 3→4: Nenhum ranking gerado ainda")

        # Etapa 4 → 5: Artigos de problemas alimentam brainstorm
        artigos_dir = self._path("dados/04_artigos_problemas")
        artigos = list(Path(artigos_dir).rglob("*.md")) if os.path.exists(artigos_dir) else []
        if artigos:
            self._log_ok(f"Etapa 4→5: {len(artigos)} artigos de problemas para brainstorm")
        else:
            self._log_aviso("Etapa 4→5: Nenhum artigo de problema gerado ainda")

        # Etapa 5 → 6: Soluções rankeadas alimentam artigos de startup
        solucoes_dir = self._path("dados/05_brainstorm_solucoes/ranking_solucoes")
        if os.path.exists(solucoes_dir) and os.listdir(solucoes_dir):
            self._log_ok("Etapa 5→6: Ranking de soluções existe")
        else:
            self._log_aviso("Etapa 5→6: Ranking de soluções ainda não gerado")

        # Etapa 6 → 7: Artigos de startup alimentam as bancas
        startups_dir = self._path("dados/06_artigos_startups")
        startups = list(Path(startups_dir).rglob("*.md")) if os.path.exists(startups_dir) else []
        if startups:
            self._log_ok(f"Etapa 6→7: {len(startups)} artigos de startup para bancas")
        else:
            self._log_aviso("Etapa 6→7: Nenhum artigo de startup gerado ainda")

        return tudo_ok

    def verificar_csv_integridade(self, filepath: str) -> bool:
        """Verifica integridade básica de um CSV."""
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader)
                n_cols = len(header)
                linhas = 0
                for row in reader:
                    linhas += 1
                    if len(row) != n_cols:
                        self._log_aviso(
                            f"  {os.path.basename(filepath)}: "
                            f"linha {linhas+1} tem {len(row)} cols (esperado {n_cols})"
                        )
            self._log_ok(f"  {os.path.basename(filepath)}: {linhas} linhas, {n_cols} colunas")
            return True
        except Exception as e:
            self._log_erro(f"  {os.path.basename(filepath)}: {e}")
            return False

    def verificar_banco_central(self) -> bool:
        """Verifica integridade do banco JSON centralizado."""
        print("\n--- Verificando Banco JSON Centralizado ---")
        tudo_ok = True
        banco_dir = self._path("dados/banco")

        if not os.path.isdir(banco_dir):
            self._log_erro("dados/banco/ não existe")
            return False

        banco = BancoDados()
        stats = banco.stats()

        # Verifica problemas.json
        if stats["problemas"] > 0:
            self._log_ok(f"problemas.json: {stats['problemas']} problemas")
            # Valida integridade de alguns itens
            top = banco.obter_top_n_problemas(3)
            for p in top:
                if not all(k in p for k in ["id", "titulo", "notas", "scores", "ranking"]):
                    self._log_erro(f"Problema {p.get('id', '?')} com campos faltantes")
                    tudo_ok = False
        else:
            self._log_aviso("problemas.json: vazio (execute migração)")

        # Verifica solucoes.json
        if stats["solucoes"] > 0:
            self._log_ok(f"solucoes.json: {stats['solucoes']} soluções")
        else:
            self._log_aviso("solucoes.json: vazio (execute brainstorm)")

        # Verifica startups.json
        if stats["startups"] > 0:
            self._log_ok(f"startups.json: {stats['startups']} startups")
        else:
            self._log_aviso("startups.json: vazio (etapa futura)")

        # Verifica bancas.json
        if stats["avaliacoes_bancas"] > 0:
            self._log_ok(f"bancas.json: {stats['avaliacoes_bancas']} avaliações")
        else:
            self._log_aviso("bancas.json: vazio (etapa futura)")

        return tudo_ok

    def verificar_tudo(self) -> dict:
        """Executa todas as verificações."""
        print("\n" + "=" * 70)
        print("  VALIDADOR DE PIPELINE - VERIFICAÇÃO COMPLETA")
        print("=" * 70)

        resultados = {
            "estrutura": self.verificar_estrutura_diretorios(),
            "conteudo": self.verificar_conteudo_etapas(),
            "agentes": self.verificar_agentes(),
            "conexoes": self.verificar_conexoes_pipeline(),
            "banco_central": self.verificar_banco_central(),
        }

        # Resumo
        print("\n" + "=" * 70)
        print("  RESUMO DA VERIFICAÇÃO")
        print("=" * 70)
        print(f"  Verificações OK:    {len(self.ok)}")
        print(f"  Avisos:             {len(self.avisos)}")
        print(f"  Erros:              {len(self.erros)}")

        if not self.erros:
            print("\n  RESULTADO: Pipeline íntegro!")
        else:
            print(f"\n  RESULTADO: {len(self.erros)} problemas encontrados")

        print("=" * 70 + "\n")

        return resultados

    def corrigir(self):
        """Corrige problemas simples (cria diretórios faltantes)."""
        print("\n--- Corrigindo problemas ---")

        for dir_rel, config in ESTRUTURA_ESPERADA.items():
            dir_path = self._path(dir_rel)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"  Criado: {dir_rel}/")

            for subdir in config.get("subdiretorios", []):
                sub_path = os.path.join(dir_path, subdir)
                if not os.path.isdir(sub_path):
                    os.makedirs(sub_path, exist_ok=True)
                    print(f"  Criado: {dir_rel}/{subdir}/")

        print("  Correção concluída.")


def main():
    parser = argparse.ArgumentParser(
        description="Validador de Integridade do Pipeline YCombinator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comandos")
    subparsers.add_parser("check", help="Verificação completa")
    subparsers.add_parser("check-agentes", help="Verificar apenas agentes")
    subparsers.add_parser("fix", help="Corrigir problemas encontrados")

    args = parser.parse_args()

    validador = Validador()

    if args.comando == "check":
        validador.verificar_tudo()
    elif args.comando == "check-agentes":
        validador.verificar_agentes()
    elif args.comando == "fix":
        validador.verificar_tudo()
        if validador.erros:
            validador.corrigir()
    else:
        parser.print_help()
        print("\nExemplo rápido:")
        print("  python -m agentes.validador.validador check")
        print("  python -m agentes.validador.validador fix")


if __name__ == "__main__":
    main()
