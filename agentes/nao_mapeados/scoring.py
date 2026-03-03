"""
Motor de Pontuação para Ideias/Soluções

Avalia cada ideia em 2 etapas:
  1. Kill Filter (3 perguntas rápidas) → pass/fail com penalização
  2. Scorecard de 5 categorias (nota holística 1-10 por categoria)

Otimizado para performance: 1 LLM call para kill filter + 5 para categorias = 6 calls/ideia.
(vs. 22 calls individuais por critério)
"""

import re
from dataclasses import dataclass, field

from .config import (
    SCORING_FRAMEWORK,
    KILL_FILTER,
    KILL_FILTER_PROMPT,
    CATEGORY_EVAL_PROMPT,
    SCORE_MIN,
    SCORE_MAX,
    MAX_POSSIBLE_SCORE,
    KILL_FILTER_THRESHOLD,
    KILL_FILTER_PENALTY,
    format_criterios_for_prompt,
)


@dataclass
class KillFilterResult:
    """Resultado do kill filter de 3 perguntas."""
    mvp_semanas: int = 5
    margem_tech: int = 5
    distribuicao_escalavel: int = 5
    passou: bool = True
    falhas: list = field(default_factory=list)

    @property
    def media(self) -> float:
        return (self.mvp_semanas + self.margem_tech + self.distribuicao_escalavel) / 3


@dataclass
class CategoryResult:
    """Resultado de uma categoria."""
    categoria_key: str
    categoria_nome: str
    peso_total: int
    nota: int  # 1-10
    pontuacao_ponderada: float  # nota * peso_total
    pontuacao_maxima: float  # peso_total * 10
    percentual: float
    razao: str = ""


@dataclass
class IdeaScore:
    """Pontuação completa de uma ideia."""
    ideia_id: int = 0
    ideia_titulo: str = ""
    ideia_descricao: str = ""
    problema: str = ""
    origem: str = ""
    kill_filter: KillFilterResult = field(default_factory=KillFilterResult)
    categorias: dict = field(default_factory=dict)  # Dict[str, CategoryResult]
    pontuacao_bruta: float = 0
    pontuacao_final: float = 0
    pontuacao_maxima: float = MAX_POSSIBLE_SCORE
    percentual: float = 0
    ranking: int = 0
    classificacao: str = ""  # S/A/B/C/D/F
    rebaixada: bool = False

    def calcular_totais(self):
        """Calcula totais a partir das categorias e aplica kill filter."""
        self.pontuacao_bruta = sum(c.pontuacao_ponderada for c in self.categorias.values())
        self.pontuacao_maxima = MAX_POSSIBLE_SCORE

        # Aplica penalização do kill filter
        if not self.kill_filter.passou:
            self.pontuacao_final = self.pontuacao_bruta * KILL_FILTER_PENALTY
            self.rebaixada = True
        else:
            self.pontuacao_final = self.pontuacao_bruta

        self.percentual = (self.pontuacao_final / self.pontuacao_maxima * 100) if self.pontuacao_maxima > 0 else 0
        self.classificacao = self._classificar()

    def _classificar(self) -> str:
        """Classifica a ideia em tiers baseado no percentual."""
        if self.rebaixada:
            # Ideias rebaixadas pelo kill filter nunca passam de B
            pct = self.percentual
            if pct >= 50:
                return "C"
            elif pct >= 35:
                return "D"
            return "F"

        pct = self.percentual
        if pct >= 80:
            return "S"
        elif pct >= 65:
            return "A"
        elif pct >= 50:
            return "B"
        elif pct >= 35:
            return "C"
        elif pct >= 20:
            return "D"
        return "F"


class IdeaScoringEngine:
    """Motor de pontuação para ideias/soluções."""

    def __init__(self, llm_evaluator=None):
        """
        Args:
            llm_evaluator: Função (prompt: str) -> str. Se None, usa heurística.
        """
        self.llm_evaluator = llm_evaluator

    def avaliar_kill_filter(self, ideia: dict) -> KillFilterResult:
        """Avalia a ideia contra o kill filter de 3 perguntas."""
        titulo = ideia.get("Ideia", ideia.get("ideia", ""))
        descricao = ideia.get("Descrição", ideia.get("descricao", ""))
        problema = ideia.get("Problema", ideia.get("problema", ""))

        if self.llm_evaluator:
            prompt = KILL_FILTER_PROMPT.format(
                ideia_titulo=titulo,
                ideia_descricao=descricao,
                problema=problema,
                kf_mvp_pergunta=KILL_FILTER["mvp_semanas"]["pergunta"],
                kf_margem_pergunta=KILL_FILTER["margem_tech"]["pergunta"],
                kf_dist_pergunta=KILL_FILTER["distribuicao_escalavel"]["pergunta"],
            )
            resposta = self.llm_evaluator(prompt)
            return self._parse_kill_filter_response(resposta)
        else:
            return self._kill_filter_heuristico(ideia)

    def avaliar_categoria(self, ideia: dict, cat_key: str) -> CategoryResult:
        """Avalia uma ideia em uma categoria específica."""
        cat = SCORING_FRAMEWORK[cat_key]
        titulo = ideia.get("Ideia", ideia.get("ideia", ""))
        descricao = ideia.get("Descrição", ideia.get("descricao", ""))
        problema = ideia.get("Problema", ideia.get("problema", ""))

        if self.llm_evaluator:
            prompt = CATEGORY_EVAL_PROMPT.format(
                ideia_titulo=titulo,
                ideia_descricao=descricao,
                problema=problema,
                categoria_nome=cat["nome"],
                categoria_tese=cat["tese"],
                criterios_formatados=format_criterios_for_prompt(cat_key),
            )
            resposta = self.llm_evaluator(prompt)
            nota, razao = self._parse_category_response(resposta)
        else:
            nota, razao = self._avaliar_categoria_heuristica(ideia, cat_key)

        nota = max(SCORE_MIN, min(SCORE_MAX, nota))
        peso = cat["peso_total"]

        return CategoryResult(
            categoria_key=cat_key,
            categoria_nome=cat["nome"],
            peso_total=peso,
            nota=nota,
            pontuacao_ponderada=nota * peso,
            pontuacao_maxima=peso * SCORE_MAX,
            percentual=(nota / SCORE_MAX * 100),
            razao=razao,
        )

    def avaliar_ideia(self, ideia: dict, ideia_id: int) -> IdeaScore:
        """Avalia uma ideia completa: kill filter + 5 categorias."""
        titulo = ideia.get("Ideia", ideia.get("ideia", ""))
        descricao = ideia.get("Descrição", ideia.get("descricao", ""))
        problema = ideia.get("Problema", ideia.get("problema", ""))
        origem = ideia.get("Origem", ideia.get("origem", ""))

        score = IdeaScore(
            ideia_id=ideia_id,
            ideia_titulo=titulo,
            ideia_descricao=descricao,
            problema=problema,
            origem=origem,
        )

        # Etapa 1: Kill Filter
        score.kill_filter = self.avaliar_kill_filter(ideia)

        # Etapa 2: 5 Categorias
        for cat_key in SCORING_FRAMEWORK:
            cat_result = self.avaliar_categoria(ideia, cat_key)
            score.categorias[cat_key] = cat_result

        score.calcular_totais()
        return score

    def rankear_ideias(self, scores: list) -> list:
        """Rankeia ideias por pontuação final descendente."""
        sorted_scores = sorted(scores, key=lambda s: s.pontuacao_final, reverse=True)
        for i, score in enumerate(sorted_scores, 1):
            score.ranking = i
        return sorted_scores

    # ========================================================================
    # PARSING DE RESPOSTAS LLM
    # ========================================================================

    def _parse_kill_filter_response(self, resposta: str) -> KillFilterResult:
        """Extrai notas do kill filter da resposta LLM."""
        result = KillFilterResult()

        mvp_match = re.search(r"MVP:\s*(\d+)", resposta)
        margem_match = re.search(r"MARGEM:\s*(\d+)", resposta)
        dist_match = re.search(r"DISTRIBUICAO:\s*(\d+)", resposta)

        if mvp_match:
            result.mvp_semanas = max(SCORE_MIN, min(SCORE_MAX, int(mvp_match.group(1))))
        if margem_match:
            result.margem_tech = max(SCORE_MIN, min(SCORE_MAX, int(margem_match.group(1))))
        if dist_match:
            result.distribuicao_escalavel = max(SCORE_MIN, min(SCORE_MAX, int(dist_match.group(1))))

        # Verifica falhas
        result.falhas = []
        if result.mvp_semanas <= KILL_FILTER_THRESHOLD:
            result.falhas.append(f"MVP em Semanas ({result.mvp_semanas}/10)")
        if result.margem_tech <= KILL_FILTER_THRESHOLD:
            result.falhas.append(f"Margem Tech ({result.margem_tech}/10)")
        if result.distribuicao_escalavel <= KILL_FILTER_THRESHOLD:
            result.falhas.append(f"Distribuição Escalável ({result.distribuicao_escalavel}/10)")

        result.passou = len(result.falhas) == 0
        return result

    def _parse_category_response(self, resposta: str) -> tuple:
        """Extrai nota e razão da resposta LLM para categoria."""
        nota = 5
        razao = "Avaliação padrão"

        nota_match = re.search(r"NOTA:\s*(\d+)", resposta)
        if nota_match:
            nota = int(nota_match.group(1))

        razao_match = re.search(r"RAZAO:\s*(.+?)(?:\n|$)", resposta, re.DOTALL)
        if razao_match:
            razao = razao_match.group(1).strip()

        return nota, razao

    # ========================================================================
    # AVALIAÇÃO HEURÍSTICA (sem LLM)
    # ========================================================================

    def _kill_filter_heuristico(self, ideia: dict) -> KillFilterResult:
        """Kill filter heurístico baseado em keywords."""
        texto = self._texto_completo(ideia)
        result = KillFilterResult()

        # MVP em Semanas
        kw_mvp_pos = ["no-code", "whatsapp", "planilha", "manual", "simples",
                       "rápido", "low-code", "concierge", "mvp", "protótipo",
                       "landing page", "zapier", "bubble", "typeform"]
        kw_mvp_neg = ["hardware", "fábrica", "anos", "pesquisa", "p&d",
                       "biotech", "infraestrutura", "construção", "satélite",
                       "aprovação regulatória", "licença médica"]
        result.mvp_semanas = self._score_keywords(texto, kw_mvp_pos, kw_mvp_neg)

        # Margem Tech
        kw_margem_pos = ["software", "saas", "plataforma", "api", "ia",
                          "algoritmo", "automação", "digital", "app",
                          "machine learning", "cloud", "dados"]
        kw_margem_neg = ["serviço manual", "consultoria", "agência",
                          "logística", "delivery", "humano", "operadores",
                          "equipe de campo", "presencial", "mão de obra"]
        result.margem_tech = self._score_keywords(texto, kw_margem_pos, kw_margem_neg)

        # Distribuição Escalável
        kw_dist_pos = ["viral", "plg", "self-service", "freemium", "orgânico",
                        "seo", "inbound", "comunidade", "marketplace",
                        "boca a boca", "rede", "compartilhar", "convidar"]
        kw_dist_neg = ["venda consultiva", "porta a porta", "enterprise sales",
                        "vendedor", "equipe comercial", "outbound",
                        "relacionamento", "apresentação presencial"]
        result.distribuicao_escalavel = self._score_keywords(texto, kw_dist_pos, kw_dist_neg)

        # Verifica falhas
        result.falhas = []
        if result.mvp_semanas <= KILL_FILTER_THRESHOLD:
            result.falhas.append(f"MVP em Semanas ({result.mvp_semanas}/10)")
        if result.margem_tech <= KILL_FILTER_THRESHOLD:
            result.falhas.append(f"Margem Tech ({result.margem_tech}/10)")
        if result.distribuicao_escalavel <= KILL_FILTER_THRESHOLD:
            result.falhas.append(f"Distribuição Escalável ({result.distribuicao_escalavel}/10)")

        result.passou = len(result.falhas) == 0
        return result

    def _avaliar_categoria_heuristica(self, ideia: dict, cat_key: str) -> tuple:
        """Avaliação heurística de uma categoria inteira."""
        texto = self._texto_completo(ideia)

        keywords_por_categoria = {
            "1_eficacia_psf": {
                "pos": ["10x", "revolução", "disruptivo", "simples", "direto",
                         "imediato", "fácil", "um botão", "automático",
                         "instantâneo", "elimina", "resolve", "focado",
                         "específico", "nicho", "beachhead", "bisturi"],
                "neg": ["complexo", "múltiplas features", "generalista",
                         "canivete", "plataforma", "tudo para todos",
                         "marginal", "melhoria incremental", "10%", "20%",
                         "difícil de explicar", "precisa de treinamento"],
            },
            "2_viabilidade_risco": {
                "pos": ["no-code", "api", "saas", "existente", "acessível",
                         "simples", "rápido", "semanas", "low-code",
                         "independente", "próprio", "livre", "open source"],
                "neg": ["hardware", "p&d", "regulação", "licença", "anos",
                         "bilhões", "nasa", "invenção", "patente",
                         "apple", "google", "facebook", "dependência",
                         "integração complexa", "treinamento meses"],
            },
            "3_distribuicao_gtm": {
                "pos": ["viral", "plg", "self-service", "freemium",
                         "compartilhar", "convidar", "orgânico", "seo",
                         "inbound", "bottom-up", "funcionário", "teste grátis",
                         "trial", "comunidade"],
                "neg": ["enterprise", "porta a porta", "vendedor",
                         "ceo", "diretoria", "12 meses", "contrato",
                         "licitação", "outbound", "cold call", "evento"],
            },
            "4_modelo_negocio": {
                "pos": ["saas", "assinatura", "recorrente", "mensal",
                         "software", "margem alta", "prepago", "antecipado",
                         "usage-based", "freemium", "premium", "digital"],
                "neg": ["gratuito", "ad-supported", "publicidade",
                         "transacional", "uma vez", "logística", "operação",
                         "fornecedor", "custo alto", "margem baixa",
                         "capital intensivo", "estoque"],
            },
            "5_moats": {
                "pos": ["efeito de rede", "rede", "marketplace", "dados",
                         "ia", "machine learning", "lock-in", "integração",
                         "sistema de registro", "comunidade", "ecossistema",
                         "escala", "custo marginal zero", "proprietário"],
                "neg": ["copiável", "commodity", "sem diferencial",
                         "qualquer um", "fácil de replicar", "genérico",
                         "open source", "sem barreiras"],
            },
        }

        kw = keywords_por_categoria.get(cat_key, {"pos": [], "neg": []})
        nota = self._score_keywords(texto, kw["pos"], kw["neg"])

        # Gera razão
        matches_pos = [k for k in kw["pos"] if k in texto]
        matches_neg = [k for k in kw["neg"] if k in texto]
        partes = []
        if matches_pos:
            partes.append(f"Positivos: {', '.join(matches_pos[:3])}")
        if matches_neg:
            partes.append(f"Negativos: {', '.join(matches_neg[:3])}")
        razao = "; ".join(partes) if partes else "Análise heurística do contexto geral"

        return nota, razao

    def _texto_completo(self, ideia: dict) -> str:
        """Concatena todos os campos textuais da ideia."""
        campos = [
            ideia.get("Ideia", ideia.get("ideia", "")),
            ideia.get("Descrição", ideia.get("descricao", "")),
            ideia.get("Problema", ideia.get("problema", "")),
            ideia.get("Desenvolvimento", ideia.get("desenvolvimento", "")),
        ]
        return " ".join(campos).lower()

    def _score_keywords(self, texto: str, positivas: list, negativas: list) -> int:
        """Calcula score baseado em keyword matching."""
        score_pos = sum(1 for kw in positivas if kw in texto)
        score_neg = sum(1 for kw in negativas if kw in texto)
        nota = 5 + score_pos - score_neg
        return max(SCORE_MIN, min(SCORE_MAX, nota))

    # ========================================================================
    # FORMATAÇÃO
    # ========================================================================

    def formatar_pontuacao(self, idea_score: IdeaScore) -> str:
        """Formata a pontuação de uma ideia para exibição."""
        lines = []
        lines.append(f"{'=' * 80}")
        lines.append(f"IDEIA #{idea_score.ideia_id}: {idea_score.ideia_titulo}")
        lines.append(f"{'=' * 80}")
        lines.append(f"Problema: {idea_score.problema}")
        lines.append("")

        # Kill Filter
        kf = idea_score.kill_filter
        status = "PASSOU" if kf.passou else "FALHOU"
        lines.append(f"--- KILL FILTER: {status} ---")
        lines.append(f"  MVP em Semanas:        {kf.mvp_semanas}/10")
        lines.append(f"  Margem Tech:           {kf.margem_tech}/10")
        lines.append(f"  Distribuição Escalável:{kf.distribuicao_escalavel}/10")
        if kf.falhas:
            lines.append(f"  Falhas: {', '.join(kf.falhas)}")
            lines.append(f"  → Penalização de {int((1 - KILL_FILTER_PENALTY) * 100)}% aplicada")
        lines.append("")

        # Categorias
        for cat_key, cat_result in idea_score.categorias.items():
            barra = "█" * cat_result.nota + "░" * (10 - cat_result.nota)
            lines.append(
                f"  [{barra}] {cat_result.nota}/10 "
                f"(peso {cat_result.peso_total}) = {cat_result.pontuacao_ponderada:.0f}pts "
                f"| {cat_result.categoria_nome}"
            )
            if cat_result.razao:
                lines.append(f"    → {cat_result.razao}")
        lines.append("")

        # Totais
        lines.append(f"{'=' * 80}")
        if idea_score.rebaixada:
            lines.append(
                f"PONTUAÇÃO BRUTA: {idea_score.pontuacao_bruta:.0f} "
                f"→ FINAL (penalizada): {idea_score.pontuacao_final:.0f}"
                f"/{idea_score.pontuacao_maxima:.0f} ({idea_score.percentual:.1f}%)"
            )
        else:
            lines.append(
                f"PONTUAÇÃO FINAL: {idea_score.pontuacao_final:.0f}"
                f"/{idea_score.pontuacao_maxima:.0f} ({idea_score.percentual:.1f}%)"
            )
        lines.append(f"CLASSIFICAÇÃO: {idea_score.classificacao}")
        if idea_score.ranking > 0:
            lines.append(f"RANKING: #{idea_score.ranking}")
        lines.append(f"{'=' * 80}")

        return "\n".join(lines)
