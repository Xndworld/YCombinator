# RegFlow AI - Pipeline de Descoberta de Oportunidades

Sistema de análise de problemas societais e descoberta de oportunidades de startup,
usando avaliação multi-critério inspirada em Y Combinator, Lean Startup e VC.

## 🚀 Pipeline RegFlow

O pipeline é orquestrado de ponta a ponta, transformando dados brutos em soluções avaliadas.

```text
01_RELATÓRIOS → 02_PROBLEMAS → 03_RANKING → 04_ARTIGOS → 05_BRAINSTORM → 06_STARTUPS
                                    ↕                          ↕                          
                              dados/banco/              dados/banco/                      
                            problemas.json            solucoes.json

06_STARTUPS → 07_BANCA_REDBULL → (edital formatado)
           └─> 08_BANCA_YCOMBINATOR → (ranking fase 2)

09_PROTOCOLO_ATUALIZACAO → re-alimenta etapas 02-08
```

| Etapa | Descrição | Status |
|-------|-----------|--------|
| 01 | Relatórios de mercado (geopolítica, clima, IA, economia) | Concluído |
| 02 | Análise combinatória → planilha de problemas (batches) | Concluído |
| 03 | Ranking de problemas (7 categorias, 55+ critérios) | Concluído |
| 04 | Artigos analíticos dos top problemas | Concluído (498 artigos) |
| 05 | Brainstorm: 5 agentes × 5 soluções = 25 por problema | Implementado |
| 06 | Top 100 soluções → artigos de startup | Implementado |
| 07 | Banca RedBull (formata para edital) | Implementado (Interface BaseBanca) |
| 08 | Banca YCombinator (ranking fase 2) | Placeholder |
| 09 | Protocolo de Atualização (novos insights → re-ranking) | Placeholder |

## 📦 Banco JSON Centralizado

Todos os agentes leem e escrevem em `dados/banco/` - **fonte única de dados**.

```text
dados/banco/
├── problemas.json    # 498 problemas com 50 métricas, scores, tags, ranking
├── solucoes.json     # Soluções de brainstorm com ranking automático (top 100)
├── startups.json     # Artigos de startup compactos
└── bancas.json       # Avaliações das bancas
```

**Economia de tokens**: Agentes usam contexto compacto (~200 tokens) em vez de
ler artigos completos (~4000 tokens). Artigos .md existem para leitura humana, agentes usam o JSON.

## 📂 Estrutura do Projeto

```text
YCombinator/
├── orquestrador/
│   └── main.py              # CÉREBRO DO SISTEMA (Gerencia o fluxo)
├── agentes/
│   ├── rankers/
│   │   └── yc_ranker/       # Avaliação de problemas (YC Framework)
│   ├── articuladores/       # Geração de ideias e artigos
│   ├── bancas/
│   │   ├── base_banca.py    # Interface Abstrata para novos editais
│   │   └── redbull/         # Avaliação específica Red Bull Basement
│   └── nao_mapeados/        # Pasta de transição para agentes legados
├── database/
│   └── db_writer.py         # Módulo central de acesso a dados
├── dados/
│   ├── banco/               # BANCO CENTRAL (fonte primária)
│   ├── 01_relatorios/       # Relatórios fonte
│   └── 04_artigos_problemas/# 498 artigos .md (leitura humana)
├── relatorios/              # CSVs e rankings exportados
└── artigos/                 # Artigos de startup gerados
```

## 🤖 Agentes e Comandos

O sistema é operado através do **Orquestrador Central**:

### Execução Geral
```bash
python orquestrador/main.py run-all --limite 10
```

### Ranker de Problemas (`agentes/rankers/yc_ranker/`)
Avalia batches de problemas com frameworks YC/Lean.
```bash
python orquestrador/main.py rank --batch "2026-03-01_initial"
```

### Articulador de Ideias (`agentes/articuladores/`)
Transforma problemas em ideias de startup e gera artigos analíticos.
```bash
python orquestrador/main.py articulate --limite 10
```

### Banca Avaliadora (`agentes/bancas/redbull/`)
Avalia as ideias de startup contra editais específicos (ex: Red Bull Basement).
```bash
python orquestrador/main.py evaluate --limite 5
```

## 🛠️ Setup

1. **Instalação das dependências**:
   ```bash
   pip install -r requirements.txt
   npm install -g @anthropic-ai/claude-code
   ```

2. **Chaves de API**:
   ```bash
   export ANTHROPIC_API_KEY='sua-chave'
   ```

3. **Verificação**:
   Execute o orquestrador para garantir que a estrutura está correta.
