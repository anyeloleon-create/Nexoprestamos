"""
pf_Algoritmos
Proyecto: NexoPréstamos — Gestor Inteligente de Préstamos
Módulo: clsUsuarios — Gestión de usuarios del sistema
Autores: Anyelo León León / Andres Felipe Barbas Cuavas
Curso: Algoritmia y Programación — Universidad de Antioquia 2026-1
"""

import re
import os
import csv

# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────
ARCHIVO_USUARIOS = os.path.join(os.path.dirname(__file__), "..", "data", "usuarios.txt")
TIEMPOS_PERMITIDOS = [5, 10, 15, 30]


class clsUsuarios:
    """
    pf_Algoritmos
    Clase que representa un usuario del sistema NexoPréstamos.
    Almacena información personal y tiempo máximo de préstamo.
    """

    def __init__(self, nombre: str, apellido: str, documento: str,
                 correo: str, tiempo_prestamo: int):
        """
        pf_Algoritmos
        Constructor de la clase clsUsuarios.
        Parámetros:
            nombre        (str): Nombre del usuario.
            apellido      (str): Apellido del usuario.
            documento     (str): Número de documento de identidad.
            correo        (str): Correo electrónico.
            tiempo_prestamo (int): Días permitidos de préstamo (5,10,15,30).
        """
        self.nombre = nombre
        self.apellido = apellido
        self.documento = documento
        self.correo = correo
        self.tiempo_prestamo = tiempo_prestamo

    # ── Representación ──────────────────────────────────────────────────────
    def __str__(self):
        """pf_Algoritmos — Representación legible del usuario."""
        return (f"[{self.documento}] {self.nombre} {self.apellido} | "
                f"{self.correo} | Plazo: {self.tiempo_prestamo} días")

    def to_csv_row(self) -> str:
        """pf_Algoritmos — Serializa el usuario como línea CSV."""
        return f"{self.nombre}|{self.apellido}|{self.documento}|{self.correo}|{self.tiempo_prestamo}\n"

    @staticmethod
    def from_csv_row(linea: str) -> "clsUsuarios":
        """pf_Algoritmos — Crea un usuario desde una línea CSV del archivo plano."""
        partes = linea.strip().split("|")
        return clsUsuarios(partes[0], partes[1], partes[2], partes[3], int(partes[4]))


# ═══════════════════════════════════════════════════════════════════
#  Funciones de Validación
# ═══════════════════════════════════════════════════════════════════

def validar_nombre(valor: str, campo: str = "Nombre") -> tuple[bool, str]:
    """
    pf_Algoritmos
    Valida nombre o apellido: mínimo 3 letras, sin números.
    Retorna (True, "") si es válido, o (False, mensaje_error).
    """
    if len(valor.strip()) < 3:
        return False, f"❌ {campo} muy corto (mínimo 3 letras)."
    if any(c.isdigit() for c in valor):
        return False, f"❌ {campo} no puede contener números."
    return True, ""


def validar_documento(valor: str) -> tuple[bool, str]:
    """
    pf_Algoritmos
    Valida documento: solo dígitos, entre 3 y 15 caracteres.
    """
    valor = valor.strip()
    if not valor.isdigit():
        return False, "❌ El documento solo puede contener números."
    if not (3 <= len(valor) <= 15):
        return False, "❌ El documento debe tener entre 3 y 15 dígitos."
    return True, ""


def validar_correo(valor: str) -> tuple[bool, str]:
    """
    pf_Algoritmos
    Valida correo electrónico: debe tener '@' y terminar en '.com'.
    """
    patron = r"^[^@\s]+@[^@\s]+\.com$"
    if not re.match(patron, valor.strip(), re.IGNORECASE):
        return False, "❌ Correo inválido. Debe contener '@' y terminar en '.com'."
    return True, ""


def validar_tiempo(valor: str) -> tuple[bool, str]:
    """
    pf_Algoritmos
    Valida que el tiempo de préstamo sea 5, 10, 15 o 30 días.
    """
    try:
        dias = int(valor)
        if dias not in TIEMPOS_PERMITIDOS:
            return False, f"❌ Tiempo inválido. Opciones: {TIEMPOS_PERMITIDOS}."
        return True, ""
    except ValueError:
        return False, "❌ Ingresa un número válido."


# ═══════════════════════════════════════════════════════════════════
#  Funciones de Persistencia
# ═══════════════════════════════════════════════════════════════════

def guardar_usuario(usuario: clsUsuarios):
    """
    pf_Algoritmos
    Guarda un usuario en el archivo plano usuarios.txt.
    Si el documento ya existe, no lo duplica.
    """
    os.makedirs(os.path.dirname(ARCHIVO_USUARIOS), exist_ok=True)
    # Verificar duplicado
    existentes = cargar_usuarios()
    for u in existentes:
        if u.documento == usuario.documento:
            return False  # ya existe
    with open(ARCHIVO_USUARIOS, "a", encoding="utf-8") as f:
        f.write(usuario.to_csv_row())
    return True


def cargar_usuarios() -> list[clsUsuarios]:
    """
    pf_Algoritmos
    Lee el archivo plano y retorna lista de objetos clsUsuarios.
    """
    usuarios = []
    if not os.path.exists(ARCHIVO_USUARIOS):
        return usuarios
    with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                try:
                    usuarios.append(clsUsuarios.from_csv_row(linea))
                except Exception:
                    pass
    return usuarios


def buscar_usuario_por_documento(documento: str) -> clsUsuarios | None:
    """
    pf_Algoritmos
    Busca y retorna un usuario por su número de documento.
    Retorna None si no existe.
    """
    for u in cargar_usuarios():
        if u.documento == documento.strip():
            return u
    return None


def exportar_usuarios_csv(ruta_csv: str):
    """
    pf_Algoritmos
    Exporta todos los usuarios al archivo CSV indicado.
    """
    usuarios = cargar_usuarios()
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Nombre", "Apellido", "Documento", "Correo", "Tiempo_Prestamo_Dias"])
        for u in usuarios:
            writer.writerow([u.nombre, u.apellido, u.documento, u.correo, u.tiempo_prestamo])


# ═══════════════════════════════════════════════════════════════════
#  Función interactiva de registro
# ═══════════════════════════════════════════════════════════════════

def registrar_usuario_interactivo() -> clsUsuarios | None:
    """
    pf_Algoritmos
    Flujo interactivo para registrar un nuevo usuario desde consola.
    Retorna el objeto clsUsuarios creado o None si se canceló.
    """
    print("\n" + "─" * 50)
    print("  👤  REGISTRAR NUEVO USUARIO")
    print("─" * 50)

    def pedir(prompt, validador, *args):
        while True:
            val = input(f"  {prompt}: ").strip()
            ok, msg = validador(val, *args) if args else validador(val)
            if ok:
                return val
            print(f"  {msg}")

    nombre   = pedir("Nombre", validar_nombre, "Nombre")
    apellido = pedir("Apellido", validar_nombre, "Apellido")
    documento = pedir("Documento (solo números)", validar_documento)
    correo   = pedir("Correo electrónico", validar_correo)

    print(f"  Tiempo de préstamo — Opciones: {TIEMPOS_PERMITIDOS} días")
    tiempo_str = pedir("Días de préstamo", validar_tiempo)
    tiempo = int(tiempo_str)

    usuario = clsUsuarios(nombre, apellido, documento, correo, tiempo)
    guardado = guardar_usuario(usuario)

    if guardado:
        print(f"\n  ✅ Usuario registrado exitosamente:")
        print(f"  {usuario}")
    else:
        print(f"\n  ⚠️  Ya existe un usuario con documento {documento}.")

    return usuario if guardado else None
