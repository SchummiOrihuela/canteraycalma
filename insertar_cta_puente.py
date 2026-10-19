#!/usr/bin/env python3
"""
insertar_cta_puente.py
────────────────────────────────────────────────────────────────
Cantera & Calma — Inserta (o actualiza) un CTA-PUENTE contextual al
final del cuerpo de cada artículo del blog, justo antes de </article>.

Por qué: el embudo GA4 (blog → click_whatsapp) mostró que los posts
con un puente emocional historia→hospedaje (p. ej. Día de Muertos)
convierten, mientras que los que solo tenían CTA arriba/abajo
quedaban en 0 %. Este script replica esa fórmula ganadora en TODOS
los artículos, con copy propio para cada uno.

Cada puente lleva un enlace wa.me → dispara el evento click_whatsapp
que ya está marcado como evento clave en GA4, así que entra medido.

Ejecutar desde la raíz del repo:
    python3 insertar_cta_puente.py

Es idempotente: si ya existe el bloque marcado, lo reemplaza.
────────────────────────────────────────────────────────────────
"""

import os
import re
import sys
import urllib.parse

BLOG_DIR = "blog"
INICIO   = "<!-- CTA-PUENTE-INICIO -->"
FIN      = "<!-- CTA-PUENTE-FIN -->"
WA_NUM   = "5215562513258"

# Marco ESTANDARIZADO del mensaje de WhatsApp. Todos los artículos
# abren igual ("Vengo del blog de Cantera & Calma (<Artículo>)") para
# que el anfitrión reconozca al instante, en su bandeja, que el lead
# viene del blog y de qué artículo. %s = etiqueta del artículo.
WA_TEMPLATE = ("Hola! 👋 Vengo del blog de Cantera & Calma (%s) "
               "y quiero hospedarme en Malinalco. ¿Tienen disponibilidad?")

# slug -> (gancho, copy, etiqueta_articulo)
DATA = {
    "10-restaurantes-malinalco": (
        "¿Se te antojó Malinalco?",
        "Despierta a pasos de estos restaurantes y recórrelos todos sin prisa. Hospédate en el centro, desde <strong>$600/noche</strong> y reserva directa sin comisión de Airbnb.",
        "Restaurantes en Malinalco"),
    "3-dias-malinalco": (
        "¿Listo para esos 3 días?",
        "Tener base en el corazón del pueblo te ahorra traslados y te deja vivir Malinalco a pie. Desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "3 días en Malinalco"),
    "48-horas-malinalco": (
        "48 horas rinden más si duermes en el centro",
        "Despierta a pasos de la plaza y aprovecha cada hora. Hospédate directo con nosotros, desde <strong>$600/noche</strong> y sin comisión de Airbnb.",
        "48 horas en Malinalco"),
    "barrios-de-malinalco": (
        "San Juan es, justamente, donde te hospedas con nosotros",
        "Despierta en el barrio más tradicional de Malinalco, a pasos de la plaza y las capillas que acabas de conocer. Desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "Los barrios de Malinalco"),
    "casa-de-las-aguilas": (
        "Visita la Casa de las Águilas sin madrugar traslados",
        "Nuestras propiedades están a minutos del acceso al Cerro de los Ídolos. Hospédate en el centro, desde <strong>$600/noche</strong> y reserva directa.",
        "La Casa de las Águilas"),
    "convento-agustino-malinalco": (
        "El convento está a unas calles de donde dormirías",
        "Hospédate en el centro histórico y recorre el convento, la plaza y el mercado caminando. Desde <strong>$600/noche</strong>, reserva directa.",
        "El Convento Agustino"),
    "dia-de-muertos-malinalco": (
        "Día de Muertos se llena primero",
        "Las fechas (28 oct–2 nov) son las de mayor demanda del año y el hospedaje se agota. Asegura tu lugar en el centro, desde <strong>$600/noche</strong> y reserva directa sin comisión de Airbnb.",
        "Día de Muertos"),
    "donde-desayunar-malinalco": (
        "El mejor desayuno empieza por despertar aquí",
        "Hospédate a pasos de estos lugares y arranca el día sin prisas. Desde <strong>$600/noche</strong>, reserva directa.",
        "Dónde desayunar"),
    "donde-hospedarse-malinalco": (
        "¿Listo para reservar directo?",
        "Hospédate en el centro del Pueblo Mágico con un SuperAnfitrión de 8 años — desde <strong>$600/noche</strong>, confirmación inmediata y sin comisión de Airbnb.",
        "Dónde hospedarse"),
    "escapada-romantica-malinalco": (
        "Una escapada en pareja empieza por el lugar correcto",
        "Despierten juntos en el corazón de Malinalco, a pasos de todo. Desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "Escapada romántica"),
    "festival-cultural-malinalco": (
        "El hospedaje será lo primero en agotarse",
        "Se esperan 25–40 mil visitantes el fin de semana del festival. Asegura tu lugar en el centro, a pasos de las sedes — desde <strong>$600/noche</strong>, reserva directa.",
        "Festival Cultural"),
    "fiesta-divino-salvador": (
        "El 6 de agosto Malinalco se llena",
        "Vive la fiesta desde el centro, a pasos de la pólvora y la danza. Reserva con anticipación — desde <strong>$600/noche</strong>, directo y sin comisión de Airbnb.",
        "Fiesta del 6 de agosto"),
    "fin-de-semana-malinalco-cdmx": (
        "A 70 km de CDMX, tu fin de semana empieza aquí",
        "Escápate del ruido y despierta en el Pueblo Mágico. Hospédate directo, desde <strong>$600/noche</strong> y sin comisión de Airbnb.",
        "Fin de semana desde CDMX"),
    "guardianes-del-cerro": (
        "La energía del valle se siente más de noche",
        "Quédate a dormir y vive el Malinalco que los visitantes de paso nunca conocen. Desde <strong>$600/noche</strong>, reserva directa.",
        "Los guardianes del cerro"),
    "guerreros-aguila-jaguar": (
        "Camina donde se forjó la élite azteca",
        "Los guerreros se iniciaban en el Cerro de los Ídolos. Nuestras propiedades están a 5 minutos caminando — hospédate en el corazón del Pueblo Mágico, desde <strong>$600/noche</strong> y reserva directa.",
        "Guerreros Águila y Jaguar"),
    "judea-malinalco-semana-santa": (
        "Semana Santa en Malinalco se vive mejor desde adentro",
        "Hospédate en el centro para no perderte la Judea, los caballos y el fuego. Reserva con anticipación — desde <strong>$600/noche</strong>, directo.",
        "La Judea / Semana Santa"),
    "malinalco-con-familia": (
        "Unas vacaciones en familia empiezan por el lugar correcto",
        "Espacio, cocina equipada y ubicación a pasos de todo para los peques. Desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "Malinalco con familia"),
    "malinalco-pueblo-magico-historia": (
        "¿Te enamoró la historia de Malinalco?",
        "Vívela en persona: hospédate en el corazón del Pueblo Mágico, a pasos de la zona arqueológica. Desde <strong>$600/noche</strong>, reserva directa.",
        "Historia del Pueblo Mágico"),
    "malinalxochitl-leyenda": (
        "¿Te atrapó la historia de la hechicera?",
        "Malinalxóchitl eligió este valle por su magia. Puedes sentir esa misma energía quedándote a pasos de donde fundó su reino — desde <strong>$600/noche</strong>, reserva directa y sin comisión de Airbnb.",
        "Leyenda de Malinalxóchitl"),
    "navidad-posadas-malinalco": (
        "Diciembre en Malinalco se agota pronto",
        "Vive las posadas, el ponche y la nochebuena en el Pueblo Mágico. Asegura tu lugar — desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "Navidad y posadas"),
    "pesca-trucha-mezcal-malinalco": (
        "Pesca, mezcal… y una buena cama cerca",
        "Hospédate en el centro y combina aventura y descanso sin manejar de más. Desde <strong>$600/noche</strong>, reserva directa.",
        "Pesca de trucha y mezcal"),
    "ruta-5-dias-malinalco": (
        "Haz de Malinalco tu base de operaciones",
        "Explora los pueblos mágicos del sur con una base cómoda en el centro. Desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "Ruta 5 días"),
    "subida-cerro-idolos": (
        "Sube al Cerro de los Ídolos descansado",
        "Hospédate a 5 minutos del acceso y arranca la subida temprano, sin traslados. Desde <strong>$600/noche</strong>, reserva directa.",
        "Subida al Cerro de los Ídolos"),
    "suenos-en-malinalco": (
        "¿Y si el próximo sueño intenso es el tuyo?",
        "Hay algo en el aire de Malinalco que solo sientes durmiendo aquí. Quédate y compruébalo — desde <strong>$600/noche</strong>, reserva directa sin comisión de Airbnb.",
        "Sueños en Malinalco"),
}


def build_bloque(hook: str, copy: str, label: str) -> str:
    wa_text = WA_TEMPLATE % label
    wa_link = "https://wa.me/%s?text=%s" % (WA_NUM, urllib.parse.quote(wa_text))
    return (
        INICIO + "\n"
        '    <aside style="margin:2.4rem 0;padding:1.5rem 1.6rem;'
        'background:linear-gradient(135deg,#F4EEE3 0%,#ECE3D3 100%);'
        'border-left:5px solid #8B5E3C;border-radius:14px;'
        "font-family:'Inter',system-ui,sans-serif\">\n"
        '      <p style="margin:0 0 .35rem;font-family:\'Fraunces\',serif;'
        "font-size:1.18rem;font-weight:600;color:#2E4E44;line-height:1.3\">"
        + hook + "</p>\n"
        '      <p style="margin:0 0 1.1rem;font-size:.95rem;line-height:1.55;'
        'color:#3a3630">' + copy + "</p>\n"
        '      <a href="' + wa_link + '" target="_blank" rel="noopener" '
        'style="display:inline-flex;align-items:center;gap:.5rem;'
        'background:#25D366;color:#fff;text-decoration:none;'
        'padding:.8rem 1.6rem;border-radius:50px;font-size:.95rem;'
        'font-weight:700;box-shadow:0 5px 15px rgba(37,211,102,.3)">'
        '<i class="fa-brands fa-whatsapp ico"></i> '
        "Ver disponibilidad por WhatsApp</a>\n"
        "    </aside>\n"
        "    " + FIN
    )


def procesar(slug: str, hook: str, copy: str, label: str) -> str:
    path = os.path.join(BLOG_DIR, slug, "index.html")
    if not os.path.isfile(path):
        return "SKIP (no existe)"
    html = open(path, encoding="utf-8").read()

    # Idempotencia: elimina cualquier bloque previo (con el espaciado que lo rodea)
    html = re.sub(
        r"\n*[ \t]*" + re.escape(INICIO) + r".*?" + re.escape(FIN) + r"\n*",
        "\n",
        html,
        flags=re.S,
    )

    if "</article>" not in html:
        return "SKIP (sin </article>)"

    bloque = build_bloque(hook, copy, label)
    # Inserta antes del PRIMER cierre de artículo (el cuerpo principal)
    html = html.replace("</article>", bloque + "\n  </article>", 1)

    open(path, "w", encoding="utf-8").write(html)
    return "OK"


def main() -> int:
    if not os.path.isdir(BLOG_DIR):
        print("ERROR: ejecuta desde la raíz del repo (no existe ./blog)")
        return 1
    ok = 0
    for slug in sorted(DATA):
        res = procesar(slug, *DATA[slug])
        print("  %-34s %s" % (slug, res))
        if res == "OK":
            ok += 1
    print("\n%d/%d artículos con CTA-puente." % (ok, len(DATA)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
