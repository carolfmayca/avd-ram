#!/usr/bin/env python3
"""Análise de um projeto fatorial 2^k r para o Mini Estudo 2 (ICC305).

Lê um CSV com as medições da matriz experimental, calcula:
  - q0, efeitos principais e interações (tabela de sinais);
  - soma de quadrados (SQ) de cada termo e do erro experimental;
  - percentual da variação explicada por cada termo;
  - resumo por combinação (média e desvio padrão das replicações).

Métrica principal: percentual de uso da RAM (uso_percent).

Formato esperado do CSV (uma linha por medição):
    A,B,C,rep,uso_percent
onde A, B, C ∈ {-1, +1} são os níveis codificados dos fatores e `rep`
identifica a replicação (1..r). Linhas com uso_percent vazio são ignoradas
(células ainda não coletadas), permitindo rodar com o template parcial.

Uso:
    python analise_fatorial.py dados_2k_r.csv
"""

from __future__ import annotations

import csv
import sys
from itertools import combinations
from pathlib import Path

# Fatores do projeto. Ajuste os rótulos se os fatores mudarem.
FATORES = ["A", "B", "C"]
ROTULOS = {
    "A": "Sistema Operacional (Linux=-1, Windows=+1)",
    "B": "Tamanho da RAM (8 GB=-1, 16 GB=+1)",
    "C": "Carga de trabalho (repouso=-1, pesada=+1)",
}


def termos(fatores):
    """Lista de termos do modelo: efeitos principais + interações."""
    todos = []
    for ordem in range(1, len(fatores) + 1):
        for combo in combinations(fatores, ordem):
            todos.append("".join(combo))
    return todos


def ler_csv(caminho):
    """Retorna lista de dicts {A,B,C,rep,y} ignorando medições vazias."""
    linhas = []
    with open(caminho, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            bruto = (linha.get("uso_percent") or "").strip()
            if bruto == "":
                continue  # célula ainda não coletada
            registro = {fator: int(linha[fator]) for fator in FATORES}
            registro["rep"] = linha.get("rep", "")
            registro["y"] = float(bruto.replace(",", "."))
            linhas.append(registro)
    return linhas


def sinal(linha, termo):
    """Produto dos níveis dos fatores que compõem o termo (coluna de sinais)."""
    s = 1
    for fator in termo:
        s *= linha[fator]
    return s


def analisar(linhas):
    k = len(FATORES)
    n_comb = 2**k
    todos_termos = termos(FATORES)

    # Agrupa por combinação (assinatura dos sinais dos fatores principais).
    grupos = {}
    for linha in linhas:
        chave = tuple(linha[fator] for fator in FATORES)
        grupos.setdefault(chave, []).append(linha["y"])

    if len(grupos) != n_comb:
        print(f"[aviso] esperadas {n_comb} combinações, encontradas {len(grupos)}.")

    r_por_comb = {chave: len(ys) for chave, ys in grupos.items()}
    r = min(r_por_comb.values()) if r_por_comb else 0
    if len(set(r_por_comb.values())) > 1:
        print(f"[aviso] replicações desiguais por combinação: {r_por_comb}")

    N = sum(len(ys) for ys in grupos.values())
    media_geral = sum(linha["y"] for linha in linhas) / N

    # Coeficientes (efeitos): q_termo = média(sinal * y) sobre todas as medições.
    coef = {}
    for termo in todos_termos:
        acc = sum(sinal(linha, termo) * linha["y"] for linha in linhas)
        coef[termo] = acc / N

    # Soma de quadrados de cada termo: SQ = N * q^2  (projeto 2^k r balanceado).
    sq = {termo: N * coef[termo] ** 2 for termo in todos_termos}

    # Erro experimental: variação dentro de cada combinação.
    sq_erro = 0.0
    for chave, ys in grupos.items():
        m = sum(ys) / len(ys)
        sq_erro += sum((y - m) ** 2 for y in ys)

    sst = sum((linha["y"] - media_geral) ** 2 for linha in linhas)

    return {
        "k": k,
        "r": r,
        "N": N,
        "media_geral": media_geral,
        "coef": coef,
        "sq": sq,
        "sq_erro": sq_erro,
        "sst": sst,
        "grupos": grupos,
        "termos": todos_termos,
    }


def imprimir(res):
    print("=" * 64)
    print("PROJETO FATORIAL 2^k r — ANÁLISE")
    print("=" * 64)
    print(f"k = {res['k']}   r = {res['r']}   N = {res['N']}")
    print(f"q0 (média geral) = {res['media_geral']:.4f} %")
    print()

    print("Resumo por combinação (média ± desvio padrão das replicações):")
    cab = "  ".join(FATORES) + "  | n  | média    | desv.pad."
    print("  " + cab)
    print("  " + "-" * len(cab))
    for chave in sorted(res["grupos"]):
        ys = res["grupos"][chave]
        m = sum(ys) / len(ys)
        if len(ys) > 1:
            var = sum((y - m) ** 2 for y in ys) / (len(ys) - 1)
            dp = var**0.5
        else:
            dp = 0.0
        niveis = "  ".join(f"{v:+d}" for v in chave)
        print(f"  {niveis}  | {len(ys):<2} | {m:8.4f} | {dp:8.4f}")
    print()

    sst = res["sst"]
    print("Efeitos, soma de quadrados e variação explicada:")
    print(f"  {'Termo':<6} | {'coef (q)':>10} | {'SQ':>12} | {'% variação':>10}")
    print("  " + "-" * 46)
    for termo in res["termos"]:
        pct = 100 * res["sq"][termo] / sst if sst else 0.0
        print(
            f"  {termo:<6} | {res['coef'][termo]:>10.4f} | "
            f"{res['sq'][termo]:>12.4f} | {pct:>9.2f}%"
        )
    pct_erro = 100 * res["sq_erro"] / sst if sst else 0.0
    print(
        f"  {'Erro':<6} | {'—':>10} | {res['sq_erro']:>12.4f} | " f"{pct_erro:>9.2f}%"
    )
    print("  " + "-" * 46)
    soma_pct = sum(100 * res["sq"][t] / sst for t in res["termos"]) + pct_erro
    print(f"  {'Total':<6} | {'':>10} | {sst:>12.4f} | {soma_pct:>9.2f}%")
    print()

    print("Fatores em ordem de impacto (% da variação):")
    ordenado = sorted(res["termos"], key=lambda t: res["sq"][t], reverse=True)
    for termo in ordenado:
        pct = 100 * res["sq"][termo] / sst if sst else 0.0
        print(f"  {termo:<6} {pct:6.2f}%   {ROTULOS.get(termo, '')}")
    print()


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 1
    caminho = Path(argv[1])
    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        return 1
    linhas = ler_csv(caminho)
    if not linhas:
        print("Nenhuma medição preenchida no CSV (coluna uso_percent vazia).")
        return 1
    imprimir(analisar(linhas))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
