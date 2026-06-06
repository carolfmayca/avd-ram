# Relatório — Métodos de Batch Means para Simulação de Fila M/M/1

**ICC305 — Avaliação de Desempenho**  
**Carolina Maycá, Luiza Caxeixa e Nicolas Mady**

Prof. Edjair Mota, Dr.-Ing. — Instituto de Computação / UFAM

---

## Parâmetros do Sistema

Os exercícios 7–9 utilizam quatro cenários de carga, todos com μ = 10 clientes/s:

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
- **IC:** 95 % (z₀,₉₇₅ = 1,96)
- **Seed:** 42

---

## Implementação

Cada método é implementado como função independente que reutiliza a infraestrutura do notebook (`MM1Queue`, `mser5y`, `OnlineStats`). O fluxo geral é:

1. Gerar 20 000 observações iniciais com `sim.generate()`
2. Aplicar MSER-5Y para determinar d (ponto de truncagem)
3. Descartar as primeiras d observações e acumular o estado estacionário
4. Iterar adicionando lotes até satisfazer H/X̄ ≤ 5 %

### Estrutura comum — detecção de transiente

```python
sim = MM1Queue(lam=lam, mu=mu, seed=seed)
sim._reset()

buf = sim.generate(INIT_WARMUP)   # 20 000 obs
d = None
while d is None:
    d = mser5y(buf)
    if d is None:
        buf = np.concatenate([buf, sim.generate(EXTRA_WARMUP)])

buf_steady = buf[d:]              # descarta transiente
```

---

## Exercício 7 — Método NBM (Non-overlapping Batch Means)

### Descrição

A série pós-transiente é dividida em **B lotes não sobrepostos** de tamanho m. A média de cada lote $\bar{Y}_j$ é calculada e a variância é estimada sobre as B médias:

$$\hat{\sigma}^2_{\text{NBM}} = \frac{1}{B-1}\sum_{j=1}^{B}(\bar{Y}_j - \bar{X})^2, \qquad H = z_{0{,}975}\,\frac{\hat{\sigma}_{\text{NBM}}}{\sqrt{B}}$$

Inicia-se com B = 20 lotes e incrementa-se de 20 em 20 até H/X̄ ≤ 5 %.

### Código

```python
# ── Passo 2: NBM com parada por precisão relativa ────────────────────────────
all_batch_means = []
n_target = B  # começa com B=20

while True:
    batches_needed = n_target - len(all_batch_means)
    n_to_gen = batches_needed * BATCH_SIZE_GEN - len(buf_steady)
    if n_to_gen > 0:
        buf_steady = np.concatenate([buf_steady, sim.generate(n_to_gen)])

    for i in range(len(all_batch_means), n_target):
        start = i * BATCH_SIZE_GEN
        end   = min(start + BATCH_SIZE_GEN, len(buf_steady))
        if end > start:
            all_batch_means.append(float(buf_steady[start:end].mean()))

    batch_means_arr = np.array(all_batch_means)
    X_bar = batch_means_arr.mean()
    H = Z95 * np.sqrt(np.var(batch_means_arr, ddof=1) / len(all_batch_means))

    if X_bar > 0 and H / X_bar <= epsilon:
        break

    n_target += B
```

### Resultados Obtidos

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N           | d | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | ----------- | - | ------- |
| I       | 0,70 | 0,233068 | 0,010163 | [0,222905 ; 0,243231]      | 200 000     | 0 | ✓       |
| II      | 0,80 | 0,392189 | 0,018495 | [0,373694 ; 0,410683]      | 200 295     | 295 | ✓     |
| III     | 0,90 | 0,892682 | 0,039986 | [0,852696 ; 0,932669]      | 700 000     | 0 | ✓       |
| IV      | 0,95 | 1,854680 | 0,090263 | [1,764417 ; 1,944944]      | 1 700 000   | 0 | ✓       |

**E[X] teórico:** I = 0,2333 s · II = 0,4000 s · III = 0,9000 s · IV = 1,9000 s

O tamanho amostral cresce acentuadamente com ρ: de N = 200 000 (ρ=0,70) a N = 1 700 000 (ρ=0,95), refletindo que séries mais autocorrelacionadas exigem lotes maiores para satisfazer a precisão relativa.

![Gráfico Exercício 7 — NBM: estimativas e IC 95% por cenário](imgs/exercicio7.png)

> **NBM** (B=20, ε=5%): menor erro relativo no Cenário I (0,11%). Tamanho amostral cresce com ρ: de N=200 000 (ρ=0,70) a N=1 700 000 (ρ=0,95).

---

## Exercício 8 — Método SBM (Spaced Batch Means)

### Descrição

Variante do NBM que insere **S observações de espaçamento** entre lotes consecutivos, reduzindo a correlação entre médias de lote. A variância é estimada da mesma forma que no NBM:

$$H = z_{0{,}975}\,\frac{\hat{\sigma}_{\text{SBM}}}{\sqrt{M}}, \qquad \hat{\sigma}^2_{\text{SBM}} = \frac{1}{M-1}\sum_{j=1}^{M}(\bar{Y}_j - \bar{X})^2$$

Testado com dois valores de S:
- **S = 1** (fixo): espaçamento mínimo, idêntico ao NBM com lag=1
- **S = ⌊M/10⌋** (adaptativo): espaçamento cresce com M

### Código

```python
# ── Passo 2: SBM com parada por precisão relativa ────────────────────────────
M = 10
while True:
    S = 1 if S_mode == 'fixed' else max(1, M // 10)

    N_needed = M * S + S - 1
    while len(buf_steady) < N_needed:
        buf_steady = np.concatenate([buf_steady, sim.generate(5_000)])

    batch_means = [float(buf_steady[j:j+S].mean()) for j in range(M)
                   if j + S <= len(buf_steady)]

    X_bar = np.mean(batch_means)
    # Ajuste para autocorrelação no lag 1
    rho_lag1 = np.corrcoef(batch_means[:-1], batch_means[1:])[0, 1]
    correction_factor = max(1.0, 1 + 2 * rho_lag1)
    H = Z95 * np.sqrt(np.var(batch_means, ddof=1) * correction_factor / len(batch_means))

    if X_bar > 0 and H / X_bar <= 0.05:
        break
    M += 10
```

### Resultados Obtidos

#### S = 1 (fixo)

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N      | d   | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | ------ | --- | ------- |
| I       | 0,70 | 0,206623 | 0,013923 | [0,192701 ; 0,220546]      | 20 000 | 0   | ✗       |
| II      | 0,80 | 0,393451 | 0,020650 | [0,372801 ; 0,414101]      | 20 000 | 295 | ✓       |
| III     | 0,90 | 0,658331 | 0,032851 | [0,625479 ; 0,691182]      | 20 000 | 0   | ✗       |
| IV      | 0,95 | 1,863257 | 0,091878 | [1,771379 ; 1,955135]      | 20 000 | 0   | ✓       |

#### S = ⌊M/10⌋ (adaptativo)

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N       | d     | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | ------- | ----- | ------- |
| I       | 0,70 | 0,209562 | 0,010459 | [0,199103 ; 0,220021]      | 145 000 | 1 395 | ✗       |
| II      | 0,80 | 0,475684 | 0,023624 | [0,452060 ; 0,499308]      | 450 000 | 0     | ✗       |
| III     | 0,90 | 0,843005 | 0,041991 | [0,801014 ; 0,884996]      | 350 000 | 0     | ✗       |
| IV      | 0,95 | 3,787387 | 0,079252 | [3,708135 ; 3,866639]      | 20 000  | 9 065 | ✗       |

O SBM com S = 1 satisfaz a precisão relativa H/X̄ ≤ 5 % com apenas N = 20 000 observações (limite da proteção contra loop infinito), mas 2 dos 4 ICs não contêm E[X] teórico — evidenciando que a amostra é insuficiente para os cenários de baixa carga.

O SBM adaptativo (S = M/10) apresenta resultados problemáticos, especialmente no Cenário IV onde X̄ = 3,79 s está muito afastado de E[X] = 1,9 s. Isso indica que o espaçamento crescente, ao descartar muitas observações entre lotes, reduz excessivamente o tamanho efetivo da amostra e pode capturar apenas a fase de transiente inicial quando d é elevado.

![Gráfico Exercício 8 — SBM S=1: estimativas e IC 95% por cenário](imgs/exercicio8_s1.png)

![Gráfico Exercício 8 — SBM S=M/10: estimativas e IC 95% por cenário](imgs/exercicio8_sM10.png)

> **SBM**: espaçamento adaptativo (S=M/10) usa batches maiores mas exige mais observações. No Cenário IV: N=20 000 (S=1) vs N=20 000 (S=M/10).

---

## Exercício 9 — Método OBM (Overlapping Batch Means)

### Descrição

Generalização do NBM em que lotes de tamanho **m = 100** se sobrepõem com passo **lag**. O grau de sobreposição determina o lag e, consequentemente, a correlação entre lotes consecutivos:

| Sobreposição | lag |
|:---:|:---:|
| 100 % | 1 |
| 50 % | m/2 = 50 |
| 25 % | 3m/4 = 75 |

### Código

```python
# ── Passo 2: Define lag baseado no overlap ────────────────────────────────────
S = 100  # tamanho fixo do batch
if   overlap_pct == 100: lag = 1
elif overlap_pct ==  50: lag = S // 2
elif overlap_pct ==  25: lag = (3 * S) // 4

M = 10
while True:
    N_needed = (M - 1) * lag + S
    while len(buf_steady) < N_needed:
        buf_steady = np.concatenate([buf_steady, sim.generate(5_000)])

    batch_means = [float(buf_steady[j*lag : j*lag+S].mean())
                   for j in range(M) if j*lag + S <= len(buf_steady)]

    X_bar = np.mean(batch_means)
    rho_lag1 = np.corrcoef(batch_means[:-1], batch_means[1:])[0, 1]
    correction_factor = max(1.0, 1 + 2 * rho_lag1)
    H = Z95 * np.sqrt(np.var(batch_means, ddof=1) * correction_factor / len(batch_means))

    if X_bar > 0 and H / X_bar <= 0.05:
        break
    M += 10
```

### Resultados Obtidos

#### Sobreposição 100 % (lag = 1)

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N      | d     | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | ------ | ----- | ------- |
| I       | 0,70 | 0,076815 | 0,003382 | [0,073433 ; 0,080197]      | 20 000 | 1 395 | ✗       |
| II      | 0,80 | 0,114458 | 0,005487 | [0,108971 ; 0,119945]      | 20 000 | 0     | ✗       |
| III     | 0,90 | 0,354187 | 0,009132 | [0,345055 ; 0,363319]      | 20 000 | 0     | ✗       |
| IV      | 0,95 | 3,554445 | 0,033859 | [3,520585 ; 3,588304]      | 20 000 | 9 065 | ✗       |

#### Sobreposição 50 % (lag = 50)

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N       | d   | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | ------- | --- | ------- |
| I       | 0,70 | 0,241981 | 0,012085 | [0,229896 ; 0,254065]      | 115 000 | 0   | ✓       |
| II      | 0,80 | 0,407371 | 0,020360 | [0,387010 ; 0,427731]      | 145 000 | 400 | ✓       |
| III     | 0,90 | 0,930200 | 0,046400 | [0,883800 ; 0,976599]      | 235 000 | 0   | ✓       |
| IV      | 0,95 | 1,806040 | 0,090076 | [1,715964 ; 1,896116]      | 230 000 | 0   | ✗       |

#### Sobreposição 25 % (lag = 75)

| Cenário | ρ    | X̄(n)    | H        | IC (95 %)                  | N       | d | E[X]∈IC |
| ------- | ---- | -------- | -------- | -------------------------- | ------- | - | ------- |
| I       | 0,70 | 0,238266 | 0,011880 | [0,226386 ; 0,250146]      | 85 000  | 0 | ✓       |
| II      | 0,80 | 0,399009 | 0,019916 | [0,379093 ; 0,418925]      | 155 000 | 0 | ✓       |
| III     | 0,90 | 0,809682 | 0,040481 | [0,769200 ; 0,850163]      | 215 000 | 0 | ✗       |
| IV      | 0,95 | 2,298483 | 0,127561 | [2,170922 ; 2,426044]      | 380 000 | 0 | ✗       |

O OBM com sobreposição 100 % (lag=1) produz resultados degradados em todos os cenários: com N=20 000 observações e lotes de tamanho S=100, cria-se M≈9 900 lotes que compartilham quase todas as observações entre si, tornando as médias altamente dependentes e o estimador de variância inválido. A sobreposição 50 % equilibra reúso e independência, obtendo 3/4 ICs válidos. A 25 % approxima-se do NBM mas com 2/4 ICs válidos no Cenário IV.

![Gráfico Exercício 9 — OBM 100% overlap: estimativas e IC 95% por cenário](imgs/exercicio9_100.png)

![Gráfico Exercício 9 — OBM 50% overlap: estimativas e IC 95% por cenário](imgs/exercicio9_50.png)

![Gráfico Exercício 9 — OBM 25% overlap: estimativas e IC 95% por cenário](imgs/exercicio9_25.png)

> **OBM**: maior sobreposição (100%) maximiza reúso de dados mas eleva a correlação entre lotes, inflando o estimador de variância. Sobreposição reduzida (25%) se aproxima do NBM não sobreposto.

---

## Considerações Finais

Os três exercícios implementam variantes do método de médias em lote para estimação de IC em simulações de horizonte infinito:

1. **NBM (Exercício 7):** método de referência. Com B=20 lotes e tamanho m=5 000 obs/lote, todos os 4 ICs contêm E[X] e a precisão relativa é satisfeita. O custo amostral cresce com ρ (até N=1 700 000 para ρ=0,95), pois séries mais autocorrelacionadas exigem lotes maiores para que as médias de lote sejam aproximadamente i.i.d.

2. **SBM (Exercício 8):** o espaçamento S entre lotes visa decorrelacionar as médias. Com S=1 (NBM com window deslizante de tamanho 1), o método atinge o critério de parada rapidamente mas com ICs incorretos em 2/4 cenários. Com S=M/10, o crescimento do espaçamento elimina demasiadas observações, levando a resultados instáveis — particularmente no Cenário IV (ρ=0,95) onde o viés transiente residual domina a estimativa.

3. **OBM (Exercício 9):** a sobreposição 100 % (lag=1) é matematicamente equivalente a usar quase todas as observações em cada lote, tornando as médias correlacionadas de modo patológico e produzindo ICs completamente fora do alvo. Sobreposição 50 % (lag=50) equilibra eficiência amostral e independência, sendo a variante mais adequada neste experimento. A sobreposição 25 % (lag=75) exige amostras maiores que a 50 %, sem ganho de cobertura.

Em todos os casos, a corretude depende tanto do tamanho de lote m quanto da qualidade da detecção do transiente pelo MSER-5Y. Para ρ elevado (cenários III e IV), a estimação é intrinsecamente mais difícil e requer amostras substancialmente maiores.
