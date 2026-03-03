"""
Protocolo de Atualização - Ingestão de Novos Insights
======================================================

Fluxo automático quando um novo insight/dado chega:

    1. INGESTÃO: Recebe novo insight (texto, relatório, dado)
    2. CLASSIFICAÇÃO: Agente classifica como problema/oportunidade
       → Gera notas nas 50 métricas do framework
       → Calcula score e insere em problemas.json
    3. DECISÃO TOP 50:
       ├── SIM (top 50) → Etapa 4: Brainstorm (5×5=25 soluções)
       │                 → Soluções inseridas em solucoes.json
       │                 → Se top 100 → Artigo Startup → Bancas
       └── NÃO → Fica no banco de problemas para referência futura
    4. RE-RANKING: Rankings globais são recalculados automaticamente

Economia de tokens:
    - Novo insight processado uma vez
    - Score calculado e persistido
    - Brainstorm só dispara se top 50 (evita processamento desnecessário)
    - Bancas só avaliam se solução é top 100

Pipeline:
    Input:  Novo insight (texto livre, relatório, dado estruturado)
    Output: dados/banco/problemas.json (atualizado)
            dados/banco/solucoes.json (se top 50)
            dados/banco/startups.json (se top 100)
            dados/09_protocolo_atualizacao/ (log de atualizações)

Status: PLACEHOLDER - A ser implementado
"""
