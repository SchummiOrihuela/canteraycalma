#!/usr/bin/env python3
"""
insertar_cta_blog.py
────────────────────────────────────────────────────────────────
Cantera & Calma — Inserta o actualiza el bloque CTA de reserva
directa en TODOS los artículos del blog.

Ejecutar desde la raíz del repo:
    python3 insertar_cta_blog.py

El script:
  1. Descubre automáticamente todos los artículos en /blog/
  2. Si ya existe un CTA marcado → lo reemplaza (idempotente)
  3. Si hay un CTA básico sin estilo → lo reemplaza
  4. Si no hay CTA → lo inserta antes de "Sigue explorando"
  5. Imprime un resumen y el comando git listo para copiar
────────────────────────────────────────────────────────────────
"""

import os
import re
import sys

BLOG_DIR   = "blog"
CTA_INICIO = "<!-- CTA-CANTERA-INICIO -->"
CTA_FIN    = "<!-- CTA-CANTERA-FIN -->"

# ── Mapping slug → categoría ────────────────────────────────
CATEGORIAS = {
    "convento-agustino-malinalco":       "historia",
    "malinalco-pueblo-magico-historia":  "historia",
    "barrios-de-malinalco":              "historia",
    "malinalxochitl-leyenda":            "leyendas",
    "guardianes-del-cerro":              "leyendas",
    "suenos-en-malinalco":               "leyendas",
    "casa-de-las-aguilas":               "prehispanico",
    "guerreros-aguila-jaguar":           "prehispanico",
    "subida-cerro-idolos":               "prehispanico",
    "fiesta-divino-salvador":            "fiestas",
    "judea-malinalco-semana-santa":      "fiestas",
    "dia-de-muertos-malinalco":          "fiestas",
    "10-restaurantes-malinalco":         "gastronomia",
    "pesca-trucha-mezcal-malinalco":     "gastronomia",
    "donde-desayunar-malinalco":         "gastronomia",
    "48-horas-malinalco":                "finde",
    "3-dias-malinalco":                  "finde",
    "ruta-5-dias-malinalco":             "finde",
    "malinalco-con-familia":             "finde",
    "escapada-romantica-malinalco":      "finde",
    "fin-de-semana-malinalco-cdmx":      "finde",
    "fin-de-semana-malinalco":           "finde",
}

# ── Copy CTA por categoría ──────────────────────────────────
CTAS = {
    "historia": {
        "headline": "¿La historia te tiene atrapado? Imagina contarla desde aquí.",
        "subtext":  "Nuestras propiedades están en el Barrio de San Juan, en el corazón histórico del Pueblo Mágico.",
        "wa_text":  "Hola! Leí sobre la historia de Malinalco en su blog y me interesa reservar una estancia.",
        "emoji":    "🏛️",
    },
    "leyendas": {
        "headline": "La energía del pueblo se siente más de noche. ¿Te quedas?",
        "subtext":  "4 propiedades en el corazón del Pueblo Mágico. La magia empieza en la habitación.",
        "wa_text":  "Hola! Leí sobre las leyendas de Malinalco en su blog y me interesa reservar.",
        "emoji":    "🌙",
    },
    "prehispanico": {
        "headline": "A 5 minutos caminando del Cerro de los Ídolos.",
        "subtext":  "Sal del desayuno, llega al templo antes que nadie. Así se vive Malinalco bien vivido.",
        "wa_text":  "Hola! Leí sobre la zona arqueológica de Malinalco en su blog y me interesa reservar.",
        "emoji":    "🦅",
    },
    "fiestas": {
        "headline": "No seas espectador — vívelo desde adentro.",
        "subtext":  "En temporada de fiestas la disponibilidad se agota rápido. Reserva directo y asegura tu lugar.",
        "wa_text":  "Hola! Leí sobre las fiestas de Malinalco en su blog y me interesa reservar para esa época.",
        "emoji":    "🎆",
    },
    "gastronomia": {
        "headline": "Todo lo que leíste está a 5 minutos de aquí. Literalmente.",
        "subtext":  "Nuestras propiedades son la base perfecta para explorar la gastronomía de Malinalco sin prisa.",
        "wa_text":  "Hola! Leí sobre los restaurantes de Malinalco en su blog y me interesa reservar.",
        "emoji":    "🍽️",
    },
    "finde": {
        "headline": "El itinerario está listo. Solo falta tu fecha.",
        "subtext":  "Escríbenos y confirmamos disponibilidad en minutos. Sin tarifas de plataforma, trato directo.",
        "wa_text":  "Hola! Vi el itinerario en el blog de Cantera & Calma y me interesa reservar para Malinalco.",
        "emoji":    "🗓️",
    },
}

# ── Patrones de CTAs básicos ya existentes (sin marcador) ───
OLD_CTA_PATTERNS = [
    (r'<section[^>]*class="[^"]*article-cta[^"]*"[^>]*>.*?</section>', re.DOTALL),
    (r'<div[^>]*class="[^"]*cta-reserva[^"]*"[^>]*>.*?</div>', re.DOTALL),
    (r'<div[^>]*class="[^"]*cta-block[^"]*"[^>]*>.*?</div>', re.DOTALL),
]
OLD_CTA_KEYWORDS = ["reservar", "Reservar", "WhatsApp", "whatsapp", "Cantera", "canteraycalma"]

# ── Anclas de inserción (orden de prioridad) ─────────────────
INSERT_ANCHORS = [
    r'(<section[^>]*class="[^"]*related[^"]*"[^>]*>)',
    r'(<section[^>]*id="[^"]*related[^"]*"[^>]*>)',
    r'(<section[^>]*class="[^"]*blog-related[^"]*"[^>]*>)',
    r'(<section[^>]*class="[^"]*sigue[^"]*"[^>]*>)',
    r'(<div[^>]*class="[^"]*related[^"]*"[^>]*>)',
    r'(<h2[^>]*>\s*(?:&#128214;|📖)?\s*Sigue explorando)',
    r'(<h2[^>]*>\s*Sigue explorando)',
    r'(<!-- sigue-explorando -->)',
    r'(<!-- related -->)',
    r'(</article>)',
    r'(<footer[\s>])',
    r'(<!-- footer)',
]


def wa_encode(text: str) -> str:
    replacements = [
        (" ", "%20"), ("!", "%21"), ("?", "%3F"), ("&", "%26"),
        ("'", "%27"), ("á", "%C3%A1"), ("é", "%C3%A9"), ("í", "%C3%AD"),
        ("ó", "%C3%B3"), ("ú", "%C3%BA"), ("ñ", "%C3%B1"), ("ü", "%C3%BC"),
    ]
    for a, b in replacements:
        text = text.replace(a, b)
    return text


def build_cta(slug: str, categoria: str) -> str:
    d = CTAS.get(categoria, CTAS["finde"])
    wa_link = f"https://wa.me/5215562513258?text={wa_encode(d['wa_text'])}"
    return f"""{CTA_INICIO}
<section class="article-cta-reserva" style="background:linear-gradient(135deg,#6B3210 0%,#8B5E3C 55%,#7A4A28 100%);border-radius:20px;padding:2.8rem 2rem 2.5rem;margin:3.5rem 0 3rem;text-align:center;overflow:hidden;position:relative;box-shadow:0 8px 32px rgba(107,50,16,0.22);">
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 80% 20%,rgba(255,255,255,0.06) 0%,transparent 60%),radial-gradient(ellipse at 10% 80%,rgba(255,255,255,0.04) 0%,transparent 50%);pointer-events:none;"></div>
  <div style="position:relative;z-index:1;max-width:560px;margin:0 auto;">
    <p style="display:inline-block;background:rgba(245,239,230,0.14);border:1px solid rgba(245,239,230,0.28);border-radius:50px;padding:0.35rem 1.1rem;font-family:'Inter',system-ui,sans-serif;font-size:0.75rem;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;color:#F5EFE6;margin:0 0 1.3rem;">⭐ SuperAnfitrión &nbsp;·&nbsp; 8 años &nbsp;·&nbsp; 4.93★ Airbnb · 402 reseñas</p>
    <h2 style="font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-size:clamp(1.35rem,4vw,1.85rem);font-weight:700;color:#F5EFE6;line-height:1.35;margin:0 0 0.85rem;">{d['emoji']} {d['headline']}</h2>
    <p style="font-family:'Inter',system-ui,sans-serif;font-size:0.92rem;line-height:1.65;color:rgba(245,239,230,0.82);margin:0 0 0.5rem;">{d['subtext']}</p>
    <p style="font-family:'Inter',system-ui,sans-serif;font-size:0.88rem;font-weight:600;color:#F5EFE6;margin:0 0 2rem;letter-spacing:0.01em;">Reserva directo y ahorra hasta 20&nbsp;% vs Airbnb.</p>
    <div style="display:flex;gap:0.85rem;justify-content:center;flex-wrap:wrap;">
      <a href="{wa_link}" style="display:inline-flex;align-items:center;gap:0.4rem;background:#25D366;color:#fff;text-decoration:none;padding:0.88rem 1.75rem;border-radius:50px;font-family:'Inter',system-ui,sans-serif;font-size:0.92rem;font-weight:700;letter-spacing:0.01em;box-shadow:0 4px 16px rgba(0,0,0,0.28);">💬 Reservar directo</a>
      <a href="https://www.canteraycalma.com/#departamentos" style="display:inline-flex;align-items:center;gap:0.35rem;background:transparent;color:#F5EFE6;text-decoration:none;padding:0.88rem 1.5rem;border-radius:50px;font-family:'Inter',system-ui,sans-serif;font-size:0.92rem;font-weight:500;border:1.5px solid rgba(245,239,230,0.45);">Ver propiedades →</a>
    </div>
  </div>
</section>
{CTA_FIN}"""


def get_categoria(slug: str) -> str:
    return CATEGORIAS.get(slug, "finde")


def _write(filepath: str, content: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def process_article(filepath: str, slug: str) -> tuple[bool, str]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    categoria = get_categoria(slug)
    cta_html  = build_cta(slug, categoria)

    # CASO 1: Ya tiene marcador propio → siempre reemplazar (idempotente)
    if CTA_INICIO in content:
        pattern = re.compile(
            re.escape(CTA_INICIO) + r".*?" + re.escape(CTA_FIN),
            re.DOTALL
        )
        new_content = pattern.sub(cta_html, content)
        _write(filepath, new_content)
        return True, "reemplazado (marcador propio) ✓ idempotente"

    # CASO 2: CTA básico sin marcador → detectar y reemplazar
    for pattern_str, flags in OLD_CTA_PATTERNS:
        m = re.search(pattern_str, content, flags)
        if m:
            matched = m.group(0)
            if any(kw in matched for kw in OLD_CTA_KEYWORDS):
                new_content = content[:m.start()] + cta_html + content[m.end():]
                _write(filepath, new_content)
                return True, "reemplazado (CTA básico sin marcador)"

    # CASO 3: Sin CTA → insertar en el punto correcto
    for anchor in INSERT_ANCHORS:
        m = re.search(anchor, content, re.IGNORECASE)
        if m:
            pos = m.start()
            new_content = content[:pos] + "\n" + cta_html + "\n\n" + content[pos:]
            _write(filepath, new_content)
            return True, f"insertado (nuevo)"

    return False, "sin punto de inserción — revisar manualmente"


def main():
    if not os.path.isdir(BLOG_DIR):
        print(f"\n❌  No se encuentra '{BLOG_DIR}/'.")
        print(f"   cd ~/ruta/a/canteraycalma && python3 insertar_cta_blog.py\n")
        sys.exit(1)

    # Descubrir artículos (excluye blog/index.html)
    articles = sorted([
        (item, os.path.join(BLOG_DIR, item, "index.html"))
        for item in os.listdir(BLOG_DIR)
        if os.path.isfile(os.path.join(BLOG_DIR, item, "index.html"))
    ])

    print(f"\n🏠  Cantera & Calma — CTA Inserter")
    print(f"{'─'*60}")
    print(f"   Directorio : {os.path.abspath(BLOG_DIR)}/")
    print(f"   Artículos  : {len(articles)}\n")

    ok, fail = [], []

    for slug, path in articles:
        cat = get_categoria(slug)
        success, msg = process_article(path, slug)
        label = f"[{cat:12s}]  {slug}"
        if success:
            print(f"  ✅  {label}")
            print(f"       → {msg}")
            ok.append(slug)
        else:
            print(f"  ❌  {label}")
            print(f"       → {msg}")
            fail.append(slug)

    print(f"\n{'─'*60}")
    print(f"  ✅ Procesados : {len(ok)}   ❌ Sin insertar : {len(fail)}")

    if fail:
        print(f"\n  Artículos pendientes (revisar manualmente):")
        for s in fail:
            print(f"    • blog/{s}/index.html")

    print(f"""
{'─'*60}
  📤  Publicar todo de una:

  git add blog/
  git commit -m "feat: CTA reserva directa en los {len(ok)} artículos del blog"
  git push origin main
{'─'*60}
""")


if __name__ == "__main__":
    main()
