"""
Configuração central do framework de avaliação de Ideias de Startup.

Define as 5 categorias de avaliação, seus critérios, pesos e escalas de pontuação
para transformar um problema validado em uma ideia de startup estruturada.

Categorias:
1. Eficácia e Problem-Solution Fit
2. Viabilidade e Risco de Produto
3. Distribuição e Go-to-Market
4. Modelo de Negócios e Economia Unitária
5. Moats (Fossos Competitivos e Defensibilidade)

Baseado nas metodologias de:
- Y Combinator (Paul Graham / Michael Seibel)
- Lean Startup (Eric Ries)
- Zero to One (Peter Thiel)
- 7 Powers (Hamilton Helmer)
- Blitzscaling (Reid Hoffman)
- Marty Cagan (Inspired)
- Sequoia Capital / Sam Altman
"""

SCORE_MIN = 1
SCORE_MAX = 10

IDEA_SCORING_FRAMEWORK = {
    "1_eficacia_problem_solution_fit": {
        "nome": "Eficácia e Problem-Solution Fit",
        "escola_base": "Y Combinator (Paul Graham / Michael Seibel) e Peter Thiel (Zero to One)",
        "tese": (
            "Julgamos se a ideia proposta é apenas 'legal' ou se realmente aniquila "
            "o problema definido. Melhorias marginais de 10-20% não fazem os usuários "
            "mudarem de hábito."
        ),
        "criterios": {
            "regra_10x": {
                "nome": "A Regra do 10x",
                "peso": 5,
                "pergunta": (
                    "A ideia proposta é 10x mais rápida, 10x mais barata ou 10x melhor "
                    "do que a 'gambiarra' ou solução atual que o usuário usa?"
                ),
                "referencia": (
                    "Peter Thiel: Ideias com melhorias marginais de 10% ou 20% não "
                    "fazem os usuários mudarem de hábito."
                ),
                "escala": {
                    1: "Melhoria marginal (<10%), indistinguível do status quo",
                    3: "Melhoria perceptível (20-50%) mas não suficiente para mudar hábitos",
                    5: "Melhoria significativa (2-3x) que atrai early adopters",
                    7: "Melhoria substancial (5-7x) que faz a maioria migrar",
                    10: "Melhoria de 10x+ que torna a solução anterior absurda em comparação",
                },
            },
            "simplicidade_proposta_valor": {
                "nome": "Simplicidade da Proposta de Valor",
                "peso": 5,
                "pergunta": (
                    "A mecânica da solução pode ser explicada em uma frase simples "
                    "(ex: 'Apertar um botão e chamar um carro')?"
                ),
                "referencia": (
                    "Soluções complexas de explicar são complexas de vender. "
                    "Se o elevator pitch precisa de mais de 10 segundos, há um problema."
                ),
                "escala": {
                    1: "Impossível explicar sem um whiteboard de 30 minutos",
                    3: "Requer um parágrafo longo com várias ressalvas",
                    5: "Explicável em 2-3 frases com algum esforço",
                    7: "Uma frase clara, mas com um qualificador",
                    10: "Uma frase de 5 palavras que qualquer pessoa entende instantaneamente",
                },
            },
            "caminho_direto_dor": {
                "nome": "Caminho direto para a dor",
                "peso": 5,
                "pergunta": (
                    "A ideia resolve o problema primário imediatamente ou exige que o "
                    "usuário use várias 'features' periféricas antes de sentir o valor?"
                ),
                "referencia": (
                    "YC: O primeiro contato com o produto deve resolver a dor #1. "
                    "Features periféricas matam a retenção inicial."
                ),
                "escala": {
                    1: "Usuário precisa usar 5+ features antes de sentir algum valor",
                    3: "Precisa configurar e aprender antes de resolver a dor",
                    5: "Resolve parcialmente logo, mas valor total requer onboarding",
                    7: "Resolve a dor principal nos primeiros minutos de uso",
                    10: "Resolve a dor #1 no primeiro segundo — valor imediato e visceral",
                },
            },
            "alinhamento_frequencia": {
                "nome": "Alinhamento de Frequência",
                "peso": 4,
                "pergunta": (
                    "A solução propõe um uso que bate com a frequência do problema? "
                    "(Se o problema é diário, a solução é um app diário; se é anual, "
                    "a solução é automatizada e não um app que será esquecido)"
                ),
                "referencia": (
                    "YC: alta frequência constrói hábito. Desalinhamento de frequência "
                    "gera churn inevitável."
                ),
                "escala": {
                    1: "Solução diária para um problema anual — será esquecida",
                    3: "Frequência desalinhada, exige esforço consciente do usuário",
                    5: "Frequência razoavelmente alinhada com ajustes",
                    7: "Frequência bem alinhada, uso natural e consistente",
                    10: "Frequência perfeitamente alinhada — a solução se encaixa no ritmo exato do problema",
                },
            },
            "foco_beachhead": {
                "nome": "Foco no 'Beachhead' (Caso de uso inicial)",
                "peso": 4,
                "pergunta": (
                    "A ideia tenta ser um 'canivete suíço' (faz tudo para todos) ou "
                    "propõe um bisturi focado em resolver perfeitamente 1 único caso "
                    "de uso inicial?"
                ),
                "referencia": (
                    "Geoffrey Moore (Crossing the Chasm): Dominar um beachhead antes "
                    "de expandir. Soluções focadas ganham notas maiores."
                ),
                "escala": {
                    1: "Canivete suíço que tenta resolver 10 problemas de 10 personas",
                    3: "Foco em 3-4 casos de uso diferentes simultaneamente",
                    5: "Um caso de uso principal mas com distrações adjacentes",
                    7: "Bisturi focado com caso de uso claro e persona definida",
                    10: "Laser absoluto: 1 problema, 1 persona, 1 caso de uso, execução impecável",
                },
            },
        },
    },
    "2_viabilidade_risco_produto": {
        "nome": "Viabilidade e Risco de Produto",
        "escola_base": "Eric Ries (Lean Startup), Ash Maurya (Running Lean) e Marty Cagan (Inspired)",
        "tese": (
            "Avaliamos se é possível construir isso sem precisar da NASA ou de "
            "orçamentos bilionários. O MVP precisa existir amanhã, não daqui a 2 anos."
        ),
        "criterios": {
            "time_to_mvp": {
                "nome": "Time-to-MVP / Esforço Inicial",
                "peso": 5,
                "pergunta": (
                    "A primeira versão (MVP) dessa solução pode ser testada amanhã usando "
                    "ferramentas No-Code, WhatsApp ou processos manuais ('Concierge')?"
                ),
                "referencia": (
                    "Eric Ries: Concierge MVP. Soluções que exigem 1 ano de código "
                    "antes do 1º teste devem ser penalizadas."
                ),
                "escala": {
                    1: "Requer 1+ ano de desenvolvimento pesado antes de qualquer teste",
                    3: "MVP em 3-6 meses com equipe técnica dedicada",
                    5: "MVP em 1-2 meses com desenvolvimento focado",
                    7: "MVP em 1-2 semanas usando no-code/low-code ou serviço manual",
                    10: "Testável amanhã com WhatsApp, planilha ou processo manual (Concierge)",
                },
            },
            "risco_tecnologico": {
                "nome": "Risco Tecnológico ('Miracle Risk')",
                "peso": 4,
                "pergunta": (
                    "A ideia usa tecnologia que já existe e é acessível (ex: APIs de IA, "
                    "SaaS) ou exige uma invenção científica (ex: fusão nuclear, hardware inédito)?"
                ),
                "referencia": (
                    "Marty Cagan: Feasibility Risk. Separar o que é engenharia "
                    "(resolvível) do que é ciência (imprevisível)."
                ),
                "escala": {
                    1: "Requer descoberta científica ou invenção de hardware inédito",
                    3: "Tecnologia existente mas imatura, com riscos de performance",
                    5: "Tecnologia disponível mas requer integração complexa",
                    7: "Stack 100% existente, APIs e SaaS disponíveis, execução direta",
                    10: "Tecnologia commodity — tudo já existe pronto, só precisa montar",
                },
            },
            "friccao_onboarding": {
                "nome": "Fricção de Onboarding",
                "peso": 4,
                "pergunta": (
                    "Quão difícil é para o usuário começar a usar? Exige integração "
                    "complexa de TI, meses de treinamento ou instalação de hardwares?"
                ),
                "referencia": (
                    "PLG (Product-Led Growth): Quanto menor a fricção de onboarding, "
                    "maior a taxa de ativação e conversão."
                ),
                "escala": {
                    1: "Requer meses de integração de TI, treinamento e instalação de hardware",
                    3: "Semanas de setup com suporte técnico dedicado",
                    5: "Algumas horas de configuração com tutorial",
                    7: "Minutos para começar, self-service com onboarding guiado",
                    10: "Zero fricção — criar conta e usar, valor em 30 segundos",
                },
            },
            "risco_dependencia_plataforma": {
                "nome": "Risco de Dependência de Plataforma",
                "peso": 4,
                "pergunta": (
                    "A solução funciona sozinha ou morre se a Apple, Google ou WhatsApp "
                    "mudarem as regras de suas APIs amanhã?"
                ),
                "referencia": (
                    "Platform Risk: Startups que dependem 100% de uma plataforma "
                    "vivem à mercê de mudanças unilaterais."
                ),
                "escala": {
                    1: "100% dependente de uma plataforma que pode mudar regras a qualquer momento",
                    3: "Forte dependência de 1-2 plataformas, com alternativas limitadas",
                    5: "Dependência parcial, com plano B viável mas custoso",
                    7: "Mínima dependência, múltiplas alternativas para cada componente",
                    10: "Stack completamente independente, zero risco de plataforma",
                },
            },
            "risco_regulatorio_solucao": {
                "nome": "Risco Regulatório da Solução",
                "peso": 3,
                "pergunta": (
                    "O problema pode ser seguro, mas ESSA solução esbarra em leis "
                    "rigorosas (ex: prescrever remédios via IA, intermediar valores "
                    "sem licença do Banco Central)?"
                ),
                "referencia": (
                    "Risco regulatório específico da solução proposta, não do "
                    "problema em si."
                ),
                "escala": {
                    1: "Solução viola leis existentes ou requer licenças quase impossíveis",
                    3: "Zona cinzenta regulatória com riscos significativos",
                    5: "Regulação navegável com compliance e investimento legal",
                    7: "Regulação leve, requisitos claros e atingíveis",
                    10: "Zero barreira regulatória, atividade completamente livre",
                },
            },
        },
    },
    "3_distribuicao_go_to_market": {
        "nome": "Distribuição e Go-to-Market",
        "escola_base": "Reid Hoffman (Blitzscaling), Peter Thiel (Zero to One) e PLG (Wes Bush)",
        "tese": (
            "O maior cemitério de boas soluções é a falta de distribuição. "
            "Como essa solução chega nas mãos de milhões?"
        ),
        "criterios": {
            "vetor_crescimento_embutido": {
                "nome": "Vetor de Crescimento Embutido (PLG/Viralidade)",
                "peso": 5,
                "pergunta": (
                    "A própria mecânica do produto traz novos usuários? (Ex: para eu "
                    "usar o Zoom/Calendly/Pix com você, você precisa conhecer o produto)."
                ),
                "referencia": (
                    "PLG / Viralidade Intrínseca: O melhor canal de aquisição é o "
                    "próprio produto sendo usado."
                ),
                "escala": {
                    1: "Zero viralidade — cada usuário precisa ser adquirido individualmente",
                    3: "Algum boca-a-boca natural mas sem mecânica embutida",
                    5: "Incentivos para referral mas sem viralidade intrínseca",
                    7: "Viralidade moderada — uso do produto naturalmente expõe novos usuários",
                    10: "Viralidade intrínseca obrigatória — para usar, precisa convidar outros (ex: Zoom, Pix)",
                },
            },
            "escalabilidade_canal_aquisicao": {
                "nome": "Escalabilidade do Canal de Aquisição",
                "peso": 4,
                "pergunta": (
                    "A ideia se apoia em canais de marketing/vendas que podem escalar "
                    "(Inbound, Ads, Parcerias) ou dependerá de vendas de porta em porta "
                    "não-escaláveis?"
                ),
                "referencia": (
                    "Blitzscaling: Canais escaláveis são pré-requisito para crescimento "
                    "exponencial."
                ),
                "escala": {
                    1: "100% dependente de vendas porta a porta, não-escalável",
                    3: "Canais com escala limitada (eventos, cold calling presencial)",
                    5: "Mix de canais escaláveis e não-escaláveis",
                    7: "Canais digitais escaláveis dominantes (SEO, Ads, Content, Parcerias)",
                    10: "Canais infinitamente escaláveis com CAC decrescente (PLG + efeitos de rede)",
                },
            },
            "clareza_acesso_decisor": {
                "nome": "Clareza de Acesso ao Decisor (B2B)",
                "peso": 4,
                "pergunta": (
                    "Se a solução for B2B, ela mira no funcionário que sofre a dor "
                    "(fácil de vender) ou no CEO/Diretoria (ciclo de vendas de 12 meses)?"
                ),
                "referencia": (
                    "Bottom-up adoption ganha mais pontos. Atlassian e Slack cresceram "
                    "começando pelo usuário final, não pelo C-level."
                ),
                "escala": {
                    1: "Venda obrigatória para C-level com comitê de compras (12+ meses)",
                    3: "Venda para gerência média, aprovação de diretoria necessária",
                    5: "Decisor identificável mas com processo de compra moderado",
                    7: "Funcionário individual pode adotar e expandir (bottom-up)",
                    10: "Self-service B2C ou bottom-up B2B sem aprovação — uso individual expande organicamente",
                },
            },
            "barreira_ao_teste": {
                "nome": "Barreira ao Teste",
                "peso": 3,
                "pergunta": (
                    "A solução permite um 'freemium' ou teste grátis (Self-service), "
                    "ou o cliente precisa assinar um contrato às cegas para ver se funciona?"
                ),
                "referencia": (
                    "Try-before-buy reduz o risco percebido e acelera a adoção. "
                    "Freemium é o padrão de crescimento PLG."
                ),
                "escala": {
                    1: "Contrato obrigatório de 12+ meses antes de qualquer uso",
                    3: "Demo restrita com vendedor, sem acesso livre",
                    5: "Trial limitado de 14 dias com cartão de crédito",
                    7: "Freemium generoso, valor real sem pagar",
                    10: "100% self-service, gratuito para sempre no tier básico, upgrade natural",
                },
            },
        },
    },
    "4_modelo_negocios_economia_unitaria": {
        "nome": "Modelo de Negócios e Economia Unitária",
        "escola_base": "Sequoia Capital, Sam Altman e Marty Cagan (Viability Risk)",
        "tese": (
            "Se o produto for de graça, o mundo todo usa. Mas como essa solução "
            "fecha a conta? A economia unitária precisa fazer sentido desde o dia 1."
        ),
        "criterios": {
            "margem_bruta_potencial": {
                "nome": "Margem Bruta Potencial",
                "peso": 5,
                "pergunta": (
                    "A solução é baseada em software/código (margem de 80-90%) ou "
                    "envolve humanos prestando serviço/logística física pesada "
                    "(margem de 10-30%)?"
                ),
                "referencia": (
                    "Sequoia / YC: Software sempre pontua mais em bancas YC. "
                    "Margens altas financiam o crescimento."
                ),
                "escala": {
                    1: "Margem <10% — logística pesada, mão-de-obra intensiva",
                    3: "Margem 10-30% — serviço com componente humano significativo",
                    5: "Margem 30-50% — mix de software e serviço",
                    7: "Margem 50-75% — majoritariamente software com algum serviço",
                    10: "Margem 80-95% — puro software/SaaS, custo marginal quase zero",
                },
            },
            "modelo_receita_recorrente": {
                "nome": "Modelo de Receita Recorrente",
                "peso": 5,
                "pergunta": (
                    "A ideia permite cobrar assinaturas mensais/anuais (SaaS) ou "
                    "a receita dependerá de vendas transacionais (matar um leão por dia)?"
                ),
                "referencia": (
                    "SaaS / Subscription Economy: Receita recorrente é o modelo mais "
                    "valorizado por VCs por sua previsibilidade."
                ),
                "escala": {
                    1: "100% transacional, cada venda é uma conquista separada",
                    3: "Majoritariamente transacional com alguma recorrência",
                    5: "Mix 50/50 transacional e recorrente",
                    7: "Majoritariamente recorrente com upsell natural",
                    10: "100% SaaS/assinatura com expansion revenue embutido (net dollar retention >120%)",
                },
            },
            "custo_servir_vs_wtp": {
                "nome": "Custo de Servir vs. Disposição a Pagar",
                "peso": 4,
                "pergunta": (
                    "O custo operacional de entregar a solução para 1 cliente é "
                    "esmagado pelo valor que ele aceita pagar? A matemática básica "
                    "fica de pé?"
                ),
                "referencia": (
                    "Unit Economics: LTV/CAC > 3x e payback < 12 meses é o mínimo "
                    "para VCs."
                ),
                "escala": {
                    1: "Custo de servir > receita por cliente — queima dinheiro por unidade",
                    3: "Margem apertada, break-even difícil nos primeiros anos",
                    5: "Margem positiva mas modesta, requer escala para rentabilidade",
                    7: "Boa margem, custo de servir cai significativamente com escala",
                    10: "Custo de servir desprezível vs. disposição a pagar — LTV/CAC >10x",
                },
            },
            "ciclo_recebimento": {
                "nome": "Ciclo de Recebimento (Working Capital)",
                "peso": 3,
                "pergunta": (
                    "A ideia cobra do cliente antes de entregar o valor (ótimo para "
                    "fluxo de caixa) ou precisa pagar fornecedores meses antes do "
                    "cliente pagar (péssimo)?"
                ),
                "referencia": (
                    "Working Capital: Negócios que cobram antes de entregar "
                    "financiam seu próprio crescimento."
                ),
                "escala": {
                    1: "Paga fornecedores meses antes de receber do cliente",
                    3: "Capital de giro significativo necessário, recebe 60-90 dias após entrega",
                    5: "Recebe próximo à entrega, capital de giro neutro",
                    7: "Cobra antecipado (assinatura anual ou pré-pagamento)",
                    10: "100% pré-pago, cash flow negativo, financia crescimento com receita",
                },
            },
        },
    },
    "5_moats_defensibilidade": {
        "nome": "Moats (Fossos Competitivos e Defensibilidade)",
        "escola_base": "Peter Thiel (Zero to One) e Hamilton Helmer (7 Powers)",
        "tese": (
            "Se a ideia for um sucesso absoluto, o que impede a concorrência de "
            "copiar em 3 meses? Sem fossos, lucros são temporários."
        ),
        "criterios": {
            "efeitos_de_rede": {
                "nome": "Efeitos de Rede Locais ou Globais",
                "peso": 4,
                "pergunta": (
                    "A solução fica ativamente melhor para o usuário A toda vez que "
                    "o usuário B entra? (Ex: Uber, Airbnb, Marketplaces, Redes Sociais)."
                ),
                "referencia": (
                    "Helmer (Network Economies): O fosso mais poderoso que existe — "
                    "difícil de replicar e auto-reforçante."
                ),
                "escala": {
                    1: "Zero efeito de rede — produto funciona identicamente com 1 ou 1M de usuários",
                    3: "Efeito de rede fraco e indireto (ex: reviews em marketplace)",
                    5: "Efeito de rede moderado local (ex: comunidade regional)",
                    7: "Efeito de rede forte e direto (ex: marketplace bilateral ativo)",
                    10: "Efeito de rede exponencial e global (ex: protocolo ou rede social massiva)",
                },
            },
            "lockin_custo_mudanca": {
                "nome": "Lock-in / Custo de Mudança",
                "peso": 4,
                "pergunta": (
                    "Depois que a empresa ou usuário implementa a solução, seria um "
                    "pesadelo trocá-la por um concorrente porque ela se integrou aos "
                    "processos ou virou o 'sistema de registro'?"
                ),
                "referencia": (
                    "Helmer (Switching Costs): Quanto maior o custo de trocar, "
                    "maior a retenção e o poder de precificação."
                ),
                "escala": {
                    1: "Troca trivial em minutos — zero custo de mudança",
                    3: "Algum inconveniente (reconfigurar, re-aprender) mas fazível em dias",
                    5: "Custo moderado: migração de dados e retraining de equipe",
                    7: "Alto custo: integrado a processos críticos, migração custosa e arriscada",
                    10: "Lock-in extremo: sistema de registro com dados irreplicáveis e integração profunda",
                },
            },
            "acumulo_dados_proprietarios": {
                "nome": "Acúmulo de Dados Proprietários (Data Moat)",
                "peso": 3,
                "pergunta": (
                    "O uso contínuo da solução treina um modelo de IA ou cria uma "
                    "base de dados que torna o produto impossível de ser alcançado "
                    "por um novato?"
                ),
                "referencia": (
                    "Cornered Resource / Data Moat: Dados proprietários são o novo "
                    "petróleo — quem tem mais, ganha."
                ),
                "escala": {
                    1: "Zero geração de dados proprietários — commodity total",
                    3: "Dados genéricos que qualquer concorrente pode replicar",
                    5: "Dados moderadamente únicos, vantagem temporal de 6-12 meses",
                    7: "Base de dados proprietária significativa que melhora o produto",
                    10: "Data moat irreplicável: modelo de IA que melhora com cada uso, flywheel de dados",
                },
            },
            "economia_de_escala": {
                "nome": "Economia de Escala",
                "peso": 3,
                "pergunta": (
                    "Conforme a solução cresce, o custo unitário cai tanto que ela "
                    "pode esmagar os concorrentes no preço sem perder dinheiro?"
                ),
                "referencia": (
                    "Helmer (Scale Economies): Vantagem de custo que cresce com o "
                    "tamanho — incumbentes podem subsidiar novos mercados."
                ),
                "escala": {
                    1: "Custo unitário constante — zero economia de escala",
                    3: "Economias de escala modestas (negociação com fornecedores)",
                    5: "Economias de escala moderadas em infraestrutura",
                    7: "Fortes economias de escala — custo unitário cai significativamente",
                    10: "Winner-takes-all: custo marginal quase zero em escala massiva",
                },
            },
        },
    },
}


def get_all_criteria():
    """Retorna uma lista plana de todos os critérios com suas categorias."""
    criteria_list = []
    for cat_key, category in IDEA_SCORING_FRAMEWORK.items():
        for crit_key, criterion in category["criterios"].items():
            criteria_list.append(
                {
                    "categoria_key": cat_key,
                    "categoria_nome": category["nome"],
                    "criterio_key": crit_key,
                    "criterio_nome": criterion["nome"],
                    "peso": criterion["peso"],
                    "pergunta": criterion["pergunta"],
                    "referencia": criterion["referencia"],
                }
            )
    return criteria_list


def get_max_possible_score():
    """Calcula a pontuação máxima possível (todos os critérios com nota 10)."""
    total = 0
    for category in IDEA_SCORING_FRAMEWORK.values():
        for criterion in category["criterios"].values():
            total += criterion["peso"] * SCORE_MAX
    return total


def get_category_max_score(category_key):
    """Calcula a pontuação máxima possível para uma categoria."""
    category = IDEA_SCORING_FRAMEWORK[category_key]
    total = 0
    for criterion in category["criterios"].values():
        total += criterion["peso"] * SCORE_MAX
    return total


def get_category_names():
    """Retorna os nomes de todas as categorias."""
    return {key: cat["nome"] for key, cat in IDEA_SCORING_FRAMEWORK.items()}


# Constantes calculadas
TOTAL_CRITERIA = sum(
    len(cat["criterios"]) for cat in IDEA_SCORING_FRAMEWORK.values()
)
MAX_POSSIBLE_SCORE = get_max_possible_score()


# Template para prompt de avaliação de critério individual
IDEA_EVALUATION_PROMPT_TEMPLATE = """Você é um analista de startups com experiência em Y Combinator, Sequoia Capital e Lean Startup.

Avalie a seguinte IDEIA DE STARTUP contra o critério especificado.

## Problema Original
**Título:** {problema_titulo}
**Descrição:** {problema_descricao}

## Ideia de Startup Proposta
{ideia_descricao}

## Critério a Avaliar
**Categoria:** {categoria_nome}
**Critério:** {criterio_nome} (Peso: {peso})
**Pergunta-guia:** {pergunta}
**Referência teórica:** {referencia}

## Escala de Avaliação
{escala_formatada}

## Instrução
Baseado na sua análise profunda da ideia e no critério acima:
1. Avalie com uma nota de 1 a 10
2. Justifique brevemente a nota (máximo 2 frases)

Responda EXCLUSIVAMENTE no formato:
NOTA: [número de 1 a 10]
JUSTIFICATIVA: [sua justificativa]
"""


# Template para prompt de geração de ideia de startup
IDEA_GENERATION_PROMPT_TEMPLATE = """Você é um sócio sênior da Y Combinator com 15 anos de experiência avaliando startups.

A partir do problema societário abaixo, desenvolva UMA ideia de startup focada, prática e viável.

## Problema
**Título:** {problema_titulo}
**Descrição:** {problema_descricao}
**Desenvolvimento:** {problema_desenvolvimento}

## Instruções para a Ideia
Desenvolva a ideia respondendo de forma CONCISA e DIRETA:

1. **Nome da Startup** (criativo, memorável, máx 2 palavras)
2. **Tagline** (uma frase de impacto, máx 10 palavras)
3. **O que é** (explicação em 2-3 frases)
4. **Para quem** (persona específica — cargo, setor, dor)
5. **Como funciona** (mecânica central em 3 passos simples)
6. **Modelo de negócio** (como cobra, de quem, quanto aproximadamente)
7. **Diferencial 10x** (por que é 10x melhor que a gambiarra atual)
8. **MVP mínimo** (o que construir nas primeiras 2 semanas)

Seja PRÁTICO. Prefira soluções com:
- Stack tecnológico existente (APIs, SaaS, no-code)
- Receita recorrente (SaaS/assinatura)
- Margens altas (software > serviço)
- Viralidade embutida
- Foco em 1 beachhead claro

Responda em português brasileiro.
"""


# Template para prompt do artigo final
ARTICLE_PROMPT_TEMPLATE = """Você é um escritor de pitch decks e análises de startups com experiência em Y Combinator.

Escreva um artigo CONCISO (máximo 2 páginas de texto corrido) sobre a ideia de startup abaixo.

## Problema Original
**Título:** {problema_titulo}
**Descrição:** {problema_descricao}

## Ideia de Startup
{ideia_descricao}

## Pontuação do Framework
{pontuacao_formatada}

## Pontuação Total: {pontuacao_total} / {pontuacao_maxima} ({percentual}%)

## Instrução para o Artigo

O artigo deve ser em TEXTO CORRIDO (sem tópicos, sem tabelas, sem listas), com no máximo 2 páginas, cobrindo TODOS estes pontos de forma fluida:

1. **Abertura**: O problema, por que dói, e a ideia proposta em uma frase.
2. **Problem-Solution Fit**: Como a ideia aniquila o problema (regra do 10x, simplicidade, caminho direto para a dor).
3. **Viabilidade**: Quão rápido dá para construir o MVP, riscos tecnológicos e regulatórios.
4. **Distribuição**: Como a solução chega nas mãos de milhões (viralidade, canais, acesso ao decisor).
5. **Modelo de Negócio e Economia**: Como lucra, margens, recorrência, e se a conta fecha.
6. **Moats**: O que impede a cópia em 3 meses (rede, lock-in, dados, escala).
7. **Concorrentes**: Quem já existe, quais features oferecem, onde falham.
8. **Business Model Canvas** (em forma narrativa, não tabela): Segmento, proposta de valor, canais, relacionamento, fontes de receita, recursos-chave, atividades-chave, parceiros e estrutura de custos.
9. **Como vender e lucrar**: Estratégia de go-to-market prática (primeiros 100 clientes, depois escala).
10. **MVP**: O que construir na primeira versão, com quais ferramentas, em quanto tempo.

**Tom**: Analítico mas acessível. Como um sócio da YC explicaria a oportunidade para um founder inteligente.
**Idioma**: Português brasileiro.
**Tamanho**: Texto corrido de no MÁXIMO 2 páginas. Seja denso e objetivo.

NÃO use listas, NÃO use tabelas, NÃO use markdown com cabeçalhos. Texto corrido dividido em parágrafos.
"""
