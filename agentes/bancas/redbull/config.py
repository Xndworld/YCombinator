"""
Configuração do framework de avaliação RBB Judge Agent.

Define os 5 pilares do Red Bull Basement, seus pesos, critérios,
prompts LLM e o schema de saída JSON esperado.

Framework baseado nos dois metaprompts oficiais do RBB:
  Pilar 1 - Problema Sistêmico e Impacto Social/Ambiental:  35 pts (35%)
  Pilar 2 - Solução Tecnológica (Diferencial de IA):        20 pts (20%)
  Pilar 3 - Storytelling, Vivência e Fator Red Bull:        25 pts (25%)
  Pilar 4 - Viabilidade de Execução e Negócio:             10 pts (10%)
  Pilar 5 - Equipe e Escalabilidade do Impacto:            10 pts (10%)
  Total máximo:                                            100 pts
"""

# ============================================================================
# AS 9 ÁREAS OFICIAIS DO EDITAL RBB
# ============================================================================

AREAS_INTERESSE = [
    "Educação e Carreira",
    "Esportes e Desempenho Humano",
    "Mídia e Entretenimento",
    "Evolução Urbana",
    "Experiência do Consumidor",
    "Indústria Inteligente",
    "Alimentação e Nutrição",
    "Viagem",
    "Sustentabilidade",
]

# ============================================================================
# FRAMEWORK DOS 5 PILARES
# ============================================================================

SCORING_FRAMEWORK = {
    "pilar_1_impacto_social_sistemico": {
        "nome": "Problema Sistêmico e Impacto Social/Ambiental",
        "peso_maximo": 35,
        "peso_percentual": "35%",
        "tese": (
            "O CORAÇÃO do projeto RBB. Avaliamos se a dor é real, profunda e estrutural. "
            "Projetos de conveniência de luxo são penalizados severamente. "
            "Buscamos impacto transformador em comunidades esquecidas ou ecossistemas ameaçados."
        ),
        "criterios": [
            {
                "nome": "Magnitude da Dor",
                "descricao": "A dor afeta comunidades inteiras, ecossistemas ou populações vulneráveis? Não é uma conveniência de luxo?",
            },
            {
                "nome": "Alinhamento com as 9 Áreas Oficiais",
                "descricao": "O projeto atua diretamente na raiz de problemas nas 9 áreas do edital RBB?",
            },
            {
                "nome": "Transformação Real",
                "descricao": "O projeto muda vidas concretas ou salva recursos naturais de forma comprovável e mensurável?",
            },
            {
                "nome": "Resolução de Causa Raiz",
                "descricao": "Resolve o núcleo estrutural do problema (não apenas o sintoma superficial)?",
            },
            {
                "nome": "Tradução Acadêmica / Aplicação Prática",
                "descricao": "Se derivado de pesquisa, consegue sair do laboratório para aplicação social prática e imediata?",
            },
            {
                "nome": "Mitigação de Externalidades",
                "descricao": "Reduz externalidades negativas — poluição, exclusão, desigualdade — de forma sistêmica?",
            },
        ],
    },
    "pilar_2_solucao_tecnologica_ia": {
        "nome": "Solução Tecnológica — Diferencial de IA",
        "peso_maximo": 20,
        "peso_percentual": "20%",
        "tese": (
            "A IA deve ser meio viabilizador, não buzzword. Avaliamos se a tecnologia resolve "
            "um problema que humanos não conseguiriam em escala, se é viável com a stack atual "
            "(Azure, AMD, APIs abertas) e se democratiza algo que hoje é privilégio de poucos."
        ),
        "criterios": [
            {
                "nome": "Justificativa Real da IA",
                "descricao": "A IA/ML resolve algo que humanos não conseguiriam em escala? (Não é só buzzword)?",
            },
            {
                "nome": "Uso de ML/NLP/CV",
                "descricao": "Processa padrões, linguagem ou imagens que humanos não conseguiriam sozinhos na velocidade necessária?",
            },
            {
                "nome": "Viabilidade do Protótipo (Show, Don't Tell)",
                "descricao": "Pode ser construído com a stack atual (Azure, AMD, APIs de IA, open source)? Não desafia leis da física?",
            },
            {
                "nome": "Arquitetura Ética (LGPD / Vieses)",
                "descricao": "O uso da tecnologia é ético, sem vieses discriminatórios, respeitando LGPD e privacidade?",
            },
            {
                "nome": "Democratização Tecnológica",
                "descricao": "Torna barato e acessível algo que hoje custa caro ou é privilégio de poucos?",
            },
            {
                "nome": "Eficiência Computacional",
                "descricao": "Edge computing, custo computacional razoável, interoperável com sistemas existentes?",
            },
        ],
    },
    "pilar_3_storytelling_fator_redbull": {
        "nome": "Storytelling, Vivência e Fator Red Bull",
        "peso_maximo": 25,
        "peso_percentual": "25%",
        "tese": (
            "O DNA do RBB é a história autêntica e inspiradora. Buscamos projetos com 'Fator Red Bull': "
            "uma narrativa que emociona, um fundador que viveu a dor e uma solução tão criativa que "
            "renderia um mini-documentário ou viral no TikTok/Instagram."
        ),
        "criterios": [
            {
                "nome": "Conexão Emocional Autêntica",
                "descricao": "O fundador viveu a dor na pele ou na comunidade? A história é genuína e não performática?",
            },
            {
                "nome": "Fator Uau / Potencial Midiático",
                "descricao": "A solução é criativa, empolgante e renderia um mini-doc ou viral nas redes? Tem apelo visual?",
            },
            {
                "nome": "Simplicidade do Pitch",
                "descricao": "A equipe consegue explicar a solução de forma brilhante, sem jargões técnicos? Em 1 frase?",
            },
            {
                "nome": "Carisma e Embaixadoria",
                "descricao": "O projeto tem energia que inspira outros jovens a inovar? O fundador é um embaixador natural?",
            },
            {
                "nome": "Potencial Gamificado / Engajador",
                "descricao": "A experiência do usuário tem elementos engajadores, gamificação ou comunidade que criam vínculo?",
            },
            {
                "nome": "Clareza do Pedido (The Ask)",
                "descricao": "O projeto sabe o que precisa (mentoria, parcerias, visibilidade)? O pedido é claro e específico?",
            },
        ],
    },
    "pilar_4_viabilidade_execucao": {
        "nome": "Viabilidade de Execução e Negócio",
        "peso_maximo": 10,
        "peso_percentual": "10%",
        "tese": (
            "O foco não é lucro bilionário, mas garantir que o projeto não dependa eternamente de doações. "
            "Avaliamos se há modelo sustentável (B2B, B2B2C, SaaS de impacto, B2G/ESG) e se pode gerar "
            "impacto tangível rapidamente, sem precisar de milagres regulatórios ou bilhões de dólares."
        ),
        "criterios": [
            {
                "nome": "Sustentabilidade Financeira",
                "descricao": "Como o projeto se mantém vivo? Não pode depender EXCLUSIVAMENTE de doações/caridade passiva.",
            },
            {
                "nome": "Modelo de Receita Claro",
                "descricao": "Tem modelo definido (B2B, B2B2C, SaaS, B2G, ESG corporativo)? Quem paga e quanto?",
            },
            {
                "nome": "Agilidade Executiva",
                "descricao": "Pode gerar impacto tangível nos próximos 12 meses? Não depende de novas leis aprovadas?",
            },
            {
                "nome": "Validação no Mundo Real",
                "descricao": "A equipe já conversou com ONGs, comunidades afetadas, clientes ou parceiros reais?",
            },
            {
                "nome": "Atratividade Institucional",
                "descricao": "Tem potencial de atração de investimento ESG, impacto, governo ou parceiros corporativos?",
            },
        ],
    },
    "pilar_5_equipe_escalabilidade": {
        "nome": "Equipe e Escalabilidade do Impacto",
        "peso_maximo": 10,
        "peso_percentual": "10%",
        "tese": (
            "Avaliamos se o projeto pode sair do Brasil e resolver o mesmo problema globalmente, "
            "e se a equipe de 1-2 pessoas tem o mix técnico + comunicacional para executar. "
            "Skin in the game é fundamental: o projeto não pode ser apenas um trabalho de escola."
        ),
        "criterios": [
            {
                "nome": "Escala Global de Impacto",
                "descricao": "A solução pode sair do Brasil e resolver o mesmo problema na Índia, Quênia ou Filipinas?",
            },
            {
                "nome": "Complementaridade da Equipe",
                "descricao": "A equipe (1-2 pessoas) tem mix de habilidades técnicas e comunicacionais para executar?",
            },
            {
                "nome": "Skin in the Game",
                "descricao": "Fica claro o compromisso de longo prazo? Não é apenas um projeto de hackathon/escola?",
            },
            {
                "nome": "Escala via Software",
                "descricao": "O custo marginal de expansão tende a zero? Pode crescer sem multiplicar custos operacionais?",
            },
            {
                "nome": "Independência de Milagres",
                "descricao": "O projeto roda sem depender de uma tecnologia não inventada ou aprovação regulatória improvável?",
            },
        ],
    },
}

# ============================================================================
# CONSTANTES
# ============================================================================

MAX_POSSIBLE_SCORE = sum(p["peso_maximo"] for p in SCORING_FRAMEWORK.values())  # 100

# Thresholds de status (conforme metaprompt)
THRESHOLD_APROVADO = 80
THRESHOLD_OBSERVACAO = 60

# ============================================================================
# SYSTEM PROMPT — PERSONA DO RBB AI JUDGE
# ============================================================================

RBB_SYSTEM_PROMPT = """Você é o "RBB AI Judge", um agente avaliador especialista em inovação de impacto, treinado especificamente para a banca do Red Bull Basement.

Diferente de investidores tradicionais que buscam unicórnios financeiros (como a Y Combinator), seu objetivo primário é o IMPACTO SOCIAL E AMBIENTAL. Você busca "Idealismo Pragmático com Viés Midiático": projetos que atacam dores reais e estruturais, usam tecnologia (especialmente IA) como meio viabilizador, e possuem uma história autêntica e inspiradora ("O Fator Red Bull").

A viabilidade financeira importa apenas para garantir que o projeto não dependa de caridade para sobreviver, mas o lucro não é o fim — a mudança no mundo é o fim.

# AS 9 ÁREAS DE INTERESSE OFICIAIS DO EDITAL
O projeto DEVE se encaixar em uma ou mais destas áreas:
1. Educação e Carreira
2. Esportes e Desempenho Humano
3. Mídia e Entretenimento
4. Evolução Urbana
5. Experiência do Consumidor
6. Indústria Inteligente
7. Alimentação e Nutrição
8. Viagem
9. Sustentabilidade

# REGRAS CRÍTICAS DE AVALIAÇÃO
1. Analise com foco em IMPACTO SOCIAL/AMBIENTAL. Um projeto com mercado pequeno mas impacto transformador em uma comunidade esquecida vale mais do que um projeto bilionário que resolve uma futilidade.
2. Seja rigoroso: projetos vagos, cheios de buzzwords sem aplicação prática, devem ser penalizados.
3. Se o projeto depender EXCLUSIVAMENTE de doações para sempre (caridade passiva sem inovação), corte pontos no Pilar 4.
4. Se o projeto for apenas "um app banal" que não resolve problema sistêmico, penalize severamente o Pilar 1.
5. A IA deve ser meio, não fim. Penalize buzzword de IA sem aplicação real.
6. Sua saída deve ser ÚNICA E EXCLUSIVAMENTE um objeto JSON válido, sem formatação Markdown (sem ```json), sem textos introdutórios ou conclusivos."""

# ============================================================================
# PROMPT DE AVALIAÇÃO — TEMPLATE COM SCHEMA DE SAÍDA
# ============================================================================

EVALUATION_PROMPT = """Analise o projeto/startup descrito abaixo e retorne APENAS o JSON de avaliação conforme o schema.

## PROJETO A AVALIAR
{conteudo_artigo}

## SCHEMA DE SAÍDA OBRIGATÓRIO
Retorne APENAS o JSON abaixo. Substitua os valores entre colchetes pela sua avaliação real.

{{
  "nome_projeto": "[Extraia do texto — nome/título do projeto ou startup]",
  "resumo_avaliador": "[Resumo de 2 linhas focado no problema social resolvido e na tecnologia usada]",
  "areas_interesse_relacionadas": ["[Somente áreas das 9 oficiais que se aplicam]"],
  "ods_relacionados": ["[Ex: ODS 3 - Saúde e Bem-Estar, ODS 11 - Cidades Sustentáveis]"],
  "score_total": [Soma de todos os pilares — número de 0 a 100],
  "pontuacoes": {{
    "pilar_1_impacto_social_sistemico": {{
      "nota": [0 a 35],
      "justificativa": "[Análise da magnitude da dor, transformação real e causa raiz. Máx 3 linhas.]"
    }},
    "pilar_2_solucao_tecnologica_ia": {{
      "nota": [0 a 20],
      "justificativa": "[Análise da viabilidade técnica, uso real da IA e democratização. Máx 3 linhas.]"
    }},
    "pilar_3_storytelling_fator_redbull": {{
      "nota": [0 a 25],
      "justificativa": "[Análise da conexão pessoal, fator uau, criatividade e potencial midiático. Máx 3 linhas.]"
    }},
    "pilar_4_viabilidade_execucao": {{
      "nota": [0 a 10],
      "justificativa": "[Análise do modelo de receita, sustentabilidade e agilidade para implantar. Máx 3 linhas.]"
    }},
    "pilar_5_equipe_escalabilidade": {{
      "nota": [0 a 10],
      "justificativa": "[Análise do potencial de escala global e complementaridade da equipe. Máx 3 linhas.]"
    }}
  }},
  "parecer_banca": {{
    "pontos_fortes": [
      "[Ponto forte 1 — foco na solução social]",
      "[Ponto forte 2 — foco na tecnologia ou vivência]"
    ],
    "pontos_fracos_riscos": [
      "[Risco 1 — foco em barreiras de execução]",
      "[Risco 2 — outro risco relevante]"
    ],
    "recomendacao_acao": "[Conselho direto e pragmático para a equipe melhorar o impacto ou a clareza. 1-2 frases.]",
    "status_ranqueamento": "[Aprovado | Em Observação | Reprovado]"
  }}
}}

IMPORTANTE: O campo "status_ranqueamento" deve seguir a regra: Aprovado se score_total >= 80, Em Observação se 60-79, Reprovado se < 60.
Retorne APENAS o JSON. Nenhum texto antes ou depois."""


# ============================================================================
# PALAVRAS-CHAVE PARA AVALIAÇÃO HEURÍSTICA (sem LLM)
# ============================================================================

HEURISTIC_KEYWORDS = {
    "pilar_1_impacto_social_sistemico": {
        "positivas": [
            "impacto social", "impacto ambiental", "comunidade", "vulnerável",
            "pobreza", "desigualdade", "sustentabilidade", "meio ambiente",
            "educação", "saúde pública", "água", "saneamento", "clima",
            "emissão", "carbono", "reciclagem", "inclusão", "acessibilidade",
            "periférico", "quilombola", "indígena", "refugiado", "favela",
            "escola pública", "ods", "transformação", "causa raiz", "sistêmico",
            "estrutural", "ecossistema", "biodiversidade", "poluição", "resíduo",
        ],
        "negativas": [
            "luxo", "premium", "exclusivo", "vip", "alto padrão", "boutique",
            "conveniência", "lifestyle", "tendência", "moda", "entretenimento banal",
            "influencer", "selfie", "gamification casual",
        ],
    },
    "pilar_2_solucao_tecnologica_ia": {
        "positivas": [
            "inteligência artificial", "ia", "machine learning", "nlp", "visão computacional",
            "deep learning", "algoritmo", "automação", "sensor", "iot", "dados",
            "análise preditiva", "modelo", "api", "open source", "cloud",
            "democratiza", "acessível", "lgpd", "ético", "edge computing",
            "processamento", "reconhecimento", "detecção", "classificação",
        ],
        "negativas": [
            "manual", "humano", "planilha", "papel", "presencial",
            "consultoria", "agência", "sem tecnologia",
        ],
    },
    "pilar_3_storytelling_fator_redbull": {
        "positivas": [
            "viveu", "experiência pessoal", "comunidade local", "história real",
            "inspirador", "autêntico", "fundador", "empreendedor", "missão",
            "propósito", "visual", "criativo", "inovador", "viral",
            "documentário", "mídia", "redes sociais", "engajamento",
            "simples de explicar", "frase", "slogan", "impacto visível",
        ],
        "negativas": [
            "técnico demais", "jargão", "complexo", "difícil de entender",
            "abstrato", "sem história", "sem fundador",
        ],
    },
    "pilar_4_viabilidade_execucao": {
        "positivas": [
            "receita", "modelo de negócio", "b2b", "saas", "assinatura",
            "parceria", "cliente", "validação", "piloto", "mvp", "tração",
            "esg", "governo", "ong parceira", "contrato", "revenue",
            "sustentável financeiramente", "autossustentável",
        ],
        "negativas": [
            "doação", "caridade", "filantropia", "sem receita", "gratuito forever",
            "depende de subsídio", "apenas doação", "sem modelo de negócio",
        ],
    },
    "pilar_5_equipe_escalabilidade": {
        "positivas": [
            "global", "escala", "internacional", "replicável", "modular",
            "equipe", "cofundador", "tech", "negócio", "multidisciplinar",
            "comprometido", "longo prazo", "foco", "startup", "spin-off",
            "custo marginal", "crescer sem custo adicional",
        ],
        "negativas": [
            "trabalho de escola", "hackathon apenas", "projeto temporário",
            "sem equipe definida", "sozinho sem plano",
        ],
    },
}
