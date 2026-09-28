# -*- coding: utf-8 -*-
"""
=====================================================================
 MÓDULO 4: DETERMINANTES Y PROPIEDADES
 Calculadora de Álgebra Lineal - Proyecto Integrador - GRUPO 2
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Segundo Corte Evaluativo - Programa 4

 Calcula el determinante de una matriz cuadrada por EXPANSIÓN DE
 COFACTORES a lo largo de la primera fila:

     det(A) = a11·C11 - a12·C12 + a13·C13 - ...

 donde cada cofactor Cij es el determinante de la submatriz que queda
 al tachar la fila i y la columna j (el menor), con el signo alternado
 (-1)^(i+j).

 El caso base es la matriz 1x1 (su determinante es su única entrada) y
 la 2x2, que se resuelve con la fórmula ad - bc.

 PENDIENTE para el siguiente programa: regla de Sarrus, cálculo por
 reducción a forma triangular y la pantalla Tkinter de este módulo.

 Restricción cumplida:
   - Solo se usa Python estándar (fractions). NO se usan NumPy, SciPy
     ni funciones de álgebra lineal de math.
=====================================================================
"""

from fractions import Fraction

from modulos import (
    formato, _validar_matriz, _leer_dimensiones, LOGO_DETERMINANTES,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_matriz,
    mostrar_matriz, pausa, preguntar,
)
from teoremas.resumen_teoremas import texto_teoremas


def validar_cuadrada(A, nombre="A"):
    """Exige que la matriz sea cuadrada.

    Procedimiento algebraico: el determinante solo está definido para
    matrices cuadradas, porque la expansión por cofactores necesita que
    al tachar una fila y una columna quede otra matriz cuadrada.
    """
    _validar_matriz(A, nombre)
    filas, columnas = _leer_dimensiones(A)
    if filas != columnas:
        raise ValueError(
            "La matriz " + nombre + " es " + str(filas) + "x" + str(columnas)
            + ". El determinante solo existe para matrices cuadradas."
        )
    return filas


def submatriz(A, fila_tachada, columna_tachada):
    """Devuelve la matriz que queda al tachar una fila y una columna.

    Es el MENOR del elemento (fila_tachada, columna_tachada), que es lo
    que se necesita para calcular su cofactor.
    """
    resultado = []
    for i in range(len(A)):
        if i == fila_tachada:
            continue
        fila = []
        for j in range(len(A[0])):
            if j == columna_tachada:
                continue
            fila.append(A[i][j])
        resultado.append(fila)
    return resultado


def determinante(A):
    """Calcula det(A) por expansión de cofactores sobre la primera fila.

    Procedimiento algebraico:
      - Si A es 1x1, det(A) = a11.
      - Si A es 2x2, det(A) = ad - bc.
      - Si es mayor, se recorre la primera fila y por cada entrada a1j
        se suma (-1)^(1+j) · a1j · det(menor de a1j). El signo alterna
        empezando en positivo.
    """
    n = validar_cuadrada(A)
    A = [[Fraction(valor) for valor in fila] for fila in A]

    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]

    total = Fraction(0)
    for j in range(n):
        if A[0][j] == 0:
            continue                      # un cero anula todo el término
        signo = 1 if j % 2 == 0 else -1   # (-1)^(1+j) con j desde 0
        menor = determinante(submatriz(A, 0, j))
        total = total + signo * A[0][j] * menor
    return total


def pasos_determinante(A):
    """Devuelve el desarrollo escrito del determinante, para mostrarlo."""
    n = validar_cuadrada(A)
    A = [[Fraction(valor) for valor in fila] for fila in A]
    pasos = ["Determinante por expansión de cofactores (primera fila):"]
    if n == 1:
        pasos.append("   Matriz 1x1: det(A) = " + formato(A[0][0]))
        return pasos
    if n == 2:
        pasos.append("   Matriz 2x2: det(A) = ad - bc")
        pasos.append("   = (" + formato(A[0][0]) + ")(" + formato(A[1][1]) + ")"
                     + " - (" + formato(A[0][1]) + ")(" + formato(A[1][0]) + ")"
                     + " = " + formato(determinante(A)))
        return pasos
    terminos = []
    for j in range(n):
        signo = "+" if j % 2 == 0 else "-"
        menor = determinante(submatriz(A, 0, j))
        terminos.append("   " + signo + " (" + formato(A[0][j]) + ")·det(M1"
                        + str(j + 1) + ")  con det(M1" + str(j + 1) + ") = "
                        + formato(menor))
    pasos.extend(terminos)
    pasos.append("   det(A) = " + formato(determinante(A)))
    return pasos


def es_invertible(A):
    """Una matriz cuadrada es invertible si y solo si su determinante
    es distinto de cero. Se usará en el módulo de la matriz inversa."""
    return determinante(A) != 0


# =====================================================================
# MENÚ DE CONSOLA DEL MÓDULO 4 (MODO CLI)
# =====================================================================

def menu_consola():
    """Menú de texto del Módulo 4: Determinantes y Propiedades."""
    while True:
        mostrar_cabecera(LOGO_DETERMINANTES)
        print("   0. Ver Teoremas Clave del Módulo")
        print("   1. Calcular el determinante de una matriz cuadrada")
        print("   2. ¿La matriz es invertible?")
        print("   9. Volver al menú principal")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("determinantes"))
            pausa()
        elif opcion in ("1", "2"):
            _consola_determinante(opcion == "2")
        else:
            print("   Opción no válida.")
            pausa()


def _consola_determinante(preguntar_inversa):
    """Pide una matriz cuadrada y calcula su determinante."""
    mostrar_cabecera(LOGO_DETERMINANTES)
    print("   " + ("¿LA MATRIZ ES INVERTIBLE?" if preguntar_inversa
                   else "DETERMINANTE DE UNA MATRIZ"))
    print()
    try:
        n = leer_entero("   Tamaño de la matriz cuadrada (n) = ")
        print()
        A = leer_matriz("A", n, n)
        det = determinante(A)
        print()
        mostrar_matriz(A, titulo="   MATRIZ A:")
        print()
        for linea in pasos_determinante(A):
            print("   " + linea)
        print()
        print("   det(A) = " + formato(det))
        if preguntar_inversa:
            print()
            if det != 0:
                print("   det(A) distinto de cero  ->  la matriz SÍ es INVERTIBLE.")
                print("   Sus columnas son linealmente independientes.")
            else:
                print("   det(A) = 0  ->  la matriz NO es invertible (es SINGULAR).")
                print("   Sus columnas son linealmente dependientes.")
    except ValueError as error:
        print("\n   " + str(error))
    pausa()
