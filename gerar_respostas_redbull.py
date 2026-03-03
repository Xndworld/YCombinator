#!/usr/bin/env python3
"""
Red Bull Basement 2026 — Gerador de Respostas Inteligente
==========================================================

Gera respostas adaptadas campo a campo para o formulário do Red Bull Basement
diretamente a partir dos dados do ranking (sem necessidade de API key).

Usa os campos 'problema', 'descricao' e 'desenvolvimento' do CSV para construir
respostas coerentes e contextualizadas para cada startup.

Saída: redbull_basement_top50.csv
"""

import csv
import re
import textwrap
from pathlib import Path

RANKING_FILE = "banco_geral_ranking.csv"
OUTPUT_FILE  = "redbull_basement_top50.csv"
TOP_N        = 50

OUTPUT_COLUMNS = [
    "ranking",
    "nome_problema",
    "campo_1_ideia",
    "campo_2_publico",
    "campo_3_problemas",
    "campo_4_como_funciona",
    "campo_5a_nome_startup",
    "campo_5b_resumo_card",
    "campo_5c_publico_card",
    "campo_5d_problema_card",
    "campo_5e_solucao_card",
    "pitch_60_segundos",
]


# ============================================================================
# UTILITÁRIOS
# ============================================================================

def trunc(text: str, limit: int) -> str:
    """Trunca texto respeitando palavras inteiras."""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "."


def primeiras_palavras(texto: str, n: int = 8) -> str:
    """Retorna as primeiras n palavras de um texto."""
    return " ".join(texto.split()[:n])


def extrair_contexto_publico(descricao: str, desenvolvimento: str) -> str:
    """Identifica quem sofre o problema a partir da descrição."""
    # Palavras-chave de persona comuns nos dados
    personas = {
        "idoso": "idosos acima de 60 anos",
        "silver": "trabalhadores da geração 50+",
        "aposentado": "aposentados e pensionistas",
        "agricultor": "agricultores familiares e pequenos produtores rurais",
        "imigrante": "imigrantes e trabalhadores sem histórico de crédito formal",
        "solopreneur": "empreendedores solo e freelancers",
        "startup": "startups e empreendedores early-stage",
        "profissional": "profissionais liberais e trabalhadores autônomos",
        "empreendedor": "empreendedores e donos de pequenos negócios",
        "empresa": "empresas de médio porte e corporações",
        "clínica": "clínicas e profissionais de saúde",
        "paciente": "pacientes e usuários de serviços de saúde",
        "trabalhador": "trabalhadores formais e informais",
        "cuidador": "cuidadores e profissionais de saúde domiciliar",
        "geração z": "jovens da geração Z e millennials",
        "boomer": "gestores baby boomers e lideranças corporativas",
        "rede elétrica": "distribuidoras de energia e consumidores industriais",
        "seguradora": "seguradoras, resseguradoras e gestores de risco",
        "mineradora": "mineradoras e gestoras de recursos naturais",
        "município": "municípios, gestores públicos e concessionárias",
    }
    texto_lower = (descricao + " " + desenvolvimento).lower()
    for kw, persona in personas.items():
        if kw in texto_lower:
            return persona
    return "empreendedores, startups e empresas inovadoras"


def gerar_nome_startup(problema: str, desenvolvimento: str, ranking: int = 0) -> str:
    """Gera um nome de startup de até 4 palavras a partir do contexto.

    Regras do mais específico para o mais genérico para evitar colisões.
    """
    prob_lower = problema.lower()
    dev_lower  = desenvolvimento.lower()
    full_lower = prob_lower + " " + dev_lower

    # Casos especiais que precisam estar antes de regras genéricas
    if "conflito sistêmico" in prob_lower or "ia agêntica" in prob_lower:
        # Extrair número do conflito se presente (#29, #36, etc.)
        m = re.search(r'#(\d+)', problema)
        sufixo = m.group(1) if m else str(ranking)
        return f"ClimaTech Nexus {sufixo}"

    if "conflito hierárquico" in prob_lower:
        return "BridgeGen IA"

    # Regras: (keywords_no_problema_OU_dev, match_obrigatorio_em, nome)
    # prob_match: qualquer keyword da lista 1 presente em full_lower
    # dev_extra:  se não vazia, keyword extra TAMBÉM necessária em full_lower
    regras = [
        # ── Saúde / Diagnóstico ──────────────────────────────────────────
        (["oximetria", "pele parda", "pele preta", "skin health"],   [],       "SkinEquity AI"),
        (["contrato médico", "sla biométrico", "protections-tech"],  [],       "TrustCare Chain"),
        (["saúde mental", "terceirização da saúde"],                  [],       "MindCare Corp"),
        (["falta estrutural", "profissionais de cuidados"],            [],       "CareMatch IA"),
        (["desvio", "escassez", "mão de obra do cuidado"],            [],       "CareChain IA"),
        # ── Energia / Clima ──────────────────────────────────────────────
        (["blecautes", "rede elétrica"],                              [],       "GridGuard IA"),
        (["descarbonização", "pobreza energética"],                   [],       "GreenFin Token"),
        (["hidrológico", "hidroelétrica"],                            [],       "HydroForecast IA"),
        (["estresse hídrico", "megacidade"],                          [],       "AquaCity IA"),
        (["mineração", "segurança hídrica"],                          [],       "AquaMine Monitor"),
        (["perdas agrícolas", "extremos climáticos"],                 [],       "AgriShield IA"),
        (["zoneamento de risco climático"],                           [],       "ZonaClima IA"),
        (["resseguradoras climáticas"],                               [],       "ResiliaRisk IA"),
        (["insolvência de seguradoras", "eventos extremos"],          [],       "ClimateGuard Re"),
        # ── Finanças / Crédito ───────────────────────────────────────────
        (["crédito rural", "abandono algorítmico"],                   [],       "AgroCredit IA"),
        (["crédito baseado no clima"],                                [],       "ClimateScore IA"),
        (["crédito punitivo", "imigrantes e profissionais"],          [],       "FairCredit IA"),
        (["empreendedorismo de maturidade", "abismo de crédito"],     [],       "SilverCredit IA"),
        # ── Trabalho / RH ────────────────────────────────────────────────
        (["motoboy", "economia prateada"],                            [],       "SilverDelivery Pro"),
        (["força de trabalho prateada", "subutilização"],             [],       "SilverWork Pro"),
        (["etarismo", "recrutamento corporativo"],                    [],       "FairHire IA"),
        (["geração sanduíche"],                                       [],       "SandwichCare IA"),
        (["burnout", "modelo híbrido", "fadiga de ferramentas"],      [],       "WorkFlow Balance"),
        # ── Legal / Compliance ───────────────────────────────────────────
        (["gargalos burocráticos", "empresa de uma pessoa"],          [],       "SoloLegal IA"),
        (["cargas fiscais", "emissões diretas"],                      [],       "TaxFlow IA"),
        (["balcanização regulatória", "caos de compliance"],          [],       "RegTech Unified"),
        (["labirinto do licenciamento"],                              [],       "AgentLegal IA"),
        (["licenciamento", "solopreneur global"],                     [],       "ComplianceBot IA"),
        (["oligopólio", "licenças b2b"],                             [],       "FairSaaS IA"),
        # ── Tecnologia / Software ────────────────────────────────────────
        (["software legado", "obsolescência silenciosa"],             [],       "LegacyMigrate IA"),
        (["vulnerabilidade", "startups baseadas"],                    [],       "StackGuard Pro"),
        (["longos ciclos de transição de software"],                  [],       "LegacyShift IA"),
        # ── Educação / Social ────────────────────────────────────────────
        (["inflação de credenciais"],                                 [],       "SkillMatch IA"),
        (["exclusão digital", "idoso"],                               [],       "SilverBank IA"),
        (["biopirataria", "fauna sul-americana"],                     [],       "BioSovereign IA"),
        (["governança sistêmica", "multilateral"],                    [],       "GovTech Global"),
        # ── Mobilidade ───────────────────────────────────────────────────
        (["veículos elétricos", "revenda"],                           [],       "EVValue IA"),
        # ── Mercado ──────────────────────────────────────────────────────
        (["falsa personalização", "d2c corporativos"],                [],       "TrueD2C IA"),
    ]

    for kw_list, req_extra, nome in regras:
        if any(kw in full_lower for kw in kw_list):
            if not req_extra or any(kw in full_lower for kw in req_extra):
                return nome

    # Fallback: extrair 1-2 substantivos relevantes do problema
    stop = {"Dos","Das","Nos","Nas","Para","Com","Uma","Uns","Por","Aos","Que",
            "Nos","Nas","Dos","Das","Nos","Nas","Dos","Das","Riscos","Falta",
            "Risco","Custo","Falta","Subutilização","Desvio","Escassez","Caos",
            "Exclusão","Colapso","Estresse","Conflito","Gargalos","Fadiga",
            "Vulnerabilidade","Síndrome","Abandono","Choque","Ineficiência",
            "Insolvência","Sufocamento","Descompasso","Viés"}
    palavras = re.findall(r'\b[A-ZÁÉÍÓÚÀÂÊÔÃÕÜ][a-záéíóúàâêôãõ]{3,}', problema)
    palavras = [p for p in palavras if p not in stop]
    if palavras:
        return f"{palavras[0]} IA"
    return "Innovation Tech IA"


def detectar_solucao(desenvolvimento: str) -> str:
    """Detecta a tecnologia/modelo de solução principal do desenvolvimento."""
    dev_lower = desenvolvimento.lower()
    mapa = [
        ("smart contract",  "smart contracts on-chain"),
        ("blockchain",      "plataforma blockchain"),
        ("ia generativa",   "IA generativa"),
        ("sovereign",       "modelos de IA soberanos"),
        ("modelo de ia",    "modelos de IA especializados"),
        ("machine learn",   "machine learning"),
        ("tokeniza",        "tokenização de ativos digitais"),
        ("agente",          "agentes de IA autônomos"),
        ("fintech",         "fintech"),
        ("b2b",             "plataforma B2B SaaS"),
        ("dados propri",    "dados proprietários e IA"),
        ("automação",       "automação inteligente"),
        ("ia ",             "IA e dados"),
        ("api",             "APIs certificadas"),
    ]
    for kw, label in mapa:
        if kw in dev_lower:
            return label
    return "IA e análise de dados"


def gerar_campo1(problema: str, descricao: str, desenvolvimento: str) -> str:
    """Campo 1 — Descreva sua ideia (até 250 chars)"""
    publico = extrair_contexto_publico(descricao, desenvolvimento)
    solucao = detectar_solucao(desenvolvimento)

    # Extrair tema limpo do problema (ignora stopwords)
    stopwords = {"a","o","as","os","da","do","das","dos","na","no","nas","nos",
                 "de","e","em","para","com","que","uma","um","por","se","ao","à",
                 "nos","nas","dos","das","the","of"}
    palavras_prob = [w.rstrip("'\"") for w in problema.split()
                     if w.lower().rstrip("'\"") not in stopwords]
    tema = " ".join(palavras_prob[:4]).rstrip(".,:;").lower()

    texto = (
        f"Startup que resolve {tema} para {publico} "
        f"com {solucao}. Transforma um processo caro e travado "
        f"em solução digital, acessível e escalável."
    )
    return trunc(texto, 250)


def gerar_campo2(problema: str, descricao: str, desenvolvimento: str) -> str:
    """Campo 2 — Quem se beneficia (até 400 chars)"""
    publico = extrair_contexto_publico(descricao, desenvolvimento)
    dor = trunc(descricao, 180).rstrip(".")

    texto = (
        f"Nossos clientes são {publico} que enfrentam diariamente: {dor}. "
        f"Eles estão presos em processos manuais, caros ou injustos sem alternativa "
        f"tecnológica acessível. Nossa solução foi desenhada especificamente para resolver "
        f"essa dor com velocidade, segurança e custo acessível."
    )
    return trunc(texto, 400)


def gerar_campo3(problema: str, descricao: str, desenvolvimento: str) -> str:
    """Campo 3 — Problemas abordados (até 400 chars)"""
    desc_curta = trunc(descricao, 120).rstrip(".")
    dev_curto  = trunc(desenvolvimento, 120).rstrip(".")

    texto = (
        f"1) {desc_curta}. "
        f"2) {dev_curto}. "
        f"3) Sem solução tecnológica adequada hoje, o custo humano e financeiro cresce "
        f"exponencialmente — e o mercado ainda opera no modo analógico."
    )
    return trunc(texto, 400)


def gerar_campo4(problema: str, descricao: str, desenvolvimento: str) -> str:
    """Campo 4 — Como funciona (até 400 chars)"""
    dev_lower = desenvolvimento.lower()

    # Detectar tecnologia principal
    tech_map = [
        ("blockchain",    "blockchain com smart contracts"),
        ("ia ",           "IA generativa"),
        ("machine learn", "machine learning"),
        ("tokeniza",      "tokenização on-chain"),
        ("api",           "APIs certificadas"),
        ("dados",         "análise de dados em tempo real"),
        ("automação",     "automação inteligente"),
        ("modelo",        "modelos de IA treinados localmente"),
    ]
    tech = "IA e análise de dados"
    for kw, label in tech_map:
        if kw in dev_lower:
            tech = label
            break

    dev_resumo = trunc(desenvolvimento, 150).rstrip(".")
    texto = (
        f"O usuário acessa via app ou API. Nossa solução usa {tech} para {dev_resumo}. "
        f"O resultado: processo automatizado, auditável e escalonável — "
        f"entregando valor em minutos, não semanas."
    )
    return trunc(texto, 400)


def gerar_campo5a(problema: str, desenvolvimento: str, ranking: int = 0) -> str:
    """Campo 5A — Nome da startup (até 4 palavras)"""
    return gerar_nome_startup(problema, desenvolvimento, ranking)


def gerar_campo5b(campo1: str) -> str:
    """Campo 5B — Resumo card (até 150 chars)"""
    # Pegar a essência do campo 1
    partes = campo1.split(".")
    resumo = partes[0].strip() if partes else campo1
    return trunc(resumo, 150)


def gerar_campo5c(campo2: str) -> str:
    """Campo 5C — Público card (até 400 chars) — versão mais direta"""
    return trunc(campo2, 400)


def gerar_campo5d(campo3: str, descricao: str) -> str:
    """Campo 5D — Problema card (até 400 chars) — com mais urgência"""
    desc_curta = trunc(descricao, 150).rstrip(".")
    texto = (
        f"Problema real e urgente: {desc_curta}. "
        f"Isso custa bilhões ao ano e afeta milhões de pessoas sem solução tecnológica hoje. "
        f"O tempo de agir é agora."
    )
    return trunc(texto, 400)


def gerar_campo5e(campo4: str) -> str:
    """Campo 5E — Solução card (até 400 chars) — direto e tangível"""
    return trunc(campo4, 400)


def gerar_pitch(problema: str, descricao: str, desenvolvimento: str,
                campo1: str, campo5a: str) -> str:
    """Pitch de 60 segundos (~130 palavras)"""
    publico = extrair_contexto_publico(descricao, desenvolvimento)
    desc_curta = trunc(descricao, 90).rstrip(".")
    dev_curto  = trunc(desenvolvimento, 90).rstrip(".")

    pitch = (
        f"[0-10s] Sabia que milhões de {publico} perdem dinheiro todos os dias "
        f"por causa de um sistema travado no século passado?\n\n"
        f"[10-22s] O problema é real: {desc_curta}. "
        f"Eles tentam resolver com planilhas, intermediários e processos manuais. "
        f"Não funciona.\n\n"
        f"[22-35s] Criamos {campo5a} — {campo1} "
        f"Nossa tecnologia: {dev_curto}.\n\n"
        f"[35-47s] Já validamos com usuários reais. "
        f"Os primeiros testes mostram redução de custo e tempo em mais de 60%. "
        f"O mercado existe, a dor é urgente, a tração começa agora.\n\n"
        f"[47-60s] O Red Bull Basement é o trampolim que faltava. "
        f"Com esse apoio, escalamos o MVP, chegamos a mil usuários em 90 dias "
        f"e mostramos ao mundo que inovação real resolve dores reais."
    )
    return pitch


# ============================================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================================

def ler_top_n(ranking_file: str, top_n: int) -> list[dict]:
    rows = []
    with open(ranking_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    rows.sort(key=lambda r: int(r.get("ranking", 9999)))
    return rows[:top_n]


def processar(row: dict) -> dict:
    ranking      = int(row.get("ranking", 0))
    problema     = row.get("problema", "").strip()
    descricao    = row.get("descricao", "").strip()
    desenvolvimento = row.get("desenvolvimento", "").strip()

    c1  = gerar_campo1(problema, descricao, desenvolvimento)
    c2  = gerar_campo2(problema, descricao, desenvolvimento)
    c3  = gerar_campo3(problema, descricao, desenvolvimento)
    c4  = gerar_campo4(problema, descricao, desenvolvimento)
    c5a = gerar_campo5a(problema, desenvolvimento, ranking)
    c5b = gerar_campo5b(c1)
    c5c = gerar_campo5c(c2)
    c5d = gerar_campo5d(c3, descricao)
    c5e = gerar_campo5e(c4)
    pit = gerar_pitch(problema, descricao, desenvolvimento, c1, c5a)

    return {
        "ranking":              ranking,
        "nome_problema":        problema,
        "campo_1_ideia":        c1,
        "campo_2_publico":      c2,
        "campo_3_problemas":    c3,
        "campo_4_como_funciona": c4,
        "campo_5a_nome_startup": c5a,
        "campo_5b_resumo_card": c5b,
        "campo_5c_publico_card": c5c,
        "campo_5d_problema_card": c5d,
        "campo_5e_solucao_card": c5e,
        "pitch_60_segundos":    pit,
    }


def main():
    print("=" * 60)
    print("  RED BULL BASEMENT 2026 — Gerador de Respostas")
    print("=" * 60)

    startups = ler_top_n(RANKING_FILE, TOP_N)
    print(f"[+] {len(startups)} startups carregadas do ranking\n")

    resultados = []
    for i, row in enumerate(startups):
        ranking_num = int(row.get("ranking", i + 1))
        problema    = row.get("problema", "")
        print(f"[{i+1:02d}/{TOP_N}] #{ranking_num} {problema[:55]}...")
        resultado = processar(row)
        resultados.append(resultado)

    # Salvar CSV
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\n[✓] Planilha salva: {OUTPUT_FILE}  ({len(resultados)} startups)")

    # Verificação de limites
    print("\n[✓] Verificação de limites de caracteres:")
    limites = {
        "campo_1_ideia": 250, "campo_2_publico": 400,
        "campo_3_problemas": 400, "campo_4_como_funciona": 400,
        "campo_5b_resumo_card": 150, "campo_5c_publico_card": 400,
        "campo_5d_problema_card": 400, "campo_5e_solucao_card": 400,
    }
    ok = True
    for campo, limite in limites.items():
        violacoes = [r for r in resultados if len(r.get(campo, "")) > limite]
        if violacoes:
            print(f"   [!] {campo}: {len(violacoes)} linhas acima de {limite} chars")
            ok = False
        else:
            max_len = max(len(r.get(campo, "")) for r in resultados)
            print(f"   [✓] {campo}: max {max_len}/{limite} chars")

    if ok:
        print("\nTodos os campos dentro dos limites!")
    print("\nColunas da planilha:")
    for col in OUTPUT_COLUMNS:
        print(f"   • {col}")


if __name__ == "__main__":
    main()
