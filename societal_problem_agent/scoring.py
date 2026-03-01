"""
Motor de Pontuação (Scoring Engine)

Avalia cada problema contra todos os critérios do framework,
calcula pontuações ponderadas por categoria e total,
e gera o ranking final.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from .config import (
    SCORING_FRAMEWORK,
    SCORE_MIN,
    SCORE_MAX,
    EVALUATION_PROMPT_TEMPLATE,
    get_max_possible_score,
    get_category_max_score,
)


@dataclass
class CriterionScore:
    """Pontuação de um critério individual."""
    categoria_key: str
    categoria_nome: str
    criterio_key: str
    criterio_nome: str
    peso: int
    nota: int  # 1-10
    nota_ponderada: float  # nota * peso
    justificativa: str

    @property
    def nota_maxima_ponderada(self) -> float:
        return self.peso * SCORE_MAX


@dataclass
class CategoryScore:
    """Pontuação agregada de uma categoria."""
    categoria_key: str
    categoria_nome: str
    pontuacao_obtida: float
    pontuacao_maxima: float
    percentual: float
    criterios: list  # List[CriterionScore]

    @property
    def nota_media(self) -> float:
        if not self.criterios:
            return 0
        return sum(c.nota for c in self.criterios) / len(self.criterios)


@dataclass
class ProblemScore:
    """Pontuação completa de um problema."""
    problema_id: int
    problema_titulo: str
    problema_descricao: str
    problema_desenvolvimento: str
    categorias: dict = field(default_factory=dict)  # Dict[str, CategoryScore]
    pontuacao_total: float = 0
    pontuacao_maxima: float = 0
    percentual: float = 0
    ranking: int = 0
    artigo: str = ""

    def calcular_totais(self):
        """Calcula os totais a partir das categorias."""
        self.pontuacao_total = sum(c.pontuacao_obtida for c in self.categorias.values())
        self.pontuacao_maxima = get_max_possible_score()
        self.percentual = (self.pontuacao_total / self.pontuacao_maxima * 100) if self.pontuacao_maxima > 0 else 0


class ScoringEngine:
    """Motor de pontuação que avalia problemas contra o framework."""

    def __init__(self, llm_evaluator=None):
        """
        Args:
            llm_evaluator: Função que recebe um prompt e retorna a resposta do LLM.
                          Assinatura: (prompt: str) -> str
        """
        self.llm_evaluator = llm_evaluator
        self.framework = SCORING_FRAMEWORK

    def avaliar_criterio(self, problema: dict, categoria_key: str, criterio_key: str) -> CriterionScore:
        """Avalia um único critério para um problema."""
        categoria = self.framework[categoria_key]
        criterio = categoria["criterios"][criterio_key]

        # Formata a escala para o prompt
        escala_formatada = "\n".join(
            f"  - {nota}: {desc}" for nota, desc in criterio["escala"].items()
        )

        prompt = EVALUATION_PROMPT_TEMPLATE.format(
            problema_titulo=problema["Problema"],
            problema_descricao=problema.get("Descrição Geral", problema.get("Descricao Geral", "")),
            problema_desenvolvimento=problema.get("Desenvolvimento", ""),
            categoria_nome=categoria["nome"],
            criterio_nome=criterio["nome"],
            peso=criterio["peso"],
            pergunta=criterio["pergunta"],
            referencia=criterio["referencia"],
            escala_formatada=escala_formatada
        )

        if self.llm_evaluator:
            resposta = self.llm_evaluator(prompt)
            nota, justificativa = self._parse_evaluation_response(resposta)
        else:
            # Avaliação heurística quando não há LLM disponível
            nota, justificativa = self._avaliacao_heuristica(
                problema, categoria_key, criterio_key
            )

        # Garantir que a nota está nos limites
        nota = max(SCORE_MIN, min(SCORE_MAX, nota))

        return CriterionScore(
            categoria_key=categoria_key,
            categoria_nome=categoria["nome"],
            criterio_key=criterio_key,
            criterio_nome=criterio["nome"],
            peso=criterio["peso"],
            nota=nota,
            nota_ponderada=nota * criterio["peso"],
            justificativa=justificativa
        )

    def avaliar_categoria(self, problema: dict, categoria_key: str) -> CategoryScore:
        """Avalia todos os critérios de uma categoria para um problema."""
        categoria = self.framework[categoria_key]
        criterios_scores = []

        for criterio_key in categoria["criterios"]:
            score = self.avaliar_criterio(problema, categoria_key, criterio_key)
            criterios_scores.append(score)

        pontuacao_obtida = sum(c.nota_ponderada for c in criterios_scores)
        pontuacao_maxima = get_category_max_score(categoria_key)
        percentual = (pontuacao_obtida / pontuacao_maxima * 100) if pontuacao_maxima > 0 else 0

        return CategoryScore(
            categoria_key=categoria_key,
            categoria_nome=categoria["nome"],
            pontuacao_obtida=pontuacao_obtida,
            pontuacao_maxima=pontuacao_maxima,
            percentual=percentual,
            criterios=criterios_scores
        )

    def avaliar_problema(self, problema: dict, problema_id: int) -> ProblemScore:
        """Avalia um problema completo contra todas as categorias."""
        problem_score = ProblemScore(
            problema_id=problema_id,
            problema_titulo=problema["Problema"],
            problema_descricao=problema.get("Descrição Geral", problema.get("Descricao Geral", "")),
            problema_desenvolvimento=problema.get("Desenvolvimento", "")
        )

        for categoria_key in self.framework:
            cat_score = self.avaliar_categoria(problema, categoria_key)
            problem_score.categorias[categoria_key] = cat_score

        problem_score.calcular_totais()
        return problem_score

    def rankear_problemas(self, scores: list) -> list:
        """Rankeia uma lista de ProblemScores por pontuação total descendente."""
        sorted_scores = sorted(scores, key=lambda s: s.pontuacao_total, reverse=True)
        for i, score in enumerate(sorted_scores, 1):
            score.ranking = i
        return sorted_scores

    def _parse_evaluation_response(self, resposta: str) -> tuple:
        """Extrai nota e justificativa da resposta do LLM."""
        nota = 5  # default
        justificativa = "Avaliação padrão"

        # Tenta extrair a nota
        nota_match = re.search(r"NOTA:\s*(\d+)", resposta)
        if nota_match:
            nota = int(nota_match.group(1))

        # Tenta extrair a justificativa
        just_match = re.search(r"JUSTIFICATIVA:\s*(.+?)(?:\n|$)", resposta, re.DOTALL)
        if just_match:
            justificativa = just_match.group(1).strip()

        return nota, justificativa

    def _avaliacao_heuristica(self, problema: dict, categoria_key: str, criterio_key: str) -> tuple:
        """
        Avaliação heurística baseada em análise textual do problema.
        Usada quando não há LLM disponível.
        Analisa keywords no texto para estimar notas.
        """
        texto = (
            problema.get("Problema", "") + " " +
            problema.get("Descrição Geral", problema.get("Descricao Geral", "")) + " " +
            problema.get("Desenvolvimento", "")
        ).lower()

        # Dicionários de palavras-chave por critério (simplificado)
        keywords_positivas = {
            # Categoria 1: Dor
            "intensidade_dor_financeira": ["perda", "custo", "prejuízo", "receita", "bilhões", "milhões", "financeiro", "econômico", "falência", "colapso"],
            "existencia_gambiarras": ["planilha", "manual", "improviso", "gambiarra", "whatsapp", "papel", "processo manual", "artesanal"],
            "frequencia_problema": ["diário", "constante", "frequente", "recorrente", "crônico", "permanente", "contínuo", "rotina"],
            "urgencia_percebida": ["urgente", "imediato", "crise", "emergência", "crítico", "inadiável", "pressão"],
            "intensidade_dor_tempo": ["tempo", "horas", "demora", "lento", "burocracia", "espera", "produtividade"],
            "risco_atrelado": ["multa", "processo", "morte", "acidente", "risco", "regulação", "penalidade", "compliance"],
            "nivel_frustracao": ["frustrante", "estresse", "caos", "confusão", "ineficiente", "complicado", "complexo"],
            "consequencia_erro": ["falha", "erro", "colapso", "destruição", "catastrófico", "irreversível"],
            "observabilidade_comportamento": ["visível", "mensurável", "dados", "métricas", "observável", "tangível"],
            "clareza_persona": ["empresa", "setor", "profissional", "gestor", "operador", "agricultor", "médico", "indústria"],
            # Categoria 2: Mercado
            "tam": ["global", "bilhões", "trilhões", "mundial", "massivo", "mercado", "setor inteiro"],
            "crescimento_mercado": ["crescimento", "expansão", "acelerado", "boom", "emergente", "explosão"],
            "capacidade_monopolio_nicho": ["nicho", "especializado", "único", "primeiro", "pioneiro"],
            "amplitude_demografica": ["população", "milhões de pessoas", "massa", "universal", "todos"],
            "escalabilidade_nao_linear": ["software", "plataforma", "digital", "automatizado", "escalável", "IA", "algoritmo"],
            "tamanho_ticket": ["enterprise", "corporativo", "contrato", "assinatura", "premium"],
            "potencial_expansao_produto": ["plataforma", "ecossistema", "módulos", "adjacente", "expansão"],
            "penetracao_digital": ["digital", "tecnologia", "online", "app", "sistema", "software"],
            "capacidade_internacionalizacao": ["global", "mundial", "internacional", "países", "universal"],
            "dependencia_infraestrutura_fisica": ["digital", "software", "cloud", "virtual", "online"],
            # Categoria 3: Timing
            "timing_tecnologico": ["IA", "LLM", "blockchain", "API", "machine learning", "inteligência artificial", "GPT", "automação"],
            "timing_regulatorio": ["regulação", "lei", "LGPD", "compliance", "obrigatório", "decreto", "norma"],
            "mudanca_comportamental": ["geração Z", "envelhecimento", "urbanização", "digital", "remoto", "sustentabilidade"],
            "pressao_macroeconomica": ["crise", "inflação", "juros", "recessão", "custo", "economia"],
            "janela_oportunidade": ["emergente", "nascente", "início", "oportunidade", "vácuo"],
            # Categoria 4: Validação
            "acesso_usuarios": ["acessível", "comunidade", "online", "fácil acesso", "disponível"],
            "velocidade_validacao": ["rápido", "simples", "teste", "validação", "experimento"],
            "facilidade_mvp": ["simples", "no-code", "serviço", "consultoria", "manual"],
            "necessidade_mudanca_habito": ["intuitivo", "natural", "existente", "atual", "fluxo"],
            "densidade_dados": ["dados", "API", "relatório", "pesquisa", "estatística", "base de dados"],
            "tempo_aha_moment": ["imediato", "instantâneo", "rápido", "valor", "resultado"],
            "dependencia_multiplos_lados": ["direto", "unilateral", "simples", "B2B", "B2C"],
            "visibilidade_feedback": ["mensurável", "métrica", "feedback", "resultado", "indicador"],
            # Categoria 5: Monetização
            "disposicao_pagar": ["pagar", "investir", "orçamento", "comprar", "contratar", "adquirir"],
            "clareza_pagador": ["empresa", "corporativo", "B2B", "comprador", "cliente"],
            "orcamento_preexistente": ["orçamento", "budget", "verba", "investimento", "gasto atual"],
            "ciclo_vendas": ["rápido", "self-service", "online", "imediato", "PLG"],
            "frequencia_monetizacao": ["mensal", "recorrente", "assinatura", "SaaS", "subscription"],
            "poder_precificacao": ["crítico", "essencial", "vital", "indispensável", "insubstituível"],
            "cac_projetado": ["orgânico", "viral", "boca a boca", "comunidade", "SEO", "inbound"],
            # Categoria 6: Defensibilidade
            "ausencia_monopolios": ["fragmentado", "nenhum líder", "vácuo", "sem solução", "desatendido"],
            "potencial_efeito_rede": ["rede", "comunidade", "marketplace", "plataforma", "ecossistema"],
            "switching_cost": ["integração", "dados", "treinamento", "migração", "lock-in"],
            "acumulo_dados_proprietarios": ["dados proprietários", "base própria", "inteligência", "benchmark"],
            "diferenciacao_10x": ["revolução", "disruptivo", "inovador", "nunca antes", "primeiro"],
            "fragmentacao_concorrencia": ["fragmentado", "pequenos", "artesanal", "informal", "disperso"],
            # Categoria 7: Riscos
            "risco_tarpit": ["novo", "inédito", "diferente", "único", "inovador"],
            "risco_legal": ["legal", "regulado", "permitido", "livre", "simples"],
            "dependencia_parceiro": ["independente", "próprio", "autônomo", "infraestrutura própria"],
            "alinhamento_ods": ["sustentável", "clima", "social", "ambiental", "ODS", "ESG", "inclusão", "saúde"],
        }

        keywords_negativas = {
            "dependencia_infraestrutura_fisica": ["fábrica", "logística", "hardware", "construção", "físico", "infraestrutura pesada"],
            "risco_tarpit": ["app", "rede social", "marketplace", "descobrir bares", "agenda", "centenas tentaram"],
            "risco_legal": ["ilegal", "proibido", "regulado", "cadeia", "multa milionária", "restrito"],
            "dependencia_parceiro": ["Facebook", "Apple", "Google", "API", "plataforma terceira"],
        }

        # Contagem de matches
        positivas = keywords_positivas.get(criterio_key, [])
        negativas = keywords_negativas.get(criterio_key, [])

        score_pos = sum(1 for kw in positivas if kw in texto)
        score_neg = sum(1 for kw in negativas if kw in texto)

        # Calcula nota base (5) + ajustes
        nota_base = 5
        nota = nota_base + score_pos - score_neg

        # Para critérios invertidos (onde negativo = nota baixa)
        criterios_invertidos = [
            "risco_tarpit", "risco_legal", "dependencia_parceiro",
            "dependencia_infraestrutura_fisica", "dependencia_multiplos_lados",
            "necessidade_mudanca_habito"
        ]

        if criterio_key in criterios_invertidos and score_neg > score_pos:
            nota = nota_base - (score_neg - score_pos)

        # Clamping
        nota = max(SCORE_MIN, min(SCORE_MAX, nota))

        # Justificativa
        matches = [kw for kw in positivas if kw in texto]
        if matches:
            justificativa = f"Análise heurística: palavras-chave detectadas - {', '.join(matches[:3])}"
        else:
            justificativa = "Análise heurística: avaliação baseada no contexto geral do problema"

        return nota, justificativa

    def formatar_pontuacao(self, problem_score: ProblemScore) -> str:
        """Formata a pontuação de um problema para exibição."""
        lines = []
        lines.append(f"{'='*80}")
        lines.append(f"PROBLEMA #{problem_score.problema_id}: {problem_score.problema_titulo}")
        lines.append(f"{'='*80}")
        lines.append("")

        for cat_key, cat_score in problem_score.categorias.items():
            lines.append(f"### {cat_score.categoria_nome}")
            lines.append(f"    Pontuação: {cat_score.pontuacao_obtida:.0f}/{cat_score.pontuacao_maxima:.0f} ({cat_score.percentual:.1f}%)")
            lines.append("")

            for crit in cat_score.criterios:
                barra = "█" * crit.nota + "░" * (10 - crit.nota)
                lines.append(f"    [{barra}] {crit.nota}/10 (x{crit.peso}) = {crit.nota_ponderada:.0f}pts | {crit.criterio_nome}")
                lines.append(f"      → {crit.justificativa}")
            lines.append("")

        lines.append(f"{'='*80}")
        lines.append(f"PONTUAÇÃO TOTAL: {problem_score.pontuacao_total:.0f}/{problem_score.pontuacao_maxima:.0f} ({problem_score.percentual:.1f}%)")
        if problem_score.ranking > 0:
            lines.append(f"RANKING: #{problem_score.ranking}")
        lines.append(f"{'='*80}")

        return "\n".join(lines)
