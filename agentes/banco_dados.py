#!/usr/bin/env python3
"""
Banco de Dados Central - Sistema Unificado de Informações
==========================================================

Módulo central que todos os agentes usam para ler/escrever dados.
Elimina redundância de arquivos e economiza tokens ao fornecer
apenas os campos necessários para cada operação.

Arquivos gerenciados (dados/banco/):
    problemas.json   - 498 problemas com scores e metadados compactos
    solucoes.json    - Soluções de brainstorm com ranking
    startups.json    - Artigos de startup compactos
    bancas.json      - Avaliações das bancas RedBull + YCombinator

Princípios:
    1. Single source of truth - cada dado vive em UM arquivo
    2. Representações compactas - JSON estruturado, sem texto redundante
    3. Rankings pré-computados - mantidos atualizados a cada escrita
    4. Artigos sob demanda - gerados quando necessário, não armazenados
    5. Contexto mínimo - cada agente recebe só o que precisa
"""

import json
import os
from datetime import datetime
from typing import Optional


# Raiz do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BANCO_DIR = os.path.join(PROJECT_ROOT, "dados", "banco")

# Arquivos do banco
PROBLEMAS_JSON = os.path.join(BANCO_DIR, "problemas.json")
SOLUCOES_JSON = os.path.join(BANCO_DIR, "solucoes.json")
STARTUPS_JSON = os.path.join(BANCO_DIR, "startups.json")
BANCAS_JSON = os.path.join(BANCO_DIR, "bancas.json")

# Máximos do framework (constantes para cálculos)
MAX_CATEGORIAS = {
    "dor": 410,
    "mercado": 340,
    "timing": 220,
    "validacao": 300,
    "monetizacao": 260,
    "defensibilidade": 200,
    "riscos": 160,
}
MAX_TOTAL = 1890

# Mapeamento de nomes curtos para nomes completos
NOMES_CATEGORIAS = {
    "dor": "A Natureza da Dor e o Comportamento",
    "mercado": "Tamanho de Mercado e Potencial de Escala",
    "timing": "Timing e Why Now",
    "validacao": "Validação e Execução Lean",
    "monetizacao": "Monetização e Viabilidade de Negócio",
    "defensibilidade": "Defensibilidade e Competição",
    "riscos": "Riscos Fatais (Red Flags)",
}

# Mapeamento de campos de notas para suas categorias
NOTAS_POR_CATEGORIA = {
    "dor": [
        "dor_financeira", "gambiarras", "frequencia", "urgencia",
        "dor_tempo", "risco", "frustracao", "consequencia_erro",
        "observabilidade", "clareza_persona"
    ],
    "mercado": [
        "tam", "crescimento", "monopolio_local", "amplitude",
        "escala_nao_linear", "ticket", "expansao", "penetracao_digital",
        "internacionalizacao", "dep_infraestrutura"
    ],
    "timing": [
        "timing_tech", "timing_regulatorio", "mudanca_comportamental",
        "pressao_macro", "janela"
    ],
    "validacao": [
        "acesso_usuarios", "velocidade_validacao", "facilidade_mvp",
        "mudanca_habito", "dados_disponiveis", "aha_moment",
        "multiplos_lados", "feedback"
    ],
    "monetizacao": [
        "wtp", "clareza_pagador", "orcamento", "ciclo_vendas",
        "recorrencia", "poder_preco", "cac"
    ],
    "defensibilidade": [
        "ausencia_monopolios", "efeito_rede", "switching_cost",
        "dados_proprietarios", "diferenciacao_10x", "fragmentacao"
    ],
    "riscos": [
        "tarpit", "risco_legal", "platform_risk", "alinhamento_ods"
    ],
}

# Pesos por critério (framework original)
PESOS = {
    "dor_financeira": 5, "gambiarras": 4, "frequencia": 5, "urgencia": 4,
    "dor_tempo": 4, "risco": 5, "frustracao": 3, "consequencia_erro": 5,
    "observabilidade": 3, "clareza_persona": 3,
    "tam": 5, "crescimento": 5, "monopolio_local": 3, "amplitude": 3,
    "escala_nao_linear": 4, "ticket": 3, "expansao": 3, "penetracao_digital": 3,
    "internacionalizacao": 2, "dep_infraestrutura": 3,
    "timing_tech": 5, "timing_regulatorio": 4, "mudanca_comportamental": 4,
    "pressao_macro": 5, "janela": 4,
    "acesso_usuarios": 4, "velocidade_validacao": 4, "facilidade_mvp": 4,
    "mudanca_habito": 4, "dados_disponiveis": 3, "aha_moment": 4,
    "multiplos_lados": 4, "feedback": 3,
    "wtp": 5, "clareza_pagador": 4, "orcamento": 3, "ciclo_vendas": 4,
    "recorrencia": 4, "poder_preco": 3, "cac": 3,
    "ausencia_monopolios": 4, "efeito_rede": 4, "switching_cost": 3,
    "dados_proprietarios": 3, "diferenciacao_10x": 3, "fragmentacao": 3,
    "tarpit": 5, "risco_legal": 4, "platform_risk": 4, "alinhamento_ods": 3,
}


def _carregar_json(filepath: str, default: dict = None) -> dict:
    """Carrega um arquivo JSON ou retorna default."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or {"versao": "2.0", "total": 0, "itens": []}


def _salvar_json(filepath: str, data: dict):
    """Salva dados em JSON compacto."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data["atualizado_em"] = datetime.now().isoformat()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def calcular_scores(notas: dict) -> dict:
    """Calcula scores de categorias e total a partir das notas brutas."""
    categorias = {}
    total_pts = 0

    for cat_key, campos in NOTAS_POR_CATEGORIA.items():
        pts = 0
        for campo in campos:
            nota = notas.get(campo, 5)
            peso = PESOS.get(campo, 3)
            pts += nota * peso
        max_cat = MAX_CATEGORIAS[cat_key]
        categorias[cat_key] = {
            "pts": pts,
            "max": max_cat,
            "pct": round(pts / max_cat * 100, 1) if max_cat > 0 else 0,
        }
        total_pts += pts

    return {
        "total": total_pts,
        "max": MAX_TOTAL,
        "pct": round(total_pts / MAX_TOTAL * 100, 1),
        "categorias": categorias,
    }


def gerar_tags(titulo: str, descricao: str, notas: dict) -> list:
    """Gera tags automáticas baseadas no conteúdo e scores."""
    tags = []
    texto = (titulo + " " + descricao).lower()

    mapa_tags = {
        "saude": ["saúde", "médic", "farmac", "hospital", "doença"],
        "clima": ["clima", "carbono", "emissão", "aquecimento", "térmico"],
        "agua": ["água", "hídric", "seca", "irrigação", "dessalinização"],
        "ia": ["inteligência artificial", " ia ", "machine learning", "algoritmo", "llm"],
        "fintech": ["financ", "crédito", "banco", "pagamento", "fintech"],
        "educacao": ["educação", "ensino", "escola", "aprendiza", "capacitação"],
        "energia": ["energia", "elétric", "solar", "eólica", "bateria"],
        "logistica": ["logística", "transporte", "cadeia de suprimento", "frete"],
        "agro": ["agrícol", "agronegoç", "safra", "plantação", "rural"],
        "regulacao": ["regulação", "lei", "compliance", "governança", "regulatório"],
        "seguranca": ["segurança", "cibernético", "fraude", "proteção", "risco"],
        "trabalho": ["trabalho", "emprego", "reskilling", "profissional"],
    }

    for tag, keywords in mapa_tags.items():
        if any(kw in texto for kw in keywords):
            tags.append(tag)

    # Tags baseadas em scores fortes
    for cat_key, campos in NOTAS_POR_CATEGORIA.items():
        media = sum(notas.get(c, 5) for c in campos) / len(campos)
        if media >= 7.5:
            tags.append(f"forte_{cat_key}")

    return tags[:8]


class BancoDados:
    """Interface central para acesso a dados do pipeline."""

    def __init__(self, banco_dir: str = BANCO_DIR):
        self.banco_dir = banco_dir
        self._problemas_path = os.path.join(banco_dir, "problemas.json")
        self._solucoes_path = os.path.join(banco_dir, "solucoes.json")
        self._startups_path = os.path.join(banco_dir, "startups.json")
        self._bancas_path = os.path.join(banco_dir, "bancas.json")

    # =========================================================================
    # PROBLEMAS
    # =========================================================================

    def carregar_problemas(self) -> dict:
        """Carrega o banco de problemas completo."""
        return _carregar_json(self._problemas_path)

    def salvar_problemas(self, data: dict):
        """Salva o banco de problemas."""
        _salvar_json(self._problemas_path, data)

    def obter_problema(self, problema_id: str) -> Optional[dict]:
        """Retorna um problema pelo ID."""
        data = self.carregar_problemas()
        for item in data.get("itens", []):
            if item["id"] == problema_id:
                return item
        return None

    def obter_top_n_problemas(self, n: int = 50) -> list:
        """Retorna os top N problemas por ranking."""
        data = self.carregar_problemas()
        itens = sorted(data.get("itens", []), key=lambda x: x.get("ranking", 9999))
        return itens[:n]

    def obter_problemas_resumo(self, n: int = None) -> list:
        """Retorna lista compacta: id, titulo, pct, ranking. Mínimo de tokens."""
        data = self.carregar_problemas()
        itens = sorted(data.get("itens", []), key=lambda x: x.get("ranking", 9999))
        if n:
            itens = itens[:n]
        return [
            {
                "id": p["id"],
                "titulo": p["titulo"],
                "pct": p["scores"]["pct"],
                "ranking": p["ranking"],
                "tags": p.get("tags", []),
            }
            for p in itens
        ]

    def adicionar_problema(self, problema: dict) -> str:
        """Adiciona um problema ao banco. Retorna o ID gerado."""
        data = self.carregar_problemas()
        itens = data.get("itens", [])

        # Gera ID sequencial
        max_id = 0
        for item in itens:
            num = int(item["id"][1:])
            if num > max_id:
                max_id = num
        novo_id = f"P{max_id + 1:04d}"

        problema["id"] = novo_id
        if "scores" not in problema and "notas" in problema:
            problema["scores"] = calcular_scores(problema["notas"])
        if "tags" not in problema:
            problema["tags"] = gerar_tags(
                problema.get("titulo", ""),
                problema.get("descricao", ""),
                problema.get("notas", {}),
            )

        itens.append(problema)
        data["itens"] = itens
        data["total"] = len(itens)
        self._reranquear_problemas(data)
        self.salvar_problemas(data)
        return novo_id

    def _reranquear_problemas(self, data: dict):
        """Reordena os problemas por score total descendente."""
        itens = data.get("itens", [])
        itens.sort(key=lambda x: x.get("scores", {}).get("pct", 0), reverse=True)
        for i, item in enumerate(itens, 1):
            item["ranking"] = i
        data["itens"] = itens

    # =========================================================================
    # CONTEXTOS PARA AGENTES (economia de tokens)
    # =========================================================================

    def contexto_para_brainstorm(self, problema_id: str) -> Optional[dict]:
        """
        Retorna contexto MÍNIMO para o agente de brainstorm.
        ~200 tokens em vez de ~4000 tokens de um artigo completo.
        """
        p = self.obter_problema(problema_id)
        if not p:
            return None
        return {
            "id": p["id"],
            "titulo": p["titulo"],
            "descricao": p["descricao"],
            "desenvolvimento": p["desenvolvimento"],
            "tags": p.get("tags", []),
            "score_pct": p["scores"]["pct"],
            "pontos_fortes": [
                cat for cat, dados in p["scores"]["categorias"].items()
                if dados["pct"] >= 65
            ],
            "pontos_fracos": [
                cat for cat, dados in p["scores"]["categorias"].items()
                if dados["pct"] < 50
            ],
        }

    def contexto_para_classificacao(self, titulo: str, descricao: str,
                                     desenvolvimento: str) -> dict:
        """
        Retorna contexto mínimo para classificação de um novo problema.
        Inclui benchmarks do banco existente para calibração.
        """
        data = self.carregar_problemas()
        itens = data.get("itens", [])

        # Estatísticas para calibração
        pcts = [i["scores"]["pct"] for i in itens] if itens else [50]
        media = sum(pcts) / len(pcts)
        top_50_min = sorted(pcts, reverse=True)[49] if len(pcts) >= 50 else 0

        return {
            "titulo": titulo,
            "descricao": descricao,
            "desenvolvimento": desenvolvimento,
            "benchmark": {
                "total_problemas": len(itens),
                "media_pct": round(media, 1),
                "top_50_corte": round(top_50_min, 1),
                "melhor_pct": round(max(pcts), 1) if pcts else 0,
            },
        }

    def contexto_para_artigo_startup(self, solucao_id: str) -> Optional[dict]:
        """Retorna contexto compacto para gerar artigo de startup."""
        sol = self.obter_solucao(solucao_id)
        if not sol:
            return None
        prob = self.obter_problema(sol["problema_id"])
        return {
            "solucao": sol,
            "problema": {
                "id": prob["id"],
                "titulo": prob["titulo"],
                "descricao": prob["descricao"],
                "tags": prob.get("tags", []),
                "score_pct": prob["scores"]["pct"],
            } if prob else None,
        }

    def contexto_para_banca(self, startup_id: str) -> Optional[dict]:
        """Retorna contexto compacto para avaliação por banca."""
        data = _carregar_json(self._startups_path)
        for item in data.get("itens", []):
            if item["id"] == startup_id:
                return item
        return None

    # =========================================================================
    # SOLUÇÕES (Brainstorm)
    # =========================================================================

    def carregar_solucoes(self) -> dict:
        """Carrega o banco de soluções."""
        return _carregar_json(self._solucoes_path)

    def obter_solucao(self, solucao_id: str) -> Optional[dict]:
        """Retorna uma solução pelo ID."""
        data = self.carregar_solucoes()
        for item in data.get("itens", []):
            if item["id"] == solucao_id:
                return item
        return None

    def obter_top_n_solucoes(self, n: int = 100) -> list:
        """Retorna as top N soluções por ranking."""
        data = self.carregar_solucoes()
        itens = sorted(data.get("itens", []), key=lambda x: x.get("ranking", 9999))
        return itens[:n]

    def adicionar_solucoes(self, solucoes: list, problema_id: str,
                           agente_id: int = 1) -> list:
        """
        Adiciona soluções ao banco e recomputa ranking.
        Retorna lista de IDs gerados.

        Args:
            solucoes: Lista de dicts com campos da solução.
            problema_id: ID do problema pai.
            agente_id: Número do agente de brainstorm (1-5).
        """
        data = self.carregar_solucoes()
        itens = data.get("itens", [])

        # Gera IDs sequenciais
        max_id = 0
        for item in itens:
            num = int(item["id"][1:])
            if num > max_id:
                max_id = num

        ids_gerados = []
        for sol in solucoes:
            max_id += 1
            novo_id = f"S{max_id:05d}"
            sol["id"] = novo_id
            sol["problema_id"] = problema_id
            sol["agente"] = agente_id
            sol["criado_em"] = datetime.now().isoformat()

            # Calcula score se não fornecido
            if "score" not in sol and "metricas" in sol:
                metricas = sol["metricas"]
                sol["score"] = round(
                    sum(metricas.values()) / len(metricas) * 10, 1
                )

            itens.append(sol)
            ids_gerados.append(novo_id)

        # Reranquear todas as soluções
        itens.sort(key=lambda x: x.get("score", 0), reverse=True)
        for i, item in enumerate(itens, 1):
            item["ranking"] = i

        data["itens"] = itens
        data["total"] = len(itens)
        data["top_100"] = [
            {"id": s["id"], "titulo": s["titulo"], "score": s["score"],
             "problema_id": s["problema_id"]}
            for s in itens[:100]
        ]

        _salvar_json(self._solucoes_path, data)
        return ids_gerados

    # =========================================================================
    # STARTUPS
    # =========================================================================

    def carregar_startups(self) -> dict:
        """Carrega o banco de startups."""
        return _carregar_json(self._startups_path)

    def adicionar_startup(self, startup: dict) -> str:
        """Adiciona uma startup ao banco."""
        data = self.carregar_startups()
        itens = data.get("itens", [])

        max_id = 0
        for item in itens:
            num = int(item["id"][2:])
            if num > max_id:
                max_id = num

        novo_id = f"ST{max_id + 1:04d}"
        startup["id"] = novo_id
        startup["criado_em"] = datetime.now().isoformat()

        itens.append(startup)
        data["itens"] = itens
        data["total"] = len(itens)
        _salvar_json(self._startups_path, data)
        return novo_id

    # =========================================================================
    # BANCAS
    # =========================================================================

    def carregar_bancas(self) -> dict:
        """Carrega avaliações das bancas."""
        return _carregar_json(self._bancas_path)

    def adicionar_avaliacao_banca(self, banca: str, startup_id: str,
                                   avaliacao: dict):
        """Adiciona avaliação de uma banca para uma startup."""
        data = self.carregar_bancas()
        if "avaliacoes" not in data:
            data["avaliacoes"] = []

        data["avaliacoes"].append({
            "banca": banca,
            "startup_id": startup_id,
            "avaliacao": avaliacao,
            "data": datetime.now().isoformat(),
        })
        data["total"] = len(data["avaliacoes"])
        _salvar_json(self._bancas_path, data)

    # =========================================================================
    # ESTATÍSTICAS
    # =========================================================================

    def stats(self) -> dict:
        """Retorna estatísticas gerais do banco."""
        prob = self.carregar_problemas()
        sol = self.carregar_solucoes()
        start = self.carregar_startups()
        ban = self.carregar_bancas()

        return {
            "problemas": prob.get("total", 0),
            "solucoes": sol.get("total", 0),
            "startups": start.get("total", 0),
            "avaliacoes_bancas": ban.get("total", 0),
        }
