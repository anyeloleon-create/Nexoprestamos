"""
pf_Algoritmos
Proyecto: NexoPréstamos — Gestor Inteligente de Préstamos
Módulo: documentos — Generación de certificados y facturas
Autores: Anyelo León León / Andres Felipe Barbas Cuavas
Curso: Algoritmia y Programación — Universidad de Antioquia 2026-1
"""

import os
import datetime

from clsUsuarios import clsUsuarios
from clsPrestamo import clsItem, clsPrestamo, IMPUESTO_CONCHUDEZ

_DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "documentos")


def _asegurar_dir():
    """pf_Algoritmos — Crea la carpeta de documentos si no existe."""
    os.makedirs(_DOC_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
#  Certificado de Devolución
# ═══════════════════════════════════════════════════════════════════

def generar_certificado_devolucion(
        usuario: clsUsuarios,
        item: clsItem,
        prestamo: clsPrestamo,
        fecha_devolucion: str) -> str:
    """
    pf_Algoritmos
    Genera un certificado de devolución en texto plano.
    Nombre del archivo: <NombreUsuario>_<FechaDevolucion>_<ItemID>.txt
    Retorna la ruta del archivo generado.
    """
    _asegurar_dir()
    nombre_archivo = (
        f"{usuario.nombre}_{usuario.apellido}_{fecha_devolucion}_{item.item_id}.txt"
    ).replace(" ", "_")
    ruta = os.path.join(_DOC_DIR, nombre_archivo)

    dias = prestamo.dias_transcurridos()
    linea = "═" * 58

    contenido = f"""
{linea}
          NEXOPRÉSTAMOS — CERTIFICADO DE DEVOLUCIÓN
{linea}

  Fecha de emisión   : {datetime.date.today().isoformat()}
  Número de préstamo : {prestamo.prestamo_id}

  DATOS DEL PRESTADOR
  ─────────────────────────────────────────────────────
  Nombre completo    : {usuario.nombre} {usuario.apellido}
  Documento          : {usuario.documento}
  Correo             : {usuario.correo}

  DATOS DEL ARTÍCULO
  ─────────────────────────────────────────────────────
  ID del artículo    : {item.item_id}
  Nombre             : {item.nombre}
  Categoría          : {item.categoria}
  Estado al préstamo : {item.estado} ({item.puntaje_estado}/10)
  Precio de adquisic.: ${item.precio:,.2f} COP

  DATOS DEL PRÉSTAMO
  ─────────────────────────────────────────────────────
  Fecha de préstamo  : {prestamo.fecha_prestamo}
  Fecha de devolución: {fecha_devolucion}
  Días transcurridos : {dias} días
  Plazo acordado     : {usuario.tiempo_prestamo} días

  RESULTADO
  ─────────────────────────────────────────────────────
  ✅ Artículo devuelto ANTES del vencimiento.
     No se genera cobro adicional.

{linea}
  Este certificado valida que el artículo fue devuelto
  en conformidad y que el préstamo queda cerrado.
{linea}

  Firma del prestador: _______________________________
  Firma de quien devuelve: ___________________________
"""

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)

    # Intentar generar PDF adicional (bonificación)
    _intentar_pdf(ruta, contenido)

    return ruta


# ═══════════════════════════════════════════════════════════════════
#  Factura de Venta
# ═══════════════════════════════════════════════════════════════════

def generar_factura_venta(
        usuario: clsUsuarios,
        items_prestados: list[tuple[clsItem, clsPrestamo]]) -> str:
    """
    pf_Algoritmos
    Genera una factura de venta para ítems con más de 30 días prestados.
    Aplica impuesto por conchudez del 23%.
    Nombre del archivo: <NombreUsuario>_factura_<Documento>.txt
    Retorna la ruta del archivo generado.
    """
    _asegurar_dir()
    fecha_hoy = datetime.date.today().isoformat()
    nombre_archivo = (
        f"{usuario.nombre}_{usuario.apellido}_factura_{usuario.documento}.txt"
    ).replace(" ", "_")
    ruta = os.path.join(_DOC_DIR, nombre_archivo)

    subtotal = sum(i.precio for i, _ in items_prestados)
    impuesto = subtotal * IMPUESTO_CONCHUDEZ
    total    = subtotal + impuesto
    linea    = "═" * 58

    detalle_items = ""
    for idx, (item, prestamo) in enumerate(items_prestados, 1):
        dias = prestamo.dias_transcurridos()
        detalle_items += (
            f"  {idx}. [{item.item_id}] {item.nombre}\n"
            f"     Categoría: {item.categoria} | Estado: {item.estado}\n"
            f"     Días prestado: {dias} | Precio: ${item.precio:,.2f} COP\n\n"
        )

    contenido = f"""
{linea}
             NEXOPRÉSTAMOS — FACTURA DE VENTA
{linea}

  Fecha de emisión   : {fecha_hoy}
  Factura N°         : FACT-{usuario.documento}-{fecha_hoy.replace('-','')}

  MOTIVACIÓN DE LA VENTA
  ─────────────────────────────────────────────────────
  Los artículos detallados a continuación llevan más de
  30 días en préstamo. Conforme al acuerdo celebrado
  entre las partes, al superar el plazo de un (1) mes,
  el prestatario está obligado a adquirir el artículo
  al precio de adquisición original. Se aplica además
  un impuesto especial por incumplimiento del plazo.

  DATOS DEL COMPRADOR
  ─────────────────────────────────────────────────────
  Nombre completo    : {usuario.nombre} {usuario.apellido}
  Documento          : {usuario.documento}
  Correo             : {usuario.correo}

  DETALLE DE ARTÍCULOS
  ─────────────────────────────────────────────────────
{detalle_items}
  RESUMEN FINANCIERO
  ─────────────────────────────────────────────────────
  Subtotal                      : ${subtotal:>12,.2f} COP
  Impuesto por conchudez (23 %) : ${impuesto:>12,.2f} COP
  ──────────────────────────────────────────────────
  TOTAL A PAGAR                 : ${total:>12,.2f} COP

{linea}
  Esta factura constituye documento soporte de la venta
  forzosa por incumplimiento del plazo acordado.
{linea}

  Firma del vendedor: ________________________________
  Firma del comprador: _______________________________
"""

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)

    # Intentar generar PDF adicional (bonificación)
    _intentar_pdf(ruta, contenido)

    return ruta


# ═══════════════════════════════════════════════════════════════════
#  Generación PDF (Bonificación)
# ═══════════════════════════════════════════════════════════════════

def _intentar_pdf(ruta_txt: str, contenido: str):
    """
    pf_Algoritmos
    Intenta generar una versión PDF del documento usando fpdf2.
    Si la librería no está instalada, el error se ignora silenciosamente.
    La función genera el PDF con el mismo nombre que el .txt pero extensión .pdf.
    """
    try:
        from fpdf import FPDF

        ruta_pdf = ruta_txt.replace(".txt", ".pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=9)

        for linea in contenido.split("\n"):
            # Reemplazar caracteres especiales no soportados por latin-1
            linea_safe = linea.encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 5, linea_safe, ln=True)

        pdf.output(ruta_pdf)
    except Exception:
        # Si fpdf2 no está instalado, simplemente no se genera el PDF
        pass
