"""
Idea Ranking Agent - Avaliador de Ideias/Soluções de Startup
============================================================

Agente que julga e rankeia ideias provenientes do brainstorm agent e
problem solving, pontuando-as em 5 categorias baseadas no framework YC:

1. Eficácia e Problem-Solution Fit (Peso total: 23)
2. Viabilidade e Risco de Produto (Peso total: 20)
3. Distribuição e Go-to-Market (Peso total: 16)
4. Modelo de Negócios e Economia Unitária (Peso total: 17)
5. Moats / Fossos Competitivos (Peso total: 14)

Inclui filtro matador (Kill Filter) de 3 perguntas antes do scorecard completo.
"""

__version__ = "1.0.0"
