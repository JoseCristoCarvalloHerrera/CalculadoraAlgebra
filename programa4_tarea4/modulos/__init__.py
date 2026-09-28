# -*- coding: utf-8 -*-
"""
=====================================================================
 INICIALIZADOR DEL PAQUETE 'modulos'
 Calculadora de Álgebra Lineal - Proyecto Integrador - GRUPO 2
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Segundo Corte Evaluativo - Programa 4

 Este archivo convierte la carpeta 'modulos' en un paquete de Python
 y reúne lo que TODOS los módulos comparten:
   - La paleta de colores y las constantes de la interfaz.
   - Las funciones de lectura y formato de números (Fraction exacto).
   - Los validadores genéricos de matrices.
   - Los logotipos ASCII de cada módulo.
 De esta forma ningún módulo repite código y todos se ven igual.

 Restricción cumplida:
   - Solo se usa Python estándar (tkinter, fractions). NO se usan
     NumPy, SciPy ni funciones de álgebra lineal de math.
=====================================================================
"""

import sys
from fractions import Fraction


# Para que los acentos y símbolos (₀₁₂…, ⇔, ·) se vean bien en consola.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# =====================================================================
# CONSTANTES Y PALETA DE COLORES
# Usamos la paleta personalizada: fondo blanco, texto negro y
# detalles en tonos océano para los botones.
# =====================================================================
FONDO              = "#FFFFFF"   # Blanco puro para fondos y tarjetas
TARJETA            = "#FFFFFF"  
TEXTO              = "#000000"   # Negro puro para números y ecuaciones
TEXTO_SUAVE        = "#333333"   # Gris oscuro para subtítulos


ACENTO             = "#0077B6"   # Vibrante Zafiro (Botón principal)
ACENTO_HOVER       = "#023E8A"   # Oscuro Índigo (Hover del principal)
BOTON_SEC          = "#90E0EF"   # Claro Aguamarina (Botones de apoyo)
BOTON_SEC_HOVER    = "#00B4D8"   # Tabla de Surf (Hover de apoyo)
CELDA_BORDE        = "#00B4D8"   # Bordes de la matriz
LINEA_MATRIZ       = "#00B4D8"   # Líneas de la cuadrícula de la matriz
BARRA_AB           = "#023E8A"   # Barra que separa A de b en [A|b]
CELDA_FONDO        = "#FFFFFF"   # Fondo normal de una casilla
CELDA_FOCO         = "#CAF0F8"   # Casilla donde se está escribiendo
CELDA_ERROR        = "#F8D7DA"   # Casilla con un valor inválido


EXITO              = "#059669"   # Verde para la comprobación correcta
ADVERTENCIA        = "#8A4E02"   # Oscuro Mandarina (Infinitas soluciones)
ERROR              = "#8A0A02"   # Rico Escarlata (Sistema inconsistente)


LETRA_MONO         = "Consolas"
MAX_DIMENSION      = 8          


AYUDA_NUMERO = "Ingresa un entero, decimal o fracción (ej: 3, -2.5 o 3/4). Una casilla vacía vale 0."




# =====================================================================
# BLOQUE 1: LECTURA Y FORMATO DE NÚMEROS
# En esta parte se aseguró de que el programa entienda
# las fracciones (como "3/4") y no pierda decimales haciendo divisiones.
# Todo se maneja de forma exacta para que el resultado cuadre perfecto.
# =====================================================================
def a_numero(texto):
    """Convierte lo que el usuario escribe en una fracción matemática exacta."""
    texto = texto.strip().replace(" ", "")
    if texto == "":
        return Fraction(0)


    if "/" in texto:
        partes = texto.split("/")
        if len(partes) != 2 or partes[0] == "" or partes[1] == "":
            raise ValueError("Fracción mal escrita. " + AYUDA_NUMERO)
        try:
            numerador = Fraction(partes[0])
            denominador = Fraction(partes[1])
        except (ValueError, ZeroDivisionError):
            raise ValueError("Fracción mal escrita. " + AYUDA_NUMERO)
        if denominador == 0:
            raise ValueError("El denominador no puede ser cero.")
        return numerador / denominador


    try:
        return Fraction(texto)
    except (ValueError, ZeroDivisionError):
        raise ValueError("Valor no reconocido. " + AYUDA_NUMERO)


def formato(valor):
    """Muestra el número bonito en pantalla (ej. '5' en lugar de '5/1')."""
    valor = Fraction(valor)
    if valor.denominator == 1:
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


# Usamos los dígitos en subíndice del propio Unicode (₀₁₂₃...), 
# que Tkinter ya sabe dibujar más pequeños.
_TABLA_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def con_subindice(nombre):
    """Convierte el número final de un nombre de variable en subíndice.
    'x1' -> 'x₁', 'x12' -> 'x₁₂'. Si el nombre no termina en dígitos
    (por ejemplo una variable escrita como 'x' o 'z' sola), se deja tal
    cual, porque no hay número que convertir."""
    corte = len(nombre)
    while corte > 0 and nombre[corte - 1].isdigit():
        corte -= 1
    letras, numero = nombre[:corte], nombre[corte:]
    if numero:
        return letras + numero.translate(_TABLA_SUBINDICES)
    return nombre


def nombre_variable(indice_base_uno):
    """Nombre de columna para mostrar en la interfaz, ya con su
    subíndice pequeño: nombre_variable(1) -> 'x₁'."""
    return con_subindice(f"x{indice_base_uno}")


def formato_matriz(matriz, col_barra=None, sangria="    "):
    """Convierte nuestra matriz matemática en texto alineado para mostrar en la interfaz."""
    if not matriz:
        return []
    anchos = [0] * len(matriz[0])
    for fila in matriz:
        for c, valor in enumerate(fila):
            anchos[c] = max(anchos[c], len(formato(valor)))


    lineas = []
    for fila in matriz:
        piezas = []
        for c, valor in enumerate(fila):
            if col_barra is not None and c == col_barra:
                piezas.append("|")
            piezas.append(formato(valor).rjust(anchos[c]))
        lineas.append(sangria + "[ " + "  ".join(piezas) + " ]")
    return lineas





# =====================================================================
# BLOQUE M1: OPERACIONES MATRICIALES BÁSICAS
# Suma, resta, escalar y multiplicación A(m×n) · B(n×p) con bucles
# anidados. Solo se usa Python estándar; cada función documenta el
# procedimiento algebraico equivalente.
# =====================================================================

def _es_matriz_valida(M):
    """Verifica que M  sea una lista no vacía de listas del mismo ancho."""
    if not isinstance(M, list) or not M:
        return False
    filas = len(M)
    columnas = len(M[0])
    if columnas == 0:
        return False
    for fila in M:
        if not isinstance(fila, list) or len(fila) != columnas:
            return False
    return True


def _validar_matriz(M, nombre):
    """Lanza un error descriptivo si M no es una matriz bien formada."""
    if not _es_matriz_valida(M):
        raise ValueError("La matriz " + nombre + " no es válida: debe ser una "
                         "tabla rectangular, sin filas vacías.")


def _leer_dimensiones(M):
    """Devuelve (filas, columnas) de una matriz ya validada."""
    return len(M), len(M[0])




# =====================================================================
# LOGOTIPOS ASCII DE CADA MÓDULO
# Cada módulo abre con su cabecera en arte ASCII, tal como pide la
# Tarea 4. Se dibujan con fuente monoespaciada para que las líneas
# queden alineadas.
# =====================================================================
LOGO_SISTEMAS = (
    "==================================================\n"
    " [ [1 2 | 3] ]   MODULO: SISTEMAS DE ECUACIONES (SEL)\n"
    " [ [0 1 | 5] ]   Metodos: Gauss, Gauss-Jordan\n"
    "=================================================="
)

LOGO_VECTORES = (
    "==================================================\n"
    "      MODULO: VECTORES E INDEPENDENCIA LINEAL\n"
    "        Combinaciones Lineales, L.I. y L.D.\n"
    "                    A x = 0\n"
    "=================================================="
)

LOGO_MATRICES = (
    "==================================================\n"
    " [ A ][ B ]   MODULO: ALGEBRA DE MATRICES\n"
    " [ C ][ D ]   Operaciones, Traspuesta y Matriz Inversa\n"
    "=================================================="
)

LOGO_DETERMINANTES = (
    "==================================================\n"
    " | a b |      MODULO: DETERMINANTES Y PROPIEDADES\n"
    " | c d | = ad - bc\n"
    "=================================================="
)

LOGO_PRINCIPAL = (
    "==================================================\n"
    "   CALCULADORA DE ALGEBRA LINEAL  -  GRUPO 2\n"
    "   Universidad Americana (UAM)  -  MTM0120\n"
    "=================================================="
)


# =====================================================================
# AYUDANTES DE CONSOLA (MODO CLI)
# La Tarea 4 pide que cada módulo tenga su cabecera con logotipo ASCII
# y un menú interno de texto. Estas funciones son las que leen datos
# desde el teclado y dibujan las cabeceras, y las comparten los cuatro
# módulos para que la consola se vea y se comporte igual en todos.
# =====================================================================

class SalirDeLaConsola(Exception):
    """Se lanza cuando el usuario corta la entrada (Ctrl+C o fin de
    archivo). Sirve para cerrar la calculadora con un mensaje limpio en
    lugar de mostrar un error de Python."""


def preguntar(mensaje=""):
    """input() que no revienta si se corta la entrada.

    Si el usuario presiona Ctrl+C, o si el programa se ejecuta con la
    entrada redirigida y esta se agota, se lanza SalirDeLaConsola y el
    menú principal cierra ordenadamente.
    """
    try:
        return input(mensaje)
    except (EOFError, KeyboardInterrupt):
        raise SalirDeLaConsola()


def limpiar_pantalla():
    """Deja unas líneas en blanco para separar una pantalla de la otra.
    No se usa os.system('cls') para no depender del sistema operativo."""
    print("\n" * 2)


def mostrar_cabecera(logo):
    """Imprime el logotipo ASCII del módulo."""
    limpiar_pantalla()
    print(logo)
    print()


def leer_entero(mensaje, minimo=1, maximo=MAX_DIMENSION):
    """Pide un número entero por teclado y no se rinde hasta obtenerlo.

    Vuelve a preguntar si el usuario escribe letras o un valor fuera
    del rango permitido, de modo que el programa nunca se cae por una
    entrada inválida.
    """
    while True:
        try:
            valor = int(preguntar(mensaje).strip())
        except ValueError:
            print("   Eso no es un número entero. Intentá de nuevo.")
            continue
        if valor < minimo or valor > maximo:
            print("   Debe estar entre " + str(minimo) + " y " + str(maximo) + ".")
            continue
        return valor


def leer_numero(mensaje):
    """Pide un número (entero, decimal o fracción) y lo devuelve como
    Fraction exacto, reutilizando a_numero()."""
    while True:
        try:
            return a_numero(preguntar(mensaje).strip())
        except ValueError as error:
            print("   " + str(error))


def _trocear_numeros(texto):
    """Parte un texto en los números que contiene.

    Acepta separadores comunes: espacios, comas, punto y coma o
    tabuladores, de modo que "1 0 0", "1,0,0" y "1, 0, 0" se leen igual.
    No se usa el módulo re: se recorre carácter por carácter, como pide
    la restricción del sílabo de usar solo Python estándar básico.
    """
    partes = []
    actual = ""
    for caracter in texto:
        if caracter in " ,;\t":
            if actual:
                partes.append(actual)
                actual = ""
        else:
            actual = actual + caracter
    if actual:
        partes.append(actual)
    return partes


def leer_fila_numeros(mensaje, cantidad):
    """Lee 'cantidad' números escritos en UNA sola línea.

    El usuario puede escribir "1 0 0" o "1, 0, 0". Si la cantidad no
    coincide, se avisa y se vuelve a preguntar, de modo que el programa
    nunca se cae por una entrada mal escrita.
    """
    while True:
        texto = preguntar(mensaje).strip()
        partes = _trocear_numeros(texto)
        if len(partes) != cantidad:
            print("   Esperaba " + str(cantidad) + " número(s) y recibí "
                  + str(len(partes)) + ". Escribilos separados por espacios "
                  "o comas, por ejemplo:  1 0 0")
            continue
        try:
            return [a_numero(parte) for parte in partes]
        except ValueError as error:
            print("   " + str(error))


def leer_vector(nombre, n):
    """Pide por teclado las n entradas de un vector, en una sola línea."""
    return leer_fila_numeros(
        "      " + nombre + " (" + str(n) + " entradas) = ", n)


def leer_matriz(nombre, filas, columnas):
    """Pide por teclado una matriz de filas x columnas, una fila por línea."""
    print("   Matriz " + nombre + " (" + str(filas) + "x" + str(columnas)
          + "), una fila por línea:")
    matriz = []
    for i in range(filas):
        matriz.append(leer_fila_numeros(
            "      fila " + str(i + 1) + " = ", columnas))
    return matriz


def mostrar_matriz(matriz, col_barra=None, titulo=None):
    """Imprime una matriz en consola usando el mismo formato que la
    interfaz gráfica."""
    if titulo:
        print(titulo)
    for linea in formato_matriz(matriz, col_barra):
        print(linea)


def pausa():
    """Espera a que el usuario presione Enter antes de volver al menú."""
    preguntar("\n   (Presioná Enter para continuar) ")
