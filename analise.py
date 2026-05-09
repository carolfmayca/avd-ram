#!/usr/bin/env python3
"""
Análise Estatística - Uso de RAM por SO
Projeto: Avaliação de Desempenho 2026/01 - UFAM
Pergunta: O sistema operacional influencia no uso da RAM?

Descobre automaticamente todos os experimentos em subpastas de cada pessoa
e produz estatísticas descritivas, intervalos de confiança e boxplots.
"""

import json
import os
import sys
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
SAIDA_DIR = BASE_DIR / "resultados"
SAIDA_DIR.mkdir(exist_ok=True)

# Paleta de cores por SO (parcial match, case-insensitive)
COR_SO = {
    "ubuntu": "#E95420",   # laranja Ubuntu
    "windows": "#0078D4",  # azul Windows
    "fedora": "#41B96C",   # verde Fedora
    "linux": "#F5A623",    # amarelo genérico Linux
}
COR_PADRAO = "#888888"

ALPHA_IC = 0.05  # 95% de confiança


def cor_para_so(so: str) -> str:
    so_low = so.lower()
    for chave, cor in COR_SO.items():
        if chave in so_low:
            return cor
    return COR_PADRAO


def so_curto(so: str) -> str:
    """Retorna rótulo curto para o SO."""
    so_low = so.lower()
    if "ubuntu" in so_low:
        return "Ubuntu 24.04"
    if "windows" in so_low:
        return "Windows 11"
    if "fedora" in so_low:
        return "Fedora 44"
    return so.split()[0]


# ---------------------------------------------------------------------------
# Descoberta de dados
# ---------------------------------------------------------------------------
def descobrir_experimentos() -> pd.DataFrame:
    """Percorre subpastas de cada pessoa e carrega todos os CSVs de experimentos."""
    frames = []
    pessoas_dir = [
        d for d in BASE_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "resultados"
    ]
    pessoas_dir.sort()

    for pessoa_dir in pessoas_dir:
        pessoa = pessoa_dir.name
        experimentos = sorted(pessoa_dir.glob("experimento_*"))

        if not experimentos:
            continue

        for exp_dir in experimentos:
            csv_path = exp_dir / "medicoes_ram.csv"
            meta_path = exp_dir / "medicoes_ram_metadados.json"

            if not csv_path.exists():
                continue

            # Metadados
            meta = {}
            if meta_path.exists():
                with open(meta_path, encoding="utf-8") as f:
                    meta = json.load(f)

            df = pd.read_csv(csv_path)
            df["pessoa"] = pessoa
            df["experimento"] = exp_dir.name
            df["so_original"] = meta.get("so", df["so"].iloc[0] if "so" in df.columns else "?")
            df["so_label"] = df["so_original"].apply(so_curto)
            df["ram_total_gb"] = meta.get("ram_total_gb", np.nan)
            df["cpu_cores_fisicos"] = meta.get("cpu_cores_fisicos", np.nan)
            df["cpu_percent_inicial"] = meta.get("cpu_percent", np.nan)

            frames.append(df)

    if not frames:
        print("Nenhum experimento encontrado.")
        sys.exit(1)

    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# Estatísticas
# ---------------------------------------------------------------------------
def resumo_estatistico(serie: pd.Series, nome: str = "") -> dict:
    """Calcula estatísticas descritivas + IC 95% via t de Student."""
    n = len(serie)
    media = serie.mean()
    desvio = serie.std(ddof=1)
    erro_padrao = desvio / np.sqrt(n)
    t_critico = stats.t.ppf(1 - ALPHA_IC / 2, df=n - 1)
    margem = t_critico * erro_padrao
    q1, mediana, q3 = np.percentile(serie, [25, 50, 75])
    iqr = q3 - q1

    return {
        "grupo": nome,
        "n": n,
        "media": round(media, 4),
        "mediana": round(mediana, 4),
        "desvio_padrao": round(desvio, 4),
        "erro_padrao": round(erro_padrao, 4),
        "ic95_inferior": round(media - margem, 4),
        "ic95_superior": round(media + margem, 4),
        "min": round(float(serie.min()), 4),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "max": round(float(serie.max()), 4),
        "iqr": round(iqr, 4),
        "cv_percent": round((desvio / media) * 100, 2) if media != 0 else np.nan,
    }


# ---------------------------------------------------------------------------
# Teste t entre dois grupos
# ---------------------------------------------------------------------------
def formatar_p(p_valor: float) -> str:
    """Formata p-valor: usa notação científica para valores muito pequenos."""
    if p_valor < 0.0001:
        return f"{p_valor:.2e}"
    return f"{p_valor:.6f}"


def teste_t(grupo_a: pd.Series, grupo_b: pd.Series, nome_a: str, nome_b: str) -> dict:
    """Teste t de Welch (variâncias desiguais) entre dois grupos independentes."""
    t_stat, p_valor = stats.ttest_ind(grupo_a, grupo_b, equal_var=False)
    d = (grupo_a.mean() - grupo_b.mean()) / np.sqrt(
        (grupo_a.std(ddof=1) ** 2 + grupo_b.std(ddof=1) ** 2) / 2
    )
    return {
        "comparacao": f"{nome_a} vs {nome_b}",
        "t_stat": round(t_stat, 4),
        "p_valor": formatar_p(p_valor),
        "p_valor_raw": p_valor,
        "cohen_d": round(d, 4),
        "significativo_95": "SIM" if p_valor < 0.05 else "NÃO",
    }


# ---------------------------------------------------------------------------
# Plot: boxplot por pessoa
# ---------------------------------------------------------------------------
def plotar_por_pessoa(df: pd.DataFrame, pessoa: str):
    dados_pessoa = df[df["pessoa"] == pessoa]
    sos = sorted(dados_pessoa["so_label"].unique())
    grupos = [dados_pessoa[dados_pessoa["so_label"] == so]["uso_percent"].values for so in sos]
    cores = [cor_para_so(so) for so in sos]

    fig, ax = plt.subplots(figsize=(8, 6))
    bp = ax.boxplot(
        grupos,
        patch_artist=True,
        widths=0.45,
        medianprops=dict(color="black", linewidth=2),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker="o", markersize=5, alpha=0.6),
    )
    for patch, cor in zip(bp["boxes"], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.8)

    # Pontos individuais com jitter
    for i, (grupo, cor) in enumerate(zip(grupos, cores), start=1):
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, size=len(grupo))
        ax.scatter(np.full(len(grupo), i) + jitter, grupo,
                   color=cor, alpha=0.4, s=20, zorder=3)

    # Anotações de IC 95%
    for i, (grupo, so) in enumerate(zip(grupos, sos), start=1):
        serie = pd.Series(grupo)
        r = resumo_estatistico(serie)
        ax.plot([i - 0.35, i + 0.35], [r["ic95_inferior"]] * 2,
                color="gray", linestyle="--", linewidth=1, alpha=0.7)
        ax.plot([i - 0.35, i + 0.35], [r["ic95_superior"]] * 2,
                color="gray", linestyle="--", linewidth=1, alpha=0.7)
        ax.annotate(
            f"IC95%\n[{r['ic95_inferior']:.1f}, {r['ic95_superior']:.1f}]",
            xy=(i + 0.3, r["media"]),
            fontsize=7, color="dimgray", va="center",
        )

    ax.set_xticks(range(1, len(sos) + 1))
    ax.set_xticklabels(sos, fontsize=11)
    ax.set_ylabel("Uso de RAM (%)", fontsize=12)
    ax.set_xlabel("Sistema Operacional", fontsize=12)
    ax.set_title(f"Uso de RAM em Repouso — {pessoa.capitalize()}", fontsize=14, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    legenda = [mpatches.Patch(color=cor_para_so(so), label=so, alpha=0.8) for so in sos]
    ax.legend(handles=legenda, fontsize=9, loc="upper right")

    plt.tight_layout()
    caminho = SAIDA_DIR / f"boxplot_{pessoa}.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Gráfico salvo: {caminho.relative_to(BASE_DIR)}")


# ---------------------------------------------------------------------------
# Plot: boxplot geral (todas as pessoas e SOs)
# ---------------------------------------------------------------------------
def plotar_geral(df: pd.DataFrame):
    pessoas = sorted(df["pessoa"].unique())
    sos_unicos = sorted(df["so_label"].unique())

    # Uma coluna por pessoa, uma cor por SO
    n_pessoas = len(pessoas)
    n_sos = len(sos_unicos)
    largura = 0.7 / n_sos
    pos_base = np.arange(n_pessoas)

    fig, ax = plt.subplots(figsize=(max(10, n_pessoas * 3.5), 7))

    for j, so in enumerate(sos_unicos):
        cor = cor_para_so(so)
        posicoes = pos_base + (j - (n_sos - 1) / 2) * largura
        grupos = [
            df[(df["pessoa"] == p) & (df["so_label"] == so)]["uso_percent"].values
            for p in pessoas
        ]
        # Remove grupos vazios mantendo posição
        grupos_validos = [g if len(g) > 0 else np.array([np.nan]) for g in grupos]

        bp = ax.boxplot(
            grupos_validos,
            positions=posicoes,
            patch_artist=True,
            widths=largura * 0.85,
            medianprops=dict(color="black", linewidth=1.8),
            whiskerprops=dict(linewidth=1.3),
            capprops=dict(linewidth=1.3),
            flierprops=dict(marker="o", markersize=4, alpha=0.5),
            manage_ticks=False,
        )
        for patch in bp["boxes"]:
            patch.set_facecolor(cor)
            patch.set_alpha(0.8)

    ax.set_xticks(pos_base)
    ax.set_xticklabels([p.capitalize() for p in pessoas], fontsize=12)
    ax.set_ylabel("Uso de RAM (%)", fontsize=12)
    ax.set_xlabel("Participante", fontsize=12)
    ax.set_title("Uso de RAM em Repouso — Todos os Participantes", fontsize=14, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    legenda = [mpatches.Patch(color=cor_para_so(so), label=so, alpha=0.8) for so in sos_unicos]
    ax.legend(handles=legenda, fontsize=10, loc="upper right")

    plt.tight_layout()
    caminho = SAIDA_DIR / "boxplot_geral.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Gráfico salvo: {caminho.relative_to(BASE_DIR)}")


# ---------------------------------------------------------------------------
# Plot: boxplot Linux vs Windows (agrupando todos os Linux juntos)
# ---------------------------------------------------------------------------
def plotar_linux_vs_windows(df: pd.DataFrame):
    df2 = df.copy()
    df2["familia"] = df2["so_label"].apply(
        lambda s: "Windows" if "Windows" in s else "Linux (Ubuntu/Fedora)"
    )

    grupos = {f: df2[df2["familia"] == f]["uso_percent"] for f in sorted(df2["familia"].unique())}
    labels = list(grupos.keys())
    dados = [grupos[l].values for l in labels]
    cores = [cor_para_so(l) for l in labels]

    fig, ax = plt.subplots(figsize=(7, 6))
    bp = ax.boxplot(
        dados,
        patch_artist=True,
        widths=0.45,
        medianprops=dict(color="black", linewidth=2),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker="o", markersize=5, alpha=0.5),
    )
    for patch, cor in zip(bp["boxes"], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.8)

    for i, (d, cor) in enumerate(zip(dados, cores), start=1):
        jitter = np.random.default_rng(0).uniform(-0.15, 0.15, size=len(d))
        ax.scatter(np.full(len(d), i) + jitter, d, color=cor, alpha=0.35, s=18, zorder=3)

    # Anotações de média e IC
    for i, (d, label) in enumerate(zip(dados, labels), start=1):
        r = resumo_estatistico(pd.Series(d))
        ax.hlines(r["media"], i - 0.35, i + 0.35, colors="black", linestyles=":", linewidth=1.5)
        ax.annotate(
            f"μ={r['media']:.1f}%\nIC95% [{r['ic95_inferior']:.1f}, {r['ic95_superior']:.1f}]",
            xy=(i + 0.28, r["media"]),
            fontsize=8, color="black", va="center",
        )

    ax.set_xticks([1, 2])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Uso de RAM (%)", fontsize=12)
    ax.set_title("Linux vs Windows — Todos os Participantes", fontsize=13, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    # Teste t entre as famílias
    if len(dados) == 2:
        res = teste_t(pd.Series(dados[0]), pd.Series(dados[1]), labels[0], labels[1])
        sig_txt = (f"Teste t de Welch: t={res['t_stat']}, p={res['p_valor']}, "
                   f"Cohen's d={res['cohen_d']} ({res['significativo_95']})")
        ax.set_xlabel(sig_txt, fontsize=9, color="dimgray")

    plt.tight_layout()
    caminho = SAIDA_DIR / "boxplot_linux_vs_windows.png"
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Gráfico salvo: {caminho.relative_to(BASE_DIR)}")


# ---------------------------------------------------------------------------
# Relatório em texto
# ---------------------------------------------------------------------------
def imprimir_separador(titulo: str):
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)


def formatar_resumo(r: dict) -> str:
    return (
        f"  n            = {r['n']}\n"
        f"  Média        = {r['media']:.4f}%\n"
        f"  Mediana      = {r['mediana']:.4f}%\n"
        f"  Desvio Pad.  = {r['desvio_padrao']:.4f}%\n"
        f"  Erro Padrão  = {r['erro_padrao']:.4f}%\n"
        f"  IC 95%       = [{r['ic95_inferior']:.4f}%, {r['ic95_superior']:.4f}%]\n"
        f"  Mín / Máx    = {r['min']:.4f}% / {r['max']:.4f}%\n"
        f"  Q1 / Q3      = {r['q1']:.4f}% / {r['q3']:.4f}%\n"
        f"  IQR          = {r['iqr']:.4f}%\n"
        f"  CV           = {r['cv_percent']:.2f}%"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Descobrindo experimentos...")
    df = descobrir_experimentos()

    print(f"Total de medições carregadas: {len(df)}")
    print(f"Pessoas: {sorted(df['pessoa'].unique())}")
    print(f"SOs encontrados: {sorted(df['so_label'].unique())}")

    todos_resumos = []
    todos_testes = []

    # -----------------------------------------------------------------------
    # 1. Análise por pessoa
    # -----------------------------------------------------------------------
    for pessoa in sorted(df["pessoa"].unique()):
        imprimir_separador(f"PESSOA: {pessoa.upper()}")
        dados_pessoa = df[df["pessoa"] == pessoa]
        sos = sorted(dados_pessoa["so_label"].unique())

        resumos_pessoa = []
        for so in sos:
            serie = dados_pessoa[dados_pessoa["so_label"] == so]["uso_percent"]
            r = resumo_estatistico(serie, nome=f"{pessoa} / {so}")
            resumos_pessoa.append((so, serie, r))
            todos_resumos.append(r)

            print(f"\n  [{so}]")
            print(formatar_resumo(r))

        # Teste t entre os dois SOs da pessoa (se houver par)
        if len(resumos_pessoa) == 2:
            (so_a, serie_a, _), (so_b, serie_b, _) = resumos_pessoa
            t_res = teste_t(serie_a, serie_b, f"{pessoa}/{so_a}", f"{pessoa}/{so_b}")
            todos_testes.append(t_res)
            print(f"\n  Teste t de Welch ({so_a} vs {so_b}):")
            print(f"    t = {t_res['t_stat']},  p = {t_res['p_valor']},  "
                  f"Cohen's d = {t_res['cohen_d']}")
            print(f"    Diferença estatisticamente significativa (\u03b1=0.05): "
                  f"{t_res['significativo_95']}")

        print(f"\n  Gerando boxplot para {pessoa}...")
        plotar_por_pessoa(df, pessoa)

    # -----------------------------------------------------------------------
    # 2. Análise por SO (todos os participantes agrupados)
    # -----------------------------------------------------------------------
    imprimir_separador("RESUMO POR SO — TODOS OS PARTICIPANTES")
    for so in sorted(df["so_label"].unique()):
        serie = df[df["so_label"] == so]["uso_percent"]
        r = resumo_estatistico(serie, nome=f"GLOBAL / {so}")
        todos_resumos.append(r)
        print(f"\n  [{so}]  (n={r['n']}, de {df[df['so_label']==so]['pessoa'].nunique()} participantes)")
        print(formatar_resumo(r))

    # -----------------------------------------------------------------------
    # 3. Análise Linux vs Windows (família de SO)
    # -----------------------------------------------------------------------
    imprimir_separador("LINUX vs WINDOWS — TODOS OS PARTICIPANTES")
    df_familia = df.copy()
    df_familia["familia"] = df_familia["so_label"].apply(
        lambda s: "Windows" if "Windows" in s else "Linux"
    )
    for familia in ["Linux", "Windows"]:
        serie = df_familia[df_familia["familia"] == familia]["uso_percent"]
        r = resumo_estatistico(serie, nome=f"GLOBAL / {familia}")
        todos_resumos.append(r)
        print(f"\n  [{familia}]  (n={r['n']})")
        print(formatar_resumo(r))

    serie_linux = df_familia[df_familia["familia"] == "Linux"]["uso_percent"]
    serie_win = df_familia[df_familia["familia"] == "Windows"]["uso_percent"]
    t_geral = teste_t(serie_linux, serie_win, "Linux", "Windows")
    todos_testes.append(t_geral)
    print(f"\n  Teste t de Welch (Linux vs Windows):")
    print(f"    t = {t_geral['t_stat']},  p = {t_geral['p_valor']},  "
          f"Cohen's d = {t_geral['cohen_d']}")
    print(f"    Diferença estatisticamente significativa (\u03b1=0.05): {t_geral['significativo_95']}")

    # -----------------------------------------------------------------------
    # 4. Boxplots gerais
    # -----------------------------------------------------------------------
    imprimir_separador("GERANDO GRÁFICOS GERAIS")
    plotar_geral(df)
    plotar_linux_vs_windows(df)

    # -----------------------------------------------------------------------
    # 5. Exportar CSVs de resumo
    # -----------------------------------------------------------------------
    df_resumos = pd.DataFrame(todos_resumos)
    caminho_resumo = SAIDA_DIR / "resumo_estatistico.csv"
    df_resumos.to_csv(caminho_resumo, index=False)
    print(f"  Tabela salva: {caminho_resumo.relative_to(BASE_DIR)}")

    df_testes = pd.DataFrame(todos_testes).drop(columns=["p_valor_raw"], errors="ignore")
    caminho_testes = SAIDA_DIR / "testes_t.csv"
    df_testes.to_csv(caminho_testes, index=False)
    print(f"  Tabela salva: {caminho_testes.relative_to(BASE_DIR)}")

    # -----------------------------------------------------------------------
    # 6. Dados brutos consolidados
    # -----------------------------------------------------------------------
    cols_exportar = [
        "pessoa", "so_label", "experimento", "medicao",
        "timestamp", "uso_percent", "ram_usada_gb", "ram_total_gb",
        "num_processos", "top1_nome", "top1_ram_mb",
    ]
    cols_existentes = [c for c in cols_exportar if c in df.columns]
    caminho_brutos = SAIDA_DIR / "dados_brutos_consolidados.csv"
    df[cols_existentes].to_csv(caminho_brutos, index=False)
    print(f"  Tabela salva: {caminho_brutos.relative_to(BASE_DIR)}")

    imprimir_separador("CONCLUÍDO")
    print(f"  Todos os resultados em: {SAIDA_DIR.relative_to(BASE_DIR)}/")


if __name__ == "__main__":
    np.random.seed(42)
    main()
