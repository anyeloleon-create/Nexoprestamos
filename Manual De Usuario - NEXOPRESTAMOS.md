# Manual de Usuario
 NexoPréstamos 💚

> ---

## Tabla de Contenidos

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Instalación y Ejecución](#2-instalación-y-ejecución)
3. [Menú Principal](#3-menú-principal)
4. [Registrar Usuario](#4-registrar-usuario)
5. [Registrar Ítem](#5-registrar-ítem)
6. [Registrar Préstamo](#6-registrar-préstamo)
7. [Registrar Devolución](#7-registrar-devolución)
8. [Ítems con más de 30 días](#8-ítems-con-más-de-30-días--generar-venta)
9. [Consultar Artículos Prestados](#9-consultar-artículos-prestados)
10. [Panel de Administrador](#10-panel-de-administrador)
11. [Archivos generados](#11-archivos-generados)
12. [Preguntas Frecuentes](#12-preguntas-frecuentes)

---

## 1. Requisitos del Sistema

| Elemento | Versión mínima |
|----------|---------------|
| Python | 3.10 o superior |
| Sistema Operativo | Windows 10 / Linux / macOS |
| Librería fpdf2 *(opcional, para PDF)* | `pip install fpdf2` |

No se requieren bases de datos externas. Toda la información se almacena en archivos de texto plano dentro de la carpeta `data/`.

---

## 2. Instalación y Ejecución

### Paso 1 — Clonar o descargar el proyecto

```bash
git clone https://github.com/<usuario>/Nexoprestamos.git
cd Nexoprestamos
```

### Paso 2 — (Opcional) Instalar fpdf2 para generar PDF

```bash
pip install fpdf2
```

### Paso 3 — Ejecutar el programa

```bash
cd src
python main.py
```

Al iniciar verás el banner de bienvenida y el menú principal.

---

## 3. Menú Principal

```
  ─────────────────────────────────────────────────────────
  Bienvenido a NexoPréstamos
  ─────────────────────────────────────────────────────────
    1. Registrar Usuario
    2. Registrar Ítem
    3. Registrar Préstamo
    4. Registrar Devolución
    5. Consultar Ítems con más de 30 días (Generar Venta)
    6. Consultar Artículos Prestados
    7. Administrador
    0. Salir
  ─────────────────────────────────────────────────────────
```

Escribe el número de la opción deseada y presiona **ENTER**.

---

## 4. Registrar Usuario

Permite ingresar un nuevo usuario al sistema.

**Campos requeridos:**

| Campo | Validación |
|-------|-----------|
| Nombre | Mínimo 3 letras, sin números |
| Apellido | Mínimo 3 letras, sin números |
| Documento | Solo dígitos, entre 3 y 15 caracteres |
| Correo electrónico | Debe contener `@` y terminar en `.com` |
| Tiempo de préstamo | Solo se aceptan: `5`, `10`, `15` o `30` días |

**Ejemplo de flujo:**
```
  Nombre: Juan
  Apellido: García
  Documento (solo números): 1023456789
  Correo electrónico: juan.garcia@gmail.com
  Días de préstamo — Opciones: [5, 10, 15, 30]: 15

  ✅ Usuario registrado exitosamente:
  [1023456789] Juan García | juan.garcia@gmail.com | Plazo: 15 días
```

> Si el documento ya está registrado, el sistema informará que el usuario ya existe.

---

## 5. Registrar Ítem

Permite registrar un artículo en el inventario de préstamos.

**Campos requeridos:**

| Campo | Descripción |
|-------|------------|
| Nombre | Mínimo 3 caracteres (puede tener números) |
| Categoría | Seleccionar de la lista numerada (1–6) |
| Precio | Valor numérico positivo |
| Puntaje de estado | Número del 0 al 10 (usa lógica difusa) |

**Categorías disponibles:**

| # | Categoría | Prefijo ID |
|---|-----------|-----------|
| 1 | Videojuegos | VJ |
| 2 | Libros | LB |
| 3 | Música y video | MV |
| 4 | Herramientas | HT |
| 5 | Dinero | DN |
| 6 | Celulares y Tecnologia | CT |

**Lógica difusa de estado:**

| Puntaje | Estado |
|---------|--------|
| 9.0 – 10 | Excelente |
| 7.0 – 8.9 | Bueno |
| 5.0 – 6.9 | Regular |
| 3.0 – 4.9 | Deteriorado |
| 0 – 2.9 | Malo |

El sistema mostrará un análisis visual de los grados de pertenencia difusa.

**El ID se asigna automáticamente**, por ejemplo: `LB-001`, `VJ-003`.

---

## 6. Registrar Préstamo

Asocia un ítem disponible a un usuario registrado.

**Pasos:**
1. Se muestra el inventario disponible con sus IDs.
2. Ingresa el **ID del artículo** a prestar.
3. Ingresa el **documento del usuario** prestatario.
4. Confirma el préstamo.

> ⚠️ Si el usuario no existe, el sistema te informará y deberás registrarlo primero.
> ⚠️ Solo se pueden prestar ítems marcados como **disponibles**.

---

## 7. Registrar Devolución

Registra la devolución de un ítem prestado.

**Pasos:**
1. Ingresa el documento del usuario.
2. Se listan sus préstamos activos.
3. Selecciona el ID del préstamo a cerrar.
4. Confirma la devolución.

**Resultados posibles:**

| Días transcurridos | Resultado |
|-------------------|-----------|
| < 20 días | Devolución normal → se genera certificado `.txt` |
| 20 – 30 días | Devolución con alerta amarilla → se genera certificado `.txt` |
| > 30 días | Venta forzosa → se genera **factura de venta** `.txt` |

Los documentos se guardan en `data/documentos/`.

---

## 8. Ítems con más de 30 días — Generar Venta

Muestra todos los préstamos activos que superaron el mes de duración, ordenados de mayor a menor por días.

Desde aquí puedes generar la **factura de venta** para un usuario específico ingresando su documento.

La factura incluye:
- Datos del comprador
- Detalle de artículos
- Subtotal
- **Impuesto por conchudez: 23 %**
- Total a pagar

---

## 9. Consultar Artículos Prestados

Muestra el estado general de todos los préstamos activos, ordenados por días transcurridos (mayor a menor).

**Leyenda de colores:**

| Símbolo | Significado |
|---------|-------------|
| 🟢 Normal | Menos de 20 días |
| 🟡 Alerta | Entre 20 y 30 días — solicitar devolución |
| 🔴 Venta | Más de 30 días — generar factura |

---

## 10. Panel de Administrador

Acceso restringido. **Credenciales por defecto:**

| Usuario | Contraseña |
|---------|-----------|
| `admin` | `nexo2026` |
| `profesor` | `udea1234` |

> Las credenciales se almacenan en `data/admins.txt` y pueden modificarse manualmente.

**Reportes disponibles:**

| Opción | Reporte |
|--------|---------|
| 1 | Total de préstamos registrados (activos y cerrados) |
| 2 | Total de ítems devueltos |
| 3 | Total de ventas realizadas y pago estimado |
| 4 | Lista completa de usuarios |
| 5 | Usuario con mayor y menor cantidad de préstamos |
| 6 | Exportar todo a CSV |

---

## 11. Archivos generados

Todos los datos se almacenan en la carpeta `data/`:

```
data/
├── usuarios.txt          ← Usuarios registrados
├── items.txt             ← Inventario de artículos
├── prestamos.txt         ← Historial de préstamos
├── admins.txt            ← Credenciales de administrador
├── documentos/           ← Certificados y facturas (.txt y .pdf)
└── exportaciones/        ← Exportaciones CSV
    ├── prestamos_export.csv
    └── items_export.csv
```

---

## 12. Preguntas Frecuentes

**¿Qué pasa si cierro el programa?**
Toda la información persiste en los archivos de texto. Al volver a ejecutar, el sistema carga los datos automáticamente.

**¿Puedo cambiar la contraseña del administrador?**
Sí, edita manualmente el archivo `data/admins.txt` con el formato `usuario|contraseña`.

**¿Se generan PDF automáticamente?**
Sí, si tienes instalada la librería `fpdf2` (`pip install fpdf2`). Si no, solo se genera el archivo `.txt`.

**¿El sistema funciona en Linux/macOS?**
Sí, es compatible con Python 3.10+ en cualquier sistema operativo.

---

*Manual elaborado por el equipo NexoPréstamos 💚
