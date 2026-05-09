---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-size: 24px;
  }
  h1 {
    font-size: 36px;
  }
  h2 {
    font-size: 30px;
  }
  table {
    font-size: 20px;
  }
---

**ICC305 2026/01 — Avaliação de Desempenho**

# Mini Estudo 1: Baseline do Uso de RAM em Sistemas Operacionais

Carolina Falabelo Maycá
Luiza da Costa Caxeixa
Nicolas Mady Corrêa Gomes


---

## Contexto

- **Trilha:** Dispositivo Pessoal
- **Pergunta:** O sistema operacional influencia no uso da RAM?
- **Objetivo:** Estabelecer um baseline de consumo de RAM em Windows vs Linux (Ubuntu/Fedora)
- **Abordagem:** Medir o percentual de RAM utilizada após estabilização do sistema com uma carga padronizada

---

## Pergunta Operacional

> Qual é o percentual de uso de RAM em estado estável após a abertura de um conjunto padronizado de aplicações, em máquinas com diferentes sistemas operacionais?

- **Métrica principal:** % de RAM utilizada (`uso_percent`)
- **Instrumento:** Script Python com `psutil.virtual_memory().percent`
- **Medição:** Direta — o kernel reporta o uso real

---

## Protocolo de Coleta

1. Reinicializar a máquina
2. Aguardar estabilização do sistema
3. Executar o script: **30 medições × 20 segundos de intervalo**
4. Dados salvos em CSV + metadados em JSON

**Controles:**
- Mesmo conjunto de aplicações durante toda a coleta
- Mesmo modo de energia
- Mesmo script (`ram_monitor.py`) em todos os ambientes

---

## Ambientes de Coleta

| Operador | SO | RAM | Máquina | CPU (fís/lóg) |
|----------|:--:|:---:|:-------:|:-------------:|
| Carolina | Ubuntu 24.04 | 15,35 GB | carole | 10/12 |
| Carolina | Windows 11 | 15,73 GB | CaroleIII | 10/12 |
| Luiza | Ubuntu 24.04 | 7,50 GB | caxeixas | 4/8 |
| Luiza | Windows 11 | 7,84 GB | swift | 4/8 |
| Nicolas | Fedora 44 | 15,13 GB | fedora | 14/18 |
| Nicolas | Windows 11 | 15,53 GB | DESKTOP-25F8DM4 | 14/18 |

---

## Dados Coletados — Resumo Estatístico

| Cenário | Média (%) | Mediana | Desvio | Mín | Máx |
|---------|:---------:|:-------:|:------:|:---:|:---:|
| Ubuntu 16 GB (Carolina) | 15,48 | 15,5 | 0,06 | 15,4 | 15,6 |
| Windows 16 GB (Carolina) | 35,22 | 32,4 | 5,10 | 31,6 | 44,5 |
| Ubuntu 8 GB (Luiza) | 55,13 | 55,0 | 0,70 | 54,4 | 57,8 |
| Windows 8 GB (Luiza) | 80,39 | 80,2 | 2,72 | 74,7 | 85,6 |
| Fedora 16 GB (Nicolas) | 15,69 | 15,7 | 0,26 | 15,0 | 16,0 |
| Windows 16 GB (Nicolas) | 40,06 | 39,9 | 0,56 | 39,2 | 41,5 |

Coleta: 2026-05-09, 30 medições por cenário

---

## Intervalos de Confiança (95%)

| Cenário | IC 95% | Precisão Relativa |
|---------|:------:|:-----------------:|
| Ubuntu 16 GB (Carolina) | [15,46 ; 15,50] | 0,14% |
| Windows 16 GB (Carolina) | [33,39 ; 37,04] | 5,18% |
| Ubuntu 8 GB (Luiza) | [54,88 ; 55,38] | 0,46% |
| Windows 8 GB (Luiza) | [79,42 ; 81,37] | 1,21% |
| Fedora 16 GB (Nicolas) | [15,59 ; 15,78] | 0,59% |
| Windows 16 GB (Nicolas) | [39,86 ; 40,26] | 0,50% |

5 de 6 cenários com precisão < 1,5% — excelente

---

## Suficiência Amostral

| Cenário | n necessário (5%) | n coletado | Suficiente? |
|---------|:-----------------:|:----------:|:-----------:|
| Ubuntu 16 GB (Carolina) | 1 | 30 | Sim |
| Windows 16 GB (Carolina) | 33 | 30 | Marginal |
| Ubuntu 8 GB (Luiza) | 1 | 30 | Sim |
| Windows 8 GB (Luiza) | 2 | 30 | Sim |
| Fedora 16 GB (Nicolas) | 1 | 30 | Sim |
| Windows 16 GB (Nicolas) | 1 | 30 | Sim |

Windows 16 GB (Carolina) apresentou maior variabilidade por atividade do antivírus MsMpEng durante a coleta.

---

## Visualização — Visão Geral

![w:600](resultados/boxplot_geral.png)

---

## Visualização — Carolina (16 GB)

![w:600](resultados/boxplot_carole.png)

Ubuntu ~15,5% vs Windows ~35% — diferença de ~20 p.p.

---

## Visualização — Luiza (8 GB)

![w:600](resultados/boxplot_luiza.png)

Ubuntu ~55% vs Windows ~80% — diferença de ~25 p.p.

---

## Visualização — Nicolas (16 GB)

![w:600](resultados/boxplot_nic.png)

Fedora ~15,7% vs Windows ~40% — diferença de ~24 p.p.

---

## Visualização — Linux vs Windows (Agregado)

![w:600](resultados/boxplot_linux_vs_windows.png)

Teste t de Welch: p = 3,51 × 10⁻¹³, Cohen's d = −1,17 (efeito grande)

---

## Interpretação

- **16 GB:** Linux usa ~15,5% vs Windows ~35–40% — diferença de 20–24 p.p.
- **8 GB:** Ubuntu usa ~55% vs Windows ~80% — diferença de ~25 p.p.
- Ubuntu e Fedora apresentam resultados muito semelhantes nas máquinas de 16 GB
- Windows opera sob pressão de memória significativamente maior

**Causa provável:** serviços nativos mais pesados no Windows (MsMpEng, explorer.exe, dwm.exe, TiWorker.exe, MemCompression)

---

## Limitações

1. Máquinas com hardware diferente entre operadores (CPUs, RAM)
2. Processos de fundo não equivalentes entre SOs
3. Carga de trabalho não representa todos os perfis de uso
4. Coletas Windows e Linux em instantes temporais diferentes
5. Overhead do próprio script de medição

---

## Conclusão

- **Windows consome significativamente mais RAM que Linux** nas condições testadas
- Diferença de 20–25 pontos percentuais em todos os pares testados
- Protocolo estável: ICs estreitos em 5/6 cenários (precisão < 1,5%)
- Baseline estabelecido com sucesso para comparações futuras
