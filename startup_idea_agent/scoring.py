"""
Motor de Pontuação para Ideias de Startup

Avalia cada ideia de startup contra os 22 critérios do framework de 5 categorias,
calcula pontuações ponderadas por categoria e total,
e gera o ranking final.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from .config import (
    IDEA_SCORING_FRAMEWORK,
    SCORE_MIN,
    SCORE_MAX,
    IDEA_EVALUATION_PROMPT_TEMPLATE,
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
class IdeaScore:
    """Pontuação completa de uma ideia de startup."""

    idea_id: int
    problema_titulo: str
    problema_descricao: str
    problema_desenvolvimento: str
    ideia_descricao: str = ""
    ideia_nome: str = ""
    ideia_tagline: str = ""
    categorias: dict = field(default_factory=dict)  # Dict[str, CategoryScore]
    pontuacao_total: float = 0
    pontuacao_maxima: float = 0
    percentual: float = 0
    ranking: int = 0
    artigo: str = ""

    def calcular_totais(self):
        """Calcula os totais a partir das categorias."""
        self.pontuacao_total = sum(
            c.pontuacao_obtida for c in self.categorias.values()
        )
        self.pontuacao_maxima = get_max_possible_score()
        self.percentual = (
            (self.pontuacao_total / self.pontuacao_maxima * 100)
            if self.pontuacao_maxima > 0
            else 0
        )


class IdeaScoringEngine:
    """Motor de pontuação que avalia ideias de startup contra o framework."""

    def __init__(self, llm_evaluator=None):
        """
        Args:
            llm_evaluator: Função que recebe um prompt e retorna a resposta do LLM.
                          Assinatura: (prompt: str) -> str
        """
        self.llm_evaluator = llm_evaluator
        self.framework = IDEA_SCORING_FRAMEWORK

    def avaliar_criterio(
        self,
        idea_score: IdeaScore,
        categoria_key: str,
        criterio_key: str,
    ) -> CriterionScore:
        """Avalia um único critério para uma ideia."""
        categoria = self.framework[categoria_key]
        criterio = categoria["criterios"][criterio_key]

        escala_formatada = "\n".join(
            f"  - {nota}: {desc}" for nota, desc in criterio["escala"].items()
        )

        prompt = IDEA_EVALUATION_PROMPT_TEMPLATE.format(
            problema_titulo=idea_score.problema_titulo,
            problema_descricao=idea_score.problema_descricao,
            ideia_descricao=idea_score.ideia_descricao,
            categoria_nome=categoria["nome"],
            criterio_nome=criterio["nome"],
            peso=criterio["peso"],
            pergunta=criterio["pergunta"],
            referencia=criterio["referencia"],
            escala_formatada=escala_formatada,
        )

        if self.llm_evaluator:
            resposta = self.llm_evaluator(prompt)
            nota, justificativa = self._parse_evaluation_response(resposta)
        else:
            nota, justificativa = self._avaliacao_heuristica(
                idea_score, categoria_key, criterio_key
            )

        nota = max(SCORE_MIN, min(SCORE_MAX, nota))

        return CriterionScore(
            categoria_key=categoria_key,
            categoria_nome=categoria["nome"],
            criterio_key=criterio_key,
            criterio_nome=criterio["nome"],
            peso=criterio["peso"],
            nota=nota,
            nota_ponderada=nota * criterio["peso"],
            justificativa=justificativa,
        )

    def avaliar_categoria(
        self, idea_score: IdeaScore, categoria_key: str
    ) -> CategoryScore:
        """Avalia todos os critérios de uma categoria para uma ideia."""
        categoria = self.framework[categoria_key]
        criterios_scores = []

        for criterio_key in categoria["criterios"]:
            score = self.avaliar_criterio(idea_score, categoria_key, criterio_key)
            criterios_scores.append(score)

        pontuacao_obtida = sum(c.nota_ponderada for c in criterios_scores)
        pontuacao_maxima = get_category_max_score(categoria_key)
        percentual = (
            (pontuacao_obtida / pontuacao_maxima * 100) if pontuacao_maxima > 0 else 0
        )

        return CategoryScore(
            categoria_key=categoria_key,
            categoria_nome=categoria["nome"],
            pontuacao_obtida=pontuacao_obtida,
            pontuacao_maxima=pontuacao_maxima,
            percentual=percentual,
            criterios=criterios_scores,
        )

    def avaliar_ideia(self, idea_score: IdeaScore) -> IdeaScore:
        """Avalia uma ideia completa contra todas as categorias."""
        for categoria_key in self.framework:
            cat_score = self.avaliar_categoria(idea_score, categoria_key)
            idea_score.categorias[categoria_key] = cat_score

        idea_score.calcular_totais()
        return idea_score

    def rankear_ideias(self, scores: list) -> list:
        """Rankeia uma lista de IdeaScores por pontuação total descendente."""
        sorted_scores = sorted(
            scores, key=lambda s: s.pontuacao_total, reverse=True
        )
        for i, score in enumerate(sorted_scores, 1):
            score.ranking = i
        return sorted_scores

    def _parse_evaluation_response(self, resposta: str) -> tuple:
        """Extrai nota e justificativa da resposta do LLM."""
        nota = 5
        justificativa = "Avaliação padrão"

        nota_match = re.search(r"NOTA:\s*(\d+)", resposta)
        if nota_match:
            nota = int(nota_match.group(1))

        just_match = re.search(
            r"JUSTIFICATIVA:\s*(.+?)(?:\n|$)", resposta, re.DOTALL
        )
        if just_match:
            justificativa = just_match.group(1).strip()

        return nota, justificativa

    def _avaliacao_heuristica(
        self, idea_score: IdeaScore, categoria_key: str, criterio_key: str
    ) -> tuple:
        """
        Avaliação heurística baseada em análise textual da ideia.
        Usada quando não há LLM disponível.
        """
        texto = (
            idea_score.problema_titulo
            + " "
            + idea_score.problema_descricao
            + " "
            + idea_score.ideia_descricao
        ).lower()

        keywords_positivas = {
            # Cat 1: Problem-Solution Fit
            "regra_10x": [
                "10x", "revolução", "elimina", "automatiza 100%", "instantâneo",
                "disruptivo", "substitui completamente", "zero esforço",
            ],
            "simplicidade_proposta_valor": [
                "simples", "um botão", "fácil", "intuitivo", "apertar",
                "automaticamente", "sem configuração",
            ],
            "caminho_direto_dor": [
                "imediato", "direto", "primeiro uso", "valor instantâneo",
                "resolve na hora", "sem setup",
            ],
            "alinhamento_frequencia": [
                "diário", "constante", "rotina", "hábito", "recorrente",
                "sempre que", "toda vez",
            ],
            "foco_beachhead": [
                "focado", "específico", "nicho", "persona clara", "um caso de uso",
                "bisturi", "especializado",
            ],
            # Cat 2: Viabilidade
            "time_to_mvp": [
                "no-code", "whatsapp", "planilha", "concierge", "manual",
                "zapier", "bubble", "typeform", "google forms",
            ],
            "risco_tecnologico": [
                "API", "SaaS", "existente", "commodity", "pronto", "open source",
                "cloud", "aws", "GPT", "openai",
            ],
            "friccao_onboarding": [
                "self-service", "sem instalação", "web", "login", "criar conta",
                "começar grátis", "zero configuração",
            ],
            "risco_dependencia_plataforma": [
                "independente", "próprio", "multi-plataforma", "web app",
                "stack próprio", "agnóstico",
            ],
            "risco_regulatorio_solucao": [
                "livre", "sem regulação", "permitido", "legal", "compliance simples",
            ],
            # Cat 3: Distribuição
            "vetor_crescimento_embutido": [
                "viral", "convite", "compartilhar", "rede", "referral",
                "convidar", "boca a boca", "PLG",
            ],
            "escalabilidade_canal_aquisicao": [
                "SEO", "content", "inbound", "ads", "digital", "parceria",
                "marketplace", "orgânico",
            ],
            "clareza_acesso_decisor": [
                "bottom-up", "self-service", "funcionário", "individual",
                "sem aprovação", "freemium",
            ],
            "barreira_ao_teste": [
                "grátis", "freemium", "trial", "teste", "sem compromisso",
                "sem cartão", "free tier",
            ],
            # Cat 4: Modelo de Negócio
            "margem_bruta_potencial": [
                "software", "SaaS", "digital", "código", "plataforma",
                "automatizado", "IA", "algoritmo",
            ],
            "modelo_receita_recorrente": [
                "assinatura", "mensal", "anual", "SaaS", "subscription",
                "recorrente", "MRR", "ARR",
            ],
            "custo_servir_vs_wtp": [
                "escalável", "margem alta", "baixo custo", "automático",
                "self-service", "zero custo marginal",
            ],
            "ciclo_recebimento": [
                "pré-pago", "antecipado", "assinatura", "cartão", "upfront",
                "cobra antes",
            ],
            # Cat 5: Moats
            "efeitos_de_rede": [
                "rede", "marketplace", "comunidade", "plataforma bilateral",
                "mais usuários melhor", "efeito rede",
            ],
            "lockin_custo_mudanca": [
                "integração", "sistema de registro", "dados do cliente",
                "workflow", "embeddado", "lock-in",
            ],
            "acumulo_dados_proprietarios": [
                "dados proprietários", "machine learning", "treina modelo",
                "base única", "data moat", "flywheel",
            ],
            "economia_de_escala": [
                "custo marginal zero", "escala", "infra compartilhada",
                "winner takes all", "consolidação",
            ],
        }

        positivas = keywords_positivas.get(criterio_key, [])
        score_pos = sum(1 for kw in positivas if kw in texto)

        nota_base = 5
        nota = nota_base + min(score_pos, 4)  # cap at +4
        nota = max(SCORE_MIN, min(SCORE_MAX, nota))

        matches = [kw for kw in positivas if kw in texto]
        if matches:
            justificativa = (
                f"Análise heurística: indicadores detectados — {', '.join(matches[:3])}"
            )
        else:
            justificativa = (
                "Análise heurística: avaliação baseada no contexto geral da ideia"
            )

        return nota, justificativa

    def formatar_pontuacao(self, idea_score: IdeaScore) -> str:
        """Formata a pontuação de uma ideia para exibição."""
        lines = []
        lines.append(f"{'=' * 80}")
        lines.append(f"IDEIA #{idea_score.idea_id}: {idea_score.ideia_nome or idea_score.problema_titulo}")
        lines.append(f"{'=' * 80}")
        lines.append("")

        for cat_key, cat_score in idea_score.categorias.items():
            lines.append(f"### {cat_score.categoria_nome}")
            lines.append(
                f"    Pontuação: {cat_score.pontuacao_obtida:.0f}/{cat_score.pontuacao_maxima:.0f} "
                f"({cat_score.percentual:.1f}%)"
            )
            lines.append("")

            for crit in cat_score.criterios:
                barra = "█" * crit.nota + "░" * (10 - crit.nota)
                lines.append(
                    f"    [{barra}] {crit.nota}/10 (x{crit.peso}) = "
                    f"{crit.nota_ponderada:.0f}pts | {crit.criterio_nome}"
                )
                lines.append(f"      → {crit.justificativa}")
            lines.append("")

        lines.append(f"{'=' * 80}")
        lines.append(
            f"PONTUAÇÃO TOTAL: {idea_score.pontuacao_total:.0f}/{idea_score.pontuacao_maxima:.0f} "
            f"({idea_score.percentual:.1f}%)"
        )
        if idea_score.ranking > 0:
            lines.append(f"RANKING: #{idea_score.ranking}")
        lines.append(f"{'=' * 80}")

        return "\n".join(lines)
