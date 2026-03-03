"""
Motor de Pontuação — RBB Judge Agent

Avalia cada artigo de startup em 5 pilares do framework Red Bull Basement:
  1. Problema Sistêmico e Impacto Social/Ambiental  (0-35 pts)
  2. Solução Tecnológica — Diferencial de IA         (0-20 pts)
  3. Storytelling, Vivência e Fator Red Bull         (0-25 pts)
  4. Viabilidade de Execução e Negócio              (0-10 pts)
  5. Equipe e Escalabilidade do Impacto             (0-10 pts)

Suporta dois modos:
  - LLM (via Anthropic API): 1 call por artigo, retorna JSON estruturado completo.
  - Heurístico (sem LLM): keyword matching por pilar, útil para testes rápidos.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional, Callable

from .config import (
    SCORING_FRAMEWORK,
    MAX_POSSIBLE_SCORE,
    THRESHOLD_APROVADO,
    THRESHOLD_OBSERVACAO,
    RBB_SYSTEM_PROMPT,
    EVALUATION_PROMPT,
    HEURISTIC_KEYWORDS,
)


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class PilarResult:
    """Resultado de um pilar de avaliação."""
    pilar_key: str
    pilar_nome: str
    peso_maximo: int
    nota: int           # 0 a peso_maximo
    percentual: float   # nota / peso_maximo * 100
    justificativa: str = ""


@dataclass
class RBBScore:
    """Pontuação completa de um artigo/projeto avaliado pelo RBB Judge."""
    # Identificação
    artigo_id: int = 0
    arquivo: str = ""
    nome_projeto: str = ""
    resumo_avaliador: str = ""

    # Classificação
    areas_interesse_relacionadas: list = field(default_factory=list)
    ods_relacionados: list = field(default_factory=list)

    # Pilares
    pilares: dict = field(default_factory=dict)  # Dict[str, PilarResult]

    # Totais
    score_total: int = 0
    percentual: float = 0.0
    status_ranqueamento: str = ""
    classificacao: str = ""  # S/A/B/C/D/F

    # Parecer
    pontos_fortes: list = field(default_factory=list)
    pontos_fracos_riscos: list = field(default_factory=list)
    recomendacao_acao: str = ""

    # Ranking
    ranking: int = 0

    # Dados brutos do JSON retornado pelo LLM
    json_raw: dict = field(default_factory=dict)

    def calcular_totais(self):
        """Recalcula score_total, percentual e classificacao a partir dos pilares."""
        self.score_total = sum(p.nota for p in self.pilares.values())
        self.percentual = (self.score_total / MAX_POSSIBLE_SCORE * 100) if MAX_POSSIBLE_SCORE > 0 else 0
        self.classificacao = self._classificar()
        self.status_ranqueamento = self._status()

    def _classificar(self) -> str:
        pct = self.percentual
        if pct >= 90:
            return "S+"
        elif pct >= 80:
            return "S"
        elif pct >= 70:
            return "A"
        elif pct >= 60:
            return "B"
        elif pct >= 50:
            return "C"
        elif pct >= 35:
            return "D"
        return "F"

    def _status(self) -> str:
        if self.score_total >= THRESHOLD_APROVADO:
            return "Aprovado"
        elif self.score_total >= THRESHOLD_OBSERVACAO:
            return "Em Observação"
        return "Reprovado"


# ============================================================================
# MOTOR DE PONTUAÇÃO
# ============================================================================

class RBBScoringEngine:
    """Motor de pontuação para artigos de startup avaliados pelo RBB Judge."""

    def __init__(self, llm_evaluator: Optional[Callable] = None):
        """
        Args:
            llm_evaluator: Função (system: str, user: str) -> str que chama o LLM.
                           Se None, usa avaliação heurística por keywords.
        """
        self.llm_evaluator = llm_evaluator

    def avaliar_artigo(self, artigo: dict, artigo_id: int = 0) -> RBBScore:
        """
        Avalia um artigo/projeto e retorna o RBBScore completo.

        Args:
            artigo: Dicionário com 'arquivo', 'titulo', 'conteudo'.
            artigo_id: ID sequencial do artigo.

        Returns:
            RBBScore populado.
        """
        score = RBBScore(
            artigo_id=artigo_id,
            arquivo=artigo.get("arquivo", ""),
            nome_projeto=artigo.get("titulo", ""),
        )

        if self.llm_evaluator:
            return self._avaliar_via_llm(artigo, score)
        else:
            return self._avaliar_heuristico(artigo, score)

    def rankear_artigos(self, scores: list) -> list:
        """Rankeia artigos por score_total descendente e atribui ranking."""
        sorted_scores = sorted(scores, key=lambda s: s.score_total, reverse=True)
        for i, score in enumerate(sorted_scores, 1):
            score.ranking = i
        return sorted_scores

    # ========================================================================
    # AVALIAÇÃO VIA LLM
    # ========================================================================

    def _avaliar_via_llm(self, artigo: dict, score: RBBScore) -> RBBScore:
        """Avalia o artigo com uma única chamada ao LLM e parseia o JSON."""
        conteudo = artigo.get("conteudo", "")
        titulo = artigo.get("titulo", "")

        # Trunca conteúdo muito longo (preserva contexto essencial)
        max_chars = 8000
        if len(conteudo) > max_chars:
            conteudo = conteudo[:max_chars] + "\n\n[... conteúdo truncado ...]"

        user_prompt = EVALUATION_PROMPT.format(conteudo_artigo=conteudo)

        resposta = self.llm_evaluator(system=RBB_SYSTEM_PROMPT, user=user_prompt)
        return self._parse_llm_response(resposta, score, titulo)

    def _parse_llm_response(self, resposta: str, score: RBBScore, titulo_fallback: str) -> RBBScore:
        """Parseia o JSON retornado pelo LLM e popula o RBBScore."""
        # Extrai JSON da resposta (remove possível markdown residual)
        json_text = resposta.strip()
        if "```" in json_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", json_text)
            if match:
                json_text = match.group(1)

        # Remove prefixo/sufixo que não seja JSON
        json_match = re.search(r"\{[\s\S]*\}", json_text)
        if json_match:
            json_text = json_match.group(0)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback: usa heurística se JSON inválido
            score.nome_projeto = titulo_fallback
            score.resumo_avaliador = "Avaliação LLM falhou — usando heurística de fallback."
            return self._avaliar_heuristico({"titulo": titulo_fallback}, score)

        score.json_raw = data
        score.nome_projeto = data.get("nome_projeto", titulo_fallback)
        score.resumo_avaliador = data.get("resumo_avaliador", "")
        score.areas_interesse_relacionadas = data.get("areas_interesse_relacionadas", [])
        score.ods_relacionados = data.get("ods_relacionados", [])

        # Pilares
        pontuacoes = data.get("pontuacoes", {})
        for pilar_key, pilar_config in SCORING_FRAMEWORK.items():
            pilar_data = pontuacoes.get(pilar_key, {})
            nota_raw = pilar_data.get("nota", 0)

            # Garante limites
            nota = max(0, min(pilar_config["peso_maximo"], int(nota_raw)))
            peso_max = pilar_config["peso_maximo"]

            score.pilares[pilar_key] = PilarResult(
                pilar_key=pilar_key,
                pilar_nome=pilar_config["nome"],
                peso_maximo=peso_max,
                nota=nota,
                percentual=(nota / peso_max * 100) if peso_max > 0 else 0,
                justificativa=pilar_data.get("justificativa", ""),
            )

        # Parecer
        parecer = data.get("parecer_banca", {})
        score.pontos_fortes = parecer.get("pontos_fortes", [])
        score.pontos_fracos_riscos = parecer.get("pontos_fracos_riscos", [])
        score.recomendacao_acao = parecer.get("recomendacao_acao", "")

        # Score total diretamente do LLM (ou recalcula)
        score_llm = data.get("score_total", None)
        score.calcular_totais()

        # Se o LLM forneceu score_total válido e diferença < 5, usa o do LLM
        if score_llm is not None:
            try:
                score_llm_int = int(score_llm)
                if abs(score_llm_int - score.score_total) <= 5:
                    score.score_total = score_llm_int
                    score.percentual = (score_llm_int / MAX_POSSIBLE_SCORE * 100)
                    score.classificacao = score._classificar()
                    score.status_ranqueamento = score._status()
            except (ValueError, TypeError):
                pass

        return score

    # ========================================================================
    # AVALIAÇÃO HEURÍSTICA (sem LLM)
    # ========================================================================

    def _avaliar_heuristico(self, artigo: dict, score: RBBScore) -> RBBScore:
        """Avaliação por keyword matching quando não há LLM disponível."""
        conteudo = artigo.get("conteudo", "")
        titulo = artigo.get("titulo", "")
        texto = (titulo + " " + conteudo).lower()

        score.nome_projeto = score.nome_projeto or titulo
        score.resumo_avaliador = "Avaliação heurística por keywords (sem LLM)."
        score.areas_interesse_relacionadas = self._detectar_areas(texto)

        for pilar_key, pilar_config in SCORING_FRAMEWORK.items():
            kw = HEURISTIC_KEYWORDS.get(pilar_key, {"positivas": [], "negativas": []})
            nota = self._score_keywords(
                texto,
                kw["positivas"],
                kw["negativas"],
                peso_maximo=pilar_config["peso_maximo"],
            )

            pos_encontradas = [k for k in kw["positivas"] if k in texto][:3]
            neg_encontradas = [k for k in kw["negativas"] if k in texto][:3]
            partes = []
            if pos_encontradas:
                partes.append(f"Indicadores positivos: {', '.join(pos_encontradas)}")
            if neg_encontradas:
                partes.append(f"Sinais negativos: {', '.join(neg_encontradas)}")
            justificativa = "; ".join(partes) or "Análise heurística do contexto geral."

            score.pilares[pilar_key] = PilarResult(
                pilar_key=pilar_key,
                pilar_nome=pilar_config["nome"],
                peso_maximo=pilar_config["peso_maximo"],
                nota=nota,
                percentual=(nota / pilar_config["peso_maximo"] * 100),
                justificativa=justificativa,
            )

        score.calcular_totais()
        return score

    def _score_keywords(self, texto: str, positivas: list, negativas: list, peso_maximo: int) -> int:
        """Calcula nota ponderada por keyword matching, escalada ao peso_maximo do pilar."""
        n_pos = sum(1 for kw in positivas if kw in texto)
        n_neg = sum(1 for kw in negativas if kw in texto)

        # Nota bruta em escala 0-10
        nota_bruta = max(0, min(10, 3 + n_pos - n_neg))

        # Escala para o peso_maximo do pilar
        nota = round((nota_bruta / 10) * peso_maximo)
        return max(0, min(peso_maximo, nota))

    def _detectar_areas(self, texto: str) -> list:
        """Detecta áreas de interesse do edital baseado em keywords."""
        mapa = {
            "Educação e Carreira": ["educação", "escola", "curso", "aprendizado", "carreira", "emprego", "trabalho", "universitário"],
            "Esportes e Desempenho Humano": ["esporte", "atleta", "desempenho", "físico", "treino", "performance", "academia"],
            "Mídia e Entretenimento": ["mídia", "entretenimento", "conteúdo", "streaming", "podcast", "música", "jogos"],
            "Evolução Urbana": ["cidade", "urbano", "mobilidade", "trânsito", "transporte", "habitação", "smart city"],
            "Experiência do Consumidor": ["consumidor", "experiência", "varejo", "e-commerce", "cliente", "ux", "compra"],
            "Indústria Inteligente": ["indústria", "manufatura", "fábrica", "produção", "industrial", "supply chain", "logística"],
            "Alimentação e Nutrição": ["alimentação", "comida", "nutrição", "agro", "alimento", "desperdício alimentar", "food"],
            "Viagem": ["viagem", "turismo", "hotel", "hospedagem", "destino", "viajante", "voo", "turista"],
            "Sustentabilidade": ["sustentabilidade", "ambiental", "carbono", "reciclagem", "energia renovável", "biodiversidade", "clima", "poluição"],
        }
        areas = []
        for area, keywords in mapa.items():
            if any(kw in texto for kw in keywords):
                areas.append(area)
        return areas[:3] if areas else ["Sustentabilidade"]

    # ========================================================================
    # FORMATAÇÃO
    # ========================================================================

    def formatar_score(self, score: RBBScore) -> str:
        """Formata a pontuação de um artigo para exibição no terminal."""
        lines = []
        sep = "=" * 80
        lines.append(sep)
        lines.append(f"PROJETO #{score.artigo_id}: {score.nome_projeto}")
        lines.append(f"Arquivo: {score.arquivo}")
        lines.append(sep)

        if score.resumo_avaliador:
            lines.append(f"Resumo: {score.resumo_avaliador}")
            lines.append("")

        if score.areas_interesse_relacionadas:
            lines.append(f"Áreas RBB: {', '.join(score.areas_interesse_relacionadas)}")
        if score.ods_relacionados:
            lines.append(f"ODS: {', '.join(score.ods_relacionados)}")
        lines.append("")

        lines.append("--- PILARES DE AVALIAÇÃO ---")
        for pilar_key, pilar in score.pilares.items():
            barra_cheia = round(pilar.percentual / 10)
            barra = "█" * barra_cheia + "░" * (10 - barra_cheia)
            lines.append(
                f"  [{barra}] {pilar.nota:2d}/{pilar.peso_maximo} "
                f"({pilar.percentual:5.1f}%) | {pilar.pilar_nome}"
            )
            if pilar.justificativa:
                lines.append(f"    → {pilar.justificativa[:120]}")
        lines.append("")

        lines.append(sep)
        lines.append(
            f"SCORE TOTAL: {score.score_total}/{MAX_POSSIBLE_SCORE} "
            f"({score.percentual:.1f}%) | [{score.classificacao}] {score.status_ranqueamento}"
        )

        if score.pontos_fortes:
            lines.append("\nPontos Fortes:")
            for pf in score.pontos_fortes:
                lines.append(f"  + {pf}")

        if score.pontos_fracos_riscos:
            lines.append("\nRiscos:")
            for risco in score.pontos_fracos_riscos:
                lines.append(f"  - {risco}")

        if score.recomendacao_acao:
            lines.append(f"\nRecomendação: {score.recomendacao_acao}")

        lines.append(sep)
        return "\n".join(lines)
