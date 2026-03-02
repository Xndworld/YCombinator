# YCombinator - Pipeline de Descoberta de Oportunidades

Sistema de análise de problemas societais e descoberta de oportunidades de startup,
usando avaliação multi-critério inspirada em Y Combinator, Lean Startup e VC.

## Pipeline

```
01_RELATÓRIOS → 02_PROBLEMAS → 03_RANKING → 04_ARTIGOS → 05_BRAINSTORM → 06_STARTUPS → 07_BANCAS
                                                                                        ├─ RedBull
                                                                                        └─ YCombinator
```

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 01 | Relatórios de mercado (geopolítica, clima, IA, economia) | Concluído |
| 02 | Análise combinatória → planilha de problemas (batches) | Concluído |
| 03 | Ranking de problemas (7 categorias, 55+ critérios) | Concluído |
| 04 | Artigos analíticos dos top problemas | Concluído (498 artigos) |
| 05 | Brainstorm: 5 agentes × 25 soluções = 125 por problema | Placeholder |
| 06 | Top 100 soluções → artigos de startup | Placeholder |
| 07 | Bancas: RedBull (edital) + YCombinator (ranking fase 2) | Placeholder |

## Estrutura do Projeto

```
YCombinator/
├── dados/                              # Dados organizados por etapa do pipeline
│   ├── 01_relatorios/                  # Relatórios fonte (.md + .docx)
│   ├── 02_problemas/                   # Problemas + batches + CSVs
│   │   └── batches/                    # Sistema de batches por data
│   ├── 03_ranking_problemas/           # Rankings finais (.csv)
│   ├── 04_artigos_problemas/           # 498 artigos de análise de problemas
│   │   └── artigos/
│   ├── 05_brainstorm_solucoes/         # [Futuro] Soluções de brainstorm
│   │   ├── solucoes/
│   │   └── ranking_solucoes/
│   ├── 06_artigos_startups/            # [Futuro] Artigos de oportunidade
│   └── 07_bancas/                      # [Futuro] Avaliações das bancas
│       ├── redbull/processo/
│       └── ycombinator/ranking_fase2/
│
├── agentes/                            # Todos os agentes do pipeline
│   ├── societal_problem_agent/         # Classificador de problemas [Implementado]
│   ├── bars_judge_agent.py             # Avaliador batch [Implementado]
│   ├── orquestrador/                   # Orquestrador do pipeline [Implementado]
│   ├── validador/                      # Validador de integridade [Implementado]
│   ├── brainstorm/                     # 5 agentes de brainstorm [Placeholder]
│   ├── banca_redbull/                  # Banca RedBull [Placeholder]
│   └── banca_ycombinator/             # Banca YCombinator [Placeholder]
│
├── requirements.txt
└── README.md
```

## Agentes

### Implementados

**Classificador de Problemas** (`agentes/societal_problem_agent/`)
- Avalia problemas com framework de 7 categorias e 55+ critérios ponderados
- Gera artigos analíticos e ranking final
- Baseado em YC, Lean Startup, VC, Blitzscaling, 7 Powers

```bash
python -m agentes.societal_problem_agent.main --info
python -m agentes.societal_problem_agent.main --limite 10
```

**Avaliador Batch** (`agentes/bars_judge_agent.py`)
- Sistema de batches para avaliação incremental de problemas
- Ranking unificado entre batches

```bash
python agentes/bars_judge_agent.py status
python agentes/bars_judge_agent.py evaluate
```

**Orquestrador** (`agentes/orquestrador/`)
- Gerencia o fluxo completo do pipeline
- Mostra status de cada etapa, executa etapas

```bash
python -m agentes.orquestrador.orquestrador status
python -m agentes.orquestrador.orquestrador diagram
```

**Validador** (`agentes/validador/`)
- Verifica integridade do pipeline (diretórios, dados, agentes)
- Detecta e corrige problemas de conexão entre etapas

```bash
python -m agentes.validador.validador check
python -m agentes.validador.validador fix
```

### A Implementar

- **Brainstorm** (5 agentes × 25 soluções) - Etapa 5
- **Banca RedBull** (formata para edital) - Etapa 7
- **Banca YCombinator** (ranking fase 2) - Etapa 7
- **Protocolo de Atualização** - Novos insights → re-ranking automático

## Fluxo de Atualização (Futuro)

```
Novo Insight → Classificação → Top 50? ─┬─ SIM → Artigo + Brainstorm
                                         └─ NÃO → Banco de problemas

Brainstorm → 125 soluções → Top 100? ─┬─ SIM → Artigo Startup → Bancas
                                       └─ NÃO → Banco de soluções
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY='sua-chave'  # Opcional: para avaliação via LLM
```
