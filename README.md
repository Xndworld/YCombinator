# YCombinator - Pipeline de Descoberta de Oportunidades

Sistema de análise de problemas societais e descoberta de oportunidades de startup,
usando avaliação multi-critério inspirada em Y Combinator, Lean Startup e VC.

## Pipeline

```
01_RELATÓRIOS → 02_PROBLEMAS → 03_RANKING → 04_ARTIGOS → 05_BRAINSTORM → 06_STARTUPS → 07_BANCAS
                                    ↕                          ↕                          ├─ RedBull
                              dados/banco/              dados/banco/                      └─ YCombinator
                            problemas.json            solucoes.json
```

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 01 | Relatórios de mercado (geopolítica, clima, IA, economia) | Concluído |
| 02 | Análise combinatória → planilha de problemas (batches) | Concluído |
| 03 | Ranking de problemas (7 categorias, 55+ critérios) | Concluído |
| 04 | Artigos analíticos dos top problemas | Concluído (498 artigos) |
| 05 | Brainstorm: 5 agentes × 5 soluções = 25 por problema | Implementado |
| 06 | Top 100 soluções → artigos de startup | Placeholder |
| 07 | Bancas: RedBull (edital) + YCombinator (ranking fase 2) | Placeholder |

## Banco JSON Centralizado

Todos os agentes leem e escrevem em `dados/banco/` - **fonte única de dados**.

```
dados/banco/
├── problemas.json    # 498 problemas com 50 métricas, scores, tags, ranking
├── solucoes.json     # Soluções de brainstorm com ranking automático (top 100)
├── startups.json     # Artigos de startup compactos
└── bancas.json       # Avaliações das bancas
```

**Economia de tokens**: Agentes usam contexto compacto (~200 tokens) em vez de
ler artigos completos (~4000 tokens). Rankings são pré-computados.
Artigos .md existem para leitura humana, agentes usam o JSON.

## Estrutura do Projeto

```
YCombinator/
├── dados/
│   ├── banco/                      # BANCO CENTRAL (fonte primária)
│   │   ├── problemas.json          # 498 problemas rankeados
│   │   ├── solucoes.json           # Soluções com ranking top 100
│   │   ├── startups.json           # Artigos de startup
│   │   └── bancas.json             # Avaliações das bancas
│   ├── 01_relatorios/              # Relatórios fonte (.md + .docx)
│   ├── 02_problemas/               # Problemas + batches + CSVs (legado)
│   ├── 03_ranking_problemas/       # Rankings CSV (legado)
│   ├── 04_artigos_problemas/       # 498 artigos .md (leitura humana)
│   ├── 05_brainstorm_solucoes/     # [Futuro] Soluções exportadas
│   ├── 06_artigos_startups/        # [Futuro] Artigos de startup
│   └── 07_bancas/                  # [Futuro] RedBull + YCombinator
│
├── agentes/
│   ├── banco_dados.py              # Módulo central de acesso a dados
│   ├── migrar_dados.py             # Script de migração
│   ├── societal_problem_agent/     # Classificador de problemas
│   ├── bars_judge_agent.py         # Avaliador batch
│   ├── brainstorm/                 # 5 agentes de brainstorm
│   ├── orquestrador/               # Orquestrador do pipeline
│   ├── validador/                  # Validador de integridade
│   ├── banca_redbull/              # Banca RedBull [Placeholder]
│   └── banca_ycombinator/          # Banca YCombinator [Placeholder]
│
├── requirements.txt
└── README.md
```

## Agentes

### Banco de Dados Central (`agentes/banco_dados.py`)

Módulo compartilhado que todos os agentes importam. Provê:
- `BancoDados.obter_top_n_problemas(50)` - top N problemas
- `BancoDados.contexto_para_brainstorm(id)` - contexto compacto (~200 tokens)
- `BancoDados.adicionar_solucoes(lista, problema_id)` - salva + re-rankeia
- `BancoDados.obter_top_n_solucoes(100)` - top 100 soluções
- `BancoDados.stats()` - estatísticas do banco

### Classificador de Problemas (`agentes/societal_problem_agent/`)

Avalia problemas com framework de 7 categorias e 55+ critérios.
Salva direto no banco central.

```bash
python -m agentes.societal_problem_agent.main --limite 10
```

### Avaliador Batch (`agentes/bars_judge_agent.py`)

Sistema de batches para avaliação incremental. Sincroniza com banco central.

```bash
python agentes/bars_judge_agent.py status
python agentes/bars_judge_agent.py rebuild   # sincroniza com banco central
```

### Brainstorm (`agentes/brainstorm/`)

5 ângulos (Tecnológico, Modelo Negócio, Social, Regulatório, Infraestrutura).
Gera soluções direto no `solucoes.json` com ranking automático.

```bash
python -m agentes.brainstorm.brainstorm_agent --problema P0001
python -m agentes.brainstorm.brainstorm_agent --top 50
python -m agentes.brainstorm.brainstorm_agent --top 10 --mode api
```

### Orquestrador (`agentes/orquestrador/`)

Gerencia pipeline + mostra status do banco central.

```bash
python -m agentes.orquestrador.orquestrador status
python -m agentes.orquestrador.orquestrador diagram
python -m agentes.orquestrador.orquestrador run --etapa 5
```

### Validador (`agentes/validador/`)

Verifica integridade do pipeline + banco central.

```bash
python -m agentes.validador.validador check
```

### A Implementar

- **Banca RedBull** (formata para edital) - Etapa 7
- **Banca YCombinator** (ranking fase 2) - Etapa 7
- **Protocolo de Atualização** - Novos insights → re-ranking automático

## Fluxo de Atualização (Futuro)

```
Novo Insight → Classificação → Top 50? ─┬─ SIM → Brainstorm (5×5=25 soluções)
                                         └─ NÃO → problemas.json (banco)

Brainstorm → 25 soluções → Top 100? ─┬─ SIM → Artigo Startup → Bancas
                                      └─ NÃO → solucoes.json (banco)
```

## Setup

```bash
pip install -r requirements.txt
python agentes/migrar_dados.py              # Migra dados para banco central
export ANTHROPIC_API_KEY='sua-chave'        # Opcional: para avaliação via LLM
```
