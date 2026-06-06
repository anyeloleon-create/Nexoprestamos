"""
pf_Algoritmos
Proyecto: NexoPréstamos — Gestor Inteligente de Préstamos
Módulo: clsPrestamo — Gestión de ítems y préstamos
Autores: Anyelo León León / Andres Felipe Barbas Cuavas
Curso: Algoritmia y Programación — Universidad de Antioquia 2026-1
"""

import os
import csv
import datetime

# ─────────────────────────────────────────────
#  Rutas de archivos planos
# ─────────────────────────────────────────────
_BASE = os.path.join(os.path.dirname(__file__), "..", "data")
ARCHIVO_ITEMS     = os.path.join(_BASE, "items.txt")
ARCHIVO_PRESTAMOS = os.path.join(_BASE, "prestamos.txt")

# ─────────────────────────────────────────────
#  Categorías y prefijos de ID
# ─────────────────────────────────────────────
CATEGORIAS = {
    "1": ("Videojuegos",       "VJ"),
    "2": ("Libros",            "LB"),
    "3": ("Música y video",    "MV"),
    "4": ("Herramientas",      "HT"),
    "5": ("Dinero",            "DN"),
    "6": ("Misceláneo y varios", "MS"),
}

IMPUESTO_CONCHUDEZ = 0.23   # 23 % impuesto por no devolver
DIAS_ALERTA        = 20     # días para mostrar alerta de recuperación
DIAS_VENTA         = 30     # días para generar factura de venta


# ═══════════════════════════════════════════════════════════════════
#  Lógica Difusa — Estado del ítem
# ═══════════════════════════════════════════════════════════════════

def calcular_estado_difuso(puntaje: float) -> str:
    """
    pf_Algoritmos
    Aplica lógica difusa para determinar el estado verbal del ítem
    a partir de un puntaje numérico ingresado por el usuario (0-10).

    Conjuntos difusos:
        Excelente  : puntaje >= 9.0
        Bueno      : 7.0 <= puntaje < 9.0
        Regular    : 5.0 <= puntaje < 7.0
        Deteriorado: 3.0 <= puntaje < 5.0
        Malo       : puntaje < 3.0
    """
    if puntaje >= 9.0:
        return "Excelente"
    elif puntaje >= 7.0:
        return "Bueno"
    elif puntaje >= 5.0:
        return "Regular"
    elif puntaje >= 3.0:
        return "Deteriorado"
    else:
        return "Malo"


def membresia_difusa(puntaje: float) -> dict:
    """
    pf_Algoritmos
    Calcula los grados de pertenencia difusa para cada conjunto.
    Permite mostrar al usuario qué tan cerca está de cada estado.
    """
    rangos = {
        "Malo":       max(0.0, 1 - puntaje / 3.0) if puntaje < 3 else 0.0,
        "Deteriorado": max(0.0, 1 - abs(puntaje - 4) / 2.0) if 2 <= puntaje <= 6 else 0.0,
        "Regular":    max(0.0, 1 - abs(puntaje - 6) / 2.0) if 4 <= puntaje <= 8 else 0.0,
        "Bueno":      max(0.0, 1 - abs(puntaje - 8) / 2.0) if 6 <= puntaje <= 10 else 0.0,
        "Excelente":  max(0.0, (puntaje - 8) / 2.0) if puntaje >= 8 else 0.0,
    }
    return {k: round(v, 2) for k, v in rangos.items() if v > 0}


# ═══════════════════════════════════════════════════════════════════
#  Clase clsItem — Ítem a prestar
# ═══════════════════════════════════════════════════════════════════

class clsItem:
    """
    pf_Algoritmos
    Representa un artículo registrado en el inventario de NexoPréstamos.
    """

    def __init__(self, nombre: str, categoria: str, precio: float,
                 item_id: str, puntaje_estado: float, disponible: bool = True):
        """
        pf_Algoritmos
        Constructor de clsItem.
        Parámetros:
            nombre          (str): Nombre del artículo.
            categoria       (str): Categoría del artículo (texto, ej. "Libros").
            precio          (float): Precio de adquisición.
            item_id         (str): Identificador único (ej. LB-001).
            puntaje_estado  (float): Calificación 0-10 para estado difuso.
            disponible      (bool): True si no está prestado actualmente.
        """
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.item_id = item_id
        self.puntaje_estado = puntaje_estado
        self.estado = calcular_estado_difuso(puntaje_estado)
        self.disponible = disponible

    def __str__(self):
        """pf_Algoritmos — Representación legible del ítem."""
        disp = "✅ Disponible" if self.disponible else "🔴 Prestado"
        return (f"[{self.item_id}] {self.nombre} | {self.categoria} | "
                f"${self.precio:,.0f} | Estado: {self.estado} ({self.puntaje_estado}/10) | {disp}")

    def to_csv_row(self) -> str:
        """pf_Algoritmos — Serializa el ítem como línea de archivo plano."""
        return (f"{self.nombre}|{self.categoria}|{self.precio}|"
                f"{self.item_id}|{self.puntaje_estado}|{int(self.disponible)}\n")

    @staticmethod
    def from_csv_row(linea: str) -> "clsItem":
        """pf_Algoritmos — Crea un ítem desde una línea del archivo plano."""
        p = linea.strip().split("|")
        return clsItem(p[0], p[1], float(p[2]), p[3], float(p[4]), bool(int(p[5])))


# ═══════════════════════════════════════════════════════════════════
#  Clase clsPrestamo — Préstamo activo
# ═══════════════════════════════════════════════════════════════════

class clsPrestamo:
    """
    pf_Algoritmos
    Representa un préstamo registrado en NexoPréstamos.
    Contiene la relación entre un usuario, un ítem y las fechas.
    """

    def __init__(self, prestamo_id: str, documento_usuario: str,
                 item_id: str, fecha_prestamo: str,
                 fecha_devolucion: str = "", activo: bool = True):
        """
        pf_Algoritmos
        Constructor de clsPrestamo.
        Parámetros:
            prestamo_id       (str): Identificador único del préstamo.
            documento_usuario (str): Documento del usuario prestatario.
            item_id           (str): ID del ítem prestado.
            fecha_prestamo    (str): Fecha de inicio (YYYY-MM-DD).
            fecha_devolucion  (str): Fecha de devolución, vacío si activo.
            activo            (bool): True si el préstamo sigue vigente.
        """
        self.prestamo_id = prestamo_id
        self.documento_usuario = documento_usuario
        self.item_id = item_id
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = fecha_devolucion
        self.activo = activo

    def dias_transcurridos(self) -> int:
        """
        pf_Algoritmos
        Calcula cuántos días han pasado desde el préstamo.
        Si ya fue devuelto, calcula entre fechas de préstamo y devolución.
        """
        inicio = datetime.date.fromisoformat(self.fecha_prestamo)
        if self.fecha_devolucion:
            fin = datetime.date.fromisoformat(self.fecha_devolucion)
        else:
            fin = datetime.date.today()
        return (fin - inicio).days

    def estado_alerta(self) -> str:
        """
        pf_Algoritmos
        Retorna el estado de alerta del préstamo según los días transcurridos.
        """
        dias = self.dias_transcurridos()
        if not self.activo:
            return "DEVUELTO"
        if dias > DIAS_VENTA:
            return "VENTA"
        elif dias >= DIAS_ALERTA:
            return "ALERTA"
        else:
            return "NORMAL"

    def __str__(self):
        """pf_Algoritmos — Representación del préstamo."""
        dias = self.dias_transcurridos()
        alerta = self.estado_alerta()
        simbolo = {"NORMAL": "🟢", "ALERTA": "🟡", "VENTA": "🔴", "DEVUELTO": "✅"}.get(alerta, "")
        return (f"[{self.prestamo_id}] Usuario: {self.documento_usuario} | "
                f"Ítem: {self.item_id} | Fecha: {self.fecha_prestamo} | "
                f"Días: {dias} {simbolo} {alerta}")

    def to_csv_row(self) -> str:
        """pf_Algoritmos — Serializa el préstamo como línea de archivo plano."""
        return (f"{self.prestamo_id}|{self.documento_usuario}|{self.item_id}|"
                f"{self.fecha_prestamo}|{self.fecha_devolucion}|{int(self.activo)}\n")

    @staticmethod
    def from_csv_row(linea: str) -> "clsPrestamo":
        """pf_Algoritmos — Crea un préstamo desde línea del archivo plano."""
        p = linea.strip().split("|")
        return clsPrestamo(p[0], p[1], p[2], p[3], p[4], bool(int(p[5])))


# ═══════════════════════════════════════════════════════════════════
#  Persistencia — Ítems
# ═══════════════════════════════════════════════════════════════════

def _asegurar_directorio():
    """pf_Algoritmos — Crea el directorio data si no existe."""
    os.makedirs(_BASE, exist_ok=True)


def cargar_items() -> list[clsItem]:
    """pf_Algoritmos — Carga todos los ítems desde el archivo plano."""
    _asegurar_directorio()
    items = []
    if not os.path.exists(ARCHIVO_ITEMS):
        return items
    with open(ARCHIVO_ITEMS, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                try:
                    items.append(clsItem.from_csv_row(linea))
                except Exception:
                    pass
    return items


def guardar_items(items: list[clsItem]):
    """pf_Algoritmos — Reescribe el archivo de ítems con la lista completa."""
    _asegurar_directorio()
    with open(ARCHIVO_ITEMS, "w", encoding="utf-8") as f:
        for item in items:
            f.write(item.to_csv_row())


def agregar_item(item: clsItem) -> bool:
    """
    pf_Algoritmos
    Agrega un ítem al archivo plano. Verifica que el ID no esté duplicado.
    Retorna True si se guardó, False si el ID ya existe.
    """
    items = cargar_items()
    for i in items:
        if i.item_id == item.item_id:
            return False
    items.append(item)
    guardar_items(items)
    return True


def actualizar_disponibilidad_item(item_id: str, disponible: bool):
    """pf_Algoritmos — Cambia el campo 'disponible' de un ítem."""
    items = cargar_items()
    for i in items:
        if i.item_id == item_id:
            i.disponible = disponible
    guardar_items(items)


def generar_id_item(categoria_clave: str) -> str:
    """
    pf_Algoritmos
    Genera un ID único para un ítem usando el prefijo de categoría
    y un número secuencial (ej. LB-003).
    """
    prefijo = CATEGORIAS.get(categoria_clave, ("", "XX"))[1]
    items = cargar_items()
    # Contar cuántos ítems tienen ese prefijo
    count = sum(1 for i in items if i.item_id.startswith(prefijo)) + 1
    return f"{prefijo}-{count:03d}"


# ═══════════════════════════════════════════════════════════════════
#  Persistencia — Préstamos
# ═══════════════════════════════════════════════════════════════════

def cargar_prestamos() -> list[clsPrestamo]:
    """pf_Algoritmos — Carga todos los préstamos desde el archivo plano."""
    _asegurar_directorio()
    prestamos = []
    if not os.path.exists(ARCHIVO_PRESTAMOS):
        return prestamos
    with open(ARCHIVO_PRESTAMOS, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                try:
                    prestamos.append(clsPrestamo.from_csv_row(linea))
                except Exception:
                    pass
    return prestamos


def guardar_prestamos(prestamos: list[clsPrestamo]):
    """pf_Algoritmos — Reescribe el archivo de préstamos."""
    _asegurar_directorio()
    with open(ARCHIVO_PRESTAMOS, "w", encoding="utf-8") as f:
        for p in prestamos:
            f.write(p.to_csv_row())


def generar_id_prestamo() -> str:
    """pf_Algoritmos — Genera un ID único para un préstamo (PR-001, PR-002…)."""
    prestamos = cargar_prestamos()
    return f"PR-{len(prestamos) + 1:04d}"


def agregar_prestamo(prestamo: clsPrestamo):
    """pf_Algoritmos — Añade un préstamo al archivo plano."""
    _asegurar_directorio()
    with open(ARCHIVO_PRESTAMOS, "a", encoding="utf-8") as f:
        f.write(prestamo.to_csv_row())


def prestamos_activos_por_usuario(documento: str) -> list[clsPrestamo]:
    """pf_Algoritmos — Retorna los préstamos activos de un usuario."""
    return [p for p in cargar_prestamos()
            if p.documento_usuario == documento and p.activo]


def buscar_prestamo_activo_por_item(item_id: str) -> "clsPrestamo | None":
    """pf_Algoritmos — Busca un préstamo activo dado el ID del ítem."""
    for p in cargar_prestamos():
        if p.item_id == item_id and p.activo:
            return p
    return None


# ═══════════════════════════════════════════════════════════════════
#  Exportación CSV
# ═══════════════════════════════════════════════════════════════════

def exportar_prestamos_csv(ruta: str):
    """pf_Algoritmos — Exporta todos los préstamos a un archivo CSV."""
    prestamos = cargar_prestamos()
    items     = {i.item_id: i for i in cargar_items()}
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID_Prestamo", "Documento_Usuario", "ID_Item",
                         "Nombre_Item", "Fecha_Prestamo", "Fecha_Devolucion",
                         "Dias_Transcurridos", "Estado_Alerta", "Activo"])
        for p in prestamos:
            item = items.get(p.item_id)
            nombre_item = item.nombre if item else "N/A"
            writer.writerow([
                p.prestamo_id, p.documento_usuario, p.item_id,
                nombre_item, p.fecha_prestamo, p.fecha_devolucion or "—",
                p.dias_transcurridos(), p.estado_alerta(), "Sí" if p.activo else "No"
            ])


def exportar_items_csv(ruta: str):
    """pf_Algoritmos — Exporta todos los ítems a un archivo CSV."""
    items = cargar_items()
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Nombre", "Categoría", "Precio",
                         "Puntaje_Estado", "Estado_Difuso", "Disponible"])
        for i in items:
            writer.writerow([i.item_id, i.nombre, i.categoria, i.precio,
                             i.puntaje_estado, i.estado,
                             "Sí" if i.disponible else "No"])
