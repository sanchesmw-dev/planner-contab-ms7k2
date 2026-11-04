#!/usr/bin/env python3
"""Monta index.html a partir de src/index.template.html, embutindo a logo (src/logo.b64)."""
import pathlib
raiz = pathlib.Path(__file__).resolve().parent.parent
html = (raiz / "src/index.template.html").read_text(encoding="utf-8")
logo = (raiz / "src/logo.b64").read_text().strip()
(raiz / "index.html").write_text(html.replace("__LOGO__", logo), encoding="utf-8")
import hashlib
(raiz / "versao.txt").write_text(hashlib.sha1((raiz / "index.html").read_bytes()).hexdigest()[:12] + "\n")
print("index.html e versao.txt gerados")
