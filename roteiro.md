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
- Destacar: Linux ~15% nas máquinas de 16 GB, Windows ~35–40%. Luiza: Ubuntu 55% vs Windows 80%.

## Slide 7 — Intervalos de Confiança (~1min)
- Mostrar os ICs e a precisão relativa.
- Enfatizar que 5/6 cenários têm precisão < 1,5%.
- Comentar que Windows 16 GB da Carolina ficou no limiar (5,18%) por causa do antivírus.

## Slide 8 — Suficiência Amostral (~30s)
- Mostrar que n=30 é mais que suficiente para quase todos os cenários.
- Comentar o caso marginal do Windows 16 GB (Carolina): n necessário = 33.

## Slides 9–13 — Visualizações (~3min total)
- **Slide 9 (Geral):** Visão geral dos boxplots — mostrar a separação clara entre Linux e Windows.
- **Slide 10 (Carolina):** Ubuntu ~15% vs Windows ~35%. Mencionar os outliers do antivírus.
- **Slide 11 (Luiza):** Ubuntu ~55% vs Windows ~80%. Windows opera sob alta pressão de memória.
- **Slide 12 (Nicolas):** Fedora ~15,7% vs Windows ~40%. Ambos com baixa variabilidade.
- **Slide 13 (Agregado):** Teste t de Welch significativo (p ≈ 0). Efeito grande (Cohen's d = −1,17).

## Slide 14 — Interpretação (~1min)
- Resumir: diferença de 20–25 p.p. em todos os pares.
- Linux (Ubuntu e Fedora) se comportam de forma muito semelhante.
- Windows consome mais por serviços nativos pesados (MsMpEng, dwm, TiWorker, MemCompression).

## Slide 15 — Limitações (~30s)
- Hardware não idêntico, processos de fundo diferentes, carga limitada a um perfil.
- Ser honesto: não dá para generalizar para todo tipo de uso.

## Slide 16 — Conclusão (~30s)
- Windows consome significativamente mais RAM que Linux.
- Protocolo estável e reprodutível.
- Baseline estabelecido para estudos futuros.
