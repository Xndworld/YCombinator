# 🧠 RegFlow AI - Log de Transição e Memória do Projeto

**Data**: 2026-03-03
**Status**: Projeto Refatorado e Unificado na Branch `main`.

---

## 🚩 Contexto do Problema (Multi-Sessão & Fragmentação)

O projeto apresentava uma alta complexidade de fragmentação devido a:
1. **Múltiplas Sessões**: O trabalho foi realizado em diversos momentos, gerando inconsistência de memória entre as instâncias de IA.
2. **Proliferação de Branches**: Diversas branches (`claude/*`, `societal_problem_agent`, etc.) continham versões isoladas e conflitantes de agentes e protocolos.
3. **Redundância de Dados**: Arquivos CSV e JSON estavam espalhados, dificultando uma "fonte única de verdade".

---

## 🛠️ O que foi Feito (Resumo da Refatoração)

Realizei um **Merge Semântico** e uma **Reestruturação Arquitetural** profunda para transformar o repositório no sistema **RegFlow AI**.

### 1. Unificação e Merge
- Consolidamos todas as branches isoladas na branch `semantic_merge_refactor` e, posteriormente, realizamos o merge definitivo para a `main`.
- Resolvemos conflitos críticos no `README.md` para alinhar a documentação com a nova realidade do código.

### 2. Nova Arquitetura de Dados (Single Source of Truth)
- Criamos o diretório `dados/banco/` para centralizar os JSONs estruturados.
- Implementamos o `database/db_writer.py`, um módulo unificado de acesso que todos os agentes devem usar para garantir consistência e economia de tokens.

### 3. Orquestração Centralizada
- Criamos o `orquestrador/main.py`. Nenhum agente deve ser rodado isoladamente sem passar pelo orquestrador agora.
- O fluxo de 9 etapas foi definido e documentado no `README.md`.

### 4. Organização de Agentes
- **Mapeados (Core)**: `agentes/rankers/yc_ranker`, `agentes/articuladores`, `agentes/bancas/redbull`.
- **Não Mapeados (Legados)**: Movidos para `agentes/nao_mapeados/`. Estes agentes precisam ser revisados para decidir se serão integrados ao novo padrão ou descartados.

### 5. Padronização de Editais
- Introduzimos a interface `BaseBanca` em `agentes/bancas/base_banca.py`. Qualquer nova banca (YC, RedBull, etc.) deve herdar dela para garantir uniformidade.

---

## 📝 Instruções para o Próximo Agente (Handover)

1. **Prioridade**: Revisar os agentes em `agentes/nao_mapeados/`.
   - `brainstorm_agent`: Precisa ser integrado à Fase 5 do Orquestrador.
   - `validador`: Precisa ser atualizado para checar a nova estrutura JSON em `dados/banco/`.
2. **Comandos**: Todo o sistema opera via `python orquestrador/main.py [comando]`. Consulte o `README.md`.
3. **Desenvolvimento**: Ao criar novos agentes, **sempre** herde de `BaseBanca` (se for avaliador) e utilize o `db_writer` para persistência.
4. **Infra**: O Claude Code CLI (`claude`) está instalado e o SDK `anthropic` está disponível no ambiente.

---

## 📅 Histórico de Commits Chave
- `1c0807a`: Refatoração inicial e movimentação de arquivos.
- `80c65a8`: Resolução de conflitos no README e documentação RegFlow.
- `d769136`: Merge final e sincronização com a branch `main`.

---
> **Nota do Orquestrador**: Este log serve como memória persistente para evitar regressões causadas por novas sessões. Mantenha este documento atualizado a cada grande mudança estrutural.
