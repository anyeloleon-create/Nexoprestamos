"""
pf_Algoritmos
Proyecto: NexoPréstamos — Gestor Inteligente de Préstamos
Módulo: administrador — Panel de administración con autenticación y reportes
Autores: Anyelo León León / Andres Felipe Barbas Cuavas
Curso: Algoritmia y Programación — Universidad de Antioquia 2026-1
"""

import os
from clsUsuarios import cargar_usuarios
from clsPrestamo  import (cargar_prestamos, cargar_items, DIAS_VENTA,
                           exportar_prestamos_csv, exportar_items_csv)

# ─────────────────────────────────────────────
#  Credenciales de administrador (archivo plano)
# ─────────────────────────────────────────────
_BASE          = os.path.join(os.path.dirname(__file__), "..", "data")
ARCHIVO_ADMINS = os.path.join(_BASE, "admins.txt")
_EXPORT_DIR    = os.path.join(_BASE, "exportaciones")

# Credenciales por defecto (se crean si el archivo no existe)
_CREDENCIALES_DEFAULT = [
    ("admin", "nexo2026"),
    ("profesor", "udea1234"),
]


def _asegurar_admins():
    """pf_Algoritmos — Crea el archivo de administradores si no existe."""
    os.makedirs(_BASE, exist_ok=True)
    if not os.path.exists(ARCHIVO_ADMINS):
        with open(ARCHIVO_ADMINS, "w", encoding="utf-8") as f:
            for usuario, clave in _CREDENCIALES_DEFAULT:
                f.write(f"{usuario}|{clave}\n")


def _cargar_admins() -> dict:
    """pf_Algoritmos — Carga credenciales de admin desde archivo plano."""
    _asegurar_admins()
    creds = {}
    with open(ARCHIVO_ADMINS, "r", encoding="utf-8") as f:
        for linea in f:
            if "|" in linea:
                u, c = linea.strip().split("|", 1)
                creds[u] = c
    return creds


def autenticar_admin(usuario: str, clave: str) -> bool:
    """
    pf_Algoritmos
    Verifica si las credenciales corresponden a un administrador registrado.
    Retorna True si son correctas, False en caso contrario.
    """
    creds = _cargar_admins()
    return creds.get(usuario) == clave


# ═══════════════════════════════════════════════════════════════════
#  Reportes de Administración
# ═══════════════════════════════════════════════════════════════════

def reporte_total_prestamos():
    """pf_Algoritmos — Muestra el total de préstamos registrados."""
    prestamos = cargar_prestamos()
    print(f"\n  📊 Total de préstamos registrados : {len(prestamos)}")
    activos  = sum(1 for p in prestamos if p.activo)
    cerrados = len(prestamos) - activos
    print(f"     ├─ Activos   : {activos}")
    print(f"     └─ Cerrados  : {cerrados}")


def reporte_items_devueltos():
    """pf_Algoritmos — Muestra el total de ítems devueltos."""
    prestamos = cargar_prestamos()
    devueltos = [p for p in prestamos if not p.activo]
    print(f"\n  📦 Total de ítems devueltos : {len(devueltos)}")


def reporte_ventas():
    """
    pf_Algoritmos
    Muestra los préstamos que generaron o deberían generar factura de venta
    (más de 30 días de préstamo activo).
    """
    prestamos = cargar_prestamos()
    items_map = {i.item_id: i for i in cargar_items()}
    ventas = [p for p in prestamos if p.dias_transcurridos() > DIAS_VENTA]

    print(f"\n  💰 Total de ventas realizadas (>30 días) : {len(ventas)}")
    total_pago = 0.0
    for p in ventas:
        item = items_map.get(p.item_id)
        if item:
            total_pago += item.precio * (1 + 0.23)
            print(f"     • {p.prestamo_id} | Ítem: {item.nombre} | "
                  f"Usuario: {p.documento_usuario} | Días: {p.dias_transcurridos()}")
    print(f"\n  💵 Total pago estimado (con impuesto 23%) : ${total_pago:,.2f} COP")


def reporte_lista_usuarios():
    """pf_Algoritmos — Lista todos los usuarios registrados."""
    usuarios = cargar_usuarios()
    print(f"\n  👥 Lista de usuarios registrados ({len(usuarios)}):")
    print("  " + "─" * 55)
    for u in usuarios:
        print(f"  {u}")
    if not usuarios:
        print("  (Sin usuarios registrados)")


def reporte_extremos_prestamos():
    """
    pf_Algoritmos
    Muestra el usuario con mayor y menor cantidad de préstamos registrados.
    """
    prestamos  = cargar_prestamos()
    conteo: dict[str, int] = {}
    for p in prestamos:
        conteo[p.documento_usuario] = conteo.get(p.documento_usuario, 0) + 1

    if not conteo:
        print("\n  ⚠️  Sin datos de préstamos para calcular extremos.")
        return

    usuarios_map = {u.documento: u for u in cargar_usuarios()}
    max_doc = max(conteo, key=conteo.get)
    min_doc = min(conteo, key=conteo.get)

    u_max = usuarios_map.get(max_doc)
    u_min = usuarios_map.get(min_doc)
    nombre_max = f"{u_max.nombre} {u_max.apellido}" if u_max else max_doc
    nombre_min = f"{u_min.nombre} {u_min.apellido}" if u_min else min_doc

    print(f"\n  📈 Mayor cantidad de préstamos : {nombre_max} ({conteo[max_doc]} préstamos)")
    print(f"  📉 Menor cantidad de préstamos : {nombre_min} ({conteo[min_doc]} préstamos)")


def exportar_todo_csv():
    """pf_Algoritmos — Exporta toda la información a CSV."""
    os.makedirs(_EXPORT_DIR, exist_ok=True)
    ruta_p = os.path.join(_EXPORT_DIR, "prestamos_export.csv")
    ruta_i = os.path.join(_EXPORT_DIR, "items_export.csv")

    exportar_prestamos_csv(ruta_p)
    exportar_items_csv(ruta_i)
    print(f"\n  ✅ Exportación completada:")
    print(f"     • Préstamos → {ruta_p}")
    print(f"     • Ítems     → {ruta_i}")


# ═══════════════════════════════════════════════════════════════════
#  Menú interactivo de administración
# ═══════════════════════════════════════════════════════════════════

def menu_administrador():
    """
    pf_Algoritmos
    Menú completo del módulo administrador.
    Requiere autenticación previa antes de mostrar las opciones.
    """
    print("\n" + "─" * 50)
    print("  🔐  ACCESO AL PANEL DE ADMINISTRADOR")
    print("─" * 50)

    intentos = 0
    while intentos < 3:
        usuario = input("  Usuario: ").strip()
        clave   = input("  Contraseña: ").strip()
        if autenticar_admin(usuario, clave):
            print("  ✅ Acceso concedido.\n")
            break
        intentos += 1
        print(f"  ❌ Credenciales incorrectas. Intentos restantes: {3 - intentos}")
    else:
        print("  🚫 Demasiados intentos fallidos. Acceso bloqueado.")
        return

    while True:
        print("\n" + "─" * 50)
        print("  ⚙️   PANEL DE ADMINISTRACIÓN — NexoPréstamos")
        print("─" * 50)
        print("  1. Total de préstamos registrados")
        print("  2. Total de ítems devueltos")
        print("  3. Total de ventas realizadas y pago estimado")
        print("  4. Lista de usuarios")
        print("  5. Usuario con mayor/menor cantidad de préstamos")
        print("  6. Exportar datos a CSV")
        print("  0. Volver al menú principal")
        print("─" * 50)

        opcion = input("  Selecciona una opción: ").strip()

        if opcion == "1":
            reporte_total_prestamos()
        elif opcion == "2":
            reporte_items_devueltos()
        elif opcion == "3":
            reporte_ventas()
        elif opcion == "4":
            reporte_lista_usuarios()
        elif opcion == "5":
            reporte_extremos_prestamos()
        elif opcion == "6":
            exportar_todo_csv()
        elif opcion == "0":
            break
        else:
            print("  ⚠️  Opción no válida.")

        input("\n  Presiona ENTER para continuar...")
