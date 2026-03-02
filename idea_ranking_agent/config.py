"""
Configuração do framework de avaliação de ideias/soluções.

Define as 5 categorias, seus critérios, pesos e o kill filter.
Cada categoria é avaliada com uma nota única (1-10) de forma holística,
considerando todos os sub-critérios — otimizado para performance.

Pesos derivados das especificações YC:
  Cat 1 - Eficácia e Problem-Solution Fit:    23 pontos (5+5+5+4+4)
  Cat 2 - Viabilidade e Risco de Produto:      20 pontos (5+4+4+4+3)
  Cat 3 - Distribuição e Go-to-Market:          16 pontos (5+4+4+3)
  Cat 4 - Modelo de Negócios e Economia:        17 pontos (5+5+4+3)
  Cat 5 - Moats / Fossos Competitivos:          14 pontos (4+4+3+3)
  Total máximo: 900 pontos (90 * 10)
"""

SCORE_MIN = 1
SCORE_MAX = 10

# ============================================================================
# KILL FILTER - Filtro matador de 3 perguntas (pass/fail com score 1-10)
# Ideias que falham (<= 4) em qualquer uma das 3 são rebaixadas.
# ============================================================================

KILL_FILTER = {
    "mvp_semanas": {
        "nome": "MVP em Semanas",
        "pergunta": "Dá para construir a versão 1.0 (MVP) em semanas ao invés de meses/anos?",
        "referencia": "Eric Ries: Concierge MVP. Se precisa de 1 ano de código antes do primeiro teste, é uma red flag massiva.",
        "escala": {
            1: "Precisa de anos de P&D e investimento massivo antes de testar",
            3: "6+ meses de desenvolvimento antes de um teste real",
            5: "2-3 meses para um MVP testável",
            7: "Semanas com low-code/no-code ou processo manual",
            10: "Pode testar amanhã com WhatsApp, planilha ou processo manual",
        },
    },
    "margem_tech": {
        "nome": "Margem de Tecnologia",
        "pergunta": "A margem bruta é de tecnologia (alta, 80-90%) e não de agência/consultoria (baixa, 10-30%)?",
        "referencia": "YC: Software sempre pontua mais que serviço. Margem bruta define se escala sem quebrar.",
        "escala": {
            1: "100% serviço humano, margem de agência (< 20%)",
            3: "Serviço pesado com alguma automação (20-40%)",
            5: "Misto de software e serviço (40-60%)",
            7: "Majoritariamente software com serviço leve (60-80%)",
            10: "Puro software/SaaS, margem 80-90%+",
        },
    },
    "distribuicao_escalavel": {
        "nome": "Distribuição Escalável",
        "pergunta": "A forma de distribuição é escalável (cresce sem precisar multiplicar vendedores/operadores)?",
        "referencia": "O maior cemitério de boas soluções é a falta de distribuição. Venda porta a porta não escala.",
        "escala": {
            1: "100% venda consultiva de porta em porta, sem canais digitais",
            3: "Vendas outbound manuais, equipe de vendas necessária para cada deal",
            5: "Mix de canais, parcialmente escalável",
            7: "Canais digitais fortes (Inbound, Ads, Parcerias), pouca venda manual",
            10: "PLG puro, viralidade embutida, self-service completo",
        },
    },
}

# ============================================================================
# FRAMEWORK DE 5 CATEGORIAS
# Cada categoria agrupa múltiplos critérios avaliados holisticamente.
# ============================================================================

SCORING_FRAMEWORK = {
    "1_eficacia_psf": {
        "nome": "Eficácia e Problem-Solution Fit",
        "peso_total": 23,
        "tese": (
            "Julgamos se a ideia proposta é apenas 'legal' ou se realmente "
            "aniquila o problema definido. Ideias com melhorias marginais de "
            "10-20% não fazem os usuários mudarem de hábito."
        ),
        "criterios": [
            {
                "id": "regra_10x",
                "nome": "A Regra do 10x",
                "peso": 5,
                "pergunta": (
                    "A ideia proposta é 10x mais rápida, 10x mais barata ou "
                    "10x melhor do que a gambiarra ou solução atual?"
                ),
            },
            {
                "id": "simplicidade_proposta",
                "nome": "Simplicidade da Proposta de Valor",
                "peso": 5,
                "pergunta": (
                    "A mecânica da solução pode ser explicada em uma frase "
                    "simples? (ex: 'Apertar um botão e chamar um carro')"
                ),
            },
            {
                "id": "caminho_direto_dor",
                "nome": "Caminho Direto para a Dor",
                "peso": 5,
                "pergunta": (
                    "A ideia resolve o problema primário imediatamente ou exige "
                    "que o usuário use várias features periféricas antes de sentir valor?"
                ),
            },
            {
                "id": "alinhamento_frequencia",
                "nome": "Alinhamento de Frequência",
                "peso": 4,
                "pergunta": (
                    "A solução propõe um uso que bate com a frequência do problema? "
                    "(Se diário, solução diária; se anual, solução automatizada)"
                ),
            },
            {
                "id": "foco_beachhead",
                "nome": "Foco no Beachhead (Caso de uso inicial)",
                "peso": 4,
                "pergunta": (
                    "A ideia é um bisturi focado em 1 caso de uso ou um "
                    "canivete suíço que tenta fazer tudo para todos?"
                ),
            },
        ],
    },
    "2_viabilidade_risco": {
        "nome": "Viabilidade e Risco de Produto",
        "peso_total": 20,
        "tese": (
            "Avaliamos se é possível construir isso sem precisar da NASA "
            "ou de orçamentos bilionários."
        ),
        "criterios": [
            {
                "id": "time_to_mvp",
                "nome": "Time-to-MVP / Esforço Inicial",
                "peso": 5,
                "pergunta": (
                    "O MVP pode ser testado amanhã usando No-Code, WhatsApp ou "
                    "processos manuais (Concierge)?"
                ),
            },
            {
                "id": "risco_tecnologico",
                "nome": "Risco Tecnológico (Miracle Risk)",
                "peso": 4,
                "pergunta": (
                    "A ideia usa tecnologia acessível (APIs de IA, SaaS) ou "
                    "exige invenção científica (fusão nuclear, hardware inédito)?"
                ),
            },
            {
                "id": "friccao_onboarding",
                "nome": "Fricção de Onboarding",
                "peso": 4,
                "pergunta": (
                    "Quão difícil é para o usuário começar a usar? Exige "
                    "integração de TI, meses de treinamento ou hardware?"
                ),
            },
            {
                "id": "risco_plataforma",
                "nome": "Risco de Dependência de Plataforma",
                "peso": 4,
                "pergunta": (
                    "A solução funciona sozinha ou morre se Apple, Google ou "
                    "WhatsApp mudarem as regras de suas APIs?"
                ),
            },
            {
                "id": "risco_regulatorio",
                "nome": "Risco Regulatório da Solução",
                "peso": 3,
                "pergunta": (
                    "Essa solução esbarra em leis rigorosas? (ex: prescrever "
                    "remédios via IA, intermediar valores sem licença do BC)"
                ),
            },
        ],
    },
    "3_distribuicao_gtm": {
        "nome": "Distribuição e Go-to-Market",
        "peso_total": 16,
        "tese": (
            "O maior cemitério de boas soluções é a falta de distribuição. "
            "Como essa solução chega nas mãos de milhões?"
        ),
        "criterios": [
            {
                "id": "vetor_crescimento",
                "nome": "Vetor de Crescimento Embutido (PLG/Viralidade)",
                "peso": 5,
                "pergunta": (
                    "A própria mecânica do produto traz novos usuários? "
                    "(Ex: Zoom/Calendly/Pix — para usar comigo, você precisa conhecer)"
                ),
            },
            {
                "id": "escalabilidade_canal",
                "nome": "Escalabilidade do Canal de Aquisição",
                "peso": 4,
                "pergunta": (
                    "A ideia se apoia em canais escaláveis (Inbound, Ads, Parcerias) "
                    "ou depende de vendas porta a porta?"
                ),
            },
            {
                "id": "acesso_decisor",
                "nome": "Clareza de Acesso ao Decisor (B2B)",
                "peso": 4,
                "pergunta": (
                    "Se B2B, mira no funcionário que sofre a dor (fácil) ou "
                    "no CEO/Diretoria (ciclo de 12 meses)?"
                ),
            },
            {
                "id": "barreira_teste",
                "nome": "Barreira ao Teste",
                "peso": 3,
                "pergunta": (
                    "Permite freemium ou teste grátis (self-service), ou o "
                    "cliente precisa assinar contrato às cegas?"
                ),
            },
        ],
    },
    "4_modelo_negocio": {
        "nome": "Modelo de Negócios e Economia Unitária",
        "peso_total": 17,
        "tese": (
            "Se o produto for de graça, o mundo todo usa. Mas como essa "
            "solução fecha a conta?"
        ),
        "criterios": [
            {
                "id": "margem_bruta",
                "nome": "Margem Bruta Potencial",
                "peso": 5,
                "pergunta": (
                    "Baseada em software/código (margem 80-90%) ou envolve "
                    "humanos/logística (margem 10-30%)?"
                ),
            },
            {
                "id": "receita_recorrente",
                "nome": "Modelo de Receita Recorrente",
                "peso": 5,
                "pergunta": (
                    "Permite cobrar assinaturas mensais/anuais (SaaS) ou "
                    "depende de vendas transacionais (matar leão por dia)?"
                ),
            },
            {
                "id": "unit_economics",
                "nome": "Custo de Servir vs. Disposição a Pagar",
                "peso": 4,
                "pergunta": (
                    "O custo de entregar para 1 cliente é esmagado pelo "
                    "valor que ele aceita pagar? A matemática básica fica de pé?"
                ),
            },
            {
                "id": "ciclo_recebimento",
                "nome": "Ciclo de Recebimento (Working Capital)",
                "peso": 3,
                "pergunta": (
                    "Cobra do cliente antes de entregar valor (ótimo) ou "
                    "paga fornecedores meses antes de receber (péssimo)?"
                ),
            },
        ],
    },
    "5_moats": {
        "nome": "Moats / Fossos Competitivos",
        "peso_total": 14,
        "tese": (
            "Se a ideia for um sucesso absoluto, o que impede a concorrência "
            "de copiar em 3 meses?"
        ),
        "criterios": [
            {
                "id": "efeitos_rede",
                "nome": "Efeitos de Rede Locais ou Globais",
                "peso": 4,
                "pergunta": (
                    "A solução fica melhor para o usuário A toda vez que o "
                    "usuário B entra? (Ex: Uber, Airbnb, Marketplaces)"
                ),
            },
            {
                "id": "lock_in",
                "nome": "Lock-in / Custo de Mudança",
                "peso": 4,
                "pergunta": (
                    "Depois que implementa, seria um pesadelo trocar por "
                    "concorrente (integração profunda, sistema de registro)?"
                ),
            },
            {
                "id": "data_moat",
                "nome": "Acúmulo de Dados Proprietários (Data Moat)",
                "peso": 3,
                "pergunta": (
                    "O uso contínuo treina IA ou cria base de dados impossível "
                    "de ser alcançada por novatos?"
                ),
            },
            {
                "id": "economia_escala",
                "nome": "Economia de Escala",
                "peso": 3,
                "pergunta": (
                    "Conforme cresce, o custo unitário cai tanto que pode "
                    "esmagar concorrentes no preço sem perder dinheiro?"
                ),
            },
        ],
    },
}

# ============================================================================
# CONSTANTES DERIVADAS
# ============================================================================

TOTAL_PESO = sum(cat["peso_total"] for cat in SCORING_FRAMEWORK.values())  # 90
MAX_POSSIBLE_SCORE = TOTAL_PESO * SCORE_MAX  # 900
KILL_FILTER_THRESHOLD = 4  # Nota <= 4 em qualquer kill filter = rebaixamento
KILL_FILTER_PENALTY = 0.7  # Multiplica score total por 70% se falhar no kill filter

# ============================================================================
# TEMPLATES DE PROMPT
# ============================================================================

KILL_FILTER_PROMPT = """Você é um avaliador de ideias de startup no padrão Y Combinator.

## Ideia a Avaliar
**Ideia:** {ideia_titulo}
**Descrição:** {ideia_descricao}
**Problema que resolve:** {problema}

## Filtro Rápido - 3 Perguntas Matadoras
Avalie cada uma das 3 perguntas com uma nota de 1 a 10.

### 1. MVP em Semanas
{kf_mvp_pergunta}
Escala: 1=Anos de P&D | 5=2-3 meses | 10=Pode testar amanhã

### 2. Margem de Tecnologia
{kf_margem_pergunta}
Escala: 1=100% serviço humano | 5=Misto | 10=Puro SaaS (80-90%)

### 3. Distribuição Escalável
{kf_dist_pergunta}
Escala: 1=Venda porta a porta | 5=Mix de canais | 10=PLG/viralidade pura

Responda EXCLUSIVAMENTE neste formato (3 linhas):
MVP: [nota]
MARGEM: [nota]
DISTRIBUICAO: [nota]
"""

CATEGORY_EVAL_PROMPT = """Você é um avaliador de ideias de startup no padrão Y Combinator.
Avalie a ideia abaixo na categoria específica de forma holística.

## Ideia
**Ideia:** {ideia_titulo}
**Descrição:** {ideia_descricao}
**Problema que resolve:** {problema}

## Categoria: {categoria_nome}
**Tese:** {categoria_tese}

## Critérios a considerar (avalie holisticamente, uma nota única):
{criterios_formatados}

Dê uma nota de 1 a 10 para esta categoria como um todo, onde:
- 1-2: Péssimo, a ideia falha gravemente nesta dimensão
- 3-4: Fraco, problemas significativos
- 5-6: Mediano, nem bom nem ruim
- 7-8: Bom, ideia forte nesta dimensão
- 9-10: Excelente, ideia excepcional nesta dimensão

Responda EXCLUSIVAMENTE no formato:
NOTA: [número de 1 a 10]
RAZAO: [máximo 2 frases justificando]
"""


def get_category_weight(cat_key: str) -> int:
    """Retorna o peso total de uma categoria."""
    return SCORING_FRAMEWORK[cat_key]["peso_total"]


def get_category_names() -> dict:
    """Retorna {key: nome} de todas as categorias."""
    return {k: v["nome"] for k, v in SCORING_FRAMEWORK.items()}


def format_criterios_for_prompt(cat_key: str) -> str:
    """Formata os critérios de uma categoria para o prompt LLM."""
    cat = SCORING_FRAMEWORK[cat_key]
    lines = []
    for c in cat["criterios"]:
        lines.append(f"- **{c['nome']}** (Peso {c['peso']}): {c['pergunta']}")
    return "\n".join(lines)
