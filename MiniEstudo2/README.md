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

> Preencher após a coleta. Rodar `python analise_fatorial.py dados_2k_r.csv`, que
> calcula automaticamente as tabelas abaixo. Os valores brutos completos ficam em
> [dados_2k_r.csv](dados_2k_r.csv).

### Repetições por combinação

| Comb. | A | B | C | $y_1$ | $y_2$ | $y_3$ |
|:-----:|:--:|:--:|:--:|:---:|:---:|:---:|
| 1 | − | − | − | _ | _ | _ |
| 2 | + | − | − | _ | _ | _ |
| 3 | − | + | − | _ | _ | _ |
| 4 | + | + | − | _ | _ | _ |
| 5 | − | − | + | _ | _ | _ |
| 6 | + | − | + | _ | _ | _ |
| 7 | − | + | + | _ | _ | _ |
| 8 | + | + | + | _ | _ | _ |

### Média e desvio padrão por combinação

| Comb. | A | B | C | $\bar{x}$ (%) | $s$ |
|:-----:|:--:|:--:|:--:|:---:|:---:|
| 1 | − | − | − | _ | _ |
| 2 | + | − | − | _ | _ |
| 3 | − | + | − | _ | _ |
| 4 | + | + | − | _ | _ |
| 5 | − | − | + | _ | _ |
| 6 | + | − | + | _ | _ |
| 7 | − | + | + | _ | _ |
| 8 | + | + | + | _ | _ |

### Efeitos, soma de quadrados e variação explicada

| Efeito | Coeficiente estimado ($q$) | Soma de quadrados | % da variação |
|:------:|:---:|:---:|:---:|
| A | _ | _ | _ |
| B | _ | _ | _ |
| C | _ | _ | _ |
| AB | _ | _ | _ |
| AC | _ | _ | _ |
| BC | _ | _ | _ |
| ABC | _ | _ | _ |
| Erro experimental | — | _ | _ |

<br>

## 7. Discussão dos resultados

> Responder após a análise.

1. Qual fator teve o maior impacto na métrica principal?
2. Esse impacto era esperado? Por quê?
3. Houve alguma interação relevante entre os fatores?
4. O resultado confirma ou contradiz a intuição inicial do grupo?
5. Algum fator escolhido parece pouco importante?
6. A variabilidade entre repetições foi pequena ou grande?
7. O valor de `r` escolhido foi suficiente?
8. Quais fatores deveriam ser investigados com mais profundidade?
9. Algum fator deveria ser descartado nas próximas etapas?
10. Que limitações ameaçam a validade dos resultados?

<br>

## 8. Conclusão

> Sintetizar após a discussão:
> - fatores que merecem maior atenção;
> - fatores que podem ser descartados;
> - recomendação para experimentos futuros.

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
