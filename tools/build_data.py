#!/usr/bin/env python3
"""Gera data.json do painel a partir das exportações do Power Automate.

Uso:
  python3 tools/build_data.py --tarefas p1.txt [p2.txt ...] --buckets buckets.csv \
      --pessoas pessoas.csv --out data.json

As páginas de tarefas são o texto que o conector Microsoft 365 devolve para
Planner_Tarefas.csv (o arquivo grande vem em várias páginas; cada página repete o
cabeçalho e termina com uma linha "[page N ...]"). Passe as páginas em ordem.
"""
import argparse
import csv
import io
import json
import re
from datetime import datetime, timezone

RODAPE = re.compile(r"\n*\[page [^\]]*\]\s*$")
PRIORIDADE = {1: "Urgente", 3: "Importante", 5: "Média", 9: "Baixa"}


def ler_paginas(caminhos):
    partes = []
    for i, caminho in enumerate(caminhos):
        texto = open(caminho, encoding="utf-8").read()
        inicio = texto.find("Titulo,")
        if inicio < 0:
            raise SystemExit(f"{caminho}: cabeçalho 'Titulo,' não encontrado")
        texto = RODAPE.sub("", texto[inicio:].rstrip())
        if i > 0:
            texto = texto.split("\n", 1)[1] if "\n" in texto else ""
        partes.append(texto)
    return "\n".join(p for p in partes if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tarefas", nargs="+", required=True)
    ap.add_argument("--buckets", required=True)
    ap.add_argument("--pessoas", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    buckets = {r["BucketId"]: r["Bucket"] for r in csv.DictReader(open(a.buckets, encoding="utf-8"))}
    pessoas = {
        r["Id"]: re.sub(r"^ULB - MSe - ", "", r["Nome"] or "").strip()
        for r in csv.DictReader(open(a.pessoas, encoding="utf-8"))
    }

    linhas = list(csv.DictReader(io.StringIO(ler_paginas(a.tarefas))))
    tarefas = []
    for r in linhas:
        if not r.get("Titulo"):
            continue
        try:
            resp = json.loads(r.get("Responsaveis") or "[]")
        except json.JSONDecodeError:
            resp = []
        ids = [x.get("userId") for x in resp if isinstance(x, dict) and x.get("userId")] if isinstance(resp, list) else list(resp)
        nomes = sorted({pessoas.get(i, "Não identificado") for i in ids})
        prio = int(r["Prioridade"]) if (r.get("Prioridade") or "").isdigit() else None
        tarefas.append({
            "t": r["Titulo"].strip(),
            "b": buckets.get(r.get("BucketId") or "", "Sem bucket"),
            "p": int(r.get("Percentual") or 0),
            "pr": PRIORIDADE.get(prio, ""),
            "v": r.get("Vencimento") or None,
            "r": nomes,
        })

    saida = {
        "gerado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tarefas": tarefas,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, separators=(",", ":"))
    abertas = sum(1 for t in tarefas if t["p"] < 100)
    print(f"{len(tarefas)} tarefas ({abertas} abertas) -> {a.out}")


if __name__ == "__main__":
    main()
