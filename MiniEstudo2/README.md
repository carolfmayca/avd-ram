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

Este Mini Estudo dá continuidade ao baseline que construímos no Mini Estudo 1, no qual
observamos que o sistema operacional influencia fortemente o percentual de uso de
RAM em repouso. Nesta etapa, nosso objetivo deixa de ser apenas *medir* o consumo e
passa a ser **entender quais fatores realmente explicam a variação do desempenho** e
se há **interações relevantes** entre eles.

Para isso, executamos um projeto fatorial completo **2³ com replicação** (`2^k r`,
com `k = 3` e `r = 3`): três fatores controláveis, cada um em dois níveis codificados
como `-1` e `+1`, com todas as `2³ = 8` combinações medidas `r` vezes. A partir da
análise, estimamos o efeito individual de cada fator, o efeito das interações, a soma
de quadrados, o percentual da variação explicada por termo e a parcela atribuída ao
**erro experimental** estimado pelas replicações.

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

Levantamos uma lista ampla de fatores que podem afetar o percentual de uso de RAM,
classificando-os em controláveis, não controláveis e mantidos constantes.

| # | Fator | Classificação |
|---|-------|---------------|
| 1 | Sistema operacional (Windows vs Linux) | Controlável |
| 2 | Tamanho da RAM física (8 GB vs 16 GB) | Controlável |
| 3 | Carga de trabalho (repouso vs aplicações abertas) | Controlável |
| 4 | Uso de SWAP / paginação habilitada | Controlável (mantido constante) |
| 5 | Modo de energia / desempenho | Controlável (mantido constante) |
| 6 | Número de processos em segundo plano | Parcialmente controlável |
| 7 | Atualizações automáticas do SO (Windows Update, dnf) | Não controlável |
| 8 | Arquitetura / geração da CPU | Não controlável (hardware fixo) |
| 9 | Velocidade / geração da RAM | Não controlável (hardware fixo) |
| 10 | Cache de disco gerenciado pelo kernel | Não controlável |
| 11 | Tempo de estabilização antes da medição | Controlável (mantido constante) |

<br>

## 3. Seleção dos fatores controláveis (k = 3)

| Fator considerado | Decisão | Justificativa |
|-------------------|---------|---------------|
| **A — Sistema operacional** | Selecionado | Foi o fator de maior impacto no nosso baseline (Mini Estudo 1); dois níveis claros (Windows / Linux). |
| **B — Tamanho da RAM** | Selecionado | Dispomos de máquinas de 8 GB e 16 GB; níveis bem definidos e fisicamente relevantes para a pressão de memória. |
| **C — Carga de trabalho** | Selecionado | Permite testar se o efeito do SO depende da carga (interação); dois níveis controláveis (repouso vs conjunto fixo de aplicações). |
| Uso de SWAP | Controlado, não analisado | Mantivemos a configuração padrão de cada SO para não introduzir um quarto fator e manter `k = 3` viável. |
| Modo de energia | Controlado, não analisado | Fixamos em "alto desempenho" em todas as combinações para isolar os fatores analisados. |
| Atualização automática | Descartado | Não controlável de forma confiável; tratamos como fonte de ruído (erro experimental). |
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

**Justificativa para `r = 3`:** adotamos `r = 3` porque ele equilibra precisão
estatística e viabilidade de coleta. Em um projeto fatorial `2³`, três repetições por
combinação produzem `8 × (3 - 1) = 16` graus de liberdade para estimar o erro
experimental, o que nos permite calcular a variabilidade dentro de cada combinação e
comparar se os efeitos dos fatores são grandes em relação ao ruído natural das
medições. Com apenas uma repetição essa comparação seria impossível, e com `r = 2` a
estimativa de erro ficaria mais frágil. Valores maiores de `r` aumentariam a
confiabilidade, mas também elevariam o custo de coleta; com `r = 3`, o experimento
totaliza 24 medições, um volume administrável para o nosso grupo. Além disso, nosso
baseline do Mini Estudo 1 indicou desvios-padrão baixos na maioria dos cenários,
tornando `r = 3` suficiente para uma análise exploratória inicial.

**Cuidados de execução:** mantivemos constantes os fatores não analisados (SWAP, modo
de energia, tempo de estabilização); usamos o mesmo procedimento de coleta
(`coleta_fatorial.py`) em todas as combinações; e registramos anomalias e medições
descartadas.

**Ordem de execução:** as combinações são fixas por máquina (A×B), então cada
integrante coletou as duas cargas (C = −1 e C = +1) na sua máquina; a alternância
entre as integrantes distribuiu as 8 combinações ao longo do dia. Dentro de cada
combinação, medimos as `r = 3` replicações em sequência (intervalo de 20 s), e não a
partir de reinicializações independentes — limitação que registramos na Seção 7
(itens 7 e 10). Não aplicamos aleatorização plena da ordem das 8 combinações, o que
reconhecemos como uma restrição do desenho por máquina/integrante.

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


<br>

## 6. Resultados

Realizamos a coleta em 2026-07-01. Os cenários de 16 GB foram medidos pela Carolina
(Ubuntu 24.04 / Windows 11) e os de 8 GB pela Luiza (Ubuntu 24.04 / Windows 11), com
`N = 24`, `r = 3` e média geral `q0 = 33,33 %`. Os valores brutos estão em
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

### Modelo fatorial ajustado

Substituindo os coeficientes estimados na forma do modelo 2³ (com $x_A, x_B, x_C \in \{-1, +1\}$):

$$
y = 33,33 + 15,38\,x_A - 2,78\,x_B + 0,74\,x_C - 2,93\,x_A x_B + 0,79\,x_A x_C + 0,66\,x_B x_C + 0,61\,x_A x_B x_C
$$

<br>

## 7. Discussão dos resultados e conclusão

**1. Qual fator teve o maior impacto na métrica principal?**
O fator **A (sistema operacional)**, responsável por **92,74 %** da variação total.
Seu coeficiente ($q_A = 15,38$) implica uma diferença média de ~30,8 pontos
percentuais entre Linux (~18 %) e Windows (~48 %) na mesma máquina.

**2. Esse impacto era esperado? Por quê?**
Sim, já esperávamos esse resultado. Nosso Mini Estudo 1 indicava que o Windows consome
sistematicamente mais RAM que distribuições Linux nas mesmas condições, por causa de
serviços nativos mais pesados (explorer.exe, dwm.exe, MsMpEng). O projeto
fatorial confirmou e quantificou esse efeito.

**3. Houve alguma interação relevante entre os fatores?**
Sim, observamos a interação **AB (SO × RAM)**, com **3,36 %** da variação — maior que
o efeito principal de B isoladamente (3,02 %). O efeito do SO depende do tamanho da
RAM: no Windows, a máquina de 8 GB usa ~54 % enquanto a de 16 GB usa ~40–46 %; no
Linux o uso permanece ~18 % nos dois tamanhos. Ou seja, a pressão de memória do
Windows é mais severa quando há menos RAM física. As demais interações (AC, BC, ABC)
mostraram-se desprezíveis (< 0,3 %).

**4. O resultado confirma ou contradiz a intuição inicial do grupo?**
Confirma nossa intuição. A hipótese da trilha ("o SO influencia o uso de RAM") foi
fortemente sustentada: o SO sozinho explica quase toda a variação observada.

**5. Algum fator escolhido parece pouco importante?**
Sim, o fator **C (carga de trabalho)**, com apenas **0,22 %** da variação. A diferença
entre repouso e carga pesada foi pequena — perceptível só no Windows 16 GB (40,2 % →
45,8 %) e quase nula no Linux. Isso indica que a "carga pesada" que definimos não
pressionou a memória o suficiente para rivalizar com o efeito do SO.

**6. A variabilidade entre repetições foi pequena ou grande?**
Muito pequena. O erro experimental representa **0,11 %** da variação total; os desvios
padrão por combinação ficaram entre 0,00 e 1,31 ponto percentual. Várias combinações
tiveram $s = 0$ (leituras idênticas).

**7. O valor de `r` escolhido foi suficiente?**
Para **estimar as médias**, sim — o erro é minúsculo e os efeitos ficam muito acima
dele. Porém, os $s = 0$ revelam baixa independência entre as replicações: tomamos as
três leituras na mesma sessão, a 20 s de intervalo, capturando praticamente o mesmo
estado do sistema. Reconhecemos que, para uma estimativa mais fiel do erro
experimental, as replicações deveriam vir de reinicializações independentes.

**8. Quais fatores deveriam ser investigados com mais profundidade?**
O fator **A (SO)** e a interação **AB (SO × RAM)**, que concentram > 96 % da variação.
Consideramos que vale aprofundar *por que* o Windows escala pior em pouca RAM (cache,
compressão de memória, serviços de segundo plano).

**9. Algum fator deveria ser descartado nas próximas etapas?**
O fator **C (carga)** tal como o definimos, além das interações AC, BC e ABC — todos
com contribuição desprezível. Caso a carga seja mantida, precisará ser redefinida para
exercer pressão real de memória.

**10. Que limitações ameaçam a validade dos resultados?**
- **Confusão fator B × hardware:** os níveis de 8 GB e 16 GB vêm de máquinas físicas
  diferentes (operadoras distintas), então o efeito de "tamanho de RAM" está misturado
  com diferenças de hardware e de processos nativos.
- **Replicações pouco independentes:** medimos na mesma sessão (20 s), o que subestima
  o erro experimental real.
- **Carga pesada fraca:** o nível +1 de C não se diferenciou o suficiente do repouso.
- **Fatores não controlados:** atualizações automáticas e serviços de segundo plano
  do Windows atuaram como ruído que não conseguimos isolar.

Diante dos itens 8 a 10, planejamos para os experimentos futuros:
- isolar o fator RAM usando a **mesma máquina** com quantidades de memória diferentes,
  eliminando a confusão com hardware;
- coletar replicações a partir de **reinicializações independentes**, para estimar o
  erro experimental de forma mais realista;
- **redefinir a carga pesada** (por exemplo, abrindo um conjunto fixo de aplicações que
  realmente demande memória) ou removê-la do projeto;
- focar o próximo estudo em **A e AB**, investigando os mecanismos internos de
  gerenciamento de memória do Windows sob pressão.

---

*Instruções de coleta e análise dos scripts: ver [USO.md](USO.md).*
