"""
Configuração central do framework de avaliação.

Define todas as 7 categorias, seus critérios, pesos e escalas de pontuação
baseados nas escolas de pensamento de startup/VC:
- Y Combinator (Paul Graham / Michael Seibel)
- Customer Development (Steve Blank)
- Lean Startup (Eric Ries / Ash Maurya)
- Venture Capital (Sequoia Capital / Sam Altman)
- Blitzscaling (Reid Hoffman)
- Zero to One (Peter Thiel)
- 7 Powers (Hamilton Helmer)
- Idealab (Bill Gross) / Marc Andreessen
- Inspired (Marty Cagan)
"""

# Escala de pontuação: 1 a 10 para cada critério
SCORE_MIN = 1
SCORE_MAX = 10

SCORING_FRAMEWORK = {
    "1_natureza_dor_comportamento": {
        "nome": "A Natureza da Dor e o Comportamento",
        "escola_base": "Y Combinator (Paul Graham / Michael Seibel) e Customer Development (Steve Blank)",
        "tese": "Faça algo que as pessoas querem muito. Se a dor não for aguda (hair on fire), a solução será ignorada.",
        "criterios": {
            "intensidade_dor_financeira": {
                "nome": "Intensidade da dor financeira",
                "peso": 5,
                "pergunta": "O problema causa perda direta de dinheiro?",
                "referencia": "Michael Seibel: as melhores dores afetam a receita.",
                "escala": {
                    1: "Nenhuma perda financeira mensurável",
                    3: "Perdas indiretas ou marginais",
                    5: "Perdas financeiras moderadas e recorrentes",
                    7: "Perdas significativas afetando a receita diretamente",
                    10: "Perdas massivas, ameaçando a sobrevivência do negócio/pessoa"
                }
            },
            "existencia_gambiarras": {
                "nome": "Existência de Gambiarras / Workarounds",
                "peso": 5,
                "pergunta": "Os usuários já usam planilhas, WhatsApp ou processos manuais para tentar resolver?",
                "referencia": "Steve Blank: prova definitiva de demanda.",
                "escala": {
                    1: "Ninguém tenta resolver; aceitam o problema passivamente",
                    3: "Algumas pessoas tentam resolver de forma ad hoc",
                    5: "Workarounds informais são comuns no setor",
                    7: "Gambiarras elaboradas e consolidadas (planilhas complexas, processos manuais estruturados)",
                    10: "Ecossistema inteiro de workarounds, investimento significativo em soluções improvisadas"
                }
            },
            "frequencia_problema": {
                "nome": "Frequência do problema",
                "peso": 5,
                "pergunta": "Acontece várias vezes ao dia/semana?",
                "referencia": "YC: alta frequência constrói o hábito.",
                "escala": {
                    1: "Raramente (uma vez por ano ou menos)",
                    3: "Mensal",
                    5: "Semanal",
                    7: "Diário",
                    10: "Múltiplas vezes ao dia, constante"
                }
            },
            "urgencia_percebida": {
                "nome": "Urgência percebida",
                "peso": 4,
                "pergunta": "O usuário sabe que tem o problema e está ativamente buscando solução?",
                "referencia": "Eric Ries: não eduque o mercado no início.",
                "escala": {
                    1: "Não sabe que tem o problema",
                    3: "Reconhece vagamente mas não busca solução",
                    5: "Sabe que tem o problema, busca passivamente",
                    7: "Busca ativamente soluções, pesquisa alternativas",
                    10: "Desesperadamente procurando solução, orçamento já alocado"
                }
            },
            "intensidade_dor_tempo": {
                "nome": "Intensidade da dor de tempo",
                "peso": 4,
                "pergunta": "Causa desperdício massivo de horas produtivas?",
                "referencia": "Tempo é o recurso mais escasso.",
                "escala": {
                    1: "Nenhum tempo desperdiçado",
                    3: "Algumas horas por mês",
                    5: "Várias horas por semana",
                    7: "Horas diárias desperdiçadas",
                    10: "Jornadas inteiras consumidas pelo problema"
                }
            },
            "risco_atrelado": {
                "nome": "Risco atrelado ao problema",
                "peso": 4,
                "pergunta": "Gera multas, processos, acidentes ou churn para quem sofre?",
                "referencia": "Risco amplifica a urgência de resolver.",
                "escala": {
                    1: "Nenhum risco tangível",
                    3: "Riscos menores e gerenciáveis",
                    5: "Riscos moderados (multas pequenas, churn parcial)",
                    7: "Riscos sérios (processos judiciais, acidentes, perda de clientes significativa)",
                    10: "Risco existencial (fechamento, prisão, morte)"
                }
            },
            "nivel_frustracao": {
                "nome": "Nível de frustração/Fricção",
                "peso": 4,
                "pergunta": "O quão estressante é lidar com o processo atual?",
                "referencia": "Frustração alta = motivação alta para adotar solução.",
                "escala": {
                    1: "Processo suave, sem estresse",
                    3: "Levemente irritante",
                    5: "Moderadamente frustrante",
                    7: "Muito estressante, causa desgaste emocional",
                    10: "Insuportável, pessoas abandonam o processo ou adoecem"
                }
            },
            "consequencia_erro": {
                "nome": "Consequência do erro",
                "peso": 4,
                "pergunta": "Falhar nesse processo custa o emprego ou a empresa do usuário?",
                "referencia": "Stakes altos = willingness to pay alta.",
                "escala": {
                    1: "Erro é facilmente corrigível, sem consequências",
                    3: "Retrabalho necessário",
                    5: "Perda de oportunidades ou recursos",
                    7: "Pode custar o emprego ou um contrato grande",
                    10: "Pode destruir a empresa ou causar danos irreversíveis"
                }
            },
            "observabilidade_comportamento": {
                "nome": "Observabilidade do comportamento",
                "peso": 3,
                "pergunta": "Dá para ver o usuário sofrendo com isso, ou é algo puramente mental/subjetivo?",
                "referencia": "Lean Startup: validação depende de observar comportamento.",
                "escala": {
                    1: "Completamente subjetivo e interno",
                    3: "Alguns sinais indiretos observáveis",
                    5: "Comportamento observável em entrevistas",
                    7: "Claramente visível no dia a dia do usuário",
                    10: "Extremamente visível, dados quantificáveis de comportamento"
                }
            },
            "clareza_persona": {
                "nome": "Clareza de quem sofre",
                "peso": 3,
                "pergunta": "É possível descrever a persona exata que sofre a dor extrema?",
                "referencia": "Persona de Steve Blank.",
                "escala": {
                    1: "Impossível definir quem sofre especificamente",
                    3: "Grupo genérico e amplo",
                    5: "Setor ou segmento identificável",
                    7: "Persona bem definida com cargo, setor e contexto claro",
                    10: "Persona hiper-específica, acessível e validável"
                }
            }
        }
    },

    "2_tamanho_mercado_escala": {
        "nome": "Tamanho de Mercado e Potencial de Escala",
        "escola_base": "Venture Capital Clássico (Sequoia Capital, Sam Altman) e Blitzscaling (Reid Hoffman)",
        "tese": "Mercados pequenos não perdoam erros. Você precisa de um mar grande onde a maré está subindo.",
        "criterios": {
            "tam": {
                "nome": "Tamanho de Mercado Total - TAM",
                "peso": 5,
                "pergunta": "O tema afeta um mercado que movimenta bilhões globalmente ou bilhões de reais localmente?",
                "referencia": "Sequoia Capital: mercados de bilhões.",
                "escala": {
                    1: "Mercado de nicho minúsculo (< R$100M)",
                    3: "Mercado pequeno (R$100M - R$1B)",
                    5: "Mercado médio (R$1B - R$10B)",
                    7: "Mercado grande (R$10B - R$100B)",
                    10: "Mercado massivo (> R$100B ou trilhões globalmente)"
                }
            },
            "crescimento_mercado": {
                "nome": "Crescimento do Mercado",
                "peso": 5,
                "pergunta": "O mercado está expandindo ano a ano?",
                "referencia": "Sam Altman: prefira um mercado pequeno crescendo rápido do que um grande estagnado.",
                "escala": {
                    1: "Mercado em contração",
                    3: "Estagnado (0-3% ao ano)",
                    5: "Crescimento moderado (3-10% ao ano)",
                    7: "Crescimento forte (10-25% ao ano)",
                    10: "Crescimento explosivo (> 25% ao ano)"
                }
            },
            "capacidade_monopolio_nicho": {
                "nome": "Capacidade de ser um monopólio local/nicho",
                "peso": 4,
                "pergunta": "Dá para dominar um sub-nicho antes de expandir?",
                "referencia": "Peter Thiel: Zero to One.",
                "escala": {
                    1: "Impossível dominar qualquer nicho",
                    3: "Difícil, muita competição mesmo no nicho",
                    5: "Possível com diferenciação significativa",
                    7: "Sub-nicho claro e dominável",
                    10: "Nicho perfeito para monopolizar e expandir concentricamente"
                }
            },
            "amplitude_demografica": {
                "nome": "Amplitude demográfica",
                "peso": 3,
                "pergunta": "Afeta grandes massas ou a maioria das empresas de um setor?",
                "referencia": "Quanto maior a base afetada, maior o potencial.",
                "escala": {
                    1: "Grupo extremamente restrito",
                    3: "Nicho específico dentro de um setor",
                    5: "Parcela significativa de um setor ou demografia",
                    7: "Maioria das empresas de um setor ou grande grupo populacional",
                    10: "Problema universal que afeta praticamente todos"
                }
            },
            "escalabilidade_nao_linear": {
                "nome": "Escalabilidade não-linear",
                "peso": 4,
                "pergunta": "A solução teórica para este tema exigirá custo marginal zero?",
                "referencia": "Reid Hoffman: software vs. serviço braçal.",
                "escala": {
                    1: "Escala 100% linear (cada cliente = mais custo proporcional)",
                    3: "Parcialmente escalável, mas com componentes manuais pesados",
                    5: "Escalável com automação parcial",
                    7: "Altamente escalável, custo marginal muito baixo",
                    10: "Custo marginal zero (puro software/plataforma)"
                }
            },
            "tamanho_ticket": {
                "nome": "Tamanho do ticket natural",
                "peso": 3,
                "pergunta": "O tema sugere contratos de alto valor (Enterprise) ou alto volume (B2C)?",
                "referencia": "Ticket alto = menos clientes necessários para viabilidade.",
                "escala": {
                    1: "Micro-transações (< R$10/mês)",
                    3: "Ticket baixo (R$10-100/mês)",
                    5: "Ticket médio (R$100-1.000/mês)",
                    7: "Ticket alto (R$1.000-10.000/mês)",
                    10: "Enterprise (> R$10.000/mês ou contratos anuais de 6+ dígitos)"
                }
            },
            "potencial_expansao_produto": {
                "nome": "Potencial de expansão de produto",
                "peso": 3,
                "pergunta": "O problema abre portas para resolver problemas adjacentes no futuro?",
                "referencia": "Plataformas > produtos pontuais.",
                "escala": {
                    1: "Solução extremamente pontual, sem adjacências",
                    3: "Uma ou duas expansões possíveis",
                    5: "Várias adjacências identificáveis",
                    7: "Potencial de plataforma com múltiplos módulos",
                    10: "Ecossistema inteiro pode ser construído ao redor"
                }
            },
            "penetracao_digital": {
                "nome": "Penetração digital do setor",
                "peso": 3,
                "pergunta": "O mercado-alvo já usa tecnologia básica ou ainda é 100% analógico e resistente?",
                "referencia": "Adoção digital facilita a entrada.",
                "escala": {
                    1: "100% analógico e resistente à tecnologia",
                    3: "Uso básico (email, WhatsApp)",
                    5: "Digitalização parcial (alguns sistemas)",
                    7: "Boa adoção digital, aberto a novas ferramentas",
                    10: "Setor totalmente digital e tech-savvy"
                }
            },
            "capacidade_internacionalizacao": {
                "nome": "Capacidade de internacionalização",
                "peso": 2,
                "pergunta": "É um problema global ou restrito à cultura local?",
                "referencia": "Problemas globais = TAM maior.",
                "escala": {
                    1: "100% local, sem aplicabilidade internacional",
                    3: "Relevante em países similares (LatAm)",
                    5: "Aplicável em mercados emergentes",
                    7: "Problema global com adaptações",
                    10: "Problema idêntico em qualquer país do mundo"
                }
            },
            "dependencia_infraestrutura_fisica": {
                "nome": "Dependência de infraestrutura física",
                "peso": 2,
                "pergunta": "Resolver isso exige construir fábricas ou logística complexa?",
                "referencia": "Mais dependência = menor nota (peso invertido).",
                "escala": {
                    1: "Requer infraestrutura física massiva (fábricas, logística pesada)",
                    3: "Infraestrutura significativa necessária",
                    5: "Alguma infraestrutura física, mas gerenciável",
                    7: "Infraestrutura mínima, majoritariamente digital",
                    10: "Zero dependência física, 100% digital"
                }
            }
        }
    },

    "3_timing_why_now": {
        "nome": "Timing e Why Now",
        "escola_base": "Bill Gross (Idealab) e Marc Andreessen",
        "tese": "O Timing é o fator número 1 de sucesso ou fracasso das startups. Por que resolver isso em 2026 e não em 2016?",
        "criterios": {
            "timing_tecnologico": {
                "nome": "Timing Tecnológico",
                "peso": 5,
                "pergunta": "Novas tecnologias (ex: LLMs, novas APIs) tornaram viável resolver isso agora?",
                "referencia": "Bill Gross: tecnologia habilitadora é o gatilho.",
                "escala": {
                    1: "Nenhuma tecnologia nova relevante",
                    3: "Tecnologias marginalmente úteis",
                    5: "Tecnologias novas que ajudam mas não são revolucionárias",
                    7: "Tecnologias recentes que mudam fundamentalmente a viabilidade",
                    10: "Breakthrough tecnológico que torna possível pela primeira vez"
                }
            },
            "timing_regulatorio": {
                "nome": "Timing Regulatório",
                "peso": 5,
                "pergunta": "Leis novas (ex: Open Finance, regulação climática, LGPD) forçam o mercado a adotar soluções?",
                "referencia": "Regulação cria demanda forçada.",
                "escala": {
                    1: "Nenhuma mudança regulatória relevante",
                    3: "Discussões regulatórias em estágio inicial",
                    5: "Regulações aprovadas mas ainda sendo implementadas",
                    7: "Regulações ativas que forçam adaptação imediata",
                    10: "Prazo regulatório iminente, multas pesadas por não-conformidade"
                }
            },
            "mudanca_comportamental": {
                "nome": "Mudança Comportamental/Demográfica",
                "peso": 4,
                "pergunta": "O tema surfa uma onda social inevitável?",
                "referencia": "Tendências demográficas são imparáveis.",
                "escala": {
                    1: "Nenhuma mudança comportamental relevante",
                    3: "Mudanças sutis e de longo prazo",
                    5: "Tendência clara em formação",
                    7: "Mudança comportamental forte e acelerando",
                    10: "Transformação social massiva e irreversível acontecendo agora"
                }
            },
            "pressao_macroeconomica": {
                "nome": "Pressão Macroeconômica",
                "peso": 4,
                "pergunta": "Crises, inflação ou juros altos tornam a resolução deste problema inadiável por economia de custo?",
                "referencia": "Pressão econômica acelera adoção de eficiência.",
                "escala": {
                    1: "Nenhuma pressão macroeconômica relevante",
                    3: "Pressão econômica indireta",
                    5: "Contexto econômico favorece busca por eficiência",
                    7: "Pressão econômica direta tornando o problema mais agudo",
                    10: "Crise econômica torna a solução questão de sobrevivência"
                }
            },
            "janela_oportunidade": {
                "nome": "Janela de Oportunidade",
                "peso": 4,
                "pergunta": "O mercado está começando a acordar para isso, mas os gigantes ainda são lentos?",
                "referencia": "Marc Andreessen: entre antes que os incumbentes reajam.",
                "escala": {
                    1: "Gigantes já dominam ou mercado não acordou",
                    3: "Mercado muito cedo ou muito tarde",
                    5: "Janela existente mas com competição crescente",
                    7: "Janela clara, incumbentes ainda lentos",
                    10: "Janela perfeita: demanda surgindo, nenhum player relevante posicionado"
                }
            }
        }
    },

    "4_validacao_execucao_lean": {
        "nome": "Validação e Execução Lean",
        "escola_base": "Eric Ries (Lean Startup) e Ash Maurya (Running Lean)",
        "tese": "Se for muito caro, demorado ou impossível validar o problema e a solução inicial, a startup morre antes de nascer.",
        "criterios": {
            "acesso_usuarios": {
                "nome": "Acesso aos Usuários",
                "peso": 5,
                "pergunta": "Os empreendedores conseguem encontrar e falar com quem tem o problema facilmente?",
                "referencia": "Ash Maurya: Canais no Lean Canvas.",
                "escala": {
                    1: "Impossível acessar (ex: generais militares, CEOs de Fortune 500)",
                    3: "Muito difícil, requer conexões especiais",
                    5: "Acessível com esforço moderado",
                    7: "Facilmente acessível online ou em comunidades",
                    10: "Ubíquos, encontráveis em qualquer lugar"
                }
            },
            "velocidade_validacao": {
                "nome": "Velocidade de Validação",
                "peso": 5,
                "pergunta": "É possível testar o interesse no tema em semanas com entrevistas ou landing pages?",
                "referencia": "Lean: valide rápido ou morra lento.",
                "escala": {
                    1: "Validação requer anos e milhões",
                    3: "Meses de estudo e investimento significativo",
                    5: "Validável em 2-3 meses com investimento moderado",
                    7: "Validável em semanas com landing page e entrevistas",
                    10: "Validável em dias com experimentos simples"
                }
            },
            "facilidade_mvp": {
                "nome": "Facilidade de criar o MVP",
                "peso": 4,
                "pergunta": "A primeira versão da solução pode ser feita em no-code ou serviço manual?",
                "referencia": "Eric Ries: Concierge MVP.",
                "escala": {
                    1: "MVP requer P&D de anos e milhões (ex: biotech, hardware complexo)",
                    3: "MVP caro e demorado (6+ meses, equipe especializada)",
                    5: "MVP viável em 2-3 meses com equipe pequena",
                    7: "MVP possível em semanas com no-code/low-code",
                    10: "MVP possível em dias com ferramentas existentes"
                }
            },
            "necessidade_mudanca_habito": {
                "nome": "Necessidade de mudança de hábito",
                "peso": 4,
                "pergunta": "O usuário precisa mudar drasticamente como vive para adotar a solução futura?",
                "referencia": "Nota alta se NÃO precisa mudar hábito.",
                "escala": {
                    1: "Requer mudança radical de comportamento e cultura",
                    3: "Mudança significativa necessária",
                    5: "Alguma adaptação requerida",
                    7: "Mínima mudança de hábito",
                    10: "Zero mudança - se encaixa perfeitamente no fluxo atual"
                }
            },
            "densidade_dados": {
                "nome": "Densidade de dados disponíveis",
                "peso": 3,
                "pergunta": "Já existem dados de mercado, relatórios ou APIs disponíveis para construir em cima?",
                "referencia": "Dados disponíveis aceleram a execução.",
                "escala": {
                    1: "Nenhum dado disponível, precisa criar do zero",
                    3: "Dados escassos e fragmentados",
                    5: "Alguns relatórios e dados parciais disponíveis",
                    7: "Boa quantidade de dados e APIs acessíveis",
                    10: "Abundância de dados, APIs abertas e relatórios detalhados"
                }
            },
            "tempo_aha_moment": {
                "nome": "Tempo de adoção / Aha Moment",
                "peso": 3,
                "pergunta": "Dá para entregar valor nos primeiros minutos de uso?",
                "referencia": "Quanto mais rápido o valor, maior a retenção.",
                "escala": {
                    1: "Meses até perceber valor",
                    3: "Semanas",
                    5: "Dias",
                    7: "Horas",
                    10: "Minutos - valor imediato e óbvio"
                }
            },
            "dependencia_multiplos_lados": {
                "nome": "Dependência de múltiplos lados",
                "peso": 3,
                "pergunta": "O tema exige criar um marketplace complexo logo no dia 1?",
                "referencia": "Problema do ovo e da galinha. Nota alta se NÃO depende.",
                "escala": {
                    1: "Marketplace complexo com 3+ lados necessários desde o dia 1",
                    3: "Dois lados fortemente dependentes",
                    5: "Alguma dependência multi-sided mas contornável",
                    7: "Mínima dependência, pode começar single-sided",
                    10: "Zero dependência, valor entregue diretamente"
                }
            },
            "visibilidade_feedback": {
                "nome": "Visibilidade de feedback",
                "peso": 3,
                "pergunta": "A startup saberá rapidamente se falhou ao tentar resolver o problema?",
                "referencia": "Feedback rápido = iteração rápida.",
                "escala": {
                    1: "Feedback invisível ou leva anos",
                    3: "Feedback lento (meses)",
                    5: "Feedback em semanas",
                    7: "Feedback em dias",
                    10: "Feedback imediato e mensurável"
                }
            }
        }
    },

    "5_monetizacao_viabilidade": {
        "nome": "Monetização e Viabilidade de Negócio",
        "escola_base": "Marty Cagan (Viability Risk) e Sequoia Capital",
        "tese": "Um problema pode ser real, mas se não houver um modelo de negócio viável para capturar valor, é caridade, não startup.",
        "criterios": {
            "disposicao_pagar": {
                "nome": "Disposição a Pagar / WTP",
                "peso": 5,
                "pergunta": "Os clientes têm capacidade financeira e histórico de pagar para resolver dores similares?",
                "referencia": "Marty Cagan: Value Risk.",
                "escala": {
                    1: "Público sem renda ou cultura de pagar por soluções",
                    3: "Baixa disposição, mercado acostumado com gratuito",
                    5: "Disposição moderada, precisa demonstrar ROI claro",
                    7: "Alta disposição, já pagam por soluções similares",
                    10: "Pagam muito e urgentemente por qualquer alívio da dor"
                }
            },
            "clareza_pagador": {
                "nome": "Clareza de quem paga",
                "peso": 5,
                "pergunta": "O usuário final é o pagador, ou depende de publicidade/terceiros?",
                "referencia": "Priorize quando quem sofre a dor é quem paga.",
                "escala": {
                    1: "Modelo depende 100% de publicidade/terceiros",
                    3: "Pagador indireto (governo, seguradora)",
                    5: "Mix entre pagador direto e indireto",
                    7: "Pagador claro, mas precisa de aprovação (ex: departamento de compras)",
                    10: "Quem sofre a dor é exatamente quem paga, sem intermediários"
                }
            },
            "orcamento_preexistente": {
                "nome": "Orçamento pré-existente",
                "peso": 4,
                "pergunta": "As empresas já têm um budget alocado onde essa solução pode entrar?",
                "referencia": "Entrar em orçamento existente é mais fácil que criar novo.",
                "escala": {
                    1: "Nenhum orçamento existente remotamente relacionado",
                    3: "Orçamento tangencial que precisaria ser redirecionado",
                    5: "Orçamento de categoria adjacente",
                    7: "Orçamento claro na categoria certa",
                    10: "Budget obrigatório e crescente na categoria exata"
                }
            },
            "ciclo_vendas": {
                "nome": "Ciclo de Vendas B2B",
                "peso": 3,
                "pergunta": "O tema sugere vendas que demoram 1 mês (ótimo) ou 18 meses (péssimo)?",
                "referencia": "Ciclos longos matam startups iniciantes.",
                "escala": {
                    1: "18+ meses de ciclo de vendas",
                    3: "6-12 meses",
                    5: "3-6 meses",
                    7: "1-3 meses",
                    10: "Self-service ou < 1 mês"
                }
            },
            "frequencia_monetizacao": {
                "nome": "Frequência de monetização",
                "peso": 3,
                "pergunta": "Permite modelo de receita recorrente (SaaS/Assinatura)?",
                "referencia": "Recorrência é o ouro do SaaS.",
                "escala": {
                    1: "Compra única e rara",
                    3: "Compra esporádica",
                    5: "Semi-recorrente (trimestral/semestral)",
                    7: "Recorrente mensal natural",
                    10: "Uso diário com billing recorrente + usage-based"
                }
            },
            "poder_precificacao": {
                "nome": "Poder de precificação",
                "peso": 3,
                "pergunta": "O problema é tão grave que a startup poderá ditar o preço?",
                "referencia": "Inelasticidade de preço = margens altas.",
                "escala": {
                    1: "Commoditizado, preço define a compra",
                    3: "Alguma sensibilidade a preço",
                    5: "Preço moderadamente importante",
                    7: "Valor percebido supera significativamente o custo",
                    10: "Preço é irrelevante diante da dor - inelástico"
                }
            },
            "cac_projetado": {
                "nome": "Custo de Aquisição (CAC) projetado",
                "peso": 3,
                "pergunta": "O tema possui canais orgânicos, virais ou baratos para atrair clientes?",
                "referencia": "CAC baixo = crescimento sustentável.",
                "escala": {
                    1: "Aquisição caríssima, sem canais claros",
                    3: "Canais caros (enterprise sales, eventos)",
                    5: "Mix de canais pagos e orgânicos",
                    7: "Canais orgânicos fortes (SEO, comunidade, boca a boca)",
                    10: "Viralidade natural, produto se vende sozinho"
                }
            }
        }
    },

    "6_defensibilidade_competicao": {
        "nome": "Defensibilidade e Competição",
        "escola_base": "Peter Thiel (Zero to One) e Hamilton Helmer (7 Powers)",
        "tese": "O capitalismo elimina os lucros. O tema precisa permitir que a startup crie fossos competitivos (Moats) ao longo do tempo.",
        "criterios": {
            "ausencia_monopolios": {
                "nome": "Ausência de monopólios estabelecidos",
                "peso": 4,
                "pergunta": "O tema já foi resolvido por Google, Microsoft ou um gigante local muito amado?",
                "referencia": "Peter Thiel: fuja da concorrência extrema.",
                "escala": {
                    1: "Dominado por um gigante com produto excelente",
                    3: "Grandes players com soluções boas",
                    5: "Competição existente mas sem dominância clara",
                    7: "Players existentes mas fracos ou desatualizados",
                    10: "Nenhum player relevante, espaço totalmente aberto"
                }
            },
            "potencial_efeito_rede": {
                "nome": "Potencial de Efeito de Rede",
                "peso": 4,
                "pergunta": "Quanto mais pessoas tiverem o problema resolvido, melhor a solução fica para todos?",
                "referencia": "Helmer: Network Economies.",
                "escala": {
                    1: "Zero efeito de rede possível",
                    3: "Efeito de rede fraco e indireto",
                    5: "Efeito de rede moderado",
                    7: "Efeito de rede forte e direto",
                    10: "Efeito de rede exponencial (ex: marketplace, rede social)"
                }
            },
            "switching_cost": {
                "nome": "Switching Cost futuro",
                "peso": 4,
                "pergunta": "Quem adotar a solução terá muita dificuldade de trocar de fornecedor depois?",
                "referencia": "Helmer: Switching Costs.",
                "escala": {
                    1: "Troca trivial, sem custo",
                    3: "Algum inconveniente na troca",
                    5: "Custo moderado de migração",
                    7: "Migração custosa (dados, treinamento, integração)",
                    10: "Lock-in extremo (dados críticos, integração profunda, retraining)"
                }
            },
            "acumulo_dados_proprietarios": {
                "nome": "Acúmulo de Dados Proprietários",
                "peso": 3,
                "pergunta": "A startup vai criar uma base de dados que ninguém mais tem?",
                "referencia": "Cornered Resource.",
                "escala": {
                    1: "Sem geração de dados proprietários",
                    3: "Dados genéricos facilmente replicáveis",
                    5: "Alguns dados únicos ao longo do tempo",
                    7: "Base de dados proprietária significativa",
                    10: "Data moat único e irreplicável"
                }
            },
            "diferenciacao_10x": {
                "nome": "Diferenciação percebida (10x melhor)",
                "peso": 3,
                "pergunta": "A dor atual é tão mal resolvida que fazer o básico bem feito já parece revolução?",
                "referencia": "Peter Thiel: seja 10x melhor.",
                "escala": {
                    1: "Soluções atuais são excelentes",
                    3: "Soluções atuais são boas",
                    5: "Soluções atuais são medianas",
                    7: "Soluções atuais são ruins",
                    10: "Não existe nada ou o que existe é desastroso"
                }
            },
            "fragmentacao_concorrencia": {
                "nome": "Fragmentação da Concorrência",
                "peso": 2,
                "pergunta": "Existem vários players pequenos e ruins (bom sinal) ou um dominando 80%?",
                "referencia": "Fragmentação = oportunidade de consolidação.",
                "escala": {
                    1: "Um player domina 80%+ do mercado",
                    3: "Poucos players fortes",
                    5: "Mercado moderadamente fragmentado",
                    7: "Muitos players pequenos, nenhum dominante",
                    10: "Extremamente fragmentado, centenas de players ruins"
                }
            }
        }
    },

    "7_riscos_fatais": {
        "nome": "Riscos Fatais (Red Flags)",
        "escola_base": "Y Combinator (Tarpit Ideas)",
        "tese": "Certos temas parecem geniais, mas são armadilhas estruturais.",
        "criterios": {
            "risco_tarpit": {
                "nome": "Risco de Tarpit Idea",
                "peso": 5,
                "pergunta": "Parece uma ideia brilhante mas centenas já tentaram e morreram pelo mesmo motivo estrutural?",
                "referencia": "YC: Armadilha de piche - ideia atraente mas estruturalmente impossível.",
                "escala": {
                    1: "Armadilha clássica conhecida, cemitério de startups",
                    3: "Vários fracassos anteriores por motivos similares",
                    5: "Alguns fracassos mas com causas identificáveis e evitáveis",
                    7: "Poucos tentaram, motivos de fracasso são diferentes",
                    10: "Território novo, sem padrão de fracasso identificável"
                }
            },
            "risco_legal": {
                "nome": "Risco Legal/Regulatório letal",
                "peso": 4,
                "pergunta": "Testar o problema pode dar cadeia ou multas milionárias?",
                "referencia": "Risco legal pode matar a empresa antes de nascer.",
                "escala": {
                    1: "Atividade ilegal ou extremamente regulada (saúde clínica, fintech não autorizada)",
                    3: "Zona cinzenta legal com riscos significativos",
                    5: "Regulação existente mas navegável com compliance",
                    7: "Regulação leve ou favorável",
                    10: "Zero risco regulatório, atividade completamente livre"
                }
            },
            "dependencia_parceiro": {
                "nome": "Dependência Crítica de Parceiro (Platform Risk)",
                "peso": 4,
                "pergunta": "O tema depende 100% de uma mudança de API do Facebook, Apple ou Google?",
                "referencia": "Platform risk pode destruir o negócio da noite para o dia.",
                "escala": {
                    1: "100% dependente de uma plataforma que pode mudar a qualquer momento",
                    3: "Forte dependência de 1-2 plataformas",
                    5: "Alguma dependência mas com alternativas",
                    7: "Mínima dependência de plataformas externas",
                    10: "Completamente independente, stack próprio"
                }
            },
            "alinhamento_ods": {
                "nome": "Alinhamento com ODS e Editais",
                "peso": 3,
                "pergunta": "O tema converge com os ODS e o foco em clima/demografia no Brasil?",
                "referencia": "Alinhamento com ODS facilita acesso a financiamento e editais.",
                "escala": {
                    1: "Nenhum alinhamento com ODS ou agenda climática",
                    3: "Alinhamento tangencial",
                    5: "Alinhamento moderado com 1-2 ODS",
                    7: "Forte alinhamento com ODS prioritários",
                    10: "Perfeitamente alinhado com múltiplos ODS e agenda climática/demográfica"
                }
            }
        }
    }
}


def get_all_criteria():
    """Retorna uma lista plana de todos os critérios com suas categorias."""
    criteria_list = []
    for cat_key, category in SCORING_FRAMEWORK.items():
        for crit_key, criterion in category["criterios"].items():
            criteria_list.append({
                "categoria_key": cat_key,
                "categoria_nome": category["nome"],
                "criterio_key": crit_key,
                "criterio_nome": criterion["nome"],
                "peso": criterion["peso"],
                "pergunta": criterion["pergunta"],
                "referencia": criterion["referencia"]
            })
    return criteria_list


def get_max_possible_score():
    """Calcula a pontuação máxima possível (todos os critérios com nota 10)."""
    total = 0
    for category in SCORING_FRAMEWORK.values():
        for criterion in category["criterios"].values():
            total += criterion["peso"] * SCORE_MAX
    return total


def get_category_max_score(category_key):
    """Calcula a pontuação máxima possível para uma categoria."""
    category = SCORING_FRAMEWORK[category_key]
    total = 0
    for criterion in category["criterios"].values():
        total += criterion["peso"] * SCORE_MAX
    return total


def get_category_names():
    """Retorna os nomes de todas as categorias."""
    return {key: cat["nome"] for key, cat in SCORING_FRAMEWORK.items()}


# Constantes calculadas
TOTAL_CRITERIA = sum(
    len(cat["criterios"]) for cat in SCORING_FRAMEWORK.values()
)
MAX_POSSIBLE_SCORE = get_max_possible_score()

# Template para prompt de avaliação
EVALUATION_PROMPT_TEMPLATE = """Você é um analista especialista em avaliação de oportunidades de negócio e problemas societais.

Analise o seguinte problema usando o framework de avaliação abaixo.

## Problema
**Título:** {problema_titulo}
**Descrição:** {problema_descricao}
**Desenvolvimento:** {problema_desenvolvimento}

## Critério a Avaliar
**Categoria:** {categoria_nome}
**Critério:** {criterio_nome} (Peso: {peso})
**Pergunta-guia:** {pergunta}
**Referência teórica:** {referencia}

## Escala de Avaliação
{escala_formatada}

## Instrução
Baseado na sua análise profunda do problema e no critério acima:
1. Avalie com uma nota de 1 a 10
2. Justifique brevemente a nota (máximo 2 frases)

Responda EXCLUSIVAMENTE no formato:
NOTA: [número de 1 a 10]
JUSTIFICATIVA: [sua justificativa]
"""

ARTICLE_PROMPT_TEMPLATE = """Você é um pesquisador e escritor especialista em análise de problemas societais e oportunidades de negócio.

Escreva um artigo analítico e aprofundado sobre o seguinte problema:

## Problema
**Título:** {problema_titulo}
**Descrição:** {problema_descricao}
**Desenvolvimento:** {problema_desenvolvimento}

## Pontuação do Framework de Avaliação
{pontuacao_formatada}

## Pontuação Total: {pontuacao_total} / {pontuacao_maxima} ({percentual}%)
## Ranking: #{ranking} de {total_problemas}

## Instruções para o Artigo

O artigo deve ter a seguinte estrutura:

### 1. Título Impactante
Um título que capture a essência do problema e sua relevância.

### 2. Resumo Executivo (2-3 parágrafos)
Visão geral do problema, por que importa agora, e a magnitude do impacto.

### 3. Anatomia do Problema
- Raízes históricas e contexto
- Dados e estatísticas que dimensionam o problema
- Quem são os mais afetados (personas)
- Como o problema se manifesta no dia a dia

### 4. Impacto nos Mercados e Setores
- Quais indústrias são diretamente afetadas
- Estimativa de perdas financeiras
- Efeitos em cadeia (consequências secundárias e terciárias)
- Impacto em diferentes geografias

### 5. Análise de Oportunidade de Negócio
- Por que este problema representa uma oportunidade (Why Now)
- Tamanho do mercado endereçável
- Modelos de negócio possíveis
- Exemplos de soluções emergentes ou análogas

### 6. Framework de Avaliação Detalhado
Análise de cada categoria do framework com os scores:
- Natureza da Dor (score e análise)
- Tamanho de Mercado (score e análise)
- Timing (score e análise)
- Validação Lean (score e análise)
- Monetização (score e análise)
- Defensibilidade (score e análise)
- Riscos (score e análise)

### 7. Conexões Societais
- Como aspectos culturais, políticos e sociais influenciam o problema
- Interdependências com outros problemas globais
- Papel de governos, ONGs e setor privado

### 8. Cenários Futuros
- Cenário otimista: o que acontece se o problema for resolvido
- Cenário pessimista: o que acontece se for ignorado
- Cenário mais provável

### 9. Recomendações para Empreendedores
- Primeiros passos para validar uma solução
- Riscos a evitar
- Vantagens competitivas a buscar

### 10. Conclusão
Síntese final conectando o problema às oportunidades.

Escreva o artigo em português brasileiro, com tom analítico mas acessível.
O artigo deve ter entre 2000-3000 palavras.
Use dados e referências quando possível (mesmo que estimados para contextualizar).
"""
