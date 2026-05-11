---
marp: false
---


# Mini Estudo 1: Baseline do Uso de RAM em Sistemas Operacionais de Dispositivos Pessoais

<div align="center", style="display: flex; align-items: center; justify-content: center; gap: 20px;">
    <img src="https://www.ripsa.org.br/wp-content/uploads/2025/08/32-UFAM-Logo.png" alt="UFAM" width="150"/>
    <img src="https://icomp.ufam.edu.br/images/icomp.png" alt="IComp" width="150"/>
</div>

<div align="center">
Instituto de Computação (IComp) – Universidade Federal do Amazonas (UFAM)<br>
Av. Rodrigo Otávio, nº 6200, Coroado I, Manaus – AM, 69080-900
</div>

<br>

**Grupo:** Carolina Falabelo Maycá, Luiza da Costa Caxeixa, Nicolas Mady Corrêa Gomes<br>
**Trilha:** Dispositivos Pessoais<br>
**Sistema analisado:** Sistemas Operacionais (Windows, Ubuntu, Fedora)<br>
**Repositório:** <https://github.com/carolfmayca/avd-ram><br>
<br>

## Introdução

Esse trabalho foi desenvolvido pelo grupo composto pelos membros citados acima e pertence à trilha de Dispositivos Pessoais. O estudo foi conduzido em dispositivos pessoais dos integrantes da equipe, diferenciando-se principalmente pelo sistema operacional instalado, especificamente o Microsoft Windows, o Ubuntu e o Fedora.

A proposta do Mini Estudo é construir um baseline experimental para observar o comportamento do consumo de memória RAM em cada sistema operacional quando submetido a uma carga de trabalho previamente definida. Para isso, será executado um conjunto equivalente de atividades, utilizando aplicações de mesma finalidade nos ambientes avaliados, buscando manter constantes as condições possíveis de controle, como o tipo de carga executada, o modo de energia, o tempo de estabilização antes da medição e o procedimento de coleta.

<br>

## Ficha de Planejamento

### 1. Qual é a pergunta operacional do Mini Estudo 1?

Qual é o percentual de uso de RAM em máquinas com diferentes sistemas operacionais (Windows, Ubuntu e Fedora)?

<br>

### 2. Qual é o sistema ou cenário-base?

O cenário-base consiste em dispositivos pessoais (notebooks) com configurações de 8 GB e 16 GB de RAM, executando os sistemas operacionais:

- **Windows 11**
- **Ubuntu 24.04**
- **Fedora Linux 44**

<br>

### 3. Qual é a métrica principal e qual é a sua unidade?

**Métrica principal:** Percentual de uso da RAM (`uso_percent`)<br>
**Unidade:** % (porcentagem da memória total)<br>

<br>

### 4. Qual instrumento será usado para medir?

Script Python (`ram_monitor.py`) utilizando a biblioteca `psutil` para acessar `psutil.virtual_memory()`. O instrumento coleta automaticamente os dados em intervalos regulares e os registra em arquivo CSV.

<br>

### 5. O instrumento mede diretamente a métrica ou apenas algo relacionado?

Mede **diretamente**. A função `psutil.virtual_memory().percent` retorna o percentual de memória RAM utilizada conforme reportado pelo kernel do sistema operacional, o que corresponde exatamente à métrica desejada.

<br>

### 6. Qual benchmark ou microbenchmark será executado?

O estudo não emprega benchmark externo. O microbenchmark consiste na observação passiva do consumo de RAM durante um estado de repouso controlado: o sistema é inicializado, aguarda-se um período de estabilização e, sem interação ativa do usuário, o script coleta o uso de memória periodicamente. O próprio ram_monitor.py, por ser um processo Python em execução, representa um overhead de instrumentação mínimo e inevitável, registrado explicitamente como limitação do estudo.

<br>

### 7. Qual carga de trabalho será aplicada?

A carga é composta pelos processos nativos do sistema operacional (serviços de sistema, cache, gerenciador de janelas e daemons de segundo plano) que não podem ser encerrados, além de um conjunto fixo de condições de uso — nenhuma aplicação adicional aberta pelo usuário durante a coleta. Representa um cenário típico de computador pessoal em repouso.

<br>

### 8. Como a carga será caracterizada?

A carga é realista por utilizar aplicações reais que representam um cenário típico de uso de computador pessoal.

**Dimensões:**

- **Volume:** número de aplicações/processos simultâneos (~194–465 processos)
- **Tamanho:** memória total demandada pelo conjunto de processos (~1,8–6,7 GB)
- **Concorrência:** todos os processos executando simultaneamente
- **Mistura:** diferentes tipos de aplicações com perfis distintos de consumo

<br>

### 9. Quantas repetições serão realizadas?

**30 medições por coleta**, com intervalo de 20 segundos entre cada uma. Cada cenário (SO × máquina) possui pelo menos uma coleta de 30 repetições, totalizando dados suficientes para análise estatística com nível de confiança de 95%.

<br>

### 10. O que será mantido constante?

- Modo de energia/desempenho da máquina
- Intervalo entre medições (20 segundos)
- Script de coleta (mesmo `ram_monitor.py` em todos os ambientes)

<br>

### 11. O que será registrado como dado bruto?

Cada medição registra em CSV:

| Campo | Descrição |
|-------|-----------|
| `medicao` | Número sequencial da medição |
| `timestamp` | Data e hora da coleta |
| `so` | Sistema operacional identificado |
| `ram_total_gb` | RAM total em GB |
| `ram_disponivel_gb` | RAM disponível em GB |
| `ram_usada_gb` | RAM usada em GB |
| `uso_percent` | % de uso da RAM |
| `num_processos` | Número de processos ativos |
| `top1..3_nome/pid/ram_mb` | Top 3 processos por consumo de RAM |

<br>

### 12. Que metadados serão registrados?

Arquivo JSON (`medicoes_ram_metadados.json`) com:

- Hostname, arquitetura, processador
- Cores físicos e lógicos da CPU
- RAM total
- SO, kernel, versão completa
- Versões de Python, psutil e distro
- Horário de início e timezone
- Configuração do experimento (nº medições, intervalo)
- Carga do sistema (load average 1/5/15 min)
- CPU % no início
- Status da bateria (%, conectada, tempo restante)
- Observações livres

<br>

### 13. Qual análise mínima será feita?

- **Resumo estatístico:** média, mediana, mínimo, máximo, desvio padrão
- **Incerteza:** intervalo de confiança a 95% (distribuição Normal para n ≥ 30, t-Student para n < 30)
- **Visualização:** boxplot comparativo entre SOs, gráfico de pontos (série temporal)
- **Comparação:** diferença percentual entre SOs para mesma máquina/operador
- **Suficiência amostral:** cálculo do n necessário para precisão relativa de 5%

<br>

### 14. O que o baseline permitirá concluir?

- Qual é o consumo típico de RAM para cada SO sob a carga padronizada definida
- Se existe diferença observável no percentual de uso de RAM entre Windows, Ubuntu e Fedora nas condições testadas
- Que o sistema de medição funciona e produz resultados estáveis e reprodutíveis
- Qual SO apresenta maior pressão sobre a memória nas condições experimentadas

<br>

### 15. O que o baseline não permitirá concluir?

- Que um SO é universalmente "melhor" que outro no gerenciamento de RAM
- Que as diferenças se devem exclusivamente ao SO e não a outros fatores (hardware distinto, serviços pré-instalados)
- Relações causais definitivas entre SO e eficiência de gerenciamento de memória
- Comportamento em cenários de ociosidade total ou saturação de RAM

<br>

### 16. Qual é a principal ameaça à validade do estudo?

A principal ameaça à validade é a diferença na inicialização automática de processos nativos de cada SO e a impossibilidade de finalizá-los para manter um conjunto homogêneo de processos entre os sistemas comparados. Somam-se a isso variações de código binário entre arquiteturas distintas e o overhead das próprias ferramentas de medição, que consomem a mesma RAM que estão medindo.

<br>

### 17. Qual cuidado metodológico principal será adotado?

- Garantir que nenhuma aplicação será aberta pelo usuário durante toda a coleta
- Aguardar estabilização do sistema antes de iniciar as medições
- Registrar metadados completos para permitir auditoria e replicação
- Utilizar o mesmo script de coleta em todos os ambientes
- Manter o modo de desempenho/energia consistente

<br>

## Ambientes de Coleta

| Operador | SO | RAM Total | Máquina | CPU Cores (fís/lóg) |
|----------|:----:|:-----------:|:---------:|:--------------------:|
| Carolina | Ubuntu 24.04 | 15,35 GB | carolina | 10/12 |
| Carolina | Windows 11 | 15,73 GB | carolinaIII | 10/12 |
| Luiza | Ubuntu 24.04 | 7,50 GB | caxeixas | 4/8 |
| Luiza | Windows 11 | 7,84 GB | swift | 4/8 |
| Nicolas | Fedora Linux 44 | 15,13 GB | fedora | 14/18 |
| Nicolas | Windows 11 | 15,53 GB | DESKTOP-25F8DM4 | 14/18 |

<br>

## Dados Coletados (Resumo)

### Coleta do Baseline (2026-05-09, 30 medições × 20s)

| Cenário | $\bar{x}$ (%) | Mediana (%) | $s$ | Mín (%) | Máx (%) | $n$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| Ubuntu 16 GB (Carolina) | 15,48 | 15,5 | 0,0592 | 15,4 | 15,6 | 30 |
| Windows 16 GB (Carolina) | 35,22 | 32,4 | 5,0959 | 31,6 | 44,5 | 30 |
| Ubuntu 8 GB (Luiza) | 23,95 | 23,8 | 0,6174 | 23,7 | 27,2 | 30 |
| Windows 8 GB (Luiza) | 64,89 | 63,6 | 4,4370 | 59,8 | 81,8 | 30 |
| Fedora 16 GB (Nicolas) | 15,69 | 15,7 | 0,2596 | 15,0 | 16,0 | 30 |
| Windows 16 GB (Nicolas) | 40,06 | 39,9 | 0,5587 | 39,2 | 41,5 | 30 |

Esses dados foram coletados com 30 medições a cada 20 segundos

<br>

## Análise Estatística

### Intervalos de Confiança (95%) — Baseline 2026-05-09

Os intervalos foram calculados com $t_{29;\,0{,}025} = 2{,}045$ (distribuição t de Student, $n-1 = 29$ graus de liberdade).

**Ubuntu 16 GB (Carolina):** $\bar{x} = 15,48\%$, $s = 0,0592$, $n = 30$

$$
IC_{95\%} = \left[15{,}48 - \frac{2{,}045 \times 0{,}0592}{\sqrt{30}}; 15{,}48 + \frac{2{,}045 \times 0{,}0592}{\sqrt{30}}\right] = [15{,}46\%; 15{,}51\%]
$$

Precisão relativa: $0,14\%$ — excelente.

**Windows 16 GB (Carolina):** $\bar{x} = 35,22\%$, $s = 5,0959$, $n = 30$

$$
IC_{95\%} = \left[35{,}22 - \frac{2{,}045 \times 5{,}0959}{\sqrt{30}}; 35{,}22 + \frac{2{,}045 \times 5{,}0959}{\sqrt{30}}\right] = [33{,}31\%; 37{,}12\%]
$$

Precisão relativa: $5,40\%$ — no limiar de 5%. O desvio padrão elevado reflete picos de uso durante a coleta (medições com ~44%), possivelmente causados por atividade do antivírus MsMpEng. $n$ necessário para 5%: 36 (≈ o $n$ atual de 30).

**Ubuntu 8 GB (Luiza):** $\bar{x} = 23,95\%$, $s = 0,6174$, $n = 30$

$$
IC_{95\%} = [23{,}95 - \frac{2{,}045 \times 0{,}6174}{\sqrt{30}}; 23{,}95 + \frac{2{,}045 \times 0{,}6174}{\sqrt{30}}] = [23{,}72\%; 24{,}18\%]
$$

Precisão relativa: $0,96\%$ — excelente.

**Windows 8 GB (Luiza):** $\bar{x} = 64,89\%$, $s = 4,4370$, $n = 30$

$$
IC_{95\%} = \left[64{,}89 - \frac{2{,}045 \times 4{,}4370}{\sqrt{30}}; 64{,}89 + \frac{2{,}045 \times 4{,}4370}{\sqrt{30}}\right] = [63{,}24\%; 66{,}55\%]
$$

Precisão relativa: $2,55\%$ — excelente. A variabilidade é influenciada pela atividade do processo TiWorker.exe (Windows Update) que atingiu até ~1.400 MB nas medições 21–23.

**Fedora 16 GB (Nicolas):** $\bar{x} = 15,69\%$, $s = 0,2596$, $n = 30$

$$
IC_{95\%} = \left[15{,}69 - \frac{2{,}045 \times 0{,}2596}{\sqrt{30}}; 15{,}69 + \frac{2{,}045 \times 0{,}2596}{\sqrt{30}}\right] = [15{,}59\%; 15{,}78\%]
$$

Precisão relativa: $0,62\%$ — excelente.

**Windows 16 GB (Nicolas):** $\bar{x} = 40,06\%$, $s = 0,5587$, $n = 30$

$$
IC_{95\%} = \left[40{,}06 - \frac{2{,}045 \times 0{,}5587}{\sqrt{30}}; 40{,}06 + \frac{2{,}045 \times 0{,}5587}{\sqrt{30}}\right] = [39{,}85\%; 40{,}27\%]
$$

Precisão relativa: $0,52\%$ — excelente.

### Suficiência Amostral

Para 5% de precisão relativa a 95% de confiança, o $n$ necessário é:

| Cenário | $n$ necessário | $n$ coletado | Suficiente? |
|---------|:---:|:---:|:---:|
| Ubuntu 16 GB (Carolina) | 1 | 30 | Sim |
| Windows 16 GB (Carolina) | 36 | 30 | Marginal |
| Ubuntu 8 GB (Luiza) | 2 | 30 | Sim |
| Windows 8 GB (Luiza) | 8 | 30 | Sim |
| Fedora 16 GB (Nicolas) | 1 | 30 | Sim |
| Windows 16 GB (Nicolas) | 1 | 30 | Sim |

<br>

## Visualização

### Visão Geral — Todos os Participantes

![Boxplot geral — todos os participantes](https://raw.githubusercontent.com/carolfmayca/avd-ram/refs/heads/main/resultados/boxplot_geral.png)

*Figura 1: Boxplot comparativo do uso de RAM em repouso para todos os participantes, agrupado por SO.*

### Por Participante

![Boxplot Carolina](https://raw.githubusercontent.com/carolfmayca/avd-ram/refs/heads/main/resultados/resultados/boxplot_carolina.png)

*Figura 2: Carolina: Ubuntu 24.04 (~15,5%) vs Windows 11 (~35%). Nota-se outliers no Windows (medições 24–30 com ~44%), causados por atividade do antivírus MsMpEng.*

![Boxplot Luiza](https://raw.githubusercontent.com/carolfmayca/avd-ram/refs/heads/main/resultados/boxplot_luiza.png)

*Figura 3: Luiza: Ubuntu 24.04 (~24%) vs Windows 11 (~65%). A variabilidade do Windows é causada pelo processo TiWorker.exe (Windows Update), que atingiu ~1.400 MB nas medições 21–23, gerando o pico de 81,8%.*

![Boxplot Nicolas](https://raw.githubusercontent.com/carolfmayca/avd-ram/refs/heads/main/resultados/boxplot_nic.png)

*Figura 4: Nicolas: Fedora 44 (~15,7%) vs Windows 11 (~40%). Ambos os SOs apresentam baixa variabilidade, com ICs estreitos.*

### Linux vs Windows — Comparação Agregada

![Linux vs Windows](https://raw.githubusercontent.com/carolfmayca/avd-ram/refs/heads/main/resultados/boxplot_linux_vs_windows.png)

*Figura 5: Comparação agregada Linux (Ubuntu/Fedora) vs Windows (n=90 cada). Linux: μ = 18,4%, IC95% [17,5%; 19,2%]. Windows: μ = 46,7%, IC95% [43,9%; 49,6%]. Teste t de Welch: t = −18,93, p = 1,70 × 10⁻³⁵, Cohen's d = −2,82 (efeito muito grande). A diferença é estatisticamente significativa.*

<br>

## Interpretação

Os dados sugerem que o **sistema operacional tem influência significativa no percentual de uso de RAM**:

- **Máquina 16 GB (Carolina):** Ubuntu usa **15,48%** (≈2,4 GB) enquanto Windows usa **35,22%** (≈5,5 GB) — diferença de **~20 pontos percentuais**.
- **Máquina 16 GB (Nicolas):** Fedora usa **15,69%** (≈2,4 GB) enquanto Windows usa **40,06%** (≈6,2 GB) — diferença de **~24 pontos percentuais**.
- **Máquina 8 GB (Luiza):** Ubuntu usa **23,95%** (≈1,8 GB) enquanto Windows usa **64,89%** (≈5,1 GB) — diferença de **~41 pontos percentuais**.
- Ubuntu e Fedora apresentam resultados muito semelhantes (~15,5–16%) nas máquinas de 16 GB. Na máquina de 8 GB, o Ubuntu também mantém uso moderado (~24%).
- O Windows consome significativamente mais RAM em todos os cenários avaliados.

O Windows consome sistematicamente mais RAM que distribuições Linux (Ubuntu e Fedora) nas mesmas condições, possivelmente devido a serviços nativos mais pesados (antivírus MsMpEng, explorer.exe, dwm.exe, TiWorker.exe, MemCompression) e maior uso de cache/buffers internos.

<br>


## Conclusão

O baseline demonstra que, para uma carga de trabalho típica de um usuário de dispositivo pessoal, **o Windows consome significativamente mais memória RAM que distribuições Linux** (Ubuntu e Fedora). Nas máquinas com 16 GB, a diferença chega a 20–24 pontos percentuais (~15% no Linux vs ~35–40% no Windows). Na máquina com 8 GB, a diferença foi de ~41 pontos percentuais (Ubuntu ~24% vs Windows ~65%).

O protocolo de coleta é estável e reprodutível. Os intervalos de confiança são estreitos para 5 dos 6 cenários (precisão relativa < 3%), validando o instrumento e a metodologia. O cenário Windows 16 GB (Carolina) apresentou maior variabilidade (precisão ~5%), possivelmente por atividade do antivírus MsMpEng; o cenário Windows 8 GB (Luiza) também apresentou variabilidade (precisão ~2,55%) devido à atividade do TiWorker.exe (Windows Update) durante a coleta.
