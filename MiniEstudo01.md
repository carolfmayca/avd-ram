---
marp: false
---

# Mini Estudo 1: Baseline do Uso de RAM em Sistemas Operacionais de Dispositivos Pessoais

**Carolina Falabelo Maycá, Luiza da Costa Caxeixa, Nicolas Mady Corrêa Gomes**

<!-- justified -->

Instituto de Computação (IComp) – Universidade Federal do Amazonas (UFAM)
Av. Rodrigo Otávio, nº 6200, Coroado I, Manaus – AM, 69080-900

---

## Introdução

Esse trabalho foi desenvolvido pelo grupo composto pelos membros citados acima e pertence à trilha de Dispositivos Pessoais. O estudo foi conduzido em dispositivos pessoais do mesmo tipo, diferenciando-se apenas pelo sistema operacional instalado, especificamente o Microsoft Windows e o Ubuntu.

A proposta do Mini Estudo é estabelecer um baseline experimental que permita observar como esses sistemas operacionais gerenciam a memória RAM quando submetidos a uma carga de trabalho padronizada, composta por um conjunto fixo de aplicações executadas simultaneamente. A partir desse procedimento controlado, busca-se analisar o comportamento da memória disponível após a estabilização do sistema, possibilitando uma comparação inicial entre os ambientes avaliados.

---

## Ficha de Planejamento

**Grupo:** Carolina Falabelo Maycá, Luiza da Costa Caxeixa, Nicolas Mady Corrêa Gomes
**Trilha:** Dispositivos Pessoais
**Sistema analisado:** Sistemas Operacionais (Windows, Ubuntu, Fedora)
**Repositório:** <https://github.com/carolfmayca/avd-ram>

---

### 1. Qual é a pergunta operacional do Mini Estudo 1?

Qual é o percentual de uso de RAM em estado estável após a abertura de um conjunto padronizado de aplicações, em máquinas com diferentes sistemas operacionais (Windows, Ubuntu e Fedora)?

---

### 2. Qual é o sistema ou cenário-base?

O cenário-base consiste em dispositivos pessoais (notebooks) com configurações de 8 GB e 16 GB de RAM, executando os sistemas operacionais:

- **Windows 11** (versão 10.0.26200)
- **Ubuntu 24.04**
- **Fedora Linux 44**

Cada operador executa o experimento na sua própria máquina, com reinicialização controlada antes de cada coleta.

---

### 3. Qual é a métrica principal e qual é a sua unidade?

**Métrica principal:** Percentual de uso da RAM (`uso_percent`)
**Unidade:** % (porcentagem da memória total)

---

### 4. Qual instrumento será usado para medir?

Script Python (`src/ram_monitor.py`) utilizando a biblioteca `psutil` para acessar `psutil.virtual_memory()`. O instrumento coleta automaticamente os dados em intervalos regulares e os registra em arquivo CSV.

---

### 5. O instrumento mede diretamente a métrica ou apenas algo relacionado?

Mede **diretamente**. A função `psutil.virtual_memory().percent` retorna o percentual de memória RAM utilizada conforme reportado pelo kernel do sistema operacional, o que corresponde exatamente à métrica desejada.

---

### 6. Qual benchmark ou microbenchmark será executado?

O experimento consiste em um **microbenchmark de estado estável**: após reinicialização do sistema, abre-se um conjunto fixo de aplicações (processos do SO + aplicações do usuário como navegador, VS Code), aguarda-se a estabilização, e coleta-se 30 medições com intervalo de 20 segundos entre cada uma.

---

### 7. Qual carga de trabalho será aplicada?

A carga é composta por:

- Processos nativos do SO (serviços de sistema, cache, gerenciador de janelas)
- Conjunto padronizado de aplicações abertas simultaneamente (navegador, editor de código, etc.)

Cada operador manteve as mesmas aplicações abertas ao longo de todas as medições.

---

### 8. Como a carga será caracterizada?

A carga é uma **combinação entre realista e sintética**:

- **Realista** por utilizar aplicações reais que representam um cenário típico de uso de computador pessoal.
- **Sintética** pelo controle rigoroso: reinicialização antes de cada coleta, mesmo conjunto de processos, mesmo modo de energia.

**Dimensões:**

- **Volume:** número de aplicações/processos simultâneos (~194–465 processos)
- **Tamanho:** memória total demandada pelo conjunto de processos (~1,8–6,7 GB)
- **Concorrência:** todos os processos executando simultaneamente
- **Mistura:** diferentes tipos de aplicações com perfis distintos de consumo

---

### 9. Quantas repetições serão realizadas?

**30 medições por coleta**, com intervalo de 20 segundos entre cada uma. Cada cenário (SO × máquina) possui pelo menos uma coleta de 30 repetições, totalizando dados suficientes para análise estatística com nível de confiança de 95%.

---

### 10. O que será mantido constante?

- Conjunto de aplicações abertas durante cada sessão de coleta
- Modo de energia/desempenho da máquina
- Intervalo entre medições (20 segundos)
- Script de coleta (mesmo `ram_monitor.py` em todos os ambientes)
- Condição de início: reinicialização controlada + estabilização antes da coleta

---

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

---

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

---

### 13. Qual análise mínima será feita?

- **Resumo estatístico:** média, mediana, mínimo, máximo, desvio padrão
- **Incerteza:** intervalo de confiança a 95% (distribuição Normal para n ≥ 30, t-Student para n < 30)
- **Visualização:** boxplot comparativo entre SOs, gráfico de pontos (série temporal)
- **Comparação:** diferença percentual entre SOs para mesma máquina/operador
- **Suficiência amostral:** cálculo do n necessário para precisão relativa de 5%

---

### 14. O que o baseline permitirá concluir?

- Qual é o consumo típico de RAM para cada SO sob a carga padronizada definida
- Se existe diferença observável no percentual de uso de RAM entre Windows, Ubuntu e Fedora nas condições testadas
- Que o sistema de medição funciona e produz resultados estáveis e reprodutíveis
- Qual SO apresenta maior pressão sobre a memória nas condições experimentadas

---

### 15. O que o baseline não permitirá concluir?

- Que um SO é universalmente "melhor" que outro no gerenciamento de RAM
- Que as diferenças observadas se mantêm sob outras cargas de trabalho (uso extremo, jogos, edição de vídeo)
- Que as diferenças se devem exclusivamente ao SO e não a outros fatores (hardware distinto, serviços pré-instalados)
- Relações causais definitivas entre SO e eficiência de gerenciamento de memória
- Comportamento em cenários de ociosidade total ou saturação de RAM

---

### 16. Qual é a principal ameaça à validade do estudo?

**Diferenças na inicialização automática de processos entre SOs.** Cada sistema operacional inicia um conjunto próprio de serviços e processos de fundo que não podem ser completamente padronizados entre Windows, Ubuntu e Fedora. Além disso, as máquinas dos integrantes possuem configurações de hardware distintas (8 GB vs 16 GB, diferentes CPUs), o que impede uma comparação direta perfeitamente controlada.

---

### 17. Qual cuidado metodológico principal será adotado?

- Reinicialização controlada antes de cada sessão de coleta
- Garantir que o mesmo conjunto de aplicações do usuário esteja ativo durante toda a coleta
- Aguardar estabilização do sistema antes de iniciar as medições
- Registrar metadados completos para permitir auditoria e replicação
- Utilizar o mesmo script de coleta em todos os ambientes
- Manter o modo de desempenho/energia consistente

---

## Ambientes de Coleta

| Operador | SO | RAM Total | Máquina | CPU Cores (fís/lóg) |
|----------|----|-----------|---------|--------------------|
| Carolina | Ubuntu 24.04 | 15,35 GB | carole | 10/12 |
| Carolina | Windows 11 (10.0.26200) | 15,73 GB | CaroleIII | 10/12 |
| Luiza | Ubuntu 24.04 | 7,50 GB | caxeixas | 4/8 |
| Luiza | Windows 11 (10.0.26200) | 7,84 GB | swift | 4/8 |
| Nicolas | Fedora Linux 44 | 15,13 GB | fedora | 14/18 |
| Nicolas | Windows 11 (10.0.26200) | 15,53 GB | DESKTOP-25F8DM4 | 14/18 |

---

## Dados Coletados (Resumo)

### Coleta do Baseline (2026-05-09, 30 medições × 20s)

| Cenário | $\bar{x}$ (%) | Mediana (%) | $s$ | Mín (%) | Máx (%) | $n$ |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| Ubuntu 16 GB (Carolina) | 15,48 | 15,5 | 0,0592 | 15,4 | 15,6 | 30 |
| Windows 16 GB (Carolina) | 35,22 | 32,4 | 5,0959 | 31,6 | 44,5 | 30 |
| Ubuntu 8 GB (Luiza) | 55,13 | 55,0 | 0,7029 | 54,4 | 57,8 | 30 |
| Windows 8 GB (Luiza) | 80,39 | 80,2 | 2,7232 | 74,7 | 85,6 | 30 |
| Fedora 16 GB (Nicolas) | 15,69 | 15,7 | 0,2596 | 15,0 | 16,0 | 30 |
| Windows 16 GB (Nicolas) | 40,06 | 39,9 | 0,5587 | 39,2 | 41,5 | 30 |

---

## Análise Estatística Mínima

### Intervalos de Confiança (95%) — Baseline 2026-05-09

**Ubuntu 16 GB (Carolina):** $\bar{x} = 15,48\%$, $s = 0,0592$, $n = 30$

$$
IC_{95\%} = \left[15,48 - \frac{0,0592 \times 1,960}{\sqrt{30}}\;;\; 15,48 + \frac{0,0592 \times 1,960}{\sqrt{30}}\right] = [15,46\%\;;\; 15,50\%]
$$

Precisão relativa: $0,14\%$ — excelente.

**Windows 16 GB (Carolina):** $\bar{x} = 35,22\%$, $s = 5,0959$, $n = 30$

$$
IC_{95\%} = \left[35,22 - \frac{5,0959 \times 1,960}{\sqrt{30}}\;;\; 35,22 + \frac{5,0959 \times 1,960}{\sqrt{30}}\right] = [33,39\%\;;\; 37,04\%]
$$

Precisão relativa: $5,18\%$ — no limiar de 5%. O desvio padrão elevado reflete um pico de uso durante a coleta (medições 24–30 com ~44%), possivelmente causado por atividade do antivírus MsMpEng. $n$ necessário para 5%: 33 (≈ o $n$ atual de 30).

**Ubuntu 8 GB (Luiza):** $\bar{x} = 55,13\%$, $s = 0,7029$, $n = 30$

$$
IC_{95\%} = \left[55,13 - \frac{0,7029 \times 1,960}{\sqrt{30}}\;;\; 55,13 + \frac{0,7029 \times 1,960}{\sqrt{30}}\right] = [54,88\%\;;\; 55,38\%]
$$

Precisão relativa: $0,46\%$ — excelente.

**Windows 8 GB (Luiza):** $\bar{x} = 80,39\%$, $s = 2,7232$, $n = 30$

$$
IC_{95\%} = \left[80,39 - \frac{2,7232 \times 1,960}{\sqrt{30}}\;;\; 80,39 + \frac{2,7232 \times 1,960}{\sqrt{30}}\right] = [79,42\%\;;\; 81,37\%]
$$

Precisão relativa: $1,21\%$ — excelente.

**Fedora 16 GB (Nicolas):** $\bar{x} = 15,69\%$, $s = 0,2596$, $n = 30$

$$
IC_{95\%} = \left[15,69 - \frac{0,2596 \times 1,960}{\sqrt{30}}\;;\ 15,69 + \frac{0,2596 \times 1,960}{\sqrt{30}}\right] = [15,59\%\;;\ 15,78\%]
$$

Precisão relativa: $0,59\%$ — excelente.

**Windows 16 GB (Nicolas):** $\bar{x} = 40,06\%$, $s = 0,5587$, $n = 30$

$$
IC_{95\%} = \left[40,06 - \frac{0,5587 \times 1,960}{\sqrt{30}}\;;\ 40,06 + \frac{0,5587 \times 1,960}{\sqrt{30}}\right] = [39,86\%\;;\ 40,26\%]
$$

Precisão relativa: $0,50\%$ — excelente.

### Suficiência Amostral

Para 5% de precisão relativa a 95% de confiança, o $n$ necessário é:

| Cenário | $n$ necessário | $n$ coletado | Suficiente? |
|---------|:---:|:---:|:---:|
| Ubuntu 16 GB (Carolina) | 1 | 30 | Sim |
| Windows 16 GB (Carolina) | 33 | 30 | Marginal |
| Ubuntu 8 GB (Luiza) | 1 | 30 | Sim |
| Windows 8 GB (Luiza) | 2 | 30 | Sim |
| Fedora 16 GB (Nicolas) | 1 | 30 | Sim |
| Windows 16 GB (Nicolas) | 1 | 30 | Sim |

---

## Interpretação

Os dados sugerem que o **sistema operacional tem influência significativa no percentual de uso de RAM**:

- **Máquina 16 GB (Carolina):** Ubuntu usa **15,48%** (≈1,76 GB) enquanto Windows usa **35,22%** (≈5,5 GB) — diferença de **~20 pontos percentuais**.
- **Máquina 16 GB (Nicolas):** Fedora usa **15,69%** (≈2,4 GB) enquanto Windows usa **40,06%** (≈6,2 GB) — diferença de **~24 pontos percentuais**.
- **Máquina 8 GB (Luiza):** Ubuntu usa **55,13%** (≈4,1 GB) enquanto Windows usa **80,39%** (≈6,3 GB) — diferença de **~25 pontos percentuais**.
- O Windows opera sob pressão de memória significativamente maior, especialmente na máquina de 8 GB (>80% de uso).
- Ubuntu e Fedora apresentam resultados muito semelhantes (~15,5%) nas máquinas de 16 GB.

O Windows consome sistematicamente mais RAM que distribuições Linux (Ubuntu e Fedora) nas mesmas condições, possivelmente devido a serviços nativos mais pesados (antivírus MsMpEng, explorer.exe, dwm.exe, TiWorker.exe, MemCompression) e maior uso de cache/buffers internos.

---

## Limitações

1. As máquinas não possuem hardware idêntico (CPUs e RAM diferentes entre operadores).
2. Não é possível garantir processos de fundo exatamente equivalentes entre SOs distintos.
3. A carga de trabalho padronizada não representa todos os perfis de uso possíveis.
4. As coletas Windows e Linux não foram realizadas rigorosamente no mesmo instante temporal.
5. O próprio script de medição consome RAM (overhead de instrumentação).

---

## Conclusão

O baseline demonstra que, para uma carga de trabalho típica de um usuário de dispositivo pessoal, **o Windows consome significativamente mais memória RAM que distribuições Linux** (Ubuntu e Fedora). Nas máquinas com 16 GB, a diferença chega a 20–24 pontos percentuais (~15% no Linux vs ~35–40% no Windows). Na máquina com 8 GB, o Windows opera sob alta pressão de memória (~80%), enquanto o Ubuntu mantém ~55% de uso.

O protocolo de coleta é estável e reprodutível. Os intervalos de confiança são estreitos para 5 dos 6 cenários (precisão relativa < 1,5%), validando o instrumento e a metodologia. O cenário Windows 16 GB (Carolina) apresentou maior variabilidade (precisão ~5%), possivelmente por atividade de processos de sistema (antivírus) durante a coleta.
