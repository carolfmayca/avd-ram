# Projeto de Experimentos — Coleta e análise (uso dos scripts)

Instruções de execução dos scripts do projeto fatorial 2³ r. O relatório está em
[README.md](README.md).

## Coleta (`coleta_fatorial.py`)

`coleta_fatorial.py` mede `r` replicações de uma combinação e já as anexa rotuladas
(`A,B,C,rep,uso_percent`) ao CSV mestre. Os fatores **A** (SO) e **B** (RAM) são
detectados automaticamente da máquina; **C** (carga) vem da flag `--carga`. Quando
`--carga pesada` é usado, o script aloca memória automaticamente para gerar pressão
de RAM. Como A×B é fixo por máquina, cada operador roda o script duas vezes por
máquina (repouso e pesada); entre os integrantes as 8 combinações são cobertas.

```bash
# antes de cada carga: deixar a máquina no estado correspondente
python coleta_fatorial.py --carga repouso -n 3 -i 20    # C = -1
python coleta_fatorial.py --carga pesada  -n 3 -i 20    # C = +1, aloca 1024 MB

# se a detecção automática não bater com o planejado, force os níveis:
python coleta_fatorial.py --carga pesada -n 3 --a 1 --b -1   # Windows, 8 GB

# ajuste a intensidade da carga, se necessário:
python coleta_fatorial.py --carga pesada -n 3 -i 20 --carga-mb 2048

# para comportamento antigo, apenas rotulando C=+1 sem alocar RAM:
python coleta_fatorial.py --carga pesada -n 3 -i 20 --carga-mb 0
```

Cada rodada também salva um CSV detalhado + `metadados.json` numa pasta própria
(top-3 processos, nº de processos, hardware, bateria) para auditoria.

## Análise (`analise_fatorial.py`)

```bash
python analise_fatorial.py dados_2k_r.csv
```

O script calcula `q0`, os coeficientes dos efeitos principais e interações pela tabela
de sinais, a soma de quadrados de cada termo (`SQ = N·q²`), o erro experimental
(variação dentro de cada combinação) e o percentual da variação explicada por termo.
