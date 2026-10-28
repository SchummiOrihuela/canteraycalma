# Pendientes — Cantera & Calma

Lista de mejoras acordadas que quedaron pendientes para una sesión futura.

---

## 🖼️ Optimizar imágenes (hero + propiedades) → WebP

**Objetivo:** reducir el peso de las imágenes para acelerar la descarga (sobre
todo en 4G/celular) sin perder calidad visual. Complementa el `preload` del
hero que ya se implementó.

**Qué hacer:**
- Generar versión **WebP** (calidad ~80) de cada imagen y servirla como formato
  principal, dejando el `.jpeg/.jpg` como respaldo (`<picture>` con `<source
  type="image/webp">`), o reemplazar directamente si todo el stack lo soporta.
- Redimensionar a un ancho máximo razonable para su uso real (p. ej. tarjetas
  ~800–1000 px de ancho; hero ~1920 px).
- Mantener el `fetchpriority="high"` y el `preload` del hero apuntando al nuevo
  archivo.

**Inventario y pesos actuales (al 2026-10-28):**

| Imagen | Ruta | Peso actual | Meta aprox. |
|--------|------|------------:|------------:|
| Hero (LCP) | `images/malinalco/ZonaArqueologica.jpg` | ~460 KB | 80–120 KB |
| Casa Marne 13 | `images/propiedades/casa-marne13.jpeg` | ~452 KB | 60–90 KB |
| Depto Cantera | `images/propiedades/depa-cantera.jpeg` | ~296 KB | 60–90 KB |
| Depto Calma | `images/propiedades/depa-calma.jpeg` | ~136 KB | 40–70 KB |
| Habitación Magia | `images/propiedades/habitacion-magia.jpeg` | ~120 KB | 40–70 KB |

**Opcional (mismo trabajo):** optimizar también las imágenes del blog
(`blog/**/*.jpg`) y la foto del host (`images/host/schummi-host.jpg`).

**Nota:** requiere procesar las imágenes (no es solo HTML), por eso se dejó
para una sesión dedicada.
