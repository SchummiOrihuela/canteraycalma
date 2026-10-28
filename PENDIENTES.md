# Pendientes — Cantera & Calma

Lista de mejoras acordadas. Se va actualizando conforme se completan.

---

## ✅ Optimizar imágenes principales → WebP (hecho · 2026-10-28)

Se optimizaron la imagen del hero y las de propiedades a WebP con fallback
JPG, priorizando el peso en celular (el grueso del tráfico).

**Hero (LCP):** `images/malinalco/ZonaArqueologica` → WebP responsive vía
`image-set()` en el CSS del hero, con variante móvil dedicada de 800 px y
preload responsive. El JPG principal se recomprimió a 1366 px (lo heredan las
~24 referencias: blog cards, `og:image`, related).

| Variante | Antes | Ahora |
|----------|------:|------:|
| Hero móvil (800 px) | 457 KB | 116 KB WebP |
| Hero desktop (1366 px) | 457 KB | 276 KB WebP |

**Propiedades:** WebP + `<picture>` en las tarjetas del home; JPG recomprimido
en sitio (raíz + `images/propiedades/`) para el resto de referencias y `og:image`.

| Imagen | Antes | JPG ahora | WebP |
|--------|------:|----------:|-----:|
| casa-marne13 | 450 KB | 221 KB | 201 KB |
| depa-cantera | 295 KB | 203 KB | 152 KB |
| depa-calma | 133 KB | 133 KB* | 105 KB |
| habitacion-magia | 117 KB | 74 KB | 37 KB |

\* `depa-calma` ya venía bien comprimida; se dejó el JPG original y se sirve
WebP en la tarjeta del home.

---

## ⏳ Opcional — imágenes del blog (`blog/**/*.jpg`)

Mismo tratamiento (WebP + recompresión) para las imágenes dentro de los
artículos y la foto del host (`schummi-host.jpg`). Menor prioridad: son
`loading="lazy"` y no afectan el LCP de las páginas principales.
