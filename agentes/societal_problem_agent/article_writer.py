"""
Motor de Geração de Artigos

Gera artigos analíticos aprofundados para cada problema,
incorporando a pontuação do framework de avaliação,
análise de impacto nos mercados e conexões societais.
"""

from .config import ARTICLE_PROMPT_TEMPLATE, get_max_possible_score
from .scoring import ProblemScore


class ArticleWriter:
    """Gerador de artigos analíticos sobre problemas societais."""

    def __init__(self, llm_writer=None):
        """
        Args:
            llm_writer: Função que recebe um prompt e retorna o artigo gerado.
                       Assinatura: (prompt: str) -> str
        """
        self.llm_writer = llm_writer

    def gerar_artigo(self, problem_score: ProblemScore, total_problemas: int) -> str:
        """Gera um artigo completo para um problema avaliado."""
        pontuacao_formatada = self._formatar_pontuacao_para_artigo(problem_score)

        prompt = ARTICLE_PROMPT_TEMPLATE.format(
            problema_titulo=problem_score.problema_titulo,
            problema_descricao=problem_score.problema_descricao,
            problema_desenvolvimento=problem_score.problema_desenvolvimento,
            pontuacao_formatada=pontuacao_formatada,
            pontuacao_total=f"{problem_score.pontuacao_total:.0f}",
            pontuacao_maxima=f"{problem_score.pontuacao_maxima:.0f}",
            percentual=f"{problem_score.percentual:.1f}",
            ranking=problem_score.ranking,
            total_problemas=total_problemas
        )

        if self.llm_writer:
            artigo = self.llm_writer(prompt)
        else:
            artigo = self._gerar_artigo_template(problem_score, total_problemas)

        return artigo

    def _formatar_pontuacao_para_artigo(self, problem_score: ProblemScore) -> str:
        """Formata a pontuação para incluir no prompt de geração do artigo."""
        lines = []
        for cat_key, cat_score in problem_score.categorias.items():
            lines.append(f"\n**{cat_score.categoria_nome}** - {cat_score.pontuacao_obtida:.0f}/{cat_score.pontuacao_maxima:.0f} ({cat_score.percentual:.1f}%)")
            for crit in cat_score.criterios:
                lines.append(f"  - {crit.criterio_nome}: {crit.nota}/10 (peso {crit.peso}) → {crit.justificativa}")
        return "\n".join(lines)

    def _gerar_artigo_template(self, ps: ProblemScore, total_problemas: int) -> str:
        """Gera um artigo usando template quando não há LLM disponível."""
        # Coleta as melhores e piores categorias
        cats_sorted = sorted(
            ps.categorias.values(),
            key=lambda c: c.percentual,
            reverse=True
        )
        melhor_cat = cats_sorted[0] if cats_sorted else None
        pior_cat = cats_sorted[-1] if cats_sorted else None

        # Coleta os critérios com melhores notas
        todos_criterios = []
        for cat in ps.categorias.values():
            todos_criterios.extend(cat.criterios)
        criterios_sorted = sorted(todos_criterios, key=lambda c: c.nota, reverse=True)
        top_criterios = criterios_sorted[:5]
        bottom_criterios = criterios_sorted[-3:]

        # Classificação do problema
        if ps.percentual >= 75:
            classificacao = "OPORTUNIDADE DE ALTO POTENCIAL"
            emoji_class = "Excelente"
        elif ps.percentual >= 60:
            classificacao = "OPORTUNIDADE PROMISSORA"
            emoji_class = "Boa"
        elif ps.percentual >= 45:
            classificacao = "OPORTUNIDADE MODERADA"
            emoji_class = "Moderada"
        else:
            classificacao = "OPORTUNIDADE DE BAIXO POTENCIAL"
            emoji_class = "Baixa"

        artigo = f"""# {ps.problema_titulo}
## Uma Análise Profunda de Oportunidade de Negócio

**Classificação: {classificacao}**
**Ranking: #{ps.ranking} de {total_problemas} problemas analisados**
**Pontuação: {ps.pontuacao_total:.0f}/{ps.pontuacao_maxima:.0f} ({ps.percentual:.1f}%)**

---

## Resumo Executivo

{ps.problema_descricao}

{ps.problema_desenvolvimento}

Este problema foi avaliado através de um framework rigoroso de 7 categorias e {len(todos_criterios)} critérios ponderados, baseado nas metodologias de Y Combinator, Lean Startup, Venture Capital clássico e estratégia competitiva. Com uma pontuação de {ps.percentual:.1f}%, este problema se posiciona como uma oportunidade de potencial {emoji_class.lower()} para empreendedores e investidores.

---

## Anatomia do Problema

### Contexto e Raízes

{ps.problema_desenvolvimento}

O problema "{ps.problema_titulo}" não existe em isolamento. Ele é produto de forças estruturais que convergem em um momento específico da história econômica e social. Para entendê-lo plenamente, é necessário analisar suas múltiplas dimensões.

### Quem São os Mais Afetados

"""
        # Adiciona informações sobre clareza de persona se disponível
        for cat in ps.categorias.values():
            for crit in cat.criterios:
                if crit.criterio_key == "clareza_persona":
                    artigo += f"A clareza sobre quem sofre com este problema recebeu nota {crit.nota}/10. {crit.justificativa}\n\n"
                    break

        artigo += f"""
---

## Impacto nos Mercados e Setores

### Perdas Financeiras e Oportunidades

"""
        # Adiciona análise financeira
        for cat in ps.categorias.values():
            for crit in cat.criterios:
                if crit.criterio_key == "intensidade_dor_financeira":
                    artigo += f"**Intensidade da Dor Financeira ({crit.nota}/10):** {crit.justificativa}\n\n"
                if crit.criterio_key == "tam":
                    artigo += f"**Tamanho de Mercado ({crit.nota}/10):** {crit.justificativa}\n\n"
                if crit.criterio_key == "crescimento_mercado":
                    artigo += f"**Crescimento do Mercado ({crit.nota}/10):** {crit.justificativa}\n\n"

        artigo += f"""
A intersecção entre a dor financeira causada por este problema e o tamanho do mercado endereçável cria um espaço de oportunidade significativo para soluções inovadoras.

---

## Análise de Timing: Por Que Agora?

"""
        # Timing
        if "3_timing_why_now" in ps.categorias:
            timing = ps.categorias["3_timing_why_now"]
            artigo += f"A categoria de Timing recebeu {timing.pontuacao_obtida:.0f}/{timing.pontuacao_maxima:.0f} pontos ({timing.percentual:.1f}%).\n\n"
            for crit in timing.criterios:
                artigo += f"- **{crit.criterio_nome} ({crit.nota}/10):** {crit.justificativa}\n"
            artigo += "\n"

        artigo += f"""
---

## Framework de Avaliação Detalhado

### Visão Geral das Categorias

| Categoria | Pontuação | Percentual |
|-----------|-----------|------------|
"""
        for cat in ps.categorias.values():
            artigo += f"| {cat.categoria_nome} | {cat.pontuacao_obtida:.0f}/{cat.pontuacao_maxima:.0f} | {cat.percentual:.1f}% |\n"

        artigo += f"| **TOTAL** | **{ps.pontuacao_total:.0f}/{ps.pontuacao_maxima:.0f}** | **{ps.percentual:.1f}%** |\n\n"

        # Detalhe de cada categoria
        for cat_key, cat_score in ps.categorias.items():
            artigo += f"### {cat_score.categoria_nome} ({cat_score.percentual:.1f}%)\n\n"
            for crit in cat_score.criterios:
                barra = "█" * crit.nota + "░" * (10 - crit.nota)
                artigo += f"- [{barra}] **{crit.criterio_nome}**: {crit.nota}/10 (peso {crit.peso})\n"
                artigo += f"  {crit.justificativa}\n\n"

        artigo += f"""
---

## Pontos Fortes (Top 5 Critérios)

"""
        for i, crit in enumerate(top_criterios, 1):
            artigo += f"{i}. **{crit.criterio_nome}** ({crit.nota}/10, peso {crit.peso}): {crit.justificativa}\n"

        artigo += f"""

## Pontos de Atenção (Critérios Mais Baixos)

"""
        for i, crit in enumerate(bottom_criterios, 1):
            artigo += f"{i}. **{crit.criterio_nome}** ({crit.nota}/10, peso {crit.peso}): {crit.justificativa}\n"

        artigo += f"""

---

## Conexões Societais

Este problema se conecta a dinâmicas mais amplas da sociedade contemporânea. As forças que o alimentam incluem mudanças demográficas, pressões econômicas, transformações tecnológicas e evolução regulatória. Entender essas conexões é crucial para desenvolver soluções que não apenas resolvam o sintoma, mas ataquem a causa raiz.

"""
        if melhor_cat:
            artigo += f"A categoria mais forte deste problema é **{melhor_cat.categoria_nome}** ({melhor_cat.percentual:.1f}%), sugerindo que as condições de mercado e contexto são particularmente favoráveis nesta dimensão.\n\n"
        if pior_cat:
            artigo += f"Por outro lado, **{pior_cat.categoria_nome}** ({pior_cat.percentual:.1f}%) representa a maior área de risco ou limitação, exigindo atenção especial de empreendedores que desejem explorar esta oportunidade.\n\n"

        artigo += f"""
---

## Cenários Futuros

### Cenário Otimista
Se soluções eficazes forem desenvolvidas e adotadas em escala, o problema pode ser significativamente mitigado, gerando valor substancial para o ecossistema e desbloqueando crescimento em setores adjacentes.

### Cenário Pessimista
Sem intervenção, o problema tende a se agravar, aumentando as perdas financeiras, ampliando riscos e criando cascatas de consequências negativas nos mercados afetados.

### Cenário Mais Provável
Soluções parciais emergerão de forma fragmentada, com startups pioneiras capturando os segmentos mais urgentes do mercado enquanto a solução completa ainda levará anos para se consolidar.

---

## Recomendações para Empreendedores

1. **Validação Rápida:** Comece entrevistando os usuários mais afetados para confirmar a intensidade da dor
2. **MVP Focado:** Construa a solução mínima que atenda ao caso de uso mais frequente e doloroso
3. **Nicho Primeiro:** Domine um sub-segmento antes de expandir (estratégia Peter Thiel)
4. **Modelo de Negócio:** Garanta que quem sofre a dor é quem paga pela solução
5. **Timing:** Aproveite as forças regulatórias e tecnológicas que tornam este o momento certo

---

## Conclusão

"{ps.problema_titulo}" representa uma oportunidade classificada como **{classificacao}** (#{ps.ranking} de {total_problemas}). Com pontuação de {ps.percentual:.1f}% no framework de avaliação, o problema demonstra {
    'forças excepcionais em múltiplas dimensões, sendo uma das melhores oportunidades identificadas' if ps.percentual >= 75
    else 'um equilíbrio favorável entre potencial de mercado, timing e viabilidade de execução' if ps.percentual >= 60
    else 'potencial moderado que requer cuidado na execução e validação rigorosa' if ps.percentual >= 45
    else 'desafios significativos que precisam ser superados para viabilizar uma solução de negócio'
}.

A chave para transformar este problema em um negócio de sucesso reside em combinar profundo entendimento da dor do usuário com execução lean e timing preciso.

---

*Artigo gerado pelo Societal Problem Agent - Framework de Avaliação v1.0*
*Baseado nas metodologias de Y Combinator, Lean Startup, Venture Capital e Estratégia Competitiva*
"""
        return artigo
