# Mini Estudo 2: Projeto de Experimentos 2³ — Fatores que Explicam o Uso de RAM

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
**Sistema analisado:** Sistemas Operacionais (Windows, Ubuntu/Fedora)<br>
**Repositório:** <https://github.com/carolfmayca/avd-ram><br>
<br>

## Introdução

Este Mini Estudo dá continuidade ao baseline construído no Mini Estudo 1, no qual
foi observado que o sistema operacional influencia fortemente o percentual de uso de
RAM em repouso. Aqui o objetivo deixa de ser apenas *medir* o consumo e passa a ser
**entender quais fatores realmente explicam a variação do desempenho** e se há
**interações relevantes** entre eles.

Para isso é executado um projeto fatorial completo **2³ com replicação** (`2^k r`,
com `k = 3` e `r = 3`): três fatores controláveis, cada um em dois níveis codificados
como `-1` e `+1`, todas as `2³ = 8` combinações medidas `r` vezes. A análise estima o
efeito individual de cada fator, o efeito das interações, a soma de quadrados, o
percentual da variação explicada por termo e a parcela atribuída ao **erro
experimental** estimado pelas replicações.

<br>

## 1. Identificação da trilha

| Item | Conteúdo |
|------|----------|
| Nome do grupo | Carolina Maycá, Luiza Caxeixa, Nicolas Mady |
| Trilha de avaliação | Dispositivos Pessoais |
| Sistema avaliado | Sistemas operacionais em notebooks pessoais |
| Métrica principal | Percentual de uso da RAM (`uso_percent`), em % |
| Métricas auxiliares | Número de processos ativos, RAM usada (GB), RAM disponível (GB) |

<br>

## 2. Brainstorming de fatores

Lista ampla de fatores que podem afetar o percentual de uso de RAM, classificados em
controláveis, não controláveis e mantidos constantes.

| # | Fator | Classificação |
|---|-------|---------------|
| 1 | Sistema operacional (Windows vs Linux) | Controlável |
| 2 | Tamanho da RAM física (8 GB vs 16 GB) | Controlável |
| 3 | Carga de trabalho (repouso vs aplicações abertas) | Controlável |
| 4 | Uso de SWAP / paginação habilitada | Controlável (mantido constante) |
| 5 | Modo de energia / desempenho | Controlável (mantido constante) |
| 6 | Número de processos em segundo plano | Parcialmente controlável |
| 7 | Atualizações automáticas do SO (Windows Update, dnf) | Não controlável |
| 8 | Atividade do antivírus (MsMpEng) | Não controlável |
| 9 | Arquitetura / geração da CPU | Não controlável (hardware fixo) |
| 10 | Velocidade / geração da RAM | Não controlável (hardware fixo) |
| 11 | Cache de disco gerenciado pelo kernel | Não controlável |
| 12 | Tempo de estabilização antes da medição | Controlável (mantido constante) |

<br>

## 3. Seleção dos fatores controláveis (k = 3)

| Fator considerado | Decisão | Justificativa |
|-------------------|---------|---------------|
| **A — Sistema operacional** | Selecionado | Foi o fator de maior impacto no baseline (Mini Estudo 1); dois níveis claros (Windows / Linux). |
| **B — Tamanho da RAM** | Selecionado | A equipe dispõe de máquinas de 8 GB e 16 GB; níveis bem definidos e fisicamente relevantes para a pressão de memória. |
| **C — Carga de trabalho** | Selecionado | Permite testar se o efeito do SO depende da carga (interação); dois níveis controláveis (repouso vs conjunto fixo de aplicações). |
| Uso de SWAP | Controlado, não analisado | Mantido na configuração padrão de cada SO para não introduzir um quarto fator e manter `k = 3` viável. |
| Modo de energia | Controlado, não analisado | Fixado em "alto desempenho" em todas as combinações para isolar os fatores analisados. |
| Atualização automática / antivírus | Descartado | Não controlável de forma confiável; tratado como fonte de ruído (erro experimental). |
| Geração de CPU/RAM | Descartado | Hardware fixo por máquina; não tem dois níveis manipuláveis dentro da trilha. |

<br>

## 4. Definição dos níveis dos fatores

| Fator | Nível `-1` | Nível `+1` |
|-------|:----------:|:----------:|
| **A** — Sistema operacional | Linux (Ubuntu/Fedora) | Windows 11 |
| **B** — Tamanho da RAM | 8 GB | 16 GB |
| **C** — Carga de trabalho | Repouso (nenhuma app aberta) | Carga pesada (conjunto fixo de aplicações) |

<br>

## 5. Planejamento experimental

| Parâmetro | Valor |
|-----------|-------|
| `k` (fatores) | 3 |
| `r` (replicações) | 3 |
| `N` total de medições | `2³ × 3 = 24` |
| Métrica registrada | `uso_percent` (% de uso da RAM) |

**Justificativa para `r = 3`:** a replicação é necessária para estimar o erro
experimental — sem repetir a medição na mesma combinação não é possível separar a
variação causada pelos fatores da variação aleatória do sistema. `r = 3` é o mínimo
exigido pela atividade e suficiente para uma primeira estimativa do erro; o baseline
mostrou desvios-padrão baixos (precisão relativa < 3% na maioria dos cenários), o que
torna `r = 3` razoável para esta etapa exploratória.

**Cuidados de execução:** manter constantes os fatores não analisados (SWAP, modo de
energia, tempo de estabilização); executar as combinações em ordem aleatória; usar o
mesmo procedimento de coleta (`coleta_fatorial.py`) em todas; registrar anomalias e
medições descartadas.

### Matriz experimental (tabela de sinais)

| Comb. | A | B | C | AB | AC | BC | ABC |
|:-----:|:--:|:--:|:--:|:--:|:--:|:--:|:---:|
| 1 | − | − | − | + | + | + | − |
| 2 | + | − | − | − | − | + | + |
| 3 | − | + | − | − | + | − | + |
| 4 | + | + | − | + | − | − | − |
| 5 | − | − | + | + | − | − | + |
| 6 | + | − | + | − | + | − | − |
| 7 | − | + | + | − | − | + | − |
| 8 | + | + | + | + | + | + | + |

Cada combinação é medida `r = 3` vezes. Os dados brutos vão em
[dados_2k_r.csv](dados_2k_r.csv) (uma linha por medição: `A,B,C,rep,uso_percent`).

<br>

## 6. Resultados

Coleta realizada em 2026-07-01. Cenários de 16 GB por Carolina (Ubuntu 24.04 /
Windows 11), cenários de 8 GB por Luiza (Ubuntu 24.04 / Windows 11). `N = 24`,
`r = 3`, média geral `q0 = 33,33 %`. Valores brutos em
[dados_2k_r.csv](dados_2k_r.csv).

### Repetições por combinação

| Comb. | A | B | C | $y_1$ | $y_2$ | $y_3$ |
|:-----:|:--:|:--:|:--:|:---:|:---:|:---:|
| 1 | − | − | − | 18,2 | 17,7 | 17,8 |
| 2 | + | − | − | 54,5 | 53,6 | 54,3 |
| 3 | − | + | − | 18,1 | 18,1 | 18,1 |
| 4 | + | + | − | 40,3 | 39,4 | 40,9 |
| 5 | − | − | + | 17,7 | 17,7 | 17,7 |
| 6 | + | − | + | 54,4 | 55,6 | 54,0 |
| 7 | − | + | + | 18,1 | 18,1 | 18,1 |
| 8 | + | + | + | 44,4 | 47,0 | 46,0 |

### Média e desvio padrão por combinação

| Comb. | A | B | C | $\bar{x}$ (%) | $s$ |
|:-----:|:--:|:--:|:--:|:---:|:---:|
| 1 | − | − | − | 17,90 | 0,26 |
| 2 | + | − | − | 54,13 | 0,47 |
| 3 | − | + | − | 18,10 | 0,00 |
| 4 | + | + | − | 40,20 | 0,76 |
| 5 | − | − | + | 17,70 | 0,00 |
| 6 | + | − | + | 54,67 | 0,83 |
| 7 | − | + | + | 18,10 | 0,00 |
| 8 | + | + | + | 45,80 | 1,31 |

### Efeitos, soma de quadrados e variação explicada

| Efeito | Coeficiente estimado ($q$) | Soma de quadrados | % da variação |
|:------:|:---:|:---:|:---:|
| A | 15,375 | 5673,38 | 92,74 % |
| B | −2,775 | 184,82 | 3,02 % |
| C | 0,742 | 13,20 | 0,22 % |
| AB | −2,925 | 205,34 | 3,36 % |
| AC | 0,792 | 15,04 | 0,25 % |
| BC | 0,658 | 10,40 | 0,17 % |
| ABC | 0,608 | 8,88 | 0,15 % |
| Erro experimental | — | 6,55 | 0,11 % |

<br>

## 7. Discussão dos resultados

**1. Qual fator teve o maior impacto na métrica principal?**
O fator **A (sistema operacional)**, responsável por **92,74 %** da variação total.
Seu coeficiente ($q_A = 15,38$) implica uma diferença média de ~30,8 pontos
percentuais entre Linux (~18 %) e Windows (~48 %) na mesma máquina.

**2. Esse impacto era esperado? Por quê?**
Sim. O Mini Estudo 1 já indicava que o Windows consome sistematicamente mais RAM que
distribuições Linux nas mesmas condições, por causa de serviços nativos mais pesados
(MsMpEng, explorer.exe, dwm.exe). O projeto fatorial confirma e quantifica esse efeito.

**3. Houve alguma interação relevante entre os fatores?**
Sim, a interação **AB (SO × RAM)**, com **3,36 %** da variação — maior que o efeito
principal de B isoladamente (3,02 %). O efeito do SO depende do tamanho da RAM: no
Windows, a máquina de 8 GB usa ~54 % enquanto a de 16 GB usa ~40–46 %; no Linux o uso
permanece ~18 % nos dois tamanhos. Ou seja, a pressão de memória do Windows é mais
severa quando há menos RAM física. As demais interações (AC, BC, ABC) são desprezíveis
(< 0,3 %).

**4. O resultado confirma ou contradiz a intuição inicial do grupo?**
Confirma. A hipótese da trilha ("o SO influencia o uso de RAM") é fortemente sustentada:
o SO sozinho explica quase toda a variação observada.

**5. Algum fator escolhido parece pouco importante?**
Sim, o fator **C (carga de trabalho)**, com apenas **0,22 %** da variação. A diferença
entre repouso e carga pesada foi pequena — perceptível só no Windows 16 GB (40,2 % →
45,8 %) e quase nula no Linux. Indica que a "carga pesada" definida não pressionou a
memória o suficiente para rivalizar com o efeito do SO.

**6. A variabilidade entre repetições foi pequena ou grande?**
Muito pequena. O erro experimental representa **0,11 %** da variação total; os desvios
padrão por combinação ficaram entre 0,00 e 1,31 ponto percentual. Várias combinações
tiveram $s = 0$ (leituras idênticas).

**7. O valor de `r` escolhido foi suficiente?**
Para **estimar as médias**, sim — o erro é minúsculo e os efeitos ficam muito acima
dele. Porém os $s = 0$ revelam baixa independência entre replicações: as três leituras
foram tomadas na mesma sessão, a 20 s de intervalo, capturando praticamente o mesmo
estado do sistema. Para uma estimativa honesta do erro experimental, replicações
deveriam vir de reinicializações independentes.

**8. Quais fatores deveriam ser investigados com mais profundidade?**
O fator **A (SO)** e a interação **AB (SO × RAM)**, que concentram > 96 % da variação.
Vale aprofundar *por que* o Windows escala pior em pouca RAM (cache, compressão de
memória, serviços de segundo plano).

**9. Algum fator deveria ser descartado nas próximas etapas?**
O fator **C (carga)** tal como foi definido, além das interações AC, BC e ABC — todos
com contribuição desprezível. Se a carga for mantida, precisa ser redefinida para
exercer pressão real de memória.

**10. Que limitações ameaçam a validade dos resultados?**
- **Confusão fator B × hardware:** os níveis de 8 GB e 16 GB vêm de máquinas físicas
  diferentes (operadoras distintas), então o efeito de "tamanho de RAM" está misturado
  com diferenças de hardware e de processos nativos.
- **Replicações pouco independentes:** medidas na mesma sessão (20 s), subestimando o
  erro experimental real.
- **Carga pesada fraca:** o nível +1 de C não se diferenciou o suficiente do repouso.
- **Fatores não controlados:** atualizações automáticas e antivírus (Windows) atuaram
  como ruído não isolado.

<br>

## 8. Conclusão

**Fatores que merecem maior atenção:** o **sistema operacional (A)** é, isoladamente, o
fator determinante do uso de RAM (92,74 % da variação), seguido da interação **SO ×
tamanho de RAM (AB)** (3,36 %). O Windows não só consome mais memória que o Linux como
sofre mais quando a RAM é escassa — é onde devem se concentrar os próximos experimentos.

**Fatores que podem ser descartados:** a **carga de trabalho (C)** como definida
(0,22 %) e as interações de ordem superior **AC, BC e ABC** (< 0,3 % cada), que não
justificam o custo de continuar sendo controladas.

**Recomendação para experimentos futuros:**
- Isolar o fator RAM usando a **mesma máquina** com quantidades de memória diferentes,
  eliminando a confusão com hardware.
- Coletar replicações a partir de **reinicializações independentes** para estimar o erro
  experimental de forma realista.
- **Redefinir a carga pesada** (ex.: abrir conjunto fixo de aplicações que realmente
  demande memória) ou removê-la do projeto.
- Focar o próximo estudo em **A e AB**, investigando os mecanismos internos de
  gerenciamento de memória do Windows sob pressão.

<br>

## Como coletar e analisar

### Coleta (`coleta_fatorial.py`)

`coleta_fatorial.py` mede `r` replicações de uma combinação e já as anexa
rotuladas (`A,B,C,rep,uso_percent`) ao CSV mestre. Os fatores **A** (SO) e **B**
(RAM) são detectados automaticamente da máquina; **C** (carga) vem da flag
`--carga`. Como A×B é fixo por máquina, cada operador roda o script duas vezes por
máquina (repouso e pesada); entre os integrantes as 8 combinações são cobertas.

```bash
# antes de cada carga: deixar a máquina no estado correspondente
python coleta_fatorial.py --carga repouso -n 3 -i 20    # C = -1
python coleta_fatorial.py --carga pesada  -n 3 -i 20    # C = +1

# se a detecção automática não bater com o planejado, force os níveis:
python coleta_fatorial.py --carga pesada -n 3 --a 1 --b -1   # Windows, 8 GB
```

Cada rodada também salva um CSV detalhado + `metadados.json` numa pasta própria
(top-3 processos, nº de processos, hardware, bateria) para auditoria.

### Análise (`analise_fatorial.py`)

```bash
python analise_fatorial.py dados_2k_r.csv
```

O script calcula `q0`, os coeficientes dos efeitos principais e interações pela tabela
de sinais, a soma de quadrados de cada termo (`SQ = N·q²`), o erro experimental
(variação dentro de cada combinação) e o percentual da variação explicada por termo.
