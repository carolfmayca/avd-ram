# Relatório — Métodos STS e Análise Comparativa para Simulação de Fila M/M/1

**ICC305 — Avaliação de Desempenho**  
**Carolina Maycá, Luiza Caxeixa e Nicolas Mady**

Prof. Edjair Mota, Dr.-Ing. — Instituto de Computação / UFAM

---

## Parâmetros do Sistema

Os exercícios 10–12 utilizam quatro cenários de carga, todos com μ = 10 clientes/s:

| Cenário | λ (clientes/s) | ρ = λ/μ | E[X] teórico (s) |
| ------- | -------------- | ------- | ---------------- |
| I       | 7              | 0,70    | **0,2333**       |
| II      | 8              | 0,80    | **0,4000**       |
| III     | 9              | 0,90    | **0,9000**       |
| IV      | 9,5            | 0,95    | **1,9000**       |

A fórmula analítica do tempo médio de espera em fila M/M/1:

$$E[X] = \frac{\rho}{\mu(1 - \rho)}, \quad \rho = \frac{\lambda}{\mu}$$

Todos os experimentos utilizam:

- **MSER-5Y** para detecção e eliminação do transiente
- **Critério de parada:** H/X̄ ≤ 5 % (precisão relativa)
- **IC:** 95 % — quantil t-Student com graus de liberdade dependentes do método
- **Seed:** 42

---

## Implementação

Os métodos STS (Standardized Time Series) constroem estatísticas que convergem em distribuição para permitir estimação de IC com alta autocorrelação. Ambos operam sobre a série pós-transiente obtida pelo MSER-5Y e compartilham a estrutura de **área geométrica** de cada lote como estimador central.

### Estrutura comum — detecção de transiente

```python
sim = MM1Queue(lam=lam, mu=mu, seed=seed)
sim._reset()

buf = sim.generate(20_000)   # observações iniciais
d = mser5y(buf)              # MSER-5Y: retorna argmin sem fallback para zero
buf_steady = buf[d:]         # descarta transiente
```

### Estrutura comum — área geométrica dos lotes

Para o i-ésimo lote de M observações consecutivas, a área geométrica é a soma ponderada pelo desvio de posição central em relação ao ponto médio do lote:

$$A_i = \sum_{j=1}^{M}\left(\frac{M+1}{2} - j\right) X_{(i-1)M+j}$$

As áreas $A_i$ têm média zero quando a série é estacionária e, pelo TCL, convergem para uma distribuição normal conforme M cresce. A normalidade é verificada por **Shapiro-Wilk** (α = 5%) antes de construir o IC.

---

## Exercício 10 — STS/ÁREA

### Descrição

O método STS/ÁREA constrói o IC diretamente a partir das áreas geométricas, sem necessidade de estimar autocorrelações individualmente. A soma dos quadrados das áreas é proporcional à variância assintótica da série:

$$H = t_{B,\,\alpha/2}\sqrt{\frac{12\sum_{i=1}^{B} A_i^2}{N^2(M^2-1)}}$$

O fator 12/(M²−1) normaliza as áreas para a escala da variância da média. Com B = 20 lotes fixos e M crescendo de 50 em 50 até as áreas serem normais e H/X̄ ≤ 5 %.

### Código

```python
# ── Passo 2: STS/ÁREA com Shapiro-Wilk e parada por precisão relativa ────────
B = 20
M = 100
ALPHA = 0.05
normalidade_confirmada = False

while True:
    N = B * M
    while len(buf_steady) < N:
        buf_steady = np.concatenate([buf_steady, sim.generate(5_000)])

    amostra = buf_steady[:N]
    blocos = amostra.reshape(B, M)
    pesos = (M + 1) / 2.0 - np.arange(1, M + 1)
    areas = blocos @ pesos   # shape (B,): área de cada lote

    if not normalidade_confirmada:
        _, p_valor = sp_stats.shapiro(areas)
        if p_valor < ALPHA:
            M += 50          # áreas não normais → lote maior
            continue
        normalidade_confirmada = True

    X_bar = float(amostra.mean())
    soma_A2 = float(np.sum(areas ** 2))
    H = sp_stats.t.ppf(1 - ALPHA/2, B) * np.sqrt(12 * soma_A2 / (N**2 * (M**2 - 1)))

    if X_bar > 0 and H / X_bar <= epsilon:
        break

    M += 50
```

### Resultados Obtidos

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N         | d     | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | --------- | ----- | ------- |
| I       | 0,70 | 0,233456 | 0,010558 | [0,222898 ; 0,244014]      | 52 000    | 0     | ✓       |
| II      | 0,80 | 0,394247 | 0,019300 | [0,374946 ; 0,413547]      | 101 000   | 0     | ✓       |
| III     | 0,90 | 0,898983 | 0,044568 | [0,854416 ; 0,943551]      | 426 910   | 4 910 | ✓       |
| IV      | 0,95 | 1,945316 | 0,097043 | [1,848274 ; 2,042359]      | 1 492 000 | 0     | ✓       |

**E[X] teórico:** I = 0,2333 s · II = 0,4000 s · III = 0,9000 s · IV = 1,9000 s

Todos os 4 ICs cobrem E[X]. M cresce acentuadamente com ρ para que as áreas geométricas satisfaçam Shapiro-Wilk, elevando N de 52 000 (ρ=0,70) a 1 492 000 (ρ=0,95). No Cenário III, o MSER-5Y detectou transiente d=4 910, descartando ≈1,1% das observações antes do estado estacionário.

![Gráfico Exercício 10 — STS/ÁREA: estimativas e IC 95% por cenário](imgs/exercicio10.png)

> **STS/ÁREA** (ε=5%): 4/4 ICs válidos. N varia de 52 000 a 1 492 000 conforme ρ.

---

## Exercício 11 — STS/CSUM

### Descrição

O método STS/CSUM combina a **área geométrica** de cada lote com a **variância inter-lote** em uma única estatística A, capturando tanto a variabilidade interna dos lotes quanto a variação entre lotes:

$$A = \sum_{i=1}^{B}\left[\frac{12\,A_i^2}{M^3 - M} + M\,(\bar{X} - \bar{X}_i)^2\right]$$

O primeiro termo é a contribuição normalizada da área geométrica; o segundo é o quadrado do desvio da média do lote $\bar{X}_i$ em relação à média global $\bar{X}$, ponderado por M. O IC usa t-Student com 2B−1 graus de liberdade:

$$H = t_{2B-1,\,\alpha/2}\sqrt{\frac{A}{N\,(2B-1)}}$$

Os 2B−1 graus de liberdade refletem a combinação de B estimativas de área (com 1 g.l. cada) e B−1 desvios inter-lote. A normalidade das áreas é verificada por Shapiro-Wilk (α = 5%) antes do cálculo de H.

### Código

```python
# ── Passo 2: STS/CSUM com Shapiro-Wilk e parada por precisão relativa ────────
B = 20
M = 100
ALPHA = 0.05
normalidade_confirmada = False

while True:
    N = B * M
    while len(buf_steady) < N:
        buf_steady = np.concatenate([buf_steady, sim.generate(5_000)])

    amostra = buf_steady[:N]
    blocos = amostra.reshape(B, M)
    pesos = (M + 1) / 2.0 - np.arange(1, M + 1)
    areas = blocos @ pesos

    if not normalidade_confirmada:
        _, p_valor = sp_stats.shapiro(areas)
        if p_valor < ALPHA:
            M += 50
            continue
        normalidade_confirmada = True

    medias_bloco = blocos.mean(axis=1)
    X_bar = float(amostra.mean())

    A = float(np.sum(12 * areas**2 / (M**3 - M) + M * (X_bar - medias_bloco)**2))
    H = sp_stats.t.ppf(1 - ALPHA/2, 2*B - 1) * np.sqrt(A / (N * (2*B - 1)))

    if X_bar > 0 and H / X_bar <= epsilon:
        break

    M += 50
```

### Resultados Obtidos

| Cenário | ρ    | X̄(n)    | H        | A/(N·(2B−1))  | IC (95 %)                  | N           | d | E[X]∈IC |
| ------- | ---- | -------- | -------- | ------------- | -------------------------- | ----------- | - | ------- |
| I       | 0,70 | 0,224999 | 0,011218 | 0,0000        | [0,213782 ; 0,236217]      | 78 000      | 0 | ✓       |
| II      | 0,80 | 0,375560 | 0,018776 | 0,0001        | [0,356784 ; 0,394336]      | 103 000     | 0 | ✗       |
| III     | 0,90 | 0,874148 | 0,043469 | 0,0005        | [0,830678 ; 0,917617]      | 539 000     | 0 | ✓       |
| IV      | 0,95 | 1,965395 | 0,098127 | 0,0024        | [1,867268 ; 2,063522]      | 3 515 000   | 0 | ✓       |

**E[X] teórico:** I = 0,2333 s · II = 0,4000 s · III = 0,9000 s · IV = 1,9000 s

3/4 ICs cobrem E[X]. O Cenário II falha: X̄=0,3756, IC=[0,3568; 0,3944], mas E[X]=0,4000 > 0,3944. Trata-se de uma falha de cobertura estatisticamente esperada (IC 95 % falha em ~5 % das realizações). Os valores de A/(N·(2B−1)) crescem de 0,0000 (ρ=0,70) a 0,0024 (ρ=0,95), refletindo o aumento da variância da média com a autocorrelação. O Cenário IV exige N=3 515 000 — o maior de todos os métodos — indicando que a combinação de dois termos em A pode ser conservadora para ρ muito elevado.

![Gráfico Exercício 11 — STS/CSUM: estimativas e IC 95% por cenário](imgs/exercicio11.png)

> **STS/CSUM** (ε=5%): 3/4 ICs válidos. Cenário II falha por cobertura. Cenário IV exige N=3 515 000.

---

## Exercício 12 — Análise Comparativa dos Seis Métodos

### Descrição

Comparação direta dos seis estimadores no **Cenário IV** (λ=9,5, ρ=0,95, E[X]=1,9 s), o mais exigente em termos de autocorrelação.

| Estimador     | Quantil IC        | Valida independência | Mecanismo central           |
| ------------- | ----------------- | -------------------- | --------------------------- |
| NBM           | t_{B−1}           | RVN                  | Lotes não sobrepostos       |
| SBM (S=1)     | t_{B−1}           | RVN                  | Descarta 1 obs/lote         |
| SBM (S=M/10)  | t_{B−1}           | RVN                  | Descarta M/10 obs/lote      |
| OBM (100%)    | t_{⌊1,5(B'−1)⌋}  | RVN em lotes NBM     | Sobreposição total (lag=1)  |
| STS/ÁREA      | t_B               | Shapiro-Wilk         | Área geométrica             |
| STS/CSUM      | t_{2B−1}          | Shapiro-Wilk         | Área + variância inter-lote |

### Resultados para o Cenário IV (ρ = 0,95 · E[X] = 1,9000 s)

| Método        | X̄(n)    | H        | IC (95 %)                  | N           | d     | Erro rel. | E[X]∈IC |
| ------------- | -------- | -------- | -------------------------- | ----------- | ----- | --------- | ------- |
| NBM           | 1,931552 | 0,096557 | [1,834995 ; 2,028110]      | 1 250 000   | 0     | +1,661 %  | ✓       |
| SBM (S=1)     | 1,931586 | 0,096577 | [1,835009 ; 2,028163]      | 1 250 000   | 0     | +1,662 %  | ✓       |
| SBM (S=M/10)  | 1,870786 | 0,093394 | [1,777392 ; 1,964180]      | 884 565     | 9 065 | −1,538 %  | ✓       |
| OBM (100%)    | 1,870855 | 0,024899 | [1,845956 ; 1,895755]      | 19 065      | 9 065 | −1,534 %  | ✗       |
| STS/ÁREA      | 1,945316 | 0,097043 | [1,848274 ; 2,042359]      | 1 492 000   | 0     | +2,385 %  | ✓       |
| STS/CSUM      | 1,965395 | 0,098127 | [1,867268 ; 2,063522]      | 3 515 000   | 0     | +3,442 %  | ✓       |

**E[X] teórico = 1,9000 s**

5 de 6 métodos produzem IC válido. O OBM (100%) falha: apesar de X̄=1,871 s (erro −1,5 %), o IC é excessivamente estreito (H=0,025 s, menos de ¼ dos demais) — o algoritmo encerrou com apenas N_steady=10 000 observações, muito antes de X̄ ser uma estimativa estável. Com B'≈9 500 lotes sobrepostos com lag=1 derivados dessas 10 000 obs, a meia-largura H colapsa para valores irrealisticamente pequenos (mas incorretos).

NBM e SBM(S=1) produzem resultados quase idênticos (+1,66% de erro, N=1 250 000) — o descarte de 1 observação por lote é irrelevante quando M é da ordem de milhares. SBM(S=M/10) é o mais eficiente: IC válido com N=884 565, o menor N entre os métodos corretos. STS/CSUM exige N=3 515 000 (2,8× o NBM) para a mesma precisão no Cenário IV, indicando que a estatística combinada A/(N·(2B−1)) converge mais lentamente sob alta autocorrelação.

![Gráfico Exercício 12 — Comparação dos métodos: X̄ e IC 95%](imgs/exercicio12_comparacao_metodos.png)

![Gráfico Exercício 12 — Largura dos ICs por método](imgs/exercicio12_largura_ics.png)

![Gráfico Exercício 12 — Tamanho amostral por método](imgs/exercicio12_tamanho_amostras.png)

---

## Considerações Finais

Os exercícios 10–12 exploram métodos STS e a comparação agregada dos seis estimadores.

1. **STS/ÁREA (Exercício 10):** 4/4 ICs válidos. A área geométrica $A_i$ é um estimador não paramétrico da variância assintótica que não requer cálculo explícito de autocorrelações. Para ρ próximo de 1, M precisa crescer mais (Shapiro-Wilk), elevando N de 52 000 (ρ=0,70) a 1 492 000 (ρ=0,95). Método robusto e confiável.

2. **STS/CSUM (Exercício 11):** 3/4 ICs válidos. A falha no Cenário II (E[X]=0,4 cai marginalmente fora do IC superior) é uma falha de cobertura estatisticamente esperada. A maior limitação é o custo amostral: N=3 515 000 para ρ=0,95 — o mais alto entre todos os métodos analisados. O segundo termo de A (variância inter-lote) adiciona conservadorismo que pode ser excessivo.

3. **Análise comparativa (Exercício 12):** para ρ=0,95, todos os métodos baseados em lotes de tamanho adequado (NBM, SBM, STS/ÁREA) produzem ICs válidos com erros relativos inferiores a 3,5 %. O OBM com sobreposição 100 % é o único que falha sistematicamente, por um problema estrutural: o algoritmo satisfaz H/X̄ ≤ 5 % com N_steady patologicamente pequeno, pois B'≈N produz um denominador inflado que colapsa H antes de X̄ convergir. O método mais eficiente para ρ=0,95 é o SBM(S=M/10), com N=884 565 e IC válido.
