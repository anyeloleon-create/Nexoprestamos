"""
pf_Algoritmos
Proyecto: NexoPréstamos — Gestor Inteligente de Préstamos
Módulo: main — Punto de entrada, menú principal de consola
Autores: Anyelo León León / Andres Felipe Barbas Cuavas
Curso: Algoritmia y Programación — Universidad de Antioquia 2026-1
"""

import os
import sys
import datetime

# Asegurar que los módulos locales sean encontrados
sys.path.insert(0, os.path.dirname(__file__))

from clsUsuarios import (registrar_usuario_interactivo, cargar_usuarios,
                          buscar_usuario_por_documento, exportar_usuarios_csv)
from clsPrestamo  import (clsItem, clsPrestamo, cargar_items, agregar_item,
                           generar_id_item, cargar_prestamos, agregar_prestamo,
                           guardar_prestamos, actualizar_disponibilidad_item,
                           prestamos_activos_por_usuario, buscar_prestamo_activo_por_item,
                           generar_id_prestamo, CATEGORIAS, DIAS_ALERTA, DIAS_VENTA,
                           membresia_difusa)
from documentos   import generar_certificado_devolucion, generar_factura_venta
from administrador import menu_administrador


# ═══════════════════════════════════════════════════════════════════
#  Pantalla de Inicio (Arte ASCII)
# ═══════════════════════════════════════════════════════════════════

BANNER = r"""
  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║    ███╗   ██╗███████╗██╗  ██╗ ██████╗                   ║
  ║    ████╗  ██║██╔════╝╚██╗██╔╝██╔═══██╗                  ║
  ║    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║                  ║
  ║    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║                  ║
  ║    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝                  ║
  ║    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝                  ║
  ║                                                          ║
  ║    P R É S T A M O S   —   Gestor Inteligente            ║
  ║    Universidad de Antioquia · 2026-1                     ║
  ╚══════════════════════════════════════════════════════════╝
"""


def limpiar():
    """pf_Algoritmos — Limpia la pantalla de la consola."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    """pf_Algoritmos — Pausa hasta que el usuario presione ENTER."""
    input("\n  Presiona ENTER para continuar...")


def menu_principal():
    """
    pf_Algoritmos
    Muestra el menú principal del sistema NexoPréstamos
    y gestiona la navegación entre opciones.
    """
    while True:
        limpiar()
        print(BANNER)
        print("  ─────────────────────────────────────────────────────────")
        print("  Bienvenido a NexoPréstamos")
        print("  ─────────────────────────────────────────────────────────")
        print("    1. Registrar Usuario")
        print("    2. Registrar Ítem")
        print("    3. Registrar Préstamo")
        print("    4. Registrar Devolución")
        print("    5. Consultar Ítems con más de 30 días (Generar Venta)")
        print("    6. Consultar Artículos Prestados")
        print("    7. Administrador")
        print("    0. Salir")
        print("  ─────────────────────────────────────────────────────────")

        opcion = input("  Selecciona una opción: ").strip()

        if opcion == "1":
            limpiar()
            registrar_usuario_interactivo()
            pausar()

        elif opcion == "2":
            limpiar()
            registrar_item_interactivo()
            pausar()

        elif opcion == "3":
            limpiar()
            registrar_prestamo_interactivo()
            pausar()

        elif opcion == "4":
            limpiar()
            registrar_devolucion_interactivo()
            pausar()

        elif opcion == "5":
            limpiar()
            consultar_items_vencidos()
            pausar()

        elif opcion == "6":
            limpiar()
            consultar_articulos_prestados()
            pausar()

        elif opcion == "7":
            limpiar()
            menu_administrador()

        elif opcion == "0":
            limpiar()
            print("\n  👋 Hasta pronto. Gracias por usar NexoPréstamos.\n")
            sys.exit(0)

        else:
            print("  ⚠️  Opción no válida. Intenta de nuevo.")
            pausar()


# ═══════════════════════════════════════════════════════════════════
#  Registrar Ítem
# ═══════════════════════════════════════════════════════════════════

def registrar_item_interactivo():
    """
    pf_Algoritmos
    Flujo interactivo para registrar un nuevo ítem en el inventario.
    Incluye selección de categoría, validaciones y lógica difusa de estado.
    """
    print("\n" + "─" * 50)
    print("  📦  REGISTRAR NUEVO ÍTEM")
    print("─" * 50)

    # ── Nombre ──────────────────────────────────────────────────────
    while True:
        nombre = input("  Nombre del artículo: ").strip()
        if len(nombre) < 3:
            print("  ❌ El nombre debe tener al menos 3 caracteres.")
        else:
            break

    # ── Categoría ───────────────────────────────────────────────────
    print("\n  Categorías disponibles:")
    for clave, (nombre_cat, prefijo) in CATEGORIAS.items():
        print(f"    {clave}. {nombre_cat} (ID prefix: {prefijo})")
    while True:
        cat_clave = input("  Selecciona categoría (1-6): ").strip()
        if cat_clave in CATEGORIAS:
            categoria = CATEGORIAS[cat_clave][0]
            break
        print("  ❌ Opción inválida.")

    # ── Precio ──────────────────────────────────────────────────────
    while True:
        precio_str = input("  Precio de adquisición ($): ").strip()
        try:
            precio = float(precio_str.replace(",", "").replace(".", "").replace("$", ""))
            if precio < 0:
                raise ValueError
            break
        except ValueError:
            print("  ❌ Ingresa un precio válido (solo números).")

    # ── Estado difuso ───────────────────────────────────────────────
    print("\n  Estado del artículo (Lógica Difusa)")
    print("  Ingresa un puntaje del 0 al 10:")
    print("    0-2.9 → Malo | 3-4.9 → Deteriorado | 5-6.9 → Regular")
    print("    7-8.9 → Bueno | 9-10 → Excelente")
    while True:
        try:
            puntaje = float(input("  Puntaje de estado (0-10): ").strip())
            if 0 <= puntaje <= 10:
                break
            print("  ❌ El puntaje debe estar entre 0 y 10.")
        except ValueError:
            print("  ❌ Ingresa un número válido.")

    # Mostrar membresía difusa
    memb = membresia_difusa(puntaje)
    print(f"\n  📊 Análisis difuso del estado:")
    for estado, grado in sorted(memb.items(), key=lambda x: -x[1]):
        barra = "█" * int(grado * 20)
        print(f"     {estado:<12} [{barra:<20}] {grado:.2f}")

    # ── Generar ID ──────────────────────────────────────────────────
    item_id = generar_id_item(cat_clave)
    print(f"\n  🔑 ID asignado automáticamente: {item_id}")

    # ── Crear y guardar ─────────────────────────────────────────────
    item = clsItem(nombre, categoria, precio, item_id, puntaje)
    if agregar_item(item):
        print(f"\n  ✅ Ítem registrado exitosamente:")
        print(f"  {item}")
    else:
        print(f"\n  ⚠️  Ya existe un ítem con ID {item_id}.")


# ═══════════════════════════════════════════════════════════════════
#  Registrar Préstamo
# ═══════════════════════════════════════════════════════════════════

def registrar_prestamo_interactivo():
    """
    pf_Algoritmos
    Flujo interactivo para registrar un nuevo préstamo.
    Valida que tanto el usuario como el ítem existan y estén disponibles.
    """
    print("\n" + "─" * 50)
    print("  🤝  REGISTRAR NUEVO PRÉSTAMO")
    print("─" * 50)

    # ── Verificar que haya ítems disponibles ────────────────────────
    items_disponibles = [i for i in cargar_items() if i.disponible]
    if not items_disponibles:
        print("\n  ⚠️  No hay artículos disponibles en el inventario.")
        return

    # ── Mostrar inventario disponible ───────────────────────────────
    print("\n  📋 Inventario disponible:")
    print("  " + "─" * 55)
    for item in items_disponibles:
        print(f"  {item}")
    print("  " + "─" * 55)

    # ── Seleccionar ítem por ID ─────────────────────────────────────
    ids_disponibles = {i.item_id for i in items_disponibles}
    while True:
        item_id = input("\n  Ingresa el ID del artículo a prestar: ").strip().upper()
        if item_id in ids_disponibles:
            item_sel = next(i for i in items_disponibles if i.item_id == item_id)
            break
        print(f"  ❌ ID '{item_id}' no encontrado o no disponible.")

    # ── Seleccionar usuario por documento ───────────────────────────
    while True:
        doc = input("  Documento del usuario prestatario: ").strip()
        usuario = buscar_usuario_por_documento(doc)
        if usuario:
            print(f"  ✅ Usuario encontrado: {usuario.nombre} {usuario.apellido}")
            break
        else:
            print(f"  ❌ No existe un usuario con documento {doc}.")
            print("     Debes registrar primero al usuario (opción 1 del menú).")
            reintentar = input("  ¿Deseas intentar con otro documento? (s/n): ").strip().lower()
            if reintentar != "s":
                return

    # ── Confirmar préstamo ──────────────────────────────────────────
    fecha_hoy = datetime.date.today().isoformat()
    prestamo_id = generar_id_prestamo()

    print(f"\n  📝 Resumen del préstamo:")
    print(f"     ID préstamo : {prestamo_id}")
    print(f"     Artículo    : {item_sel.nombre} [{item_sel.item_id}]")
    print(f"     Prestatario : {usuario.nombre} {usuario.apellido}")
    print(f"     Fecha inicio: {fecha_hoy}")
    print(f"     Plazo máximo: {usuario.tiempo_prestamo} días")

    confirmar = input("\n  ¿Confirmar préstamo? (s/n): ").strip().lower()
    if confirmar != "s":
        print("  ⚠️  Préstamo cancelado.")
        return

    prestamo = clsPrestamo(prestamo_id, usuario.documento, item_sel.item_id, fecha_hoy)
    agregar_prestamo(prestamo)
    actualizar_disponibilidad_item(item_sel.item_id, False)

    print(f"\n  ✅ Préstamo registrado exitosamente: {prestamo}")


# ═══════════════════════════════════════════════════════════════════
#  Registrar Devolución
# ═══════════════════════════════════════════════════════════════════

def registrar_devolucion_interactivo():
    """
    pf_Algoritmos
    Flujo interactivo para registrar la devolución de un ítem prestado.
    Genera certificado de devolución o factura según los días transcurridos.
    """
    print("\n" + "─" * 50)
    print("  🔄  REGISTRAR DEVOLUCIÓN")
    print("─" * 50)

    doc = input("  Documento del usuario: ").strip()
    usuario = buscar_usuario_por_documento(doc)

    if not usuario:
        print(f"  ❌ No existe un usuario con documento {doc}.")
        return

    prestamos_activos = prestamos_activos_por_usuario(doc)

    if not prestamos_activos:
        print(f"  ⚠️  {usuario.nombre} {usuario.apellido} no tiene préstamos activos.")
        return

    # ── Mostrar préstamos activos del usuario ───────────────────────
    items_map = {i.item_id: i for i in cargar_items()}
    print(f"\n  Préstamos activos de {usuario.nombre} {usuario.apellido}:")
    print("  " + "─" * 55)
    for p in prestamos_activos:
        item = items_map.get(p.item_id)
        nombre_item = item.nombre if item else "N/A"
        print(f"  {p}  |  Artículo: {nombre_item}")
    print("  " + "─" * 55)

    # ── Seleccionar préstamo a devolver ─────────────────────────────
    ids_prestamos = {p.prestamo_id for p in prestamos_activos}
    while True:
        pid = input("\n  ID del préstamo a devolver: ").strip().upper()
        if pid in ids_prestamos:
            prestamo_sel = next(p for p in prestamos_activos if p.prestamo_id == pid)
            break
        print(f"  ❌ ID '{pid}' no válido.")

    item_sel = items_map.get(prestamo_sel.item_id)
    dias = prestamo_sel.dias_transcurridos()
    fecha_hoy = datetime.date.today().isoformat()

    print(f"\n  📊 Estado del préstamo:")
    print(f"     Artículo         : {item_sel.nombre if item_sel else 'N/A'}")
    print(f"     Días transcurridos: {dias}")
    print(f"     Plazo del usuario : {usuario.tiempo_prestamo} días")

    # ── Alerta si supera 20 días ─────────────────────────────────────
    if dias >= DIAS_ALERTA and dias <= DIAS_VENTA:
        print(f"\n  🟡 ALERTA: Este préstamo lleva {dias} días — solicitar devolución.")

    # ── Venta forzosa si supera 30 días ──────────────────────────────
    if dias > DIAS_VENTA:
        print(f"\n  🔴 VENTA: Este artículo lleva {dias} días (>30). Se genera factura de venta.")
        confirmar = input("  ¿Confirmar venta y cierre del préstamo? (s/n): ").strip().lower()
        if confirmar != "s":
            return
        ruta = generar_factura_venta(usuario, [(item_sel, prestamo_sel)])
        print(f"\n  🧾 Factura de venta generada: {ruta}")
    else:
        confirmar = input("  ¿Confirmar devolución? (s/n): ").strip().lower()
        if confirmar != "s":
            return
        ruta = generar_certificado_devolucion(usuario, item_sel, prestamo_sel, fecha_hoy)
        print(f"\n  📄 Certificado de devolución generado: {ruta}")

    # ── Actualizar estados ───────────────────────────────────────────
    todos_prestamos = cargar_prestamos()
    for p in todos_prestamos:
        if p.prestamo_id == prestamo_sel.prestamo_id:
            p.activo = False
            p.fecha_devolucion = fecha_hoy
    guardar_prestamos(todos_prestamos)
    actualizar_disponibilidad_item(prestamo_sel.item_id, True)

    print(f"\n  ✅ Devolución registrada correctamente.")


# ═══════════════════════════════════════════════════════════════════
#  Consultar ítems con más de 30 días
# ═══════════════════════════════════════════════════════════════════

def consultar_items_vencidos():
    """
    pf_Algoritmos
    Muestra los ítems activos con más de 30 días de préstamo
    y ofrece generar la factura de venta correspondiente.
    """
    print("\n" + "─" * 50)
    print("  🔴  ÍTEMS CON MÁS DE 30 DÍAS PRESTADOS")
    print("─" * 50)

    prestamos  = cargar_prestamos()
    items_map  = {i.item_id: i for i in cargar_items()}
    usuarios_map = {u.documento: u for u in cargar_usuarios()}

    vencidos = [p for p in prestamos if p.activo and p.dias_transcurridos() > DIAS_VENTA]

    if not vencidos:
        print("\n  ✅ No hay ítems con más de 30 días de préstamo activo.")
        return

    print(f"\n  Se encontraron {len(vencidos)} préstamos vencidos:\n")
    for p in sorted(vencidos, key=lambda x: x.dias_transcurridos(), reverse=True):
        item    = items_map.get(p.item_id)
        usuario = usuarios_map.get(p.documento_usuario)
        nombre_item = item.nombre if item else "N/A"
        nombre_usu  = f"{usuario.nombre} {usuario.apellido}" if usuario else p.documento_usuario
        precio      = item.precio if item else 0
        print(f"  🔴 [{p.prestamo_id}] {nombre_item} | {nombre_usu} | "
              f"{p.dias_transcurridos()} días | ${precio:,.0f}")

    # Ofrecer generar factura
    print("\n  ¿Deseas generar una factura de venta para algún usuario?")
    doc = input("  Documento del usuario (o ENTER para omitir): ").strip()
    if not doc:
        return

    usuario = usuarios_map.get(doc)
    if not usuario:
        print(f"  ❌ Usuario con documento {doc} no encontrado.")
        return

    items_usuario = [(items_map[p.item_id], p)
                     for p in vencidos if p.documento_usuario == doc and p.item_id in items_map]

    if not items_usuario:
        print(f"  ⚠️  El usuario no tiene ítems vencidos.")
        return

    ruta = generar_factura_venta(usuario, items_usuario)
    print(f"\n  🧾 Factura generada: {ruta}")


# ═══════════════════════════════════════════════════════════════════
#  Consultar artículos prestados
# ═══════════════════════════════════════════════════════════════════

def consultar_articulos_prestados():
    """
    pf_Algoritmos
    Muestra todos los ítems actualmente prestados ordenados por días
    (de mayor a menor). Incluye alertas de estado.
    """
    print("\n" + "─" * 50)
    print("  📋  ARTÍCULOS PRESTADOS — ESTADO GENERAL")
    print("─" * 50)

    prestamos = cargar_prestamos()
    activos   = [p for p in prestamos if p.activo]

    if not activos:
        print("\n  ✅ No hay artículos prestados actualmente.")
        return

    items_map    = {i.item_id: i for i in cargar_items()}
    usuarios_map = {u.documento: u for u in cargar_usuarios()}

    # Ordenar por días transcurridos (mayor a menor)
    activos_sorted = sorted(activos, key=lambda p: p.dias_transcurridos(), reverse=True)

    print(f"\n  Total: {len(activos_sorted)} préstamos activos\n")
    print(f"  {'#':<4} {'ID Préstamo':<10} {'Artículo':<20} {'Usuario':<20} "
          f"{'Días':>5} {'Estado':<10}")
    print("  " + "─" * 75)

    for idx, p in enumerate(activos_sorted, 1):
        item    = items_map.get(p.item_id)
        usuario = usuarios_map.get(p.documento_usuario)
        nombre_item = (item.nombre[:18] if item else "N/A")
        nombre_usu  = ((usuario.nombre + " " + usuario.apellido)[:18] if usuario
                       else p.documento_usuario)
        dias        = p.dias_transcurridos()
        alerta      = p.estado_alerta()
        simbolo = {"NORMAL": "🟢", "ALERTA": "🟡", "VENTA": "🔴"}.get(alerta, "")

        print(f"  {idx:<4} {p.prestamo_id:<10} {nombre_item:<20} {nombre_usu:<20} "
              f"{dias:>5} {simbolo} {alerta}")

    print("\n  Leyenda: 🟢 Normal  🟡 Alerta (≥20 días)  🔴 Venta (>30 días)")


# ═══════════════════════════════════════════════════════════════════
#  Punto de entrada
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    menu_principal()
