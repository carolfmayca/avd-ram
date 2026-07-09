#!/usr/bin/env python3
"""Coleta de medições para o projeto fatorial 2³ r (Mini Estudo 2 — ICC305).

Cada rodada coleta `r` replicações de UMA combinação de fatores e as anexa, já
rotuladas com os níveis A/B/C, ao CSV mestre lido por `analise_fatorial.py`
(`A,B,C,rep,uso_percent`). Também salva um CSV detalhado + metadados por rodada,
no mesmo espírito do `ram_monitor.py` do Mini Estudo 1.

Fatores (níveis codificados -1 / +1):
    A — Sistema operacional   Linux = -1   Windows = +1   (auto)
    B — Tamanho da RAM        8 GB  = -1   16 GB   = +1   (auto, por limiar)
    C — Carga de trabalho     repouso=-1   pesada  = +1   (flag --carga)

A e B são detectados automaticamente da máquina (não mudam em tempo de execução);
podem ser forçados com --a / --b caso a detecção não corresponda ao planejado.

Uso típico (rodar 1x por carga, em cada máquina da matriz):
    python coleta_fatorial.py --carga repouso -n 3 -i 20
    python coleta_fatorial.py --carga pesada  -n 3 -i 20

No modo pesado, o script aloca memória automaticamente para gerar pressão de RAM.
Use --carga-mb para ajustar a intensidade ou --carga-mb 0 para apenas rotular a
rodada como pesada, sem gerar carga.

A combinação A×B é fixa por máquina, então cada operador roda o script duas vezes
(repouso e pesada) por máquina, cobrindo as 8 combinações entre os integrantes.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import socket
import sys
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Erro: psutil não encontrado. Instale com: pip install psutil")
    sys.exit(1)

# Limiar (GB) que separa as máquinas de 8 GB (-1) das de 16 GB (+1).
LIMIAR_RAM_GB = 12.0

# Cabeçalho do CSV mestre — precisa casar com analise_fatorial.py.
COLUNAS_MESTRE = ["A", "B", "C", "rep", "uso_percent"]

# Cabeçalho do CSV detalhado (auditoria/replicação).
COLUNAS_DETALHE = [
    "A",
    "B",
    "C",
    "rep",
    "timestamp",
    "so",
    "ram_total_gb",
    "ram_disponivel_gb",
    "ram_usada_gb",
    "uso_percent",
    "num_processos",
    "top1_nome",
    "top1_ram_mb",
    "top2_nome",
    "top2_ram_mb",
    "top3_nome",
    "top3_ram_mb",
]


def detectar_so():
    """Nome legível do SO."""
    sistema = platform.system()
    if sistema == "Linux":
        try:
            import distro

            return f"{distro.name()} {distro.version()}"
        except ImportError:
            try:
                with open("/etc/os-release") as f:
                    info = {}
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            info[k] = v.strip('"')
                    return f"{info.get('NAME', 'Linux')} {info.get('VERSION_ID', '')}"
            except (FileNotFoundError, PermissionError):
                return "Linux"
    elif sistema == "Windows":
        return f"Windows {platform.version()}"
    elif sistema == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    return sistema


def nivel_so():
    """A: Windows = +1, qualquer outro (Linux/macOS) = -1."""
    return 1 if platform.system() == "Windows" else -1


def nivel_ram():
    """B: RAM total acima do limiar = +1 (16 GB), abaixo = -1 (8 GB)."""
    total_gb = psutil.virtual_memory().total / (1024**3)
    return 1 if total_gb >= LIMIAR_RAM_GB else -1


def top_processos_ram(n=3):
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            info = p.info
            rss = info["memory_info"].rss if info["memory_info"] else 0
            procs.append((info["name"], rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x[1], reverse=True)
    return procs[:n]


def coletar_medicao(a, b, c, rep):
    """Uma replicação rotulada com os níveis dos fatores."""
    mem = psutil.virtual_memory()
    top3 = top_processos_ram(3)
    dados = {
        "A": a,
        "B": b,
        "C": c,
        "rep": rep,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "so": detectar_so(),
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "ram_disponivel_gb": round(mem.available / (1024**3), 2),
        "ram_usada_gb": round(mem.used / (1024**3), 2),
        "uso_percent": mem.percent,
        "num_processos": len(psutil.pids()),
    }
    for i in range(1, 4):
        if i <= len(top3):
            nome, rss = top3[i - 1]
            dados[f"top{i}_nome"] = nome
            dados[f"top{i}_ram_mb"] = round(rss / (1024**2), 1)
        else:
            dados[f"top{i}_nome"] = ""
            dados[f"top{i}_ram_mb"] = ""
    return dados


def coletar_metadados(a, b, c, carga, config):
    meta = {
        "hostname": socket.gethostname(),
        "arquitetura": platform.machine(),
        "processador": platform.processor() or "N/A",
        "cpu_cores_fisicos": psutil.cpu_count(logical=False),
        "cpu_cores_logicos": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "so": detectar_so(),
        "so_kernel": platform.release(),
        "plataforma": platform.platform(),
        "python_versao": platform.python_version(),
        "psutil_versao": psutil.__version__,
        "horario_inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": time.strftime("%Z"),
        "fator_A_so": a,
        "fator_B_ram": b,
        "fator_C_carga": c,
        "carga_descricao": carga,
        "configuracao": config,
        "cpu_percent": psutil.cpu_percent(interval=1),
    }
    bateria = psutil.sensors_battery()
    if bateria:
        meta["bateria_percent"] = bateria.percent
        meta["bateria_conectada"] = bateria.power_plugged
    else:
        meta["bateria_percent"] = "N/A"
        meta["bateria_conectada"] = "N/A"
    return meta


def gerar_carga_memoria(mb):
    """Aloca e toca memória para gerar carga real durante a coleta."""
    if mb <= 0:
        return []

    tamanho_bloco_mb = 64
    tamanho_bloco = tamanho_bloco_mb * 1024 * 1024
    restante = mb * 1024 * 1024
    blocos = []

    while restante > 0:
        tamanho = min(tamanho_bloco, restante)
        bloco = bytearray(tamanho)
        for i in range(0, tamanho, 4096):
            bloco[i] = 1
        blocos.append(bloco)
        restante -= tamanho

    return blocos


def anexar_mestre(caminho, linhas):
    """Anexa replicações ao CSV mestre, criando cabeçalho se não existir."""
    existe = os.path.exists(caminho) and os.path.getsize(caminho) > 0
    with open(caminho, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS_MESTRE)
        if not existe:
            writer.writeheader()
        for d in linhas:
            writer.writerow({k: d[k] for k in COLUNAS_MESTRE})


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--carga",
        required=True,
        choices=["repouso", "pesada"],
        help="Nível do fator C (repouso=-1, pesada=+1).",
    )
    p.add_argument(
        "-n",
        "--num-rep",
        type=int,
        default=3,
        help="Número de replicações (r) desta combinação (default: 3).",
    )
    p.add_argument(
        "-i",
        "--intervalo",
        type=float,
        default=20.0,
        help="Segundos entre replicações (default: 20).",
    )
    p.add_argument(
        "--csv",
        default="dados_2k_r.csv",
        help="CSV mestre lido por analise_fatorial.py (default: dados_2k_r.csv).",
    )
    p.add_argument(
        "--a",
        type=int,
        choices=[-1, 1],
        default=None,
        help="Força o nível do fator A (SO). Default: auto.",
    )
    p.add_argument(
        "--b",
        type=int,
        choices=[-1, 1],
        default=None,
        help="Força o nível do fator B (RAM). Default: auto.",
    )
    p.add_argument(
        "--dir",
        default=".",
        help="Diretório base para a pasta de detalhe/metadados (default: atual).",
    )
    p.add_argument("--obs", default="", help="Observações livres.")
    p.add_argument(
        "--carga-mb",
        type=int,
        default=1024,
        help=(
            "Memória, em MB, alocada automaticamente quando --carga pesada "
            "(default: 1024; use 0 para desativar)."
        ),
    )
    args = p.parse_args()

    if args.num_rep < 1:
        p.error("--num-rep deve ser >= 1.")
    if args.intervalo < 0:
        p.error("--intervalo deve ser >= 0.")
    if args.carga_mb < 0:
        p.error("--carga-mb deve ser >= 0.")

    a = args.a if args.a is not None else nivel_so()
    b = args.b if args.b is not None else nivel_ram()
    c = 1 if args.carga == "pesada" else -1

    rotulo_a = "Windows" if a == 1 else "Linux"
    rotulo_b = "16 GB" if b == 1 else "8 GB"

    print("=" * 60)
    print("  COLETA FATORIAL 2³ r — combinação atual")
    print("=" * 60)
    print(f"  A (SO)    = {a:+d}  ({rotulo_a})")
    print(f"  B (RAM)   = {b:+d}  ({rotulo_b})")
    print(f"  C (carga) = {c:+d}  ({args.carga})")
    print(f"  r         = {args.num_rep}   intervalo = {args.intervalo}s")
    if args.carga == "pesada":
        print(f"  carga RAM = {args.carga_mb} MB")
    print(f"  CSV mestre: {args.csv}")
    print("=" * 60)

    # Pasta de detalhe/metadados por rodada.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_pasta = f"coleta_A{a:+d}_B{b:+d}_C{c:+d}_{ts}".replace("+", "p").replace(
        "-", "m"
    )
    pasta = os.path.join(args.dir, nome_pasta)
    os.makedirs(pasta, exist_ok=True)
    detalhe_path = os.path.join(pasta, "detalhe.csv")
    meta_path = os.path.join(pasta, "metadados.json")

    config = (
        f"A={a}, B={b}, C={c} ({args.carga}); r={args.num_rep}, i={args.intervalo}s"
    )
    carga_memoria = []
    if args.carga == "pesada" and args.carga_mb > 0:
        print(f"\n  Gerando carga pesada: alocando {args.carga_mb} MB de RAM...")
        carga_memoria = gerar_carga_memoria(args.carga_mb)
        print("  Carga alocada; iniciando medições.")

    meta = coletar_metadados(a, b, c, args.carga, config)
    meta["carga_ram_mb"] = args.carga_mb if args.carga == "pesada" else 0
    meta["observacoes"] = args.obs
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    linhas = []
    with open(detalhe_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS_DETALHE)
        writer.writeheader()
        print(f"\n  {'rep':>3} | {'uso(%)':>7} | {'usada(GB)':>9} | {'proc':>5}")
        print("  " + "-" * 34)
        for rep in range(1, args.num_rep + 1):
            d = coletar_medicao(a, b, c, rep)
            writer.writerow(d)
            f.flush()
            linhas.append(d)
            print(
                f"  {rep:>3} | {d['uso_percent']:>6.1f}% | "
                f"{d['ram_usada_gb']:>9.2f} | {d['num_processos']:>5}"
            )
            if rep < args.num_rep:
                time.sleep(args.intervalo)

    anexar_mestre(args.csv, linhas)

    # Mantem a lista viva ate este ponto; depois a memoria e liberada pelo processo.
    del carga_memoria

    print("\n  " + "-" * 34)
    print(f"  {args.num_rep} replicações anexadas a {args.csv}")
    print(f"  Detalhe/metadados: {pasta}")
    print(f"\n  Próximo: rode a outra carga nesta máquina e repita nas demais.")
    print(f"  Ao completar as 8 combinações: python analise_fatorial.py {args.csv}")


if __name__ == "__main__":
    main()
