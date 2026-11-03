# Planner Contabilidade — painel para TV

Painel da equipe de Contabilidade (ULB - Missão Sergipe) para exibir numa TV.
Alterna entre tarefas por bucket, tarefas por usuário e a lista de atrasadas,
com lembrete de registro de ponto (07:30, 12:00, 13:00, 17:30 e 19:00).

## Arquivos

- `index.html` — a página. É gerada a partir de `src/index.template.html` e `src/logo.b64`:
  `python3 tools/build_page.py`. Edite o template, não o `index.html`.
- `data.json` — os dados exibidos.
- `tools/build_data.py` — gera `data.json` a partir das exportações do Power Automate no
  SharePoint (`Contabilidade/Planner/Planner_Tarefas.csv`, `Planner_Buckets.csv`,
  `Planner_Pessoas.csv`).

A página busca `data.json` de novo a cada 10 minutos e se recarrega por inteiro a cada 6 horas.

## Atualizar os dados

```
python3 tools/build_data.py --tarefas pagina1.txt pagina2.txt \
  --buckets Planner_Buckets.csv --pessoas Planner_Pessoas.csv --out data.json
```

As páginas de tarefas são o texto devolvido pelo conector Microsoft 365 para
`Planner_Tarefas.csv` (o arquivo vem em várias páginas; passe todas, em ordem).

Manutenção feita pelo Claude.
