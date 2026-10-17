#!/usr/bin/env python3
"""
insertar_link_hospedaje.py
────────────────────────────────────────────────────────────────
Cantera & Calma — Enlazado interno SEO (Fase C).

Inserta un enlace contextual hacia la landing de hospedaje
(/blog/donde-hospedarse-malinalco/) en TODOS los artículos del blog
(menos la propia landing). Pasa autoridad desde los posts culturales
de alto tráfico hacia la página que queremos posicionar para
búsquedas de reserva ("dónde hospedarse / hoteles en Malinalco").

El bloque se coloca justo antes del CTA de reserva (marcador
CTA-CANTERA-INICIO). Es idempotente: si ya existe, lo reemplaza.

Ejecutar desde la raíz del repo:
    python3 insertar_link_hospedaje.py
────────────────────────────────────────────────────────────────
"""

import os
import re
import sys

BLOG_DIR = "blog"
INICIO   = "<!-- LINK-HOSPEDAJE-INICIO -->"
FIN      = "<!-- LINK-HOSPEDAJE-FIN -->"
EXCLUIR  = {"donde-hospedarse-malinalco"}   # no auto-enlazar a sí misma
CTA_MARK = "<!-- CTA-CANTERA-INICIO -->"

BLOQUE = f"""{INICIO}
<p style="margin:2.2rem 0;padding:0.95rem 1.15rem;background:#F4EEE3;border-left:4px solid #8B5E3C;border-radius:0 10px 10px 0;font-family:'Inter',system-ui,sans-serif;font-size:0.92rem;line-height:1.65;color:#23201B;">&#128719; &iquest;Ya sabes <strong>d&oacute;nde hospedarte en Malinalco</strong>? Lee nuestra <a href="/blog/donde-hospedarse-malinalco/" style="color:#8B5E3C;font-weight:700;text-decoration:underline;">gu&iacute;a de hospedaje en Malinalco</a>: zonas, precios y c&oacute;mo reservar directo en el centro del Pueblo M&aacute;gico.</p>
{FIN}"""


def process_article(filepath: str) -> tuple[bool, str]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Idempotente: si ya existe, reemplazar
    if INICIO in content:
        pattern = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.DOTALL)
        content = pattern.sub(BLOQUE, content)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, "reemplazado (idempotente) ✓"

    # Insertar justo antes del CTA de reserva
    if CTA_MARK in content:
        content = content.replace(CTA_MARK, BLOQUE + "\n" + CTA_MARK, 1)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, "insertado (antes del CTA)"

    return False, "sin marcador CTA — revisar manualmente"


def main():
    if not os.path.isdir(BLOG_DIR):
        print(f"\n❌  No se encuentra '{BLOG_DIR}/'. Ejecuta desde la raíz del repo.\n")
        sys.exit(1)

    articles = sorted([
        (item, os.path.join(BLOG_DIR, item, "index.html"))
        for item in os.listdir(BLOG_DIR)
        if os.path.isfile(os.path.join(BLOG_DIR, item, "index.html"))
        and item not in EXCLUIR
    ])

    print(f"\n🔗  Cantera & Calma — Enlazado interno a hospedaje")
    print(f"{'─'*60}")
    print(f"   Artículos : {len(articles)}  (excluida la propia landing)\n")

    ok, fail = [], []
    for slug, path in articles:
        success, msg = process_article(path)
        if success:
            print(f"  ✅  {slug}  →  {msg}")
            ok.append(slug)
        else:
            print(f"  ❌  {slug}  →  {msg}")
            fail.append(slug)

    print(f"\n{'─'*60}")
    print(f"  ✅ Procesados : {len(ok)}   ❌ Pendientes : {len(fail)}")
    for s in fail:
        print(f"    • blog/{s}/index.html")


if __name__ == "__main__":
    main()
