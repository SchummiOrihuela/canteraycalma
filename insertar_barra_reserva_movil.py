#!/usr/bin/env python3
"""
insertar_barra_reserva_movil.py
────────────────────────────────────────────────────────────────
Cantera & Calma — Inserta (o actualiza) una barra fija inferior
"Reservar directo" SOLO en móvil en TODOS los artículos del blog.

Objetivo: capturar al lector de intención turística/cultural
(70 % móvil) y empujarlo a la reserva directa sin que tenga que
buscar el botón. En desktop no aparece (ahí sigue el widget de
WhatsApp de la esquina); en móvil se oculta ese widget para no
encimarse con la barra.

Ejecutar desde la raíz del repo:
    python3 insertar_barra_reserva_movil.py

Es idempotente: si ya existe la barra marcada, la reemplaza.
────────────────────────────────────────────────────────────────
"""

import os
import re
import sys

BLOG_DIR = "blog"
INICIO   = "<!-- BARRA-RESERVA-MOVIL-INICIO -->"
FIN      = "<!-- BARRA-RESERVA-MOVIL-FIN -->"
WA_NUM   = "5215562513258"
WA_TEXT  = "Hola! Me interesa reservar directo en Cantera & Calma."


def wa_encode(text: str) -> str:
    replacements = [
        (" ", "%20"), ("!", "%21"), ("?", "%3F"), ("&", "%26"),
        ("'", "%27"), ("á", "%C3%A1"), ("é", "%C3%A9"), ("í", "%C3%AD"),
        ("ó", "%C3%B3"), ("ú", "%C3%BA"), ("ñ", "%C3%B1"), ("ü", "%C3%BC"),
    ]
    for a, b in replacements:
        text = text.replace(a, b)
    return text


def build_barra() -> str:
    wa_link = f"https://wa.me/{WA_NUM}?text={wa_encode(WA_TEXT)}"
    return f"""{INICIO}
<style>
  .barra-reserva-movil{{display:none;position:fixed;left:0;right:0;bottom:0;z-index:1000;gap:0.6rem;padding:0.6rem 0.8rem calc(0.6rem + env(safe-area-inset-bottom));background:rgba(107,50,16,0.97);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-shadow:0 -4px 20px rgba(0,0,0,0.22);font-family:'Inter',system-ui,sans-serif;}}
  .barra-reserva-movil a{{flex:1;display:flex;align-items:center;justify-content:center;gap:0.4rem;text-decoration:none;border-radius:12px;padding:0.85rem 0.5rem;font-size:0.95rem;font-weight:700;letter-spacing:0.01em;}}
  .barra-reserva-movil .brm-wa{{background:#25D366;color:#fff;}}
  .barra-reserva-movil .brm-ver{{background:rgba(245,239,230,0.14);color:#F5EFE6;border:1.5px solid rgba(245,239,230,0.42);font-weight:600;}}
  @media (max-width:768px){{
    body{{padding-bottom:74px !important;}}
    .wa-widget{{display:none !important;}}
    .barra-reserva-movil{{display:flex !important;}}
  }}
</style>
<div class="barra-reserva-movil" role="navigation" aria-label="Reservar en Cantera y Calma">
  <a class="brm-wa" href="{wa_link}" aria-label="Reservar directo por WhatsApp">&#128172; Reservar directo</a>
  <a class="brm-ver" href="https://www.canteraycalma.com/#departamentos">Ver propiedades</a>
</div>
{FIN}"""


def process_article(filepath: str) -> tuple[bool, str]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    barra = build_barra()

    # Idempotente: si ya tiene la barra marcada, reemplazar
    if INICIO in content:
        pattern = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.DOTALL)
        new_content = pattern.sub(barra, content)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True, "reemplazada (idempotente) ✓"

    # Insertar justo antes de </body>
    m = re.search(r"</body>", content, re.IGNORECASE)
    if not m:
        return False, "sin </body> — revisar manualmente"
    pos = m.start()
    new_content = content[:pos] + barra + "\n" + content[pos:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, "insertada (nueva)"


def main():
    if not os.path.isdir(BLOG_DIR):
        print(f"\n❌  No se encuentra '{BLOG_DIR}/'. Ejecuta desde la raíz del repo.\n")
        sys.exit(1)

    articles = sorted([
        (item, os.path.join(BLOG_DIR, item, "index.html"))
        for item in os.listdir(BLOG_DIR)
        if os.path.isfile(os.path.join(BLOG_DIR, item, "index.html"))
    ])

    print(f"\n🏠  Cantera & Calma — Barra Reserva Móvil")
    print(f"{'─'*60}")
    print(f"   Artículos : {len(articles)}\n")

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
    if fail:
        for s in fail:
            print(f"    • blog/{s}/index.html")


if __name__ == "__main__":
    main()
