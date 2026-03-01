# Estado Regulador e Infraestrutura de Confiança: IA, Privacidade, Antitruste e Moedas Digitais

## 1. Visão geral

A combinação de inovação autônoma em IA generativa, dados e finanças digitais com um vácuo legislativo parcial está produzindo uma crise de autenticidade (deepfakes, golpes, desinformação) e de confiança em mercados digitais. Em resposta, EUA, União Europeia e Brasil avançam de forma assimétrica, combinando novas leis setoriais, uso agressivo de regulações já existentes e o surgimento de uma camada técnico‑institucional de “infraestrutura de confiança” (watermarking, proveniência, auditoria, supervisão ex ante).[^1][^2][^3][^4][^5][^6][^7]

A tabela abaixo sintetiza a posição relativa de cada jurisdição nos quatro eixos pedidos (IA, privacidade, antitruste, moedas digitais), com foco em mecanismos de confiança.

| Eixo / Jurisdição | União Europeia | Estados Unidos | Brasil |
|-------------------|----------------|----------------|--------|
| IA                | AI Act com regime de risco e obrigações de transparência para deepfakes e conteúdo sintético.[^1][^8][^7] | Ordem Executiva 14110 (Biden) focada em segurança, watermarking e reporte de grandes modelos; posteriormente tensionada por diretrizes pró-inovação no governo seguinte.[^9][^2][^10] | PL 2338/2023 aprovado no Senado, inspirado no AI Act, com classificação por risco e criação de sistema nacional de governança de IA.[^11][^12][^13] |
| Privacidade       | GDPR como espinha dorsal, complementado por DSA, Data Act e supervisores fortes.[^14][^15][^16] | Ausência de lei federal abrangente; mosaico de leis estaduais de privacidade e enforcement setorial.[^17][^18][^19][^20] | LGPD e ANPD como base robusta, com integração crescente com normas de IA e Drex.[^21][^22][^12][^23] |
| Antitruste / Plataformas | DMA e investigações antitruste específicas em IA, nuvem e modelos fundacionais (Meta, Google, AWS, Azure).[^24][^25][^26][^27] | FTC/DOJ usam antitruste tradicional, dividem supervisão de IA e anunciam enforcement “urgente” em chips, nuvem, modelos e parcerias.[^28][^29][^30] | CADE caminha para modelo ex ante “à la DMA” mais flexível, focando plataformas sistêmicas e nuvem.[^31][^32][^33] |
| Moedas digitais / cripto | MiCA como regime unificado para cripto e stablecoins, com foco em estabilidade e proteção do investidor.[^34][^35][^36][^37] | Estrutura em construção via projetos como Clarity for Payment Stablecoins Act e debates sobre riscos sistêmicos.[^38][^39][^40] | Drex (CBDC) em piloto com forte ênfase em supervisão, AML/KYC, privacidade e integração com arcabouço financeiro existente.[^41][^23][^42]

## 2. Conceito de “Estado regulador” e “infraestrutura de confiança”

Desde a década passada, o Estado em economias digitais avançadas desloca-se de um papel predominantemente ex post (punir abusos) para um papel combinando regulação ex ante, supervisão contínua e desenho de infraestrutura de mercado (padrões, protocolos, certificações) que condiciona a inovação. Em IA e ativos digitais, isso aparece em regimes de licenciamento e autorização (AI Act, MiCA, Drex), códigos de conduta vinculados à lei e sistemas técnicos padronizados para autenticação de conteúdo.[^24][^43][^34][^41][^7][^31][^1]

“Infraestrutura de confiança” pode ser entendida como o conjunto de leis, reguladores, padrões técnicos, mecanismos de auditoria e obrigações de transparência que tornam verificáveis a origem de dados, o comportamento de sistemas algorítmicos e a solidez de ativos digitais. Em um contexto de deepfakes corporativos e fraudes em escala (crescimentos de centenas a milhares por cento ano a ano), essa infraestrutura passa de opcional a condição de funcionamento de mercados e da própria democracia.[^3][^4][^23][^5][^6][^7]

## 3. União Europeia

### 3.1. Regulação de IA e crise de autenticidade

O AI Act estabelece o primeiro regime horizontal e vinculante de IA do mundo, baseado em classificação por risco (proibição de usos de “risco excessivo”, obrigações pesadas para sistemas de alto risco e requisitos de transparência para sistemas de risco limitado). O artigo 50 trata especificamente de transparência para sistemas que geram conteúdo sintético (incluindo deepfakes), exigindo marcação legível por máquina pelo provedor e rotulagem explícita pelo deployer quando imagens, áudios ou vídeos podem ser confundidos com conteúdo real.[^44][^45][^8][^7][^1]

Para operacionalizar essas normas, a Comissão Europeia publicou o rascunho de um Código de Prática em Transparência para Conteúdo Gerado por IA, que detalha medidas de rotulagem, watermarking, metadados e um possível “ícone comum” europeu para identificar deepfakes. O código busca orientar tanto provedores de modelos quanto plataformas sob o DSA, articulando marcações técnicas no nível do conteúdo com rótulos de interface e processos de detecção.[^46][^47][^48][^7][^16]

### 3.2. Privacidade e proteção de dados

O GDPR, em vigor desde 2018, permanece como pedra angular da proteção de dados na Europa, impondo princípios de minimização, propósito específico, segurança e accountability, com multas de até 20 milhões de euros ou 4% do faturamento global. O regulamento tem aplicação extraterritorial e exige que controladores e processadores embutam proteção de dados “by design and by default” em novos produtos, o que se estende a sistemas de IA.[^14][^15]

As regras de privacidade se articulam com o DSA e com o futuro Data Act, que regulam o uso de dados por plataformas, a portabilidade e a transparência de sistemas de recomendação, incluindo aqueles baseados em IA. Supervisores como o European Data Protection Board e autoridades nacionais atuam em conjunto com órgãos de concorrência e com a Comissão para garantir coerência na aplicação desse “livro de regras digital”.[^43][^16][^24]

### 3.3. Antitruste, DMA e IA

O Digital Markets Act (DMA) cria um regime ex ante para “gatekeepers” – hoje 23 serviços centrais oferecidos por grupos como Alphabet, Amazon, Apple, ByteDance, Meta, Microsoft e Booking – impondo obrigações de interoperabilidade, proibição de auto‑preferência e limites ao uso de dados combinados. Em 2024, o High‑Level Group do DMA explicitou que o uso de IA em serviços de gatekeepers (assistentes, chatbots, busca generativa) deve obedecer às mesmas obrigações, e que nuvem e AI estão no centro da agenda de revisão do DMA.[^49][^25][^24][^43]

Paralelamente, a Comissão abriu uma série de investigações antitruste em serviços de IA e nuvem, incluindo Google (uso de conteúdo de publishers e YouTube em modelos de IA) e Meta (integração de assistentes de IA em WhatsApp e possíveis bloqueios a rivais), com base no artigo 102 do TFUE. Há também investigações sob o DMA focadas em serviços de nuvem (AWS, Azure) para avaliar se práticas de licenciamento e integração de IA prejudicam a contestabilidade do mercado.[^26][^50][^27][^24]

### 3.4. Moedas digitais e cripto (MiCA)

O Markets in Crypto‑assets Regulation (MiCA), aprovado como Regulamento (UE) 2023/1114, é o primeiro regime abrangente de criptoativos da UE, cobrindo ofertas públicas de criptoativos, stablecoins (tokens referenciados a ativos e tokens de dinheiro eletrônico) e prestadores de serviços de criptoativos. As regras para stablecoins (ARTs e EMTs) passaram a valer em 30 de junho de 2024, enquanto a estrutura completa para prestadores de serviços entrou em vigor em 30 de dezembro de 2024, com período de transição até meados de 2026.[^34][^35][^37][^36]

MiCA impõe requisitos de autorização, capital, governança, reservas 1:1 para certos stablecoins, segregação de ativos e regras de transparência, movendo exchanges e emissores de um regime de baixa regulação para um modelo de negócio licenciado e supervisionado. A lógica é explicitamente de construção de confiança: harmonizar regras, reduzir arbitragem regulatória e aproximar o mercado cripto da supervisão financeira tradicional.[^35][^37][^36][^34]

### 3.5. Camada técnica de confiança (deepfakes e proveniência)

Além do AI Act e do DSA, a UE apoia a adoção de padrões técnicos de proveniência como o C2PA, um padrão aberto que permite registrar origem e histórico de edição de conteúdos digitais com metadados criptograficamente verificáveis. Iniciativas como a Content Authenticity Initiative (CAI) – hoje com mais de 4.000 membros, incluindo grandes plataformas, fabricantes de câmera e organizações de mídia – estão implantando “Content Credentials” C2PA em fluxos de criação e publicação para rotular materiais gerados por IA.[^5][^51][^6][^52][^53][^54][^55]

A estratégia europeia, portanto, combina: (1) obrigações legais de marcação e rotulagem de deepfakes (AI Act + DSA), (2) enforcement de plataformas de grande porte e (3) adoção de padrões de mercado para proveniência e autenticação de mídia. Essa combinação cria uma infraestrutura de confiança mais densa, embora ainda dependente da capacidade técnica de detecção e da cooperação de atores globais fora da jurisdição da UE.[^8][^7][^16][^54]

## 4. Estados Unidos

### 4.1. Regulação de IA: da ordem executiva à competição pela liderança

Em outubro de 2023, a Ordem Executiva 14110 (“Safe, Secure, and Trustworthy Development and Use of Artificial Intelligence”) estabeleceu a agenda mais abrangente até então de governança de IA pelo governo federal americano, cobrindo segurança, privacidade, direitos civis, proteção ao consumidor e competição. Entre outros pontos, a ordem determinou que o NIST desenvolvesse padrões de segurança, definiu limiares de computação para reporte obrigatório de grandes treinamentos a autoridades e orientou o Departamento de Comércio a criar guias para autenticação de conteúdo (watermarking e rastreio de proveniência) para combater fraudes e desinformação.[^2][^56][^57][^9][^58]

A mesma ordem enfatizou o uso de técnicas de proteção de privacidade (privacy‑enhancing technologies) e chamou o Congresso a aprovar legislação federal abrangente de privacidade, reconhecendo os riscos de reidentificação, extração e inferência de dados sensíveis por sistemas de IA. Em 2025, porém, o cenário político mudou: uma nova ordem executiva “Removing Barriers to American Leadership in Artificial Intelligence” revogou políticas vistas como entraves à inovação, sinalizando maior ênfase em competitividade e menor detalhamento prescritivo ex ante.[^10][^9][^59][^60]

O resultado é um quadro em transição: tecnicamente há uma infraestrutura nascente de padrões, métricas e práticas recomendadas federais para IA, mas sem um estatuto unificado comparável ao AI Act; e boa parte da governança de conteúdo sintético depende de autocompromissos de empresas e de enforcement posterior por FTC, DOJ e outras agências.[^58][^61][^29]

### 4.2. Privacidade: mosaico estadual e impasse federal

Os EUA seguem como o único país do G20 sem lei nacional abrangente de proteção de dados; o sistema permanece baseado em leis setoriais (saúde, finanças, crianças) e em um mosaico crescente de estatutos estaduais de privacidade. Em 2024 já havia 14 leis estaduais abrangentes aprovadas e 8 em vigor; em 2025 esse número sobe para 19–20, com novas legislações e emendas ampliando requisitos para dados sensíveis, biometria e menores.[^17][^18][^62][^63][^19][^64]

Tentativas de criar um marco federal, como o American Data Privacy and Protection Act (ADPPA) em 2022 e o American Privacy Rights Act em 2024, seguem travadas em debates sobre preempção de leis estaduais e direito de ação privada, sem aprovação final até o fim de 2025. Enquanto isso, a FTC expande o uso de sua autoridade contra práticas “injustas ou enganosas” em casos de vazamento, uso de dados para treinamento de IA e Dark Patterns, produzindo segurança jurídica fragmentada para empresas e usuários.[^65][^63][^19][^20]

### 4.3. Antitruste e IA

Na ausência de legislação específica como o DMA, a estratégia americana é aplicar o arsenal antitruste tradicional (Sherman Act, Clayton Act, FTC Act) à cadeia de valor da IA, da infraestrutura de chips e nuvem a modelos fundacionais e parcerias estratégicas. Em 2024, FTC e DOJ publicaram declarações conjuntas com autoridades internacionais, comprometendo‑se a “proteger a competição em todo o ecossistema de IA” e destacando riscos como concentração de insumos, auto‑preferência de plataformas e parcerias tipo “acqui‑hire”.[^28][^30][^66][^29][^67]

Em junho de 2024, os dois órgãos dividiram formalmente a supervisão de IA: a FTC ficou com preocupações competitivas envolvendo grandes empresas de software, enquanto o DOJ concentrou‑se em um grande fabricante de chips, com ambos sinalizando que examinarão com “urgência” os “pontos de estrangulamento” da cadeia de IA. Análises prospectivas indicam que, sob o governo atual, a tendência é de enforcement mais agressivo em parcerias, fusões de conveniência e uso de dados de terceiros para treinar modelos próprios, mas sempre via casos individuais, sem lista ex ante de obrigações para “gatekeepers de IA”.[^66][^29]

### 4.4. Moedas digitais e stablecoins

No campo de moedas digitais, os EUA ainda não adotaram um regime abrangente semelhante ao MiCA, mas avançam em propostas setoriais para stablecoins de pagamento, como o Clarity for Payment Stablecoins Act. O projeto estabelece que apenas “permitted issuers” (subsidiárias de bancos segurados, emissores federais ou estaduais qualificados) podem emitir stablecoins de pagamento para uso por residentes nos EUA, exigindo reservas 1:1 em ativos de alta liquidez, divulgação mensal detalhada de reservas, regras de capital e liquidez e enquadramento desses emissores como instituições financeiras para fins de Bank Secrecy Act.[^38][^39]

Think tanks e centros de estudos alertam que, se a regulação de cripto e estrutura de mercado não forem refinadas com urgência, o arranjo atual de stablecoins e infraestrutura pode gerar riscos financeiros e geopolíticos para os EUA, inclusive pela competição com CBDCs estrangeiras e stablecoins reguladas em outras jurisdições. Isso situa a política americana em um ponto de tensão entre evitar inovações de risco sistêmico e não ceder liderança financeira global para regimes mais claros, como o MiCA europeu ou iniciativas estatais de CBDC.[^40]

### 4.5. Infraestrutura de confiança: autenticidade de conteúdo

No enfrentamento da crise de autenticidade, a Ordem 14110 instruiu o Departamento de Comércio a desenvolver padrões para autenticação de conteúdo e watermarking com o objetivo de permitir que cidadãos identifiquem comunicações oficiais autênticas do governo e, por extensão, inspirar boas práticas no setor privado. Porém, especialistas enfatizam que, do ponto de vista técnico, watermarking atual pode ser removido ou adulterado, o que torna necessário combiná‑lo com técnicas de detecção probabilística de deepfakes e padrões mais robustos de proveniência.[^68][^56][^9][^2]

Paralelamente, empresas americanas lideram a criação do C2PA e da CAI, que definem padrões abertos de metadados de proveniência e se integram com grandes plataformas (Adobe, Meta, LinkedIn, OpenAI, YouTube) para rotular material gerado ou manipulado por IA. Essa infraestrutura, embora voluntária, tende a se tornar base técnica para obrigações legais futuras nos EUA (por exemplo, exigências de credenciais de conteúdo em comunicações oficiais ou em setores críticos) e já é considerada nos debates regulatórios europeus.[^51][^6][^7][^54]

## 5. Brasil

### 5.1. Regulação de IA (PL 2338/2023)

O Brasil avança para um marco específico de IA com o PL 2338/2023, aprovado no Senado e em tramitação na Câmara, inspirado em boa medida no AI Act europeu. O projeto estabelece princípios como transparência, segurança, proteção de dados, responsabilização e garantia de direitos fundamentais, além de um sistema de classificação por risco, com proibição de usos de “risco excessivo” (como vigilância em massa) e obrigações mais rigorosas para sistemas de alto risco.[^11][^12]

O PL prevê também a criação de um Sistema Nacional de Regulação e Governança de IA (SIA), articulando diferentes órgãos reguladores e de defesa de direitos fundamentais, e enfatiza a necessidade de alinhamento com a LGPD e com diretrizes da ANPD. Setores como saúde, crédito, reconhecimento facial em segurança pública e serviços financeiros tendem a ser os primeiros a sentir o impacto regulatório, com exigências de explicabilidade, registro e monitoramento de sistemas.[^13][^12][^11]

### 5.2. LGPD, ANPD e proteção de dados

A Lei Geral de Proteção de Dados (LGPD – Lei 13.709/2018) unificou dezenas de normas pré‑existentes e estabelece regras para coleta, tratamento, armazenamento e compartilhamento de dados pessoais, definindo também dados sensíveis e direitos dos titulares (acesso, correção, eliminação, revogação de consentimento, entre outros). A LGPD aplica‑se a qualquer operação realizada no Brasil ou que tenha por objetivo ofertar bens/serviços a pessoas no território, aproximando‑se da lógica extraterritorial do GDPR.[^22][^21][^69]

A ANPD, criada pela própria LGPD e consolidada como autarquia de regime especial, é responsável por regulamentar, fiscalizar e aplicar sanções, bem como exigir Relatórios de Impacto à Proteção de Dados (DPIAs) quando o controlador se baseia em legítimo interesse. No contexto de IA, ANPD e outros órgãos (como CNJ, Banco Central e CVM) vêm emitindo diretrizes específicas, reforçando a necessidade de governança de dados, segurança e não discriminação algorítmica.[^23][^21][^13][^22]

### 5.3. Antitruste digital e plataformas

No campo da concorrência, o Brasil discute um modelo ex ante para plataformas digitais sistemicamente relevantes, inspirado em parte no DMA, mas com desenho mais flexível para adequar‑se à capacidade institucional do CADE. Propostas em discussão preveem um mecanismo de designação de plataformas de “relevância sistêmica” e a imposição de obrigações como transparência, interoperabilidade e tratamento não discriminatório, com sanções que incluem multas, medidas estruturais e até suspensão de atividades.[^31][^32]

Além das discussões legislativas, o CADE já iniciou casos concretos ligados à infraestrutura de nuvem e IA, como a investigação sobre práticas de licenciamento da Microsoft em nuvem no Brasil, motivada por achados da autoridade britânica sobre efeitos anticompetitivos globais. A abordagem brasileira busca um equilíbrio entre o modelo rígido de obrigações do DMA europeu e abordagens mais flexíveis (como Reino Unido e Alemanha), usando investigações e recomendações para calibrar eventual legislação ex ante.[^33][^32][^31]

### 5.4. Drex e finanças digitais

O Drex, projeto de CBDC brasileira, está em fase piloto com emissão prevista em dois níveis: Drex wholesale para uso entre instituições financeiras e de pagamento, lastreado diretamente pelo Banco Central, e Drex retail como versão tokenizada do real, respaldada por depósitos bancários ou Drex wholesale e garantida pelo BC. O objetivo declarado do BC é criar uma infraestrutura de mercado sob sua governança onde tecnologias como dinheiro programável e smart contracts possam florescer de forma segura, promovendo novos modelos de negócio.[^41][^42][^23]

O desenho regulatório do Drex enfatiza: aplicação de normas existentes (AML, combate ao financiamento do terrorismo, sigilo bancário e LGPD), garantia de privacidade com possibilidades como uso de provas de conhecimento zero e manutenção de altos padrões de resiliência e cibersegurança equivalentes a infraestruturas críticas de mercado. O BC articula esse projeto com o ecossistema de fintechs e com a já densa regulação financeira brasileira, buscando evitar assimetrias regulatórias significativas entre ativos tokenizados e instrumentos tradicionais.[^42][^41][^23]

### 5.5. Crise de autenticidade e resposta institucional

O Brasil figura entre os países mais atingidos por fraudes com deepfakes corporativos, com relatos de prejuízos bilionários e crescimento exponencial de incidentes, incluindo golpes via videoconferência e clonagem de voz em operações financeiras. Casos recentes incluem operações policiais contra quadrilhas que utilizavam deepfakes de autoridades públicas em sites falsos, sinalizando a convergência entre fraude financeira, desinformação política e ataques à confiança em instituições.[^4][^70][^3]

A resposta regulatória ainda é fragmentada: a LGPD, o Código Penal e normas setoriais (Banco Central, CVM, SUSEP) são usados para enquadrar fraudes e vazamentos, enquanto projetos de lei debatem tipificação específica de uso malicioso de deepfakes e obrigações de transparência para plataformas. Em paralelo, empresas e órgãos públicos começam a adotar padrões de autenticação multifator, protocolos de verificação fora de banda e, em alguns casos, soluções de proveniência de conteúdo alinhadas a padrões como C2PA, ainda que sem obrigação legal explícita.[^21][^52][^13][^3][^5]

## 6. Comparando abordagens: convergências e lacunas

### 6.1. Convergências estruturais

Os três blocos caminham para uma mesma direção em três dimensões: (1) uso de estruturas de risco (IA de alto risco, cripto com impacto sistêmico), (2) fortalecimento de autoridades multissetoriais (dados, concorrência, finanças) e (3) adoção de padrões técnicos de autenticação e transparência. Há também convergência na percepção de que concentração de insumos de IA (chips, nuvem, dados) e poder de plataformas exige enforcement antitruste mais agressivo e coordenado internacionalmente.[^30][^29][^1][^24][^35][^41][^28][^31]

Em relação à crise de autenticidade, UE e EUA apontam para uma combinação de watermarking, marcações legíveis por máquina em conteúdo, rotulagem em plataformas e padrões de proveniência (C2PA/Content Credentials), enquanto o Brasil começa a importar essas práticas via mercado e cooperação regulatória.[^6][^54][^8][^2]

### 6.2. Diferenças e assimetrias

A União Europeia destaca‑se por já possuir marcos horizontais e vinculantes em IA (AI Act), criptoativos (MiCA) e plataformas (DMA/DSA), com autoridade central forte e supervisão coordenada, o que reduz o vácuo legislativo, mas também aumenta a complexidade regulatória. Os Estados Unidos, em contraste, operam com grande densidade institucional (FTC, DOJ, NIST, múltiplas agências setoriais) mas sem leis federais abrangentes em privacidade, IA ou cripto, o que gera dependência de ordens executivas, soft law e enforcement caso a caso.[^9][^25][^63][^29][^1][^24][^34][^17]

O Brasil ocupa uma posição intermediária: conta com uma lei de dados robusta (LGPD), forte regulação financeira e um Banco Central tecnicamente sofisticado, avança em PLs de IA e antitruste digital, mas ainda carece de coordenação plena e de capacidade de enforcement no mesmo nível das jurisdições centrais. Em autenticidade de conteúdo, iniciativas públicas e privadas estão mais reativas a incidentes do que ancoradas em um marco nacional explícito de proveniência e rotulagem.[^11][^21][^31][^33]

### 6.3. Riscos de vácuo regulatório e overregulation

Nos três contextos, o principal risco de vácuo regulatório não é ausência total de normas, mas descompasso entre velocidade da inovação (modelos de IA cada vez mais multimodais, criptofinanças programáveis, novos vetores de deepfake) e tempo de tramitação, implementação e coordenação institucional. Por outro lado, regulações muito rígidas e pouco calibradas podem deslocar inovação para zonas de menor controle ou beneficiar incumbentes com maior capacidade de compliance, em detrimento de novos entrantes.[^7][^24][^35][^40][^31][^11]

O desafio central para o “Estado regulador” é encontrar um equilíbrio dinâmico entre proteção de direitos e manutenção de ambientes experimentais controlados, combinando: (1) normas horizontais de princípios, (2) instrumentos ex ante e ex post ajustáveis e (3) infraestrutura técnica e institucional de confiança que reduza os custos de verificação para todos os agentes econômicos.[^1][^9][^41][^5]

## 7. Implicações estratégicas para atores públicos e privados

Para formuladores de política, a tendência é clara: a agenda de IA, privacidade, antitruste e moedas digitais tornou‑se indivisível e requer arranjos de governança integrados (como SIA no Brasil, coordenação DMA/AI Act/DSA na UE e task forces interagências nos EUA). A cooperação internacional entre autoridades de concorrência, proteção de dados e supervisores financeiros será determinante para evitar arbitragem regulatória em IA e finanças digitais.[^29][^71][^24][^30][^31][^11]

Para empresas e instituições, a lição prática é que compliance deixa de ser apenas jurídico e passa a ser arquitetural: é necessário incorporar desde o design padrões de governança de dados (LGPD/GDPR), gestão de risco de IA (AI Act/PL 2338), interoperabilidade e neutralidade competitiva (DMA/CADE) e trilhas de auditoria/proveniência de conteúdo (C2PA/Content Credentials). Organizações que conseguirem alinhar seus produtos e modelos de negócio a essa infraestrutura de confiança regulatória tendem a se posicionar melhor em um cenário de inovação autônoma, vigilância crescente e escassez de confiança.[^35][^22][^5][^6]

---

## References

1. [AI Act | Shaping Europe's digital future - European Union](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) - The AI Act (Regulation (EU) 2024 ... These include marking AI generated content and disclosing the a...

2. [White House Executive Order Demands Watermarking of AI Content](https://www.getclarity.ai/ai-deepfake-blog/white-house-executive-order-demands-watermarking-of-ai-content) - Executive Order 14110 is a move in the right direction – but it won't stop the ongoing emergence of ...

3. [Deepfake Corporativo Brasil: 822% Fraudes, R$ 4,5 Bi Prejuízo](https://encontreumnerd.com.br/blog/deepfake-corporativo-brasil-822-fraudes-r-4-5-bi-prejuizo) - Análise final do risco deepfake para empresas brasileiras em 2025 e próximos anos é que ameaça é rea...

4. [Explosão de deepfakes: relatório aponta aumento de 3.000% em ...](https://mpmt.mp.br/portalcao/news/1217/131887/explosao-de-deepfakes-relatorio-aponta-aumento-de-3000-em-tentativas-de-fraudes/34) - Deepfake é uma técnica de manipulação de mídia que utiliza inteligência artificial para criar vídeos...

5. [C2PA | Verifying Media Content Sources](https://c2pa.org) - C2PA provides an open technical standard for publishers, creators and consumers to establish the ori...

6. [5–Year Anniversary of the Content Authenticity Initiative](https://blog.adobe.com/en/publish/2024/10/14/5-year-anniversary-content-authenticity-initiative-what-it-means-whats-ahead) - Five years ago, at Adobe MAX 2019, we co-founded the Content Authenticity Initiative (CAI) with the ...

7. [A Multi-Level Strategy for Deepfake Content Moderation under EU ...](https://arxiv.org/html/2507.08879v1) - Additionally, deployers of AI systems who generate deepfakes are required to mark the output such th...

8. [Illuminating AI: The EU's First Draft Code of Practice on ...](https://www.kirkland.com/publications/kirkland-alert/2026/02/illuminating-ai-the-eus-first-draft-code-of-practice-on-transparency-for-ai) - ... deepfakes and AI-generated and manipulated text applicable to deployers of AI systems ... 01 Aug...

9. [Executive Order 14110—Safe, Secure, and Trustworthy ...](https://www.presidency.ucsb.edu/documents/executive-order-14110-safe-secure-and-trustworthy-development-and-use-artificial) - At a minimum, the Secretary shall develop tools to evaluate AI capabilities to generate outputs that...

10. [Removing Barriers to American Leadership in Artificial Intelligence](https://www.whitehouse.gov/presidential-actions/2025/01/removing-barriers-to-american-leadership-in-artificial-intelligence/) - This order revokes certain existing AI policies and directives that act as barriers to American AI i...

11. [PL 2338/2023: the impacts of regulating Artificial Intelligence in Brazil](https://www.sidi.org.br/en/blog/the-impacts-of-regulating-artificial-intelligence-in-brazil) - The main objective of PL 2338/2023 is to regulate the use of artificial intelligence in Brazil, esta...

12. [[PDF] Introdução - Portal Gov.br](https://www.gov.br/anpd/pt-br/assuntos/noticias/analise-preliminar-do-pl-2338_2023-formatado-ascom.pdf) - Nesse sentido, o PL nº 2338/2023, a um só tempo, proíbe sistemas de IA de risco excessivo, delimita ...

13. [Inteligência Artificial no Brasil: PL 2338/2023, CNJ e ANPD - Cria.AI](https://criaai.app.br/blog/regulamentacao-inteligencia-artificial-no-brasil/) - Explica a regulamentação da inteligência artificial no Brasil, incluindo PL 2338/2023, LGPD, diretri...

14. [General Data Protection Regulation](https://www.edps.europa.eu/data-protection/our-work/subjects/general-data-protection-regulation_en) - The General Data Protection Regulation (GDPR) will finally become law across the EU in May 2018 and ...

15. [What is GDPR, the EU's new data protection law?](https://gdpr.eu/what-is-gdpr/) - The GDPR entered into force in 2016 after passing European Parliament, and as of May 25, 2018, all o...

16. [The impact of the Digital Services Act on digital platforms](https://digital-strategy.ec.europa.eu/en/policies/dsa-impact-platforms) - ... deepfakes. Obligations on traceability of business users in online marketplaces. The DSA introdu...

17. [Data protection laws in the United States](https://www.dlapiperdataprotection.com/?c=US) - There is no comprehensive national privacy law in the United States. However, the US does have a num...

18. [Retrospective: 2024 in comprehensive state data privacy law - IAPP](https://iapp.org/news/a/retrospective-2024-in-comprehensive-state-data-privacy-law) - 2024 experienced a comparable level of activity to 2023 with seven new states passing comprehensive ...

19. [U.S. Privacy Law Outlook: What's on the Horizon in 2024](https://www.brookspierce.com/publication-u-s-privacy-law-outlook-whats-on-the-horizon-in-2024) - The MCDPA was signed into law on May 19, 2023, and goes into effect on Oct. 1, 2024. Of the three en...

20. [2025 Mid-Year Review: US State Privacy Law Updates (Part 2)](https://www.mayerbrown.com/en/insights/publications/2025/10/2025-mid-year-review-us-state-privacy-law-updates-part-2) - Although no new states have enacted wholly new comprehensive privacy laws this year, numerous legisl...

21. [Brazilian General Data Protection Law (LGPD) (2018) (link)](https://ciberseguranca.igarape.org.br/en/brazilian-general-data-protection-law-lgpd-2018-link/) - The Brazilian General Data Protection Law – nº 13,709 (08/14/2018) establishes rules on collecting, ...

22. [LGPD: An Overview of Brazil's General Data Protection Law](https://usercentrics.com/knowledge-hub/brazil-lgpd-general-data-protection-law-overview/) - Get a comprehensive overview of the Brazil Data Protection Law (LGPD) and understand how it impacts ...

23. [[PDF] the potential of Drex, the Brazilian CBDC Paula da Cunha Duarte ...](https://www.boeckler.de/data/downloads/OEA/Veranstaltungen/2024/v_2024_10_25_duarte.pdf) - Brazil has a comprehensive regulatory framework regarding individual privacy rights and the transpar...

24. [The DMA High Level Group Endorses Joint Paper on the Regulation ...](https://www.clearyantitrustwatch.com/2025/12/the-dma-high-level-group-endorses-joint-paper-on-the-regulation-of-ai/) - The Commission recently issued a report on the interaction of the DSA with other legal instruments (...

25. [DMA designated Gatekeepers - Digital Markets Act](https://digital-markets-act.ec.europa.eu/gatekeepers_en) - The European Commission designated for the first time six gatekeepers - Alphabet, Amazon, Apple, Byt...

26. [Ex ante but Insufficient? The Commission's Five AI Investigations ...](https://scidaproject.com/2025/12/12/ex-ante-but-insufficient-the-commissions-five-ai-investigations-launched-in-just-22-days/) - The investigations into Meta AI and Google AI Overview and AI Mode fall under Article 102 of the Tre...

27. [Google faces EU antitrust investigation over AI Overviews, YouTube](https://www.reuters.com/sustainability/boards-policy-regulation/eu-launches-antitrust-probe-into-googles-use-online-content-ai-purposes-2025-12-09/) - Last week, the European Commission launched an investigation into Meta's plans to block AI rivals fr...

28. [FTC, DOJ, and International Enforcers Issue Joint Statement on AI ...](https://www.ftc.gov/news-events/news/press-releases/2024/07/ftc-doj-international-enforcers-issue-joint-statement-ai-competition-issues) - A statement affirming a commitment to protecting competition across the artificial intelligence (AI)...

29. [FTC and DOJ Divide Responsibility over AI Antitrust Oversight — AI](https://www.mlstrategies.com/insights-center/viewpoints/54031/2024-06-25-ftc-and-doj-divide-responsibility-over-ai-antitrust) - Recent developments suggest that competition authorities are preparing to energetically pursue poten...

30. [US DOJ and FTC join G7 Competition Authorities in ... - Mayer Brown](https://www.mayerbrown.com/en/insights/publications/2024/10/us-doj-and-ftc-join-g7-competition-authorities-in-promising-vigorous-competition-enforcement-in-the-ai-industry) - October 29, 2024. US DOJ and FTC join G7 Competition Authorities in Promising Vigorous Competition E...

31. [Examining Brazil's 'Ecosystem Approach' to Digital Antitrust](https://techpolicy.press/examining-brazils-ecosystem-approach-to-digital-antitrust) - It proposes giving Brazil's competition authority, CADE, new ways to bring challenges in digital mar...

32. [Big Tech through the lenses of Brazil's competition watchdog CADE ...](https://scidaproject.com/2024/10/30/big-tech-through-the-lenses-of-brazils-competition-watchdog-cade-and-the-path-ahead/) - A new government report recommends adding new rules under the existing competition law regime enforc...

33. [Brazil Probes Microsoft Cloud Licensing as UK Antitrust Findings ...](https://erp.today/brazil-probes-microsoft-cloud-licensing-as-uk-antitrust-findings-ripple-into-latin-america/) - Brazil's competition authority, CADE, has launched an antitrust investigation into Microsoft's cloud...

34. [The European regulation Markets in Crypto-Assets (MiCA) - AMF](https://www.amf-france.org/en/news-publications/depth/mica) - The MiCA Regulation entered into force on 29 June 2023. It will apply from 30 December 2024, with th...

35. [[PDF] MiCA Legal Framework – How To Comply With the EU's Crypto ...](https://www.squirepattonboggs.com/media/yvspymyt/mica-legal-framework-how-to-comply-with-the-eus-crypto-asset-rules.pdf) - It entered into force in June 2023 and will apply in two phases: stablecoin rules from 30 June 2024,...

36. [MiCA Regulation and EU Crypto Rules: What Changes in 2026](https://sumsub.com/blog/crypto-regulations-in-the-european-union-markets-in-crypto-assets-mica/) - On December 30, 2024, MiCA fully came into effect, and the transitional grandfathering period began....

37. [MiCA's full effect drops: Take the next step into EU financial ... - EY](https://www.ey.com/en_lu/insights/digital/micas-full-effect-drops-take-the-next-step-into-eu-financial-digitalization) - The EU's Markets in Crypto-Assets (MiCA) Regulation is set to fully take effect on December 30, 2024...

38. [Info - H.R.4766 - 118th Congress (2023-2024): Clarity for Payment ...](https://www.congress.gov/bill/118th-congress/house-bill/4766/all-info) - This bill establishes a regulatory framework for payment stablecoins (digital assets which an issuer...

39. [Text - H.R.4766 - 118th Congress (2023-2024): Clarity for Payment ...](https://www.congress.gov/bill/118th-congress/house-bill/4766/text) - —The term “Federal qualified nonbank stablecoin issuer” means a nonbank entity approved by the prima...

40. [Unstable Coins: Stablecoin Regulation, Market Structure Legislation ...](https://www.csis.org/analysis/unstable-coins-stablecoin-regulation-market-structure-legislation-and-us-security-risks) - If policymakers do not urgently refine and implement cryptocurrency regulation, existing stablecoin ...

41. [Drex for gringos: get to know the Brazilian CBDC - Parfin.io](https://parfin.io/en/blog/drex-for-gringos-get-to-know-the-brazilian-cbdc) - The regulatory aspect of the Drex pilot is especially intricate, as it involves establishing a frame...

42. [[PDF] Central Bank Digital Currencies and the Drex in Brazil - IE/UFRJ](https://www.ie.ufrj.br/images/IE/TDS/2025/TD_IE_002_2025_TIGRE_PAULA.pdf) - Drex will operate within a regulatory framework, enabling the concept of "supervised automation. ......

43. [The Digital Markets Act Roundup: May 2024 | TechPolicy.Press](https://techpolicy.press/digital-markets-act-roundup-may-2024) - On the DMA, the Group writes, "data driven advantages and network effects which are leveraged by gat...

44. [Article 50: Transparency Obligations for Providers and Deployers of ...](https://artificialintelligenceact.eu/article/50/) - AI systems that create synthetic content (like deepfakes) must mark their outputs as artificially ge...

45. [High-level summary of the AI Act | EU Artificial Intelligence Act](https://artificialintelligenceact.eu/high-level-summary/) - ... deepfakes). Minimal risk is unregulated (including the majority of AI applications currently ava...

46. [What the EU's New AI Code of Practice Means for Labeling Deepfakes](https://techpolicy.press/what-the-eus-new-ai-code-of-practice-means-for-labeling-deepfakes) - In the AI Act, deepfakes are regulated through transparency requirements, mandatory labeling, and te...

47. [Transparency Code of Practice First Draft - The EU AI Act Newsletter](https://artificialintelligenceact.substack.com/p/the-eu-ai-act-newsletter-93-transparency) - For deepfakes, drafters from industry, academia and civil society propose an “EU common icon” – a sy...

48. [Taking the EU AI Act to Practice Understanding the Draft ...](https://www.twobirds.com/en/insights/2026/taking-the-eu-ai-act-to-practice-understanding-the-draft-transparency-code-of-practice) - For deepfakes (content creating a resemblance to real persons/events, etc.), the Draft Code mandates...

49. [Digital Markets Act (DMA) | Updates, Compliance, Training](https://www.eu-digital-markets-act.com) - The Digital Markets Act (DMA) affects “gatekeeper platforms” like Google, Amazon and Meta, and cover...

50. [EU Regulators Target Tech Giants in AI Competition Crackdown](https://www.gerrishlegal.com/blog/eu-regulators-target-tech-giants-in-ai-competition-crackdown) - In September 2025, Google was hit with a €2.95 billion antitrust fine for practices related to onlin...

51. [C2PA Releases Specification of World's First Industry Standard for ...](https://c2pa.org/c2pa-releases-specification-of-worlds-first-industry-standard-for-content-provenance/) - C2PA Releases Specification of World's First Industry Standard for Content Provenance. Designed for ...

52. [Introduction to the Coalition for Content Provenance and Authenticity ...](https://www.linuxfoundation.org/webinars/introduction-to-the-coalition-for-content-provenance-and-authenticity-c2pa?hsLang=en) - C2PA is a Joint Development Foundation project which has built a system to provide provenance and hi...

53. [Content Authenticity Initiative - Wikipedia](https://en.wikipedia.org/wiki/Content_Authenticity_Initiative) - Together with Arm, BBC, Intel, Microsoft and Truepic, Adobe co-founded the non-profit Coalition for ...

54. [4,000 members — a major milestone in the effort to foster online ...](https://contentauthenticity.org/blog/celebrating-4000-cai-members) - In 2024, the CAI and the Linux Foundation-based Coalition for Content Provenance and Authenticity (C...

55. [C2PA Content Credentials Specification - VerifyWise](https://verifywise.ai/es/ai-governance-library/transparency-and-documentation/c2pa-content-credentials-specification) - The C2PA (Coalition for Content Provenance and Authenticity) Content Credentials specification estab...

56. [The White House Addresses Responsible AI: Investigating in an AI ...](https://www.relativity.com/blog/the-white-house-addresses-responsible-ai-investigating-in-an-ai-world/) - Fast forward to 2023 and deepfakes are ubiquitous in media. Creating a realistic deepfake of a still...

57. [Safe, Secure, and Trustworthy Development and Use of Artificial ...](https://www.federalregister.gov/documents/2023/11/01/2023-24283/safe-secure-and-trustworthy-development-and-use-of-artificial-intelligence) - Executive Order 14110 of October 30, 2023. Safe, Secure, and Trustworthy Development and Use of Arti...

58. [Executive Order 14110 - Wikipedia](https://en.wikipedia.org/wiki/Executive_Order_14110) - Signed on October 30, 2023, the order defines the administration's policy goals regarding artificial...

59. [[PDF] Executive Order 14110 Governing Artificial Intelligence - DPCE Online](https://www.dpceonline.it/index.php/dpceonline/article/download/2354/2592/3793) - Finally, in 2023, Joe Biden signed EO 14110, Safe, Secure, and. Trustworthy Development and Use of A...

60. [2023 AI Safety Executive Order Revoked and What Lies Ahead for AI](https://www.quarles.com/newsroom/publications/2023-ai-safety-executive-order-revoked-and-what-lies-ahead-for-ai) - Although EO 14110 has been rescinded, President Biden's final week in office included several notewo...

61. [Artificial Intelligence (AI) - United States Department of State](https://2021-2025.state.gov/artificial-intelligence/) - The announcement fulfills two actions mandated by President Biden's 2023 AI Executive Order (E.O. 14...

62. [US Data Privacy Guide | White & Case LLP](https://www.whitecase.com/insight-our-thinking/us-data-privacy-guide) - Currently, a total of twenty states have enacted comprehensive data privacy laws in the United State...

63. [Status of Federal Privacy Legislation - Berman Fink Van Horn P.C.](https://www.bfvlaw.com/status-of-federal-privacy-legislation/) - No new omnibus federal privacy law passed in 2025, and it appears unlikely that any omnibus federal ...

64. [The Shifting Landscape of U.S. State Data Privacy Laws in 2024](https://www.flastergreenberg.com/newsroom-articles-shifting-landscape-us-data-privacy-laws-2024.html) - ... U.S. state data privacy laws in the U.S. has grown increasingly complex in 2024. Seven additiona...

65. [New proposed federal data privacy law suggests big changes - IBM](https://www.ibm.com/think/news/american-privacy-rights-act-federal-data-privacy-law) - With the American Privacy Rights Act of 2024, the U.S. government established the first national pri...

66. [Eyes on AI: Looking ahead to potential AI antitrust enforcement in ...](https://www.whitecase.com/insight-alert/eyes-ai-looking-ahead-potential-ai-antitrust-enforcement-trump-administration) - The Biden Administration FTC's report on AI, however, provided an early window into the current FTC'...

67. [Regulating Artificial Intelligence: Antitrust and Anti-Discrimination ...](https://legaljournal.princeton.edu/regulating-artificial-intelligence-antitrust-and-anti-discrimination-policy/) - In July 2024, the FTC, DOJ, and international antitrust enforcers affirmed their commitment to prote...

68. [President Biden's AI executive order has 'dangerous limitations ...](https://www.foxbusiness.com/media/president-bidens-ai-executive-order-dangerous-limitations-deepfake-detection-ceo) - Published November 8, 2023 5:00am EST. President Biden's AI executive order has 'dangerous limitatio...

69. [General Personal Data Protection Law - Wikipedia](https://en.wikipedia.org/wiki/General_Personal_Data_Protection_Law) - The law's primary aim is to unify 40 different Brazilian laws that regulate the processing of person...

70. [Notícias Relevantes em Direito Digital dos Últimos 14 Dias (1-14 de ...](https://femperj.org.br/noticias-relevantes-em-direito-digital-dos-ultimos-14-dias-1-14-de-novembro-de-2025/) - Notícias Relevantes em Direito Digital dos Últimos 14 Dias (1-14 de novembro de 2025)

71. [2024 Antitrust Update: Navigating the Evolving Landscape](https://www.clearygottlieb.com/news-and-insights/publication-listing/2024-antitrust-update-navigating-the-evolving-landscape) - The article discusses the shifts in antitrust leadership in the U.S., EU, and UK, and how this will ...

