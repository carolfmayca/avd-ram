#!/usr/bin/env python3
"""
RAM Monitor - Coleta de métricas de uso de memória RAM.
Projeto: Avaliação de Desempenho 2026/01 - UFAM
Pergunta: O sistema operacional influencia no uso da RAM?

Uso:
    python ram_monitor.py -n 12 -i 180          # 12 medições, 3 min entre cada
    python ram_monitor.py -n 5 -i 2 -o teste.csv  # teste rápido
"""

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


def detectar_so():
    """Retorna nome do SO de forma legível."""
    sistema = platform.system()
    if sistema == "Linux":
        try:
            import distro
            return f"{distro.name()} {distro.version()}"
        except ImportError:
            # Tenta ler /etc/os-release diretamente
            try:
                with open("/etc/os-release") as f:
                    info = {}
                    for line in f:
                        if "=" in line:
                            key, val = line.strip().split("=", 1)
                            info[key] = val.strip('"')
                    return f"{info.get('NAME', 'Linux')} {info.get('VERSION_ID', '')}"
            except (FileNotFoundError, PermissionError):
                return "Linux"
    elif sistema == "Windows":
        return f"Windows {platform.version()}"
    elif sistema == "Darwin":
        return f"macOS {platform.mac_ver()[0]}"
    return sistema


def coletar_metadados(config_str="", observacoes=""):
    """Coleta metadados do ambiente: máquina, SO, versões, carga, energia."""
    meta = {}

    # Máquina
    meta["hostname"] = socket.gethostname()
    meta["arquitetura"] = platform.machine()
    meta["processador"] = platform.processor() or "N/A"
    meta["cpu_cores_fisicos"] = psutil.cpu_count(logical=False)
    meta["cpu_cores_logicos"] = psutil.cpu_count(logical=True)
    meta["ram_total_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    # Sistema Operacional
    meta["so"] = detectar_so()
    meta["so_kernel"] = platform.release()
    meta["so_versao_completa"] = platform.version()
    meta["plataforma"] = platform.platform()

    # Versões de ferramentas
    meta["python_versao"] = platform.python_version()
    meta["psutil_versao"] = psutil.__version__
    try:
        import distro
        meta["distro_versao"] = distro.__version__
    except (ImportError, AttributeError):
        meta["distro_versao"] = "N/A"

    # Horário
    meta["horario_inicio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta["timezone"] = time.strftime("%Z")

    # Configuração do experimento
    meta["configuracao"] = config_str

    # Carga do sistema
    if hasattr(os, "getloadavg"):
        load1, load5, load15 = os.getloadavg()
        meta["carga_1min"] = round(load1, 2)
        meta["carga_5min"] = round(load5, 2)
        meta["carga_15min"] = round(load15, 2)
    else:
        meta["carga_1min"] = "N/A"
        meta["carga_5min"] = "N/A"
        meta["carga_15min"] = "N/A"
    meta["cpu_percent"] = psutil.cpu_percent(interval=1)

    # Energia / Bateria
    bateria = psutil.sensors_battery()
    if bateria:
        meta["bateria_percent"] = bateria.percent
        meta["bateria_conectada"] = bateria.power_plugged
        if bateria.secsleft >= 0:
            meta["bateria_tempo_restante_min"] = round(bateria.secsleft / 60, 1)
        else:
            meta["bateria_tempo_restante_min"] = "Calculando" if not bateria.power_plugged else "N/A (carregando)"
    else:
        meta["bateria_percent"] = "N/A (sem bateria/desktop)"
        meta["bateria_conectada"] = "N/A"
        meta["bateria_tempo_restante_min"] = "N/A"

    # Observações
    meta["observacoes"] = observacoes

    return meta


def salvar_metadados(meta, filepath):
    """Salva metadados em arquivo JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def imprimir_metadados(meta):
    """Exibe metadados no terminal de forma organizada."""
    print("\n" + "=" * 60)
    print("            METADADOS DO EXPERIMENTO")
    print("=" * 60)
    print(f"  Máquina:        {meta['hostname']}")
    print(f"  Arquitetura:    {meta['arquitetura']}")
    print(f"  Processador:    {meta['processador']}")
    print(f"  CPUs:           {meta['cpu_cores_fisicos']} físicos / {meta['cpu_cores_logicos']} lógicos")
    print(f"  RAM Total:      {meta['ram_total_gb']} GB")
    print(f"  ---")
    print(f"  SO:             {meta['so']}")
    print(f"  Kernel:         {meta['so_kernel']}")
    print(f"  Plataforma:     {meta['plataforma']}")
    print(f"  ---")
    print(f"  Python:         {meta['python_versao']}")
    print(f"  psutil:         {meta['psutil_versao']}")
    print(f"  distro:         {meta['distro_versao']}")
    print(f"  ---")
    print(f"  Horário:        {meta['horario_inicio']}")
    print(f"  Timezone:       {meta['timezone']}")
    print(f"  ---")
    print(f"  Carga (1/5/15): {meta['carga_1min']} / {meta['carga_5min']} / {meta['carga_15min']}")
    print(f"  CPU uso:        {meta['cpu_percent']}%")
    print(f"  ---")
    print(f"  Bateria:        {meta['bateria_percent']}")
    print(f"  Conectada:      {meta['bateria_conectada']}")
    print(f"  Tempo restante: {meta['bateria_tempo_restante_min']}")
    print(f"  ---")
    print(f"  Configuração:   {meta['configuracao'] or '(nenhuma)'}")
    print(f"  Observações:    {meta['observacoes'] or '(nenhuma)'}")
    print("=" * 60 + "\n")


def bytes_para_gb(valor_bytes):
    """Converte bytes para GB com 2 casas decimais."""
    return round(valor_bytes / (1024 ** 3), 2)


def top_processos_ram(n=3):
    """Retorna os top N processos por uso de memória RSS."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            info = p.info
            rss = info['memory_info'].rss if info['memory_info'] else 0
            procs.append((info['name'], info['pid'], rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x[2], reverse=True)
    return procs[:n]


def coletar_medicao(numero):
    """Coleta uma única medição de RAM e retorna um dicionário."""
    mem = psutil.virtual_memory()
    top3 = top_processos_ram(3)
    dados = {
        "medicao": numero,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "so": detectar_so(),
        "ram_total_gb": bytes_para_gb(mem.total),
        "ram_disponivel_gb": bytes_para_gb(mem.available),
        "ram_usada_gb": bytes_para_gb(mem.used),
        "uso_percent": mem.percent,
        "num_processos": len(psutil.pids()),
    }
    for i, (nome, pid, rss) in enumerate(top3, 1):
        dados[f"top{i}_nome"] = nome
        dados[f"top{i}_pid"] = pid
        dados[f"top{i}_ram_mb"] = round(rss / (1024 ** 2), 1)
    # Preencher caso haja menos de 3 processos
    for i in range(len(top3) + 1, 4):
        dados[f"top{i}_nome"] = ""
        dados[f"top{i}_pid"] = ""
        dados[f"top{i}_ram_mb"] = ""
    return dados


COLUNAS = [
    "medicao", "timestamp", "so", "ram_total_gb",
    "ram_disponivel_gb", "ram_usada_gb", "uso_percent", "num_processos",
    "top1_nome", "top1_pid", "top1_ram_mb",
    "top2_nome", "top2_pid", "top2_ram_mb",
    "top3_nome", "top3_pid", "top3_ram_mb",
]

HEADER_FMT = "{:>8} | {:>19} | {:>10} | {:>10} | {:>10} | {:>8} | {:>10}"
ROW_FMT = "{:>8} | {:>19} | {:>10.2f} | {:>10.2f} | {:>10.2f} | {:>7.1f}% | {:>10}"


def imprimir_header():
    """Imprime cabeçalho da tabela no terminal."""
    header = HEADER_FMT.format(
        "Medição", "Timestamp",
        "Total(GB)", "Disp(GB)", "Usada(GB)", "Uso(%)", "Processos"
    )
    separador = "-" * len(header)
    print(separador)
    print(header)
    print(separador)


def imprimir_linha(dados):
    """Imprime uma linha de dados no terminal."""
    print(ROW_FMT.format(
        dados["medicao"],
        dados["timestamp"],
        dados["ram_total_gb"],
        dados["ram_disponivel_gb"],
        dados["ram_usada_gb"],
        dados["uso_percent"],
        dados["num_processos"],
    ))


def imprimir_top3(dados):
    """Imprime os top 3 processos por RAM."""
    print("         Top 3 RAM:  ", end="")
    partes = []
    for i in range(1, 4):
        nome = dados.get(f"top{i}_nome", "")
        mb = dados.get(f"top{i}_ram_mb", "")
        if nome:
            partes.append(f"{i}) {nome} ({mb} MB)")
    print("  |  ".join(partes))


def main():
    parser = argparse.ArgumentParser(
        description="Coleta métricas de uso de RAM para comparação entre SOs."
    )
    parser.add_argument(
        "-n", "--num-medicoes",
        type=int, required=True,
        help="Número de medições a realizar."
    )
    parser.add_argument(
        "-i", "--intervalo",
        type=float, default=5.0,
        help="Intervalo entre medições em segundos (default: 5)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str, default="medicoes_ram.csv",
        help="Nome do arquivo CSV de saída (default: medicoes_ram.csv)."
    )
    parser.add_argument(
        "-c", "--config",
        type=str, default="",
        help="Descrição da configuração do experimento (ex: 'navegador aberto com 5 abas')."
    )
    parser.add_argument(
        "--obs",
        type=str, default="",
        help="Observações adicionais sobre o experimento."
    )
    parser.add_argument(
        "--dir",
        type=str, default=".",
        help="Diretório base onde a pasta do experimento será criada (default: pasta atual)."
    )
    args = parser.parse_args()

    if args.num_medicoes < 1:
        parser.error("O número de medições deve ser >= 1.")
    if args.intervalo < 0:
        parser.error("O intervalo deve ser >= 0.")

    # Criar pasta do experimento com timestamp
    timestamp_pasta = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_pasta = f"experimento_{timestamp_pasta}"
    pasta_saida = os.path.join(args.dir, nome_pasta)
    os.makedirs(pasta_saida, exist_ok=True)

    # Definir caminhos dos arquivos dentro da pasta
    csv_nome = args.output if args.output != "medicoes_ram.csv" else "medicoes_ram.csv"
    csv_filepath = os.path.join(pasta_saida, csv_nome)
    base = os.path.splitext(csv_nome)[0]
    meta_filepath = os.path.join(pasta_saida, f"{base}_metadados.json")

    # Coletar e salvar metadados
    config_str = args.config or f"{args.num_medicoes} medições, intervalo {args.intervalo}s"
    meta = coletar_metadados(config_str=config_str, observacoes=args.obs)
    salvar_metadados(meta, meta_filepath)
    imprimir_metadados(meta)

    print(f"=== RAM Monitor ===")
    print(f"Medições: {args.num_medicoes} | Intervalo: {args.intervalo}s")
    print(f"Pasta:    {pasta_saida}")
    print(f"CSV:      {csv_filepath}")
    print(f"Metadados:{meta_filepath}\n")

    medicoes = []

    # Abrir CSV para escrita incremental (não perde dados se interromper)
    with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUNAS)
        writer.writeheader()

        imprimir_header()

        for i in range(1, args.num_medicoes + 1):
            dados = coletar_medicao(i)
            medicoes.append(dados)

            # Escreve no CSV imediatamente
            writer.writerow(dados)
            csvfile.flush()

            # Exibe no terminal
            imprimir_linha(dados)
            imprimir_top3(dados)

            # Aguarda intervalo (exceto após a última medição)
            if i < args.num_medicoes:
                time.sleep(args.intervalo)

    # Resumo final
    print("-" * 100)
    print(f"\n{args.num_medicoes} medições concluídas. Dados salvos em: {pasta_saida}")

    # Exibir valores brutos de memória disponível para fácil cópia
    print(f"\n--- Valores de RAM disponível (GB) ---")
    for m in medicoes:
        print(f"  Medição {m['medicao']:>2}: {m['ram_disponivel_gb']:.2f} GB")

    print(f"\n--- Valores de RAM usada (GB) ---")
    for m in medicoes:
        print(f"  Medição {m['medicao']:>2}: {m['ram_usada_gb']:.2f} GB")

    print()


if __name__ == "__main__":
    main()
