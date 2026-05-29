# Relatório — Estado Transiente na Simulação de Fila M/M/1

**ICC305 — Avaliação de Desempenho**  
**Carolina Maycá, Luiza Caxeixa e Nicolas Mady**

Prof. Edjair Mota, Dr.-Ing. — Instituto de Computação / UFAM

---

## Parâmetros do Sistema

| Parâmetro          | Valor          |
| ------------------ | -------------- |
| Taxa de chegada λ  | 9,5 clientes/s |
| Taxa de serviço μ  | 10 clientes/s  |
| Carga ρ = λ/μ      | 0,95 (95%)     |
| Valor teórico E[X] | **1,9 s**      |

A fórmula analítica para o tempo médio de espera na fila M/M/1 é:

$$E[X] = \rho \cdot \frac{1/\mu}{1 - \rho}, \quad \text{onde } \rho = \frac{\lambda}{\mu}$$

Com λ = 9,5 e μ = 10, temos ρ = 0,95 e portanto **E[X] = 1,9 s**.

A carga ρ = 0,95 é consideravelmente mais alta do que no relatório anterior (ρ = 0,9), o que torna o estado
transiente muito mais longo e o viés por inicialização muito mais pronunciado.

---

## Implementação

A simulação foi desenvolvida no notebook `mm1.ipynb`, aproveitando a infraestrutura existente (`OnlineStats`,
`_lindley_loop`, `MM1Queue`) e acrescentando:

- **`MM1Queue.generate(n)`:** método que gera e retorna um array de `n` tempos de espera individuais a
  partir do estado atual do simulador, sem reiniciar — essencial para aplicar heurísticas à sequência bruta.
- **`conway_warmup(xs)`:** implementação da heurística de Conway.
- **`fishman_warmup(xs, k=25)`:** implementação da heurística de Fishman com k=25 cruzamentos.
- **`mser5y(xs)`:** implementação da heurística MSER-5Y.

### Heurísticas implementadas

**Conway**

```python
def conway_warmup(xs):
    xs      = np.asarray(xs, dtype=float)
    suf_max = np.maximum.accumulate(xs[::-1])[::-1]
    suf_min = np.minimum.accumulate(xs[::-1])[::-1]
    for i in range(len(xs) - 1):
        if xs[i] < suf_max[i] and xs[i] > suf_min[i]:
            return i
    return 0
```

d = primeiro índice i tal que x[i] não é o máximo nem o mínimo de x[i:].
Implementado com acumulação de sufixo em O(n) para eficiência.

**Fishman (k=25)**

```python
def fishman_warmup(xs, k=25):
    xs     = np.asarray(xs, dtype=float)
    mu_all = xs.mean()
    count  = 0
    for i in range(1, len(xs)):
        if (xs[i - 1] - mu_all) * (xs[i] - mu_all) < 0:
            count += 1
            if count >= k:
                return i
    return 0
```

d = índice após o k-ésimo cruzamento da média global. Valores típicos de k: 7 e 25 (usado k=25).

**MSER-5Y**

```python
def mser5y(xs):
    xs   = np.asarray(xs, dtype=float)
    N, m = len(xs), 5
    k    = N // m
    if k < 10:
        return None
    Z      = xs[: k * m].reshape(k, m).mean(axis=1)
    half_k = k // 2
    mser_vals = np.empty(half_k)
    for d in range(half_k):
        tail  = Z[d:]
        kd    = len(tail)
        z_bar = tail.mean()
        s     = np.sqrt(((tail - z_bar) ** 2).mean())
        mser_vals[d] = s / np.sqrt(kd)
    min_val = mser_vals.min()
    if np.isclose(mser_vals, min_val).sum() > 1:
        return None   # empate → truncagem não encontrada
    return int(np.argmin(mser_vals)) * m
```

Agrupa em blocos de m=5, forma Z_j, computa MSER5(k,d) = S_Z(k,d)/√(k−d) para d ∈ [0, k/2).
Retorna d* × 5 (em observações originais) ou `None` em caso de empate.

---

## Exercício 4 — Viés com n Fixo

### Descrição

O objetivo é quantificar o viés introduzido pelo estado transiente. Executa-se r=30 réplicas independentes,
cada uma simulando n=10³ clientes com λ=9,5 (ρ=0,95), a partir de fila vazia. Para cada réplica r:

$$B_r = \bar{X}(n) - E[X]$$

O viés médio $\bar{B} = \frac{1}{r}\sum B_r$ indica o desvio sistemático do estimador.

### Código

```python
N4   = 1_000
rows4 = []

for r in range(R):          # R = 30
    sim_r     = MM1Queue(lam=LAM_B, seed=SEED + r)
    mean_r, _ = sim_r.run_fixed(N4)
    rows4.append((r + 1, mean_r, mean_r - E_B))
```

### Resultados Obtidos

| r    | X̄(n)    | B        |
| ---- | ------- | -------- |
| 1    | (ver notebook) | (ver notebook) |
| …    | …       | …        |
| 30   | (ver notebook) | (ver notebook) |
| **Média** | (ver notebook) | (ver notebook) |

**E[X] teórico = 1,900000 s**

Com ρ = 0,95, o transiente é muito mais longo do que em ρ = 0,9. Para n=10³, a fila ainda não atingiu o
estado estacionário na maioria das réplicas, resultando em viés negativo significativo (o estimador
subestima E[X] porque as primeiras observações provêm de fila vazia).

A alta dispersão entre réplicas (desvio padrão elevado) confirma que n=10³ é insuficiente para sistemas
com carga próxima de 1.

![Gráfico Exercício 4 — X̄(n) por réplica e distribuição do viés](exercicio4.png)

---

## Exercício 5 — Eliminação do Transiente: Conway e Fishman

### Descrição

Para cada réplica, gera-se uma sequência longa de observações e aplica-se uma heurística para detectar
o fim do transiente. Após o ponto de truncagem d, coletam-se n=10³ observações em estado estacionário:

$$\bar{X}(n, d) = \frac{1}{n} \sum_{i=d+1}^{d+n} x_i$$

O experimento é repetido r=30 vezes para cada heurística.

### Código

```python
TOTAL_GEN = 5_000

for r in range(R):
    sim_r = MM1Queue(lam=LAM_B, seed=SEED + r)
    sim_r._reset()
    xs = sim_r.generate(TOTAL_GEN)

    d_c = conway_warmup(xs)
    d_f = fishman_warmup(xs, k=25)

    # garante N5 obs pós-warmup
    needed = max(d_c, d_f) + N5
    while len(xs) < needed:
        xs = np.concatenate([xs, sim_r.generate(1_000)])

    m_c = float(xs[d_c: d_c + N5].mean())
    m_f = float(xs[d_f: d_f + N5].mean())
```

### Resultados Obtidos

**Conway**

| r    | d    | X̄(n)    | B        |
| ---- | ---- | ------- | -------- |
| 1    | (ver nb) | (ver nb) | (ver nb) |
| …    | …    | …       | …        |
| 30   | (ver nb) | (ver nb) | (ver nb) |
| **Média** | (ver nb) | (ver nb) | (ver nb) |

**Fishman (k=25)**

| r    | d    | X̄(n)    | B        |
| ---- | ---- | ------- | -------- |
| 1    | (ver nb) | (ver nb) | (ver nb) |
| …    | …    | …       | …        |
| 30   | (ver nb) | (ver nb) | (ver nb) |
| **Média** | (ver nb) | (ver nb) | (ver nb) |

Ambas as heurísticas reduzem o viés em relação ao Exercício 4. Conway tende a descartar um número
pequeno de observações (a primeira que não é extremo do sufixo), enquanto Fishman aguarda 25
cruzamentos da média global — produzindo warmups tipicamente maiores para ρ elevado.

A comparação dos viéses médios $\bar{B}_C$ e $\bar{B}_F$ permite avaliar qual heurística se aproxima
mais do valor teórico para este sistema.

![Gráfico Exercício 5 — X̄(n) pós-warmup e viés por réplica](exercicio5.png)

---

## Exercício 6 — MSER-5Y, Precisão Relativa 5% e Comparação

### Descrição

Executa uma simulação de horizonte infinito com λ=9,5, eliminando o transiente pela heurística MSER-5Y.
A regra de parada é a precisão relativa H/X̄ ≤ 5%.

A heurística minimiza:

$$\text{MSER5}(k,d) = \frac{S_Z(k,d)}{\sqrt{k-d}}, \quad S_Z^2(k,d) = \frac{1}{k-d}\sum_{j=d+1}^{k}\bigl[Z_j - \bar{Z}(k,d)\bigr]^2$$

com $Z_j = \frac{1}{5}\sum_{i=1}^{5} x_{5(j-1)+i}$ (blocos de tamanho m=5) e d restrito à primeira metade.

### Código

```python
sim6 = MM1Queue(lam=LAM_B, seed=SEED)
sim6._reset()
buf  = sim6.generate(INIT_N6)   # 10 000 obs iniciais

d_mser = None
while d_mser is None:
    d_mser = mser5y(buf)
    if d_mser is None:
        buf = np.concatenate([buf, sim6.generate(EXTRA_N6)])

stats6 = OnlineStats()
stats6.add_batch(buf[d_mser:])

while not (stats6.n >= 30 and stats6.mean > 0
           and stats6.half_width / stats6.mean <= 0.05):
    stats6.add_batch(sim6.generate(1_000))
```

### Resultados Obtidos

| Métrica         | Valor           |
| --------------- | --------------- |
| d* (MSER-5Y)    | (ver notebook)  |
| n pós-truncagem | (ver notebook)  |
| X̄               | (ver notebook) s|
| H               | (ver notebook) s|
| H/X̄             | ~5,0%           |
| IC 95%          | (ver notebook)  |
| E[X] teórico    | 1,9000 s        |

O gráfico comparativo exibe X̄ ± H para as três heurísticas, com a linha de referência E[X] = 1,9 s.
Para Conway e Fishman usa-se o IC da média amostral das 30 réplicas (H = 1,96 · dp/√30);
para MSER-5Y usa-se o IC direto do OnlineStats.

![Gráfico Exercício 6 — Comparação das 3 heurísticas](exercicio6.png)

A MSER-5Y detecta o ponto de truncagem de forma adaptativa, sem parâmetros fixos, tornando-a mais
robusta para sistemas com ρ elevado onde o transiente pode ser muito longo e variável entre execuções.

---

## Considerações Finais

Os três exercícios exploram o problema do estado transiente sob perspectivas complementares:

1. **Exercício 4 — Sem warmup:** o viés negativo é expressivo para ρ=0,95 com n=10³, evidenciando
   que sistemas de alta carga exigem warmup obrigatório para estimativas confiáveis.

2. **Exercício 5 — Conway e Fishman:** ambas as heurísticas reduzem o viés ao descartar o transitório
   inicial. Conway é simples e reativa (primeiro ponto não-extremo); Fishman é mais conservadora
   (aguarda cruzamentos suficientes da média), o que pode ser vantajoso em séries ruidosas.

3. **Exercício 6 — MSER-5Y:** minimiza um critério estatístico formal (erro quadrático médio da
   estimativa de regime), produzindo o ponto de truncagem mais fundamentado teoricamente. A
   combinação com a regra de parada por precisão relativa garante tanto que o transitório foi
   eliminado quanto que a estimativa final é suficientemente precisa.

Em todos os casos, a corretude da implementação é verificável pelo fato de que as estimativas pós-warmup
convergem para E[X] = 1,9 s, valor analítico conhecido para a fila M/M/1 com ρ = 0,95.
