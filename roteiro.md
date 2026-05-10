# Roteiro de Apresentação — Mini Estudo 1

## Slide 1 — Título (~30s)
- Apresentar o título, disciplina e integrantes do grupo.

## Slide 2 — Contexto (~1min)
- Explicar a trilha (Dispositivos Pessoais) e a pergunta motivadora.
- Dizer que o objetivo é criar um baseline: medir RAM em Windows vs Linux com carga padronizada.

## Slide 3 — Pergunta Operacional (~1min)
- Ler a pergunta operacional.
- Explicar a métrica (`uso_percent`), o instrumento (psutil) e que a medição é direta.

## Slide 4 — Protocolo de Coleta (~1min)
- Descrever os 5 passos: reiniciar, estabilizar, medir, salvar.
- Enfatizar os controles: mesmas apps, mesmo modo de energia, mesmo script.

## Slide 5 — Ambientes (~30s)
- Mostrar a tabela com os 6 cenários (3 operadores × 2 SOs).
- Destacar que temos máquinas de 8 GB e 16 GB.

## Slide 6 — Dados Coletados (~1min)
- Apresentar a tabela de resumo estatístico.
- Destacar: Linux ~15–16% nas máquinas de 16 GB, Windows ~35–40%. Luiza: Ubuntu ~24% vs Windows ~65% na máquina de 8 GB.

## Slide 7 — Intervalos de Confiança (~1min)
- Mostrar os ICs e a precisão relativa. Multiplicador usado: t(29) = 2,045.
- Enfatizar que 5/6 cenários têm precisão < 3%.
- Comentar que Windows 16 GB da Carolina ficou no limiar (~5,40%) por causa do antivírus MsMpEng.

## Slide 8 — Suficiência Amostral (~30s)
- Mostrar que n=30 é mais que suficiente para quase todos os cenários.
- Comentar o caso marginal do Windows 16 GB (Carolina): n necessário = 36 (variabilidade do antivírus).
- Mencionar que Windows 8 GB (Luiza) exigiria n=8, portanto n=30 é confortável.

## Slides 9–13 — Visualizações (~3min total)
- **Slide 9 (Geral):** Visão geral dos boxplots — mostrar a separação clara entre Linux e Windows.
- **Slide 10 (Carolina):** Ubuntu ~15% vs Windows ~35%. Mencionar os outliers do antivírus.
- **Slide 11 (Luiza):** Ubuntu ~24% vs Windows ~65% — diferença de ~41 p.p. Mencionar que o TiWorker.exe (Windows Update) gerou pico de 81,8% nas medições 21–23, causando a variabilidade.
- **Slide 12 (Nicolas):** Fedora ~15,7% vs Windows ~40%. Ambos com baixa variabilidade.
- **Slide 13 (Agregado):** Teste t de Welch significativo (t = −18,93, p = 1,70 × 10⁻³⁵). Efeito muito grande (Cohen's d = −2,82). Linux: μ = 18,4%, Windows: μ = 46,7%.

## Slide 14 — Interpretação (~1min)
- Resumir: Carolina 20 p.p., Nicolas 24 p.p., Luiza 41 p.p.
- Linux (Ubuntu e Fedora) se comportam de forma muito semelhante (~15,5–16%) nas máquinas de 16 GB.
- Windows consome mais por serviços nativos pesados (MsMpEng, dwm, TiWorker, MemCompression).

## Slide 15 — Limitações (~30s)
- Hardware não idêntico, processos de fundo diferentes, carga limitada a um perfil.
- A RAM total reportada varia ~380 MB entre SOs na mesma máquina (mapeamento de firmware/UEFI diferente entre kernels), introduzindo assimetria no denominador do `uso_percent`.
- Ser honesto: não dá para generalizar para todo tipo de uso.

## Slide 16 — Conclusão (~30s)
- Windows consome significativamente mais RAM que Linux.
- Protocolo estável e reprodutível.
- Baseline estabelecido para estudos futuros.
