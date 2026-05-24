from math import log
from random import random

import numpy as np
import pandas as pd
import scipy.stats as st

ARRIVAL_RATE = 9
SERVICE_RATE = 10

rows = []

for e in [3, 5, 7, 9]:
    n = 10 ** e
    chegada = fim = media = m2 = 0

    for i in range(n):
        chegada += -log(random()) / ARRIVAL_RATE # proxima chegada
        inicio = max(chegada, fim)
        espera = inicio - chegada
        fim = inicio + -log(random()) / SERVICE_RATE # tempo de serviço

        delta = espera - media
        media += delta / (i + 1)
        m2 += delta * (espera - media)

    variancia = m2 / (n - 1)
    erro_padrao = np.sqrt(variancia / n)
    ic = st.t.interval(0.95, n - 1, loc=media, scale=erro_padrao)
    rows.append((n, media, ic[0], ic[1]))
    print(f"n={n:=10_} | media={media:.6f} | ic(95%)=[{ic[0]:.6f}; {ic[1]:.6f}]")

df = pd.DataFrame(rows, columns=["n", "media", "ic_inf", "ic_sup"])
print(df)