#!/usr/bin/env python3
"""
Migração de Dados - Converte estrutura antiga para banco JSON centralizado.

Converte:
    dados/02_problemas/banco_geral_dados.json (formato antigo, 1.4MB)
    →  dados/banco/problemas.json (formato novo, compacto)

Uso:
    python agentes/migrar_dados.py
"""

import json
import os
import sys

# Adiciona raiz ao path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from agentes.banco_dados import (
    BancoDados, calcular_scores, gerar_tags, BANCO_DIR
)


def migrar_problemas():
    """Migra banco_geral_dados.json para o novo formato."""
    antigo_path = os.path.join(
        PROJECT_ROOT, "dados", "02_problemas", "banco_geral_dados.json"
    )

    if not os.path.exists(antigo_path):
        print("[ERRO] Arquivo antigo não encontrado:", antigo_path)
        return False

    with open(antigo_path, "r", encoding="utf-8") as f:
        dados_antigos = json.load(f)

    print(f"[INFO] Carregados {len(dados_antigos)} problemas do formato antigo")

    # Converte cada problema
    novos_itens = []
    for i, antigo in enumerate(dados_antigos, 1):
        notas = antigo.get("notas", {})
        scores = calcular_scores(notas)
        titulo = antigo.get("problema", "")
        descricao = antigo.get("descricao", "")
        desenvolvimento = antigo.get("desenvolvimento", "")

        novo = {
            "id": f"P{i:04d}",
            "titulo": titulo,
            "descricao": descricao,
            "desenvolvimento": desenvolvimento,
            "batch": antigo.get("batch", "2026-03-01_initial"),
            "fonte": antigo.get("arquivo_fonte", ""),
            "notas": notas,
            "scores": scores,
            "tags": gerar_tags(titulo, descricao, notas),
            "ranking": 0,  # será recalculado
        }

        novos_itens.append(novo)

    # Rankear por score descendente
    novos_itens.sort(key=lambda x: x["scores"]["pct"], reverse=True)
    for i, item in enumerate(novos_itens, 1):
        item["ranking"] = i

    # Gera o banco novo
    banco_novo = {
        "versao": "2.0",
        "total": len(novos_itens),
        "itens": novos_itens,
    }

    os.makedirs(BANCO_DIR, exist_ok=True)
    banco = BancoDados()
    banco.salvar_problemas(banco_novo)

    # Tamanho comparativo
    tamanho_antigo = os.path.getsize(antigo_path)
    tamanho_novo = os.path.getsize(os.path.join(BANCO_DIR, "problemas.json"))

    print(f"\n[OK] Migração concluída!")
    print(f"  Problemas migrados: {len(novos_itens)}")
    print(f"  Top 5:")
    for item in novos_itens[:5]:
        print(f"    #{item['ranking']} ({item['scores']['pct']}%) {item['titulo'][:60]}")
    print(f"\n  Tamanho antigo: {tamanho_antigo / 1024:.0f} KB")
    print(f"  Tamanho novo:   {tamanho_novo / 1024:.0f} KB")
    print(f"  Redução:        {(1 - tamanho_novo / tamanho_antigo) * 100:.0f}%")

    return True


def inicializar_bancos_vazios():
    """Cria os arquivos JSON para soluções, startups e bancas."""
    banco = BancoDados()

    for path, nome in [
        (banco._solucoes_path, "solucoes"),
        (banco._startups_path, "startups"),
        (banco._bancas_path, "bancas"),
    ]:
        if not os.path.exists(path):
            data = {"versao": "1.0", "total": 0, "itens": []}
            if nome == "solucoes":
                data["top_100"] = []
            if nome == "bancas":
                data["avaliacoes"] = []
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            print(f"[OK] Criado: {nome}.json")


def main():
    print("=" * 60)
    print("  MIGRAÇÃO DE DADOS → BANCO JSON CENTRALIZADO")
    print("=" * 60)

    migrar_problemas()
    inicializar_bancos_vazios()

    # Estatísticas finais
    banco = BancoDados()
    stats = banco.stats()
    print(f"\n--- Banco Centralizado ---")
    print(f"  Problemas: {stats['problemas']}")
    print(f"  Soluções:  {stats['solucoes']}")
    print(f"  Startups:  {stats['startups']}")
    print(f"  Bancas:    {stats['avaliacoes_bancas']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
