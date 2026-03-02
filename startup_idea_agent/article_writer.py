"""
Motor de Geração de Artigos para Ideias de Startup

Gera artigos concisos (máx 2 páginas em texto corrido) que cobrem:
- Problem-Solution Fit e Regra do 10x
- Viabilidade e MVP
- Distribuição e Go-to-Market
- Modelo de Negócios e Economia Unitária
- Moats e Defensibilidade
- Concorrentes e Features
- Business Model Canvas (narrativo)
- Estratégia de Vendas
- MVP detalhado
"""

from .config import ARTICLE_PROMPT_TEMPLATE, get_max_possible_score
from .scoring import IdeaScore


class IdeaArticleWriter:
    """Gerador de artigos concisos sobre ideias de startup."""

    def __init__(self, llm_writer=None):
        """
        Args:
            llm_writer: Função que recebe um prompt e retorna o artigo gerado.
                       Assinatura: (prompt: str) -> str
        """
        self.llm_writer = llm_writer

    def gerar_artigo(self, idea_score: IdeaScore) -> str:
        """Gera um artigo completo para uma ideia avaliada."""
        pontuacao_formatada = self._formatar_pontuacao_para_artigo(idea_score)

        prompt = ARTICLE_PROMPT_TEMPLATE.format(
            problema_titulo=idea_score.problema_titulo,
            problema_descricao=idea_score.problema_descricao,
            ideia_descricao=idea_score.ideia_descricao,
            pontuacao_formatada=pontuacao_formatada,
            pontuacao_total=f"{idea_score.pontuacao_total:.0f}",
            pontuacao_maxima=f"{idea_score.pontuacao_maxima:.0f}",
            percentual=f"{idea_score.percentual:.1f}",
        )

        if self.llm_writer:
            artigo = self.llm_writer(prompt)
        else:
            artigo = self._gerar_artigo_template(idea_score)

        return artigo

    def _formatar_pontuacao_para_artigo(self, idea_score: IdeaScore) -> str:
        """Formata a pontuação para incluir no prompt de geração do artigo."""
        lines = []
        for cat_key, cat_score in idea_score.categorias.items():
            lines.append(
                f"\n**{cat_score.categoria_nome}** — "
                f"{cat_score.pontuacao_obtida:.0f}/{cat_score.pontuacao_maxima:.0f} "
                f"({cat_score.percentual:.1f}%)"
            )
            for crit in cat_score.criterios:
                lines.append(
                    f"  - {crit.criterio_nome}: {crit.nota}/10 "
                    f"(peso {crit.peso}) → {crit.justificativa}"
                )
        return "\n".join(lines)

    def _gerar_artigo_template(self, s: IdeaScore) -> str:
        """Gera um artigo usando template quando não há LLM disponível."""
        # Classifica a ideia
        if s.percentual >= 75:
            classificacao = "EXCELENTE"
        elif s.percentual >= 60:
            classificacao = "PROMISSORA"
        elif s.percentual >= 45:
            classificacao = "MODERADA"
        else:
            classificacao = "DESAFIADORA"

        # Coleta melhores e piores categorias
        cats_sorted = sorted(
            s.categorias.values(), key=lambda c: c.percentual, reverse=True
        )
        melhor_cat = cats_sorted[0] if cats_sorted else None
        pior_cat = cats_sorted[-1] if cats_sorted else None

        # Coleta critérios
        todos_criterios = []
        for cat in s.categorias.values():
            todos_criterios.extend(cat.criterios)
        criterios_sorted = sorted(
            todos_criterios, key=lambda c: c.nota_ponderada, reverse=True
        )
        top_3 = criterios_sorted[:3]
        bottom_3 = criterios_sorted[-3:]

        # Helper: extrai nota de um critério específico
        def nota_de(criterio_key):
            for c in todos_criterios:
                if c.criterio_key == criterio_key:
                    return c.nota, c.justificativa
            return 5, ""

        # --- Monta o artigo em texto corrido ---
        nome = s.ideia_nome or "a startup proposta"
        tagline = f' — "{s.ideia_tagline}"' if s.ideia_tagline else ""

        artigo = f"{nome.upper()}{tagline}\n\n"

        # Parágrafo 1: Abertura — Problema e Ideia
        artigo += (
            f'O problema "{s.problema_titulo}" afeta diretamente a vida e a produtividade '
            f"de milhões de pessoas e empresas. {s.problema_descricao} "
            f"Diante dessa dor, surge {nome}, uma proposta de startup que busca "
            f"transformar este cenário de forma radical. {s.ideia_descricao}\n\n"
        )

        # Parágrafo 2: Problem-Solution Fit
        n10x, j10x = nota_de("regra_10x")
        nsimp, jsimp = nota_de("simplicidade_proposta_valor")
        ndor, jdor = nota_de("caminho_direto_dor")
        nfoco, jfoco = nota_de("foco_beachhead")

        fit_cat = s.categorias.get("1_eficacia_problem_solution_fit")
        fit_pct = f"{fit_cat.percentual:.0f}%" if fit_cat else "N/A"

        artigo += (
            f"No quesito de Problem-Solution Fit, avaliado em {fit_pct} pelo framework, "
            f"a solução "
        )
        if n10x >= 7:
            artigo += (
                f"demonstra potencial de melhoria 10x em relação às alternativas atuais. "
                f"{j10x} "
            )
        elif n10x >= 5:
            artigo += (
                f"oferece uma melhoria significativa sobre o status quo, embora não "
                f"chegue ao patamar de 10x em todos os aspectos. "
            )
        else:
            artigo += (
                f"apresenta melhorias incrementais que, embora úteis, podem não ser "
                f"suficientes para forçar a mudança de hábito dos usuários. "
            )

        if nsimp >= 7:
            artigo += (
                f"A proposta de valor é clara e comunicável em uma frase, o que facilita "
                f"enormemente a venda e adoção. "
            )
        else:
            artigo += (
                f"A proposta de valor requer algum esforço para ser comunicada, "
                f"o que pode ser um obstáculo na aquisição inicial. "
            )

        if ndor >= 7:
            artigo += (
                f"O caminho até o valor é direto — o usuário sente alívio da dor principal "
                f"nos primeiros momentos de uso. "
            )

        if nfoco >= 7:
            artigo += (
                f"O foco em um único beachhead bem definido é um dos pontos fortes: "
                f"ao invés de ser um canivete suíço, a solução ataca cirurgicamente "
                f"um caso de uso específico antes de expandir.\n\n"
            )
        else:
            artigo += "\n\n"

        # Parágrafo 3: Viabilidade e MVP
        nmvp, jmvp = nota_de("time_to_mvp")
        ntech, jtech = nota_de("risco_tecnologico")
        nonb, jonb = nota_de("friccao_onboarding")
        nreg, jreg = nota_de("risco_regulatorio_solucao")

        viab_cat = s.categorias.get("2_viabilidade_risco_produto")
        viab_pct = f"{viab_cat.percentual:.0f}%" if viab_cat else "N/A"

        artigo += (
            f"Em termos de viabilidade ({viab_pct} no framework), "
        )
        if nmvp >= 7:
            artigo += (
                f"o MVP pode ser construído em questão de dias ou semanas usando "
                f"ferramentas no-code, processos manuais ou Concierge. {jmvp} "
            )
        elif nmvp >= 5:
            artigo += (
                f"o MVP requer um esforço moderado de 1-2 meses, mas é perfeitamente "
                f"executável por uma equipe enxuta. "
            )
        else:
            artigo += (
                f"o desenvolvimento do MVP é um dos maiores riscos, exigindo meses "
                f"de trabalho técnico antes do primeiro teste real com usuários. "
            )

        if ntech >= 7:
            artigo += (
                f"O risco tecnológico é baixo: toda a stack necessária já existe e "
                f"é acessível via APIs e SaaS. "
            )
        elif ntech <= 3:
            artigo += (
                f"Há risco tecnológico relevante que precisa ser mitigado — a solução "
                f"depende de tecnologias ainda imaturas ou complexas. "
            )

        if nreg <= 4:
            artigo += (
                f"Atenção especial ao risco regulatório: {jreg} "
                f"É essencial validar a conformidade legal antes de escalar. "
            )

        artigo += "\n\n"

        # Parágrafo 4: Distribuição e Go-to-Market
        nviral, jviral = nota_de("vetor_crescimento_embutido")
        ncanal, jcanal = nota_de("escalabilidade_canal_aquisicao")
        ndecis, jdecis = nota_de("clareza_acesso_decisor")
        nteste, jteste = nota_de("barreira_ao_teste")

        dist_cat = s.categorias.get("3_distribuicao_go_to_market")
        dist_pct = f"{dist_cat.percentual:.0f}%" if dist_cat else "N/A"

        artigo += (
            f"A distribuição, avaliada em {dist_pct}, é onde muitas boas ideias morrem. "
        )
        if nviral >= 7:
            artigo += (
                f"Neste caso, a mecânica do produto tem viralidade embutida — o próprio "
                f"uso traz novos usuários naturalmente. {jviral} "
            )
        elif nviral >= 5:
            artigo += (
                f"Há algum potencial viral, embora não seja uma viralidade intrínseca "
                f"obrigatória como a de produtos tipo Zoom ou Pix. "
            )
        else:
            artigo += (
                f"A falta de viralidade embutida significa que cada novo usuário "
                f"precisará ser adquirido individualmente, o que aumenta o CAC. "
            )

        if ndecis >= 7:
            artigo += (
                f"O acesso ao decisor é facilitado pela estratégia bottom-up, onde "
                f"o próprio usuário final adota a solução sem necessidade de aprovação "
                f"da diretoria. "
            )

        if nteste >= 7:
            artigo += (
                f"A barreira ao teste é mínima, com modelo freemium ou trial que permite "
                f"ao usuário experimentar sem compromisso. "
            )

        artigo += (
            f"Para os primeiros 100 clientes, a estratégia deve ser intensamente manual "
            f"— abordagem direta nas comunidades onde a persona vive, demonstrações "
            f"personalizadas e onboarding white-glove. Após validar o product-market fit, "
            f"os canais escaláveis (content marketing, SEO, parcerias e ads) assumem "
            f"o crescimento.\n\n"
        )

        # Parágrafo 5: Modelo de Negócio e Economia
        nmargem, jmargem = nota_de("margem_bruta_potencial")
        nrecorr, jrecorr = nota_de("modelo_receita_recorrente")
        ncusto, jcusto = nota_de("custo_servir_vs_wtp")
        ncaixa, jcaixa = nota_de("ciclo_recebimento")

        model_cat = s.categorias.get("4_modelo_negocios_economia_unitaria")
        model_pct = f"{model_cat.percentual:.0f}%" if model_cat else "N/A"

        artigo += (
            f"O modelo de negócios ({model_pct} no framework) "
        )
        if nmargem >= 7:
            artigo += (
                f"se beneficia de margens brutas altas típicas de software, onde o custo "
                f"marginal de servir um novo cliente é próximo de zero. "
            )
        elif nmargem >= 5:
            artigo += (
                f"apresenta margens mistas — há componentes de software com margens "
                f"altas, mas também elementos de serviço que comprimem a rentabilidade. "
            )
        else:
            artigo += (
                f"tem margens pressionadas pela necessidade de mão-de-obra ou logística "
                f"física, o que é um ponto de atenção para investidores. "
            )

        if nrecorr >= 7:
            artigo += (
                f"A receita recorrente via assinatura (SaaS) é o coração do modelo, "
                f"proporcionando previsibilidade e valuations mais altos. "
            )
        elif nrecorr >= 5:
            artigo += (
                f"Há componentes de recorrência, embora o modelo não seja 100% SaaS. "
            )
        else:
            artigo += (
                f"A dependência de receita transacional é um risco — cada mês é uma "
                f"nova conquista. Converter para recorrência deve ser prioridade. "
            )

        if ncusto >= 7:
            artigo += (
                f"A matemática unitária é favorável: o custo de servir é significativamente "
                f"menor que a disposição a pagar do cliente. "
            )

        artigo += (
            f"Em termos de Business Model Canvas narrativo: o segmento de clientes "
            f"é claramente definido pela persona que sofre a dor; a proposta de valor "
            f"é a eliminação dessa dor de forma direta; os canais são digitais e "
            f"escaláveis; o relacionamento começa self-service e evolui para sucesso "
            f"do cliente nos planos pagos; as fontes de receita são assinaturas com "
            f"tiers progressivos; os recursos-chave são a plataforma tecnológica e "
            f"a base de dados construída com o uso; as atividades-chave são "
            f"desenvolvimento de produto e aquisição de clientes; parceiros "
            f"estratégicos incluem integrações com ferramentas já usadas pelo público-alvo; "
            f"e a estrutura de custos é dominada por infraestrutura cloud e equipe "
            f"de engenharia.\n\n"
        )

        # Parágrafo 6: Moats e Defensibilidade
        nrede, jrede = nota_de("efeitos_de_rede")
        nlock, jlock = nota_de("lockin_custo_mudanca")
        ndados, jdados = nota_de("acumulo_dados_proprietarios")
        nescala, jescala = nota_de("economia_de_escala")

        moat_cat = s.categorias.get("5_moats_defensibilidade")
        moat_pct = f"{moat_cat.percentual:.0f}%" if moat_cat else "N/A"

        artigo += (
            f"A defensibilidade ({moat_pct}) determina se o sucesso será duradouro "
            f"ou efêmero. "
        )
        if nrede >= 7:
            artigo += (
                f"A presença de efeitos de rede fortes é o fosso mais poderoso: cada "
                f"novo usuário torna o produto melhor para todos os outros. "
            )
        elif nrede >= 5:
            artigo += (
                f"Há potencial para efeitos de rede moderados que, se cultivados "
                f"intencionalmente, podem se tornar um fosso relevante. "
            )

        if nlock >= 7:
            artigo += (
                f"O custo de mudança é alto — uma vez integrado aos processos do "
                f"cliente, a troca se torna custosa e arriscada. "
            )

        if ndados >= 7:
            artigo += (
                f"O acúmulo de dados proprietários cria um data moat que se torna "
                f"mais intransponível a cada dia de uso. "
            )

        if nescala >= 7:
            artigo += (
                f"As economias de escala permitem reduzir custos unitários conforme "
                f"cresce, potencialmente esmagando concorrentes no preço. "
            )

        artigo += "\n\n"

        # Parágrafo 7: Concorrentes
        artigo += (
            f"Em relação ao cenário competitivo, é provável que existam soluções "
            f"parciais tentando resolver aspectos deste problema. As principais "
            f"deficiências dos concorrentes atuais tendem a ser: fragmentação "
            f"(cada um resolve um pedaço), complexidade excessiva (ferramentas "
            f"genéricas adaptadas sem foco), e falta de integração ao fluxo "
            f"natural de trabalho do usuário. A oportunidade de {nome} está em "
            f"consolidar a solução em uma experiência única, focada e 10x melhor "
            f"no caso de uso principal.\n\n"
        )

        # Parágrafo 8: MVP
        artigo += (
            f"O MVP deve ser a versão mais enxuta possível que entrega o core value. "
        )
        if nmvp >= 7:
            artigo += (
                f"Nas primeiras duas semanas, é possível validar a hipótese central "
                f"usando ferramentas existentes — um formulário, um fluxo no WhatsApp, "
                f"uma planilha conectada, ou até um serviço manual (Concierge) que "
                f"simula o que o software fará. O objetivo não é construir tecnologia, "
                f"é provar que a dor existe e que os usuários pagam para resolvê-la. "
            )
        else:
            artigo += (
                f"Embora o MVP requeira mais investimento técnico neste caso, "
                f"é crucial resistir à tentação de construir demais antes de validar. "
                f"A primeira versão deve entregar apenas o caso de uso #1 para a "
                f"persona #1, usando o mínimo de tecnologia necessária. "
            )

        artigo += (
            f"Após a validação inicial com 10-20 usuários pagantes, a iteração "
            f"deve ser guiada por feedback direto, evoluindo do concierge para "
            f"automação gradual.\n\n"
        )

        # Conclusão
        artigo += (
            f"Em síntese, esta ideia de startup foi avaliada como {classificacao} "
            f"({s.percentual:.1f}% no framework de 5 categorias e 22 critérios). "
        )
        if melhor_cat:
            artigo += (
                f"Seu maior trunfo está em {melhor_cat.categoria_nome} "
                f"({melhor_cat.percentual:.0f}%). "
            )
        if pior_cat and pior_cat != melhor_cat:
            artigo += (
                f"O principal desafio reside em {pior_cat.categoria_nome} "
                f"({pior_cat.percentual:.0f}%), onde melhorias serão necessárias "
                f"para maximizar as chances de sucesso. "
            )
        artigo += (
            f"O próximo passo é claro: validar com 5 potenciais clientes esta semana, "
            f"cobrar pelo MVP na semana seguinte, e iterar ferozmente a partir do "
            f"feedback real."
        )

        return artigo
