"""
Startup Idea Agent - Orquestrador Principal

Agente especializado em transformar problemas societais avaliados em ideias
concretas de startup, incluindo:
1. Carregar problemas do ranking existente (banco_geral_dados.json ou CSVs)
2. Gerar ideias de startup via LLM ou template
3. Avaliar cada ideia com framework de 5 categorias e 22 critérios ponderados
4. Gerar artigos concisos (2 páginas) para cada ideia
5. Exportar resultados

Framework de avaliação:
- Eficácia e Problem-Solution Fit (Regra 10x, Simplicidade, Foco)
- Viabilidade e Risco de Produto (MVP, Tech Risk, Regulatório)
- Distribuição e Go-to-Market (Viralidade, Canais, Decisor)
- Modelo de Negócios e Economia Unitária (Margem, Recorrência, Unit Economics)
- Moats e Defensibilidade (Rede, Lock-in, Data Moat, Escala)

Baseado nas metodologias de:
- Y Combinator (Paul Graham / Michael Seibel)
- Lean Startup (Eric Ries / Ash Maurya)
- Zero to One (Peter Thiel)
- 7 Powers (Hamilton Helmer)
- Blitzscaling (Reid Hoffman)
- Inspired (Marty Cagan)
- Sequoia Capital / Sam Altman
"""

import os
import json
import csv
import time
from datetime import datetime
from typing import Optional, Callable

from .config import (
    IDEA_SCORING_FRAMEWORK,
    IDEA_GENERATION_PROMPT_TEMPLATE,
    TOTAL_CRITERIA,
    MAX_POSSIBLE_SCORE,
    get_all_criteria,
    get_category_names,
)
from .scoring import IdeaScoringEngine, IdeaScore
from .article_writer import IdeaArticleWriter


class StartupIdeaAgent:
    """
    Agente principal que orquestra o pipeline de geração e avaliação
    de ideias de startup a partir de problemas societais.

    Pipeline:
    1. Carrega problemas (de JSON, CSV ou lista)
    2. Gera ideias de startup para cada problema
    3. Avalia cada ideia com o framework de 5 categorias
    4. Gera artigos concisos (2 páginas) por ideia
    5. Exporta resultados
    """

    def __init__(
        self,
        base_dir: str = ".",
        llm_generator: Optional[Callable] = None,
        llm_evaluator: Optional[Callable] = None,
        llm_writer: Optional[Callable] = None,
        verbose: bool = True,
    ):
        """
        Args:
            base_dir: Diretório base do projeto.
            llm_generator: Função LLM para geração de ideias.
                          Assinatura: (prompt: str) -> str
            llm_evaluator: Função LLM para avaliação de critérios.
                          Assinatura: (prompt: str) -> str
            llm_writer: Função LLM para geração de artigos.
                       Assinatura: (prompt: str) -> str
            verbose: Se True, imprime progresso detalhado.
        """
        self.base_dir = base_dir
        self.verbose = verbose
        self.llm_generator = llm_generator

        self.scoring_engine = IdeaScoringEngine(llm_evaluator=llm_evaluator)
        self.article_writer = IdeaArticleWriter(llm_writer=llm_writer)

        self.problemas = []
        self.idea_scores = []
        self.stats = {
            "total_problemas": 0,
            "total_ideias_geradas": 0,
            "total_criterios_por_ideia": TOTAL_CRITERIA,
            "pontuacao_maxima_possivel": MAX_POSSIBLE_SCORE,
            "tempo_inicio": None,
            "tempo_fim": None,
            "tempo_total_segundos": 0,
        }

    def log(self, msg: str):
        """Log condicional."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {msg}")

    # =========================================================================
    # ETAPA 1: CARREGAR PROBLEMAS
    # =========================================================================

    def carregar_problemas_json(self, filepath: str = None) -> int:
        """
        Carrega problemas do banco_geral_dados.json.

        Returns:
            Número de problemas carregados.
        """
        self.log("=" * 60)
        self.log("ETAPA 1: CARREGANDO PROBLEMAS")
        self.log("=" * 60)

        if filepath is None:
            filepath = os.path.join(self.base_dir, "banco_geral_dados.json")

        if not os.path.exists(filepath):
            self.log(f"[AVISO] Arquivo não encontrado: {filepath}")
            return 0

        with open(filepath, "r", encoding="utf-8") as f:
            dados = json.load(f)

        # O JSON pode ter estruturas diferentes — adaptamos
        if isinstance(dados, list):
            self.problemas = dados
        elif isinstance(dados, dict):
            # Pode ser dict com chave "problemas" ou "rankings"
            if "problemas" in dados:
                self.problemas = dados["problemas"]
            elif "rankings" in dados:
                self.problemas = dados["rankings"]
            else:
                # Tenta extrair de qualquer lista interna
                for key, value in dados.items():
                    if isinstance(value, list) and len(value) > 0:
                        self.problemas = value
                        break

        self.stats["total_problemas"] = len(self.problemas)
        self.log(f"Problemas carregados: {len(self.problemas)}")
        return len(self.problemas)

    def carregar_problemas_csv(self, arquivos: Optional[list] = None) -> int:
        """
        Carrega problemas de arquivos CSV.

        Returns:
            Número de problemas carregados.
        """
        self.log("=" * 60)
        self.log("ETAPA 1: CARREGANDO PROBLEMAS DE CSV")
        self.log("=" * 60)

        if arquivos is None:
            arquivos = self._descobrir_csvs()

        ids_vistos = set()
        for arquivo in arquivos:
            filepath = os.path.join(self.base_dir, arquivo)
            if not os.path.exists(filepath):
                self.log(f"[AVISO] Arquivo não encontrado: {filepath}")
                continue

            problemas_csv = self._ler_csv(filepath)
            for p in problemas_csv:
                titulo = p.get("Problema", "").strip()
                if titulo and titulo not in ids_vistos:
                    ids_vistos.add(titulo)
                    self.problemas.append(p)

        self.stats["total_problemas"] = len(self.problemas)
        self.log(f"Problemas carregados: {len(self.problemas)}")
        return len(self.problemas)

    def carregar_problema_unico(self, problema: dict) -> int:
        """
        Carrega um único problema para processar.

        Args:
            problema: Dict com chaves 'Problema', 'Descrição Geral', 'Desenvolvimento'.

        Returns:
            1 se carregado com sucesso.
        """
        self.problemas = [problema]
        self.stats["total_problemas"] = 1
        self.log(f"Problema carregado: {problema.get('Problema', 'N/A')}")
        return 1

    # =========================================================================
    # ETAPA 2: GERAR IDEIAS DE STARTUP
    # =========================================================================

    def gerar_ideias(self, limite: Optional[int] = None) -> list:
        """
        Gera ideias de startup para cada problema carregado.

        Args:
            limite: Se definido, processa apenas os primeiros N problemas.

        Returns:
            Lista de IdeaScore com as ideias geradas.
        """
        self.log("=" * 60)
        self.log("ETAPA 2: GERANDO IDEIAS DE STARTUP")
        self.log("=" * 60)

        self.stats["tempo_inicio"] = time.time()

        problemas_a_processar = (
            self.problemas[:limite] if limite else self.problemas
        )
        total = len(problemas_a_processar)

        self.idea_scores = []
        for i, problema in enumerate(problemas_a_processar, 1):
            titulo = problema.get("Problema", problema.get("problema", "N/A"))
            descricao = problema.get(
                "Descrição Geral",
                problema.get("Descricao Geral", problema.get("descricao", "")),
            )
            desenvolvimento = problema.get(
                "Desenvolvimento", problema.get("desenvolvimento", "")
            )

            self.log(f"Gerando ideia [{i}/{total}]: {titulo[:60]}...")

            # Gerar ideia via LLM ou template
            if self.llm_generator:
                prompt = IDEA_GENERATION_PROMPT_TEMPLATE.format(
                    problema_titulo=titulo,
                    problema_descricao=descricao,
                    problema_desenvolvimento=desenvolvimento,
                )
                ideia_descricao = self.llm_generator(prompt)
            else:
                ideia_descricao = self._gerar_ideia_template(
                    titulo, descricao, desenvolvimento
                )

            # Extrai nome e tagline se possível
            nome, tagline = self._extrair_nome_tagline(ideia_descricao)

            idea_score = IdeaScore(
                idea_id=i,
                problema_titulo=titulo,
                problema_descricao=descricao,
                problema_desenvolvimento=desenvolvimento,
                ideia_descricao=ideia_descricao,
                ideia_nome=nome,
                ideia_tagline=tagline,
            )

            self.idea_scores.append(idea_score)

            if i % 10 == 0:
                self.log(f"  Progresso: {i}/{total} ({i/total*100:.1f}%)")

        self.stats["total_ideias_geradas"] = len(self.idea_scores)
        self.log(f"Ideias geradas: {len(self.idea_scores)}")
        return self.idea_scores

    # =========================================================================
    # ETAPA 3: AVALIAR IDEIAS
    # =========================================================================

    def avaliar_ideias(self) -> list:
        """
        Avalia todas as ideias geradas contra o framework de 5 categorias.

        Returns:
            Lista de IdeaScore avaliados.
        """
        self.log("=" * 60)
        self.log("ETAPA 3: AVALIANDO IDEIAS")
        self.log("=" * 60)

        total = len(self.idea_scores)
        for i, idea_score in enumerate(self.idea_scores, 1):
            nome = idea_score.ideia_nome or idea_score.problema_titulo
            self.log(f"Avaliando [{i}/{total}]: {nome[:60]}...")
            self.scoring_engine.avaliar_ideia(idea_score)

            if i % 10 == 0:
                self.log(f"  Progresso: {i}/{total} ({i/total*100:.1f}%)")

        # Rankear
        self.idea_scores = self.scoring_engine.rankear_ideias(self.idea_scores)

        # Imprime top 10
        self.log("\nTOP 10 IDEIAS:")
        self.log("-" * 80)
        for score in self.idea_scores[:10]:
            nome = score.ideia_nome or score.problema_titulo
            self.log(
                f"  #{score.ranking:3d} | {score.pontuacao_total:6.0f}/"
                f"{score.pontuacao_maxima:.0f} ({score.percentual:5.1f}%) | "
                f"{nome[:55]}"
            )

        return self.idea_scores

    # =========================================================================
    # ETAPA 4: GERAR ARTIGOS
    # =========================================================================

    def gerar_artigos(self, limite: Optional[int] = None) -> int:
        """
        Gera artigos concisos (2 páginas) para as ideias avaliadas.

        Args:
            limite: Se definido, gera artigos apenas para as top N ideias.

        Returns:
            Número de artigos gerados.
        """
        self.log("=" * 60)
        self.log("ETAPA 4: GERANDO ARTIGOS")
        self.log("=" * 60)

        scores_para_artigo = (
            self.idea_scores[:limite] if limite else self.idea_scores
        )
        total = len(scores_para_artigo)

        for i, idea_score in enumerate(scores_para_artigo, 1):
            nome = idea_score.ideia_nome or idea_score.problema_titulo
            self.log(f"Gerando artigo [{i}/{total}]: {nome[:50]}...")
            artigo = self.article_writer.gerar_artigo(idea_score)
            idea_score.artigo = artigo

        self.log(f"Artigos gerados: {total}")
        return total

    # =========================================================================
    # ETAPA 5: EXPORTAR RESULTADOS
    # =========================================================================

    def exportar(self, output_dir: str = "ideias_startup") -> dict:
        """
        Exporta os resultados: artigos individuais e CSV resumo.

        Args:
            output_dir: Diretório de saída (relativo ao base_dir).

        Returns:
            Dicionário com caminhos dos arquivos gerados.
        """
        self.log("=" * 60)
        self.log("ETAPA 5: EXPORTANDO RESULTADOS")
        self.log("=" * 60)

        artigos_dir = os.path.join(self.base_dir, output_dir)
        os.makedirs(artigos_dir, exist_ok=True)

        # Exportar artigos individuais
        artigos_exportados = 0
        for score in self.idea_scores:
            if score.artigo:
                nome = score.ideia_nome or score.problema_titulo
                safe_name = "".join(
                    c if c.isalnum() or c in (" ", "-", "_") else "_"
                    for c in nome[:80]
                ).strip()
                filename = f"{score.ranking:03d}_{safe_name}.md"
                filepath = os.path.join(artigos_dir, filename)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(score.artigo)
                artigos_exportados += 1

        # Exportar CSV resumo
        csv_path = os.path.join(artigos_dir, "ranking_ideias.csv")
        self._exportar_csv_resumo(csv_path)

        # Exportar JSON completo
        json_path = os.path.join(artigos_dir, "ideias_avaliadas.json")
        self._exportar_json(json_path)

        self.stats["tempo_fim"] = time.time()
        self.stats["tempo_total_segundos"] = (
            self.stats["tempo_fim"] - self.stats["tempo_inicio"]
            if self.stats["tempo_inicio"]
            else 0
        )

        self.log(f"\nArquivos gerados:")
        self.log(f"  Artigos: {artigos_exportados} em {artigos_dir}/")
        self.log(f"  CSV Resumo: {csv_path}")
        self.log(f"  JSON Completo: {json_path}")

        return {
            "artigos_dir": artigos_dir,
            "artigos_exportados": artigos_exportados,
            "csv_resumo": csv_path,
            "json_completo": json_path,
        }

    # =========================================================================
    # PIPELINE COMPLETO
    # =========================================================================

    def executar_pipeline_completo(
        self,
        fonte: str = "json",
        arquivos_csv: Optional[list] = None,
        limite: Optional[int] = None,
        limite_artigos: Optional[int] = None,
        output_dir: str = "ideias_startup",
    ) -> dict:
        """
        Executa o pipeline completo.

        Args:
            fonte: 'json' para banco_geral_dados.json ou 'csv' para CSVs.
            arquivos_csv: Lista de CSVs (se fonte='csv').
            limite: Limitar número de problemas a processar.
            limite_artigos: Limitar número de artigos a gerar.
            output_dir: Diretório de saída.

        Returns:
            Dicionário com resultados e estatísticas.
        """
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║   STARTUP IDEA AGENT - Pipeline de Desenvolvimento      ║")
        self.log("║   Framework: 5 Categorias / 22 Critérios Ponderados     ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log("")

        # Etapa 1: Carregar
        if fonte == "json":
            n_problemas = self.carregar_problemas_json()
        else:
            n_problemas = self.carregar_problemas_csv(arquivos_csv)

        if n_problemas == 0:
            self.log("[ERRO] Nenhum problema carregado.")
            return {"erro": "Nenhum problema carregado"}

        # Etapa 2: Gerar ideias
        self.gerar_ideias(limite=limite)

        # Etapa 3: Avaliar ideias
        self.avaliar_ideias()

        # Etapa 4: Gerar artigos
        self.gerar_artigos(limite=limite_artigos)

        # Etapa 5: Exportar
        resultados = self.exportar(output_dir)

        # Estatísticas finais
        self._imprimir_estatisticas()

        return {
            "status": "sucesso",
            "problemas_carregados": n_problemas,
            "ideias_geradas": len(self.idea_scores),
            "artigos_gerados": resultados["artigos_exportados"],
            "arquivos": resultados,
            "stats": self.stats,
            "top_10": [
                {
                    "ranking": s.ranking,
                    "nome": s.ideia_nome or s.problema_titulo,
                    "pontuacao": s.pontuacao_total,
                    "percentual": s.percentual,
                }
                for s in self.idea_scores[:10]
            ],
        }

    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================

    def _gerar_ideia_template(
        self, titulo: str, descricao: str, desenvolvimento: str
    ) -> str:
        """Gera uma ideia de startup usando template quando não há LLM."""
        # Gera um nome composto a partir do título
        palavras = titulo.split()[:3]
        nome_base = palavras[0] if palavras else "Startup"

        return (
            f"**Nome da Startup:** {nome_base}Tech\n"
            f"**Tagline:** Resolvendo {titulo.lower()[:40]} de forma inteligente\n\n"
            f"**O que é:** Uma plataforma SaaS que automatiza e simplifica a "
            f"resolução do problema de {titulo.lower()}. Usando tecnologia "
            f"existente (APIs de IA, automação e integrações), a solução "
            f"transforma um processo que hoje é manual, fragmentado e frustrante "
            f"em uma experiência digital fluida e eficiente.\n\n"
            f"**Para quem:** Profissionais e empresas que sofrem diretamente "
            f"com {titulo.lower()}, especialmente aqueles que hoje dependem de "
            f"planilhas, WhatsApp e processos manuais para contornar o problema.\n\n"
            f"**Como funciona:**\n"
            f"1. O usuário conecta suas fontes de dados/processos existentes\n"
            f"2. A plataforma automatiza o fluxo central de resolução do problema\n"
            f"3. Dashboards e alertas garantem visibilidade e controle contínuos\n\n"
            f"**Modelo de negócio:** SaaS com assinatura mensal. Plano básico "
            f"gratuito (freemium) para atrair early adopters, planos pagos a "
            f"partir de R$99/mês com features avançadas e suporte.\n\n"
            f"**Diferencial 10x:** Enquanto as soluções atuais são fragmentadas, "
            f"genéricas ou exigem adaptação manual, esta plataforma foi "
            f"desenhada especificamente para este problema, entregando valor "
            f"nos primeiros 5 minutos de uso.\n\n"
            f"**MVP mínimo:** Landing page + fluxo Concierge via WhatsApp/email "
            f"simulando a automação manualmente para os 10 primeiros clientes."
        )

    def _extrair_nome_tagline(self, ideia_texto: str) -> tuple:
        """Extrai nome e tagline de uma ideia gerada."""
        nome = ""
        tagline = ""

        for linha in ideia_texto.split("\n"):
            linha_lower = linha.lower().strip()
            if "nome" in linha_lower and "startup" in linha_lower and ":" in linha:
                nome = linha.split(":", 1)[1].strip().strip("*").strip()
            elif "tagline" in linha_lower and ":" in linha:
                tagline = linha.split(":", 1)[1].strip().strip("*").strip()

            if nome and tagline:
                break

        return nome, tagline

    def _descobrir_csvs(self) -> list:
        """Descobre automaticamente arquivos CSV no diretório base."""
        csvs = []
        for f in sorted(os.listdir(self.base_dir)):
            if (
                f.endswith(".csv")
                and not f.startswith("output_")
                and f != "ranking_final.csv"
                and "ranking" not in f.lower()
            ):
                csvs.append(f)
        return csvs

    def _ler_csv(self, filepath: str) -> list:
        """Lê um arquivo CSV e retorna lista de dicionários."""
        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
        content = None

        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if content is None:
            return []

        problemas = []
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            cleaned = {}
            for key, value in row.items():
                clean_key = key.strip().replace("\ufeff", "")
                cleaned[clean_key] = value.strip() if value else ""

            if "Descricao Geral" in cleaned and "Descrição Geral" not in cleaned:
                cleaned["Descrição Geral"] = cleaned["Descricao Geral"]

            if cleaned.get("Problema"):
                problemas.append(cleaned)

        return problemas

    def _exportar_csv_resumo(self, filepath: str):
        """Exporta CSV resumo com ranking das ideias."""
        cat_names = get_category_names()

        headers = [
            "Ranking",
            "ID",
            "Nome da Ideia",
            "Problema Original",
            "Pontuação Total",
            "Percentual (%)",
        ]
        for cat_nome in cat_names.values():
            headers.append(f"{cat_nome} (%)")

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

            for s in self.idea_scores:
                row = [
                    s.ranking,
                    s.idea_id,
                    s.ideia_nome or s.problema_titulo,
                    s.problema_titulo,
                    f"{s.pontuacao_total:.1f}",
                    f"{s.percentual:.1f}",
                ]
                for cat_key in IDEA_SCORING_FRAMEWORK:
                    if cat_key in s.categorias:
                        row.append(f"{s.categorias[cat_key].percentual:.1f}")
                    else:
                        row.append("")
                writer.writerow(row)

    def _exportar_json(self, filepath: str):
        """Exporta JSON completo com todas as avaliações."""
        dados = []
        for s in self.idea_scores:
            item = {
                "ranking": s.ranking,
                "idea_id": s.idea_id,
                "ideia_nome": s.ideia_nome,
                "ideia_tagline": s.ideia_tagline,
                "problema_titulo": s.problema_titulo,
                "problema_descricao": s.problema_descricao,
                "ideia_descricao": s.ideia_descricao,
                "pontuacao_total": s.pontuacao_total,
                "pontuacao_maxima": s.pontuacao_maxima,
                "percentual": s.percentual,
                "categorias": {},
            }

            for cat_key, cat_score in s.categorias.items():
                item["categorias"][cat_key] = {
                    "nome": cat_score.categoria_nome,
                    "pontuacao_obtida": cat_score.pontuacao_obtida,
                    "pontuacao_maxima": cat_score.pontuacao_maxima,
                    "percentual": cat_score.percentual,
                    "criterios": [
                        {
                            "nome": c.criterio_nome,
                            "peso": c.peso,
                            "nota": c.nota,
                            "nota_ponderada": c.nota_ponderada,
                            "justificativa": c.justificativa,
                        }
                        for c in cat_score.criterios
                    ],
                }

            dados.append(item)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def _imprimir_estatisticas(self):
        """Imprime estatísticas finais da execução."""
        self.log("")
        self.log("╔══════════════════════════════════════════════════════════╗")
        self.log("║                 ESTATÍSTICAS FINAIS                     ║")
        self.log("╚══════════════════════════════════════════════════════════╝")
        self.log(f"  Problemas carregados: {self.stats['total_problemas']}")
        self.log(f"  Ideias geradas: {self.stats['total_ideias_geradas']}")
        self.log(f"  Critérios por ideia: {TOTAL_CRITERIA}")
        self.log(
            f"  Total de avaliações: {len(self.idea_scores) * TOTAL_CRITERIA}"
        )
        self.log(f"  Pontuação máxima possível: {MAX_POSSIBLE_SCORE}")

        if self.idea_scores:
            melhor = self.idea_scores[0]
            pior = self.idea_scores[-1]
            media = sum(s.percentual for s in self.idea_scores) / len(
                self.idea_scores
            )

            melhor_nome = melhor.ideia_nome or melhor.problema_titulo
            pior_nome = pior.ideia_nome or pior.problema_titulo

            self.log(
                f"\n  Melhor: #{melhor.ranking} {melhor_nome[:40]}... "
                f"({melhor.percentual:.1f}%)"
            )
            self.log(
                f"  Pior:   #{pior.ranking} {pior_nome[:40]}... "
                f"({pior.percentual:.1f}%)"
            )
            self.log(f"  Média:  {media:.1f}%")

        tempo = self.stats.get("tempo_total_segundos", 0)
        self.log(f"\n  Tempo total: {tempo:.1f}s")

    def info(self) -> str:
        """Retorna informações sobre o framework de avaliação."""
        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║        STARTUP IDEA AGENT - Framework v1.0                  ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║                                                            ║",
            "║  Agente especializado em desenvolver problemas societais    ║",
            "║  em ideias concretas de startup.                            ║",
            "║                                                            ║",
            "║  Capacidades:                                               ║",
            "║  - Gerar ideias de startup a partir de problemas            ║",
            "║  - Avaliar com framework de 5 categorias / 22 critérios    ║",
            "║  - Gerar artigos concisos (2 páginas)                       ║",
            "║  - Business Model Canvas narrativo                          ║",
            "║  - Análise de concorrentes e MVP                            ║",
            "║  - Exportar em CSV, JSON e Markdown                         ║",
            "║                                                            ║",
            "╠══════════════════════════════════════════════════════════════╣",
            "║  CATEGORIAS DE AVALIAÇÃO                                    ║",
            "╠══════════════════════════════════════════════════════════════╣",
        ]

        total_criterios = 0
        for cat_key, category in IDEA_SCORING_FRAMEWORK.items():
            n_crits = len(category["criterios"])
            total_criterios += n_crits
            peso_total = sum(c["peso"] for c in category["criterios"].values())
            lines.append(f"║  {category['nome'][:50]:<50} ║")
            lines.append(
                f"║    Critérios: {n_crits} | Peso total: {peso_total:<23} ║"
            )
            lines.append(
                f"║    Escola: {category['escola_base'][:45]:<45}  ║"
            )
            lines.append(
                "║                                                            ║"
            )

        lines.append(
            "╠══════════════════════════════════════════════════════════════╣"
        )
        lines.append(
            f"║  Total: {total_criterios} critérios | "
            f"Pontuação máx: {MAX_POSSIBLE_SCORE:<14}   ║"
        )
        lines.append(
            "╚══════════════════════════════════════════════════════════════╝"
        )

        return "\n".join(lines)

    def obter_artigo(self, ranking_position: int) -> Optional[str]:
        """Retorna o artigo de uma ideia pelo ranking."""
        for score in self.idea_scores:
            if score.ranking == ranking_position:
                return score.artigo
        return None

    def obter_analise(self, ranking_position: int) -> Optional[str]:
        """Retorna a análise formatada de uma ideia pelo ranking."""
        for score in self.idea_scores:
            if score.ranking == ranking_position:
                return self.scoring_engine.formatar_pontuacao(score)
        return None
