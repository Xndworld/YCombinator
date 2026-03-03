#!/usr/bin/env python3
"""
RegFlow AI — Orquestrador Central
=================================

Gerencia o ciclo de vida completo do sistema:
1. Rankeamento de Problemas (YC Ranker)
2. Articulação de Soluções (Bando de Cinco / Desenvolvedor)
3. Avaliação por Bancas (RedBull / YC)
4. Persistência de Dados (DB Writer)

Uso:
    python orquestrador/main.py rank-problems
    python orquestrador/main.py articulate
    python orquestrador/main.py evaluate-redbull
    python orquestrador/main.py run-all
"""

import sys
import os
import argparse
from typing import Optional

# Adiciona a raiz ao sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from database.db_writer import BancoDados, PROBLEMAS_JSON, SOLUCOES_JSON, STARTUPS_JSON, BANCAS_JSON
from agentes.rankers.yc_ranker.yc_ranker import avaliar_batch, consolidar_banco_geral, sincronizar_com_banco_central
from agentes.articuladores.agent import StartupIdeaAgent
from agentes.bancas.redbull.agent import RBBJudgeAgent

class Orchestrator:
    def __init__(self, verbose: bool = True):
        self.db = BancoDados()
        self.verbose = verbose

    def log(self, msg: str):
        if self.verbose:
            print(f"[ORQUESTRADOR] {msg}")

    def phase_1_rank_problems(self, batch_name: str = "initial"):
        """Executa o ranking de problemas usando o YC Ranker."""
        self.log(f"Iniciando Fase 1: Ranking de Problemas (Batch: {batch_name})")
        # Nota: Por padrão usamos heurística para evitar custos sem aprovação
        avaliar_batch(ROOT, batch_name, mode="heuristic")
        resultados = consolidar_banco_geral(ROOT)
        sincronizar_com_banco_central(resultados)
        self.log("Fase 1 concluída. Dados salvos em dados/banco/problemas.json")

    def phase_2_articulate(self, limite: int = 10):
        """Transforma problemas em ideias de startup (Articulador)."""
        self.log(f"Iniciando Fase 2: Articulação de Soluções (Top {limite} problemas)")
        
        agent = StartupIdeaAgent(base_dir=ROOT, verbose=self.verbose)
        # Carrega do novo local central
        agent.carregar_problemas_json(PROBLEMAS_JSON)
        
        # Gera e avalia (internal heuristic do agent se sem LLM)
        agent.gerar_ideias(limite=limite)
        agent.avaliar_ideias()
        
        # Exporta (isso gera os arquivos e o ranking_ideias.csv)
        resultados = agent.exportar("artigos")
        
        # Sincroniza com solucoes.json
        # Convertendo IdeaScore para dict compatível com db_writer
        solucoes_formatadas = []
        for s in agent.idea_scores:
            solucoes_formatadas.append({
                "titulo": s.ideia_nome or s.problema_titulo,
                "descricao": s.ideia_descricao,
                "score": s.percentual,
                "metricas": {cat: cs.percentual for cat, cs in s.categorias.items()}
            })
        
        # Salva no banco central
        # Nota: StartupIdeaAgent lida com problemas, aqui vinculamos
        for i, sol in enumerate(solucoes_formatadas):
            prob_id = agent.idea_scores[i].problema_titulo # Simplificação se ID não disponível
            # Na verdade, precisamos do ID real do problemas.json. 
            # O orchestrator deve gerenciar isso melhor.
            pass

        self.db.adicionar_solucoes(solucoes_formatadas, "MULTIPLE", agente_id=1)
        self.log("Fase 2 concluída. Ideias salvas em dados/banco/solucoes.json")

    def phase_3_evaluate_redbull(self, limite: int = 5):
        """Avalia as top soluções na banca RedBull."""
        self.log(f"Iniciando Fase 3: Avaliação Banca RedBull (Top {limite} soluções)")
        
        judge = RBBJudgeAgent(base_dir=ROOT, verbose=self.verbose)
        # Carrega artigos gerados na fase anterior
        judge.carregar_contexto(diretorio=os.path.join(ROOT, "artigos"))
        judge.avaliar(limite=limite)
        judge.rankear()
        judge.exportar(output_ranking="relatorios/rbb_ranking.csv")
        
        self.log("Fase 3 concluída. Relatório em relatorios/rbb_ranking.csv")

def main():
    parser = argparse.ArgumentParser(description="RegFlow AI Orchestrator")
    parser.add_argument("command", choices=["rank", "articulate", "evaluate", "run-all"])
    parser.add_argument("--batch", default="2026-03-01_initial")
    parser.add_argument("--limite", type=int, default=10)
    
    args = parser.parse_args()
    orch = Orchestrator()

    if args.command == "rank":
        orch.phase_1_rank_problems(args.batch)
    elif args.command == "articulate":
        orch.phase_2_articulate(args.limite)
    elif args.command == "evaluate":
        orch.phase_3_evaluate_redbull(args.limite)
    elif args.command == "run-all":
        orch.phase_1_rank_problems(args.batch)
        orch.phase_2_articulate(args.limite)
        orch.phase_3_evaluate_redbull(5)

if __name__ == "__main__":
    main()
