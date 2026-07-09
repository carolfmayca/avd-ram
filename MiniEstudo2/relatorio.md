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
**Sistema analisado:** Sistemas Operacionais (Windows 11 e Ubuntu 24.04)<br>
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
| **C — Carga de trabalho** | Selecionado | Permite testar se o efeito do SO depende da carga (interação); dois níveis controláveis (repouso vs carga pesada gerada pelo script). |
| Uso de SWAP | Controlado, não analisado | Mantivemos a configuração padrão de cada SO para não introduzir um quarto fator e manter `k = 3` viável. |
| Modo de energia | Controlado, não analisado | Fixamos em "alto desempenho" em todas as combinações para isolar os fatores analisados. |
| Atualização automática | Descartado | Não controlável de forma confiável; tratamos como fonte de ruído (erro experimental). |
| Geração de CPU/RAM | Descartado | Hardware fixo por máquina; não tem dois níveis manipuláveis dentro da trilha. |

<br>

## 4. Definição dos níveis dos fatores

| Fator | Nível `-1` | Nível `+1` |
|-------|:----------:|:----------:|
| **A** — Sistema operacional | Linux (Ubuntu 24.04) | Windows 11 |
| **B** — Tamanho da RAM | 8 GB | 16 GB |
| **C** — Carga de trabalho | Repouso | Carga pesada (alocação de memória pelo script) |

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

Realizamos a coleta em 2026-07-08. Os cenários de 16 GB foram medidos pela Carolina
(Ubuntu 24.04 / Windows 11) e os de 8 GB pela Luiza (Ubuntu 24.04 / Windows 11), com
`N = 24`, `r = 3` e média geral `q0 = 36,48 %`. Os valores brutos estão em
[dados_2k_r.csv](dados_2k_r.csv).

### Repetições por combinação

| Comb. | A | B | C | $y_1$ | $y_2$ | $y_3$ |
|:-----:|:--:|:--:|:--:|:---:|:---:|:---:|
| 1 | − | − | − | 16,8 | 16,6 | 16,5 |
| 2 | + | − | − | 57,8 | 57,9 | 57,6 |
| 3 | − | + | − | 14,9 | 14,8 | 14,8 |
| 4 | + | + | − | 35,0 | 34,5 | 33,6 |
| 5 | − | − | + | 30,0 | 29,7 | 29,7 |
| 6 | + | − | + | 69,8 | 69,9 | 70,4 |
| 7 | − | + | + | 27,9 | 27,9 | 27,9 |
| 8 | + | + | + | 40,6 | 40,5 | 40,5 |

### Média e desvio padrão por combinação

| Comb. | A | B | C | $\bar{x}$ (%) | $s$ |
|:-----:|:--:|:--:|:--:|:---:|:---:|
| 1 | − | − | − | 16,63 | 0,15 |
| 2 | + | − | − | 57,77 | 0,15 |
| 3 | − | + | − | 14,83 | 0,06 |
| 4 | + | + | − | 34,37 | 0,71 |
| 5 | − | − | + | 29,80 | 0,17 |
| 6 | + | − | + | 70,03 | 0,32 |
| 7 | − | + | + | 27,90 | 0,00 |
| 8 | + | + | + | 40,53 | 0,06 |

### Efeitos, soma de quadrados e variação explicada

| Efeito | Coeficiente estimado ($q$) | Soma de quadrados | % da variação |
|:------:|:---:|:---:|:---:|
| A | 14,192 | 4833,68 | 62,43 % |
| B | −7,075 | 1201,34 | 15,52 % |
| C | 5,583 | 748,17 | 9,66 % |
| AB | −6,150 | 907,74 | 11,72 % |
| AC | −0,975 | 22,82 | 0,29 % |
| BC | −0,775 | 14,42 | 0,19 % |
| ABC | −0,750 | 13,50 | 0,17 % |
| Erro experimental | — | 1,38 | 0,02 % |

### Modelo fatorial ajustado

Substituindo os coeficientes estimados na forma do modelo 2³ (com $x_A, x_B, x_C \in \{-1, +1\}$):

$$
y = 36,48 + 14,19\,x_A - 7,08\,x_B + 5,58\,x_C - 6,15\,x_A x_B - 0,98\,x_A x_C - 0,78\,x_B x_C - 0,75\,x_A x_B x_C
$$

<br>

## 7. Discussão dos resultados e conclusão

**1. Qual fator teve o maior impacto na métrica principal?**
O fator **A (sistema operacional)**, responsável por **62,43 %** da variação total.
Seu coeficiente ($q_A = 14,19$) implica uma diferença média de aproximadamente
28,4 pontos percentuais entre Linux e Windows, considerando a média sobre os níveis de
RAM e carga.

**2. Esse impacto era esperado? Por quê?**
Sim, já esperávamos esse resultado. Nosso Mini Estudo 1 indicava que o Windows consome
sistematicamente mais RAM que distribuições Linux nas mesmas condições, por causa de
serviços nativos mais pesados (explorer.exe, MsMpEng e outros processos residentes).
O projeto fatorial confirmou esse efeito e mostrou que RAM, carga e a interação
SO × RAM também explicam parcelas relevantes da variação.

**3. Houve alguma interação relevante entre os fatores?**
Sim, observamos a interação **AB (SO × RAM)**, com **11,72 %** da variação. O efeito
do sistema operacional depende do tamanho da RAM: em 8 GB, o Windows ficou muito acima
do Linux (aprox. 58–70 % contra 17–30 %); em 16 GB, a diferença ainda existe, mas é
menor (aprox. 34–41 % contra 15–28 %). Ou seja, a pressão de memória do Windows é
mais severa quando há menos RAM física. As demais interações (AC, BC, ABC)
mostraram-se pequenas (< 0,3 % cada).

**4. O resultado confirma ou contradiz a intuição inicial do grupo?**
Confirma nossa intuição principal. A hipótese da trilha ("o SO influencia o uso de
RAM") foi sustentada, com um quadro mais rico: o SO é o maior fator, porém o tamanho
da RAM, a carga e a interação SO × RAM também importam.

**5. Algum fator escolhido parece pouco importante?**
Sim, as interações **AC**, **BC** e **ABC** parecem pouco importantes, todas abaixo de
0,3 % da variação. 

**6. A variabilidade entre repetições foi pequena ou grande?**
Muito pequena. O erro experimental representa **0,02 %** da variação total; os desvios
padrão por combinação ficaram entre 0,00 e 0,71 ponto percentual. Uma combinação teve
$s = 0$ (leituras idênticas) e as demais oscilaram pouco.

**7. O valor de `r` escolhido foi suficiente?**
Para **estimar as médias**, sim — o erro é minúsculo e os efeitos ficam muito acima
dele. Porém, os $s = 0$ revelam baixa independência entre as replicações: tomamos as
três leituras na mesma sessão, a 20 s de intervalo, capturando praticamente o mesmo
estado do sistema. Reconhecemos que, para uma estimativa mais fiel do erro
experimental, as replicações deveriam vir de reinicializações independentes.

**8. Quais fatores deveriam ser investigados com mais profundidade?**
Os fatores **A (SO)**, **B (RAM)**, **C (carga)** e a interação **AB (SO × RAM)**, que
juntos concentram quase toda a variação explicada. Consideramos que vale aprofundar
por que o Windows escala pior em pouca RAM (cache, compressão de memória, serviços de
segundo plano) e padronizar melhor a carga pesada para avaliar seu efeito isolado.

**9. Algum fator deveria ser descartado nas próximas etapas?**
As interações **AC**, **BC** e **ABC** poderiam ser descartadas ou tratadas como termos
secundários em uma próxima análise, pois tiveram contribuição muito pequena. O fator
**C (carga)** deve ser mantido, mas com procedimento mais padronizado.

**10. Que limitações ameaçam a validade dos resultados?**
- **Confusão fator B × hardware:** os níveis de 8 GB e 16 GB vêm de máquinas físicas
  diferentes (operadoras distintas), então o efeito de "tamanho de RAM" está misturado
  com diferenças de hardware e de processos nativos.
- **Replicações pouco independentes:** medimos na mesma sessão (20 s), o que subestima
  o erro experimental real.
- **Fatores não controlados:** atualizações automáticas e serviços de segundo plano
  do Windows atuaram como ruído que não conseguimos isolar.

---

*Instruções de coleta e análise dos scripts: ver [README.md](README.md).*
