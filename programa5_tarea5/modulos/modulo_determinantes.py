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

 Incluye además la regla de Sarrus (solo 3×3) y el cálculo por reducción
 a forma triangular, que es el método eficiente: la expansión por
 cofactores necesita del orden de n! multiplicaciones y la reducción n³.

 Incluye también la REGLA DE CRAMER, que resuelve A·x = b usando solo
 determinantes: x_i = det(A_i)/det(A), donde A_i es A con su columna i
 reemplazada por b. Solo se puede aplicar si A es cuadrada y det(A) != 0.

 Restricción cumplida:
   - Solo se usa Python estándar (fractions). NO se usan NumPy, SciPy
     ni funciones de álgebra lineal de math.
=====================================================================
"""

from fractions import Fraction

from modulos import (
    formato, formato_matriz, _validar_matriz, _leer_dimensiones,
    LOGO_DETERMINANTES, con_subindice, con_exponente, nombre_variable,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_matriz,
    leer_vector, mostrar_matriz, pausa, preguntar,
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


def _linea_con_mas_ceros(A, n):
    """Devuelve (tipo, indice, ceros): la fila o columna con más ceros.
    Es la que conviene para desarrollar por cofactores, porque cada cero
    anula un término completo y ahorra calcular ese menor."""
    mejor = ("fila", 0, -1)
    for i in range(n):
        ceros = sum(1 for v in A[i] if v == 0)
        if ceros > mejor[2]:
            mejor = ("fila", i, ceros)
    for j in range(n):
        ceros = sum(1 for i in range(n) if A[i][j] == 0)
        if ceros > mejor[2]:
            mejor = ("columna", j, ceros)
    return mejor


def _posicion_del_termino(tipo, indice, pos):
    """Convierte la posición dentro de la línea elegida en el par (i, j)."""
    if tipo == "fila":
        return indice, pos
    return pos, indice


def _resolver_menor(menor, pasos):
    """Escribe cómo se resolvió el menor y devuelve su determinante.
    Los menores 3x3 se desarrollan por Sarrus, igual que en clase."""
    valor = determinante(menor)
    if len(menor) == 3:
        pasos.append("      Se resuelve por Sarrus:")
        pasos.extend("      " + linea for linea in
                     pasos_sarrus(menor, encabezado=False, nombre="M"))
    elif len(menor) == 2:
        pasos.append("      det = (" + formato(menor[0][0]) + ")("
                     + formato(menor[1][1]) + ") - (" + formato(menor[0][1])
                     + ")(" + formato(menor[1][0]) + ") = " + formato(valor))
    else:
        pasos.append("      det = " + formato(valor))
    return valor


def _escribir_termino(A, tipo, indice, pos, pasos):
    """Escribe un término del desarrollo y devuelve su aporte a la suma."""
    i, j = _posicion_del_termino(tipo, indice, pos)
    etiqueta = str(i + 1) + str(j + 1)
    if A[i][j] == 0:
        pasos.append("a" + etiqueta + " = 0  ->  el término se anula; no hace "
                     "falta calcular ese menor")
        pasos.append("")
        return Fraction(0)
    signo = 1 if (i + j) % 2 == 0 else -1
    pasos.append("a" + etiqueta + " = " + formato(A[i][j]) + ",   signo (-1)"
                 + con_exponente(i + j + 2) + " = "
                 + ("+1" if signo > 0 else "-1"))
    pasos.append("   M" + etiqueta + " = se tacha la fila " + str(i + 1)
                 + " y la columna " + str(j + 1) + ":")
    pasos.extend("   " + linea for linea in formato_matriz(submatriz(A, i, j)))
    valor = _resolver_menor(submatriz(A, i, j), pasos)
    aporte = signo * A[i][j] * valor
    pasos.append("   Término = (" + formato(A[i][j]) + ")·("
                 + ("+1" if signo > 0 else "-1") + ")·(" + formato(valor)
                 + ") = " + formato(aporte))
    pasos.append("")
    return aporte


def pasos_determinante(A, nombre="A"):
    """Desarrollo completo del determinante por expansión de cofactores,
    eligiendo la fila o columna con más ceros, como se hace en clase.
    'nombre' es el rótulo de la matriz, para poder incrustar el desarrollo
    dentro de otro (por ejemplo al verificar det(kA) = kⁿ·det(A))."""
    n = validar_cuadrada(A)
    A = [[Fraction(valor) for valor in fila] for fila in A]
    if n == 1:
        return ["Matriz 1x1: det(" + nombre + ") = " + formato(A[0][0])]
    if n == 2:
        return ["Matriz 2x2: det(" + nombre + ") = ad - bc",
                "   = (" + formato(A[0][0]) + ")(" + formato(A[1][1])
                + ") - (" + formato(A[0][1]) + ")(" + formato(A[1][0])
                + ") = " + formato(determinante(A))]

    tipo, indice, ceros = _linea_con_mas_ceros(A, n)
    pasos = ["DETERMINANTE DE " + nombre + " POR EXPANSIÓN DE COFACTORES", "",
             "Se desarrolla por la " + tipo + " " + str(indice + 1)
             + ", que es la que tiene más ceros (" + str(ceros) + ").",
             "Cada cero anula un término completo.", "",
             "det(" + nombre + ") = suma de aij · (-1)ⁱ⁺ʲ · det(Mij) sobre esa "
             + tipo, ""]
    sumandos = [_escribir_termino(A, tipo, indice, pos, pasos)
                for pos in range(n)]
    pasos.append("Suma de los términos:")
    pasos.append("   det(" + nombre + ") = "
                 + " + ".join("(" + formato(v) + ")" for v in sumandos))
    pasos.append("   det(" + nombre + ") = " + formato(determinante(A)))
    return pasos


def pasos_sarrus(A, encabezado=True, nombre="A"):
    """Desarrollo de la regla de Sarrus: las seis diagonales con sus
    productos, la suma de cada grupo y la resta final.
    Con encabezado=False omite el título, para incrustarlo dentro de otro
    desarrollo (por ejemplo al resolver un menor 3x3)."""
    validar_cuadrada(A)
    A = [[Fraction(v) for v in fila] for fila in A]
    bajan = [(A[0][0], A[1][1], A[2][2]), (A[0][1], A[1][2], A[2][0]),
             (A[0][2], A[1][0], A[2][1])]
    suben = [(A[0][2], A[1][1], A[2][0]), (A[0][0], A[1][2], A[2][1]),
             (A[0][1], A[1][0], A[2][2])]
    pasos = []
    if encabezado:
        pasos = ["REGLA DE SARRUS (solo matrices 3x3)", "",
                 "Se repiten las dos primeras columnas a la derecha y se "
                 "multiplican", "las tres diagonales que bajan (se suman) y "
                 "las tres que suben (se restan).", ""]
    pasos.append("Diagonales que BAJAN:")
    total_bajan = _sumar_diagonales(bajan, pasos)
    pasos.append("   Suma = " + formato(total_bajan))
    pasos.append("")
    pasos.append("Diagonales que SUBEN:")
    total_suben = _sumar_diagonales(suben, pasos)
    pasos.append("   Suma = " + formato(total_suben))
    pasos.append("")
    pasos.append("det(" + nombre + ") = " + formato(total_bajan) + " - ("
                 + formato(total_suben) + ") = "
                 + formato(total_bajan - total_suben))
    return pasos


def _sumar_diagonales(diagonales, pasos):
    """Escribe el producto de cada diagonal y devuelve la suma de los tres."""
    total = Fraction(0)
    for x, y, z in diagonales:
        producto = x * y * z
        pasos.append("   (" + formato(x) + ")·(" + formato(y) + ")·("
                     + formato(z) + ") = " + formato(producto))
        total = total + producto
    return total


def determinante_sarrus(A):
    """Devuelve det(A) por la regla de Sarrus. Solo vale para matrices 3×3.
    Lanza ValueError si A no es de ese tamaño."""
    n = validar_cuadrada(A)
    # Sarrus es una regla particular del orden 3: no se generaliza a n×n.
    if n != 3:
        raise ValueError("La regla de Sarrus solo se aplica a matrices 3x3; "
                         "esta es " + str(n) + "x" + str(n) + ".")
    A = [[Fraction(v) for v in fila] for fila in A]
    diagonales_bajan = (A[0][0] * A[1][1] * A[2][2]
                        + A[0][1] * A[1][2] * A[2][0]
                        + A[0][2] * A[1][0] * A[2][1])
    diagonales_suben = (A[0][2] * A[1][1] * A[2][0]
                        + A[0][0] * A[1][2] * A[2][1]
                        + A[0][1] * A[1][0] * A[2][2])
    return diagonales_bajan - diagonales_suben


def _anotar(pasos, titulo, M):
    """Agrega a la lista de pasos un título y la matriz tal como quedó.
    Si pasos es None no hace nada, para poder reutilizar los algoritmos
    cuando solo interesa el resultado."""
    if pasos is None:
        return
    pasos.append(titulo)
    pasos.extend(formato_matriz(M))
    pasos.append("")


def _triangularizar(M, n, pasos=None):
    """Lleva M a forma triangular superior usando intercambios y reemplazos.
    Devuelve el número de intercambios, o None si una columna quedó en ceros.
    Si se le pasa una lista, va anotando cada operación y la matriz."""
    intercambios = 0
    for col in range(n):
        fila = _buscar_pivote(M, col, n)
        # Columna entera de ceros: la diagonal queda con un 0 y det = 0.
        if fila is None:
            if pasos is not None:
                pasos.append("La columna " + str(col + 1) + " es toda ceros "
                             "debajo de la diagonal: det(A) = 0.")
            return None
        if fila != col:
            M[col], M[fila] = M[fila], M[col]
            intercambios += 1          # cada intercambio cambia el signo
            _anotar(pasos, "F" + str(col + 1) + " <-> F" + str(fila + 1)
                    + "   (el determinante cambia de signo)", M)

        # Solo reemplazos Fi -> Fi - k·Fcol, que NO alteran el determinante.
        # Por eso no hace falta arrastrar ningún factor de corrección.
        for f in range(col + 1, n):
            if M[f][col] != 0:
                factor = M[f][col] / M[col][col]
                M[f] = [M[f][j] - factor * M[col][j] for j in range(n)]
                _anotar(pasos, "F" + str(f + 1) + " -> F" + str(f + 1) + " - ("
                        + formato(factor) + ")·F" + str(col + 1)
                        + "   (no altera el determinante)", M)
    return intercambios


def _buscar_pivote(M, col, n):
    """Primera fila, de col en adelante, con entrada distinta de cero en
    esa columna. Devuelve None si la columna está llena de ceros."""
    for f in range(col, n):
        if M[f][col] != 0:
            return f
    return None


def pasos_reduccion(A):
    """Desarrollo completo del determinante por reducción a triangular:
    cada operación de fila, la matriz que queda y el producto final."""
    n = validar_cuadrada(A)
    M = [[Fraction(v) for v in fila] for fila in A]
    pasos = ["DETERMINANTE POR REDUCCIÓN A FORMA TRIANGULAR", "",
             "Solo se usan intercambios y reemplazos. El reemplazo no cambia",
             "el determinante; cada intercambio le cambia el signo.", ""]
    _anotar(pasos, "Matriz de partida:", M)
    intercambios = _triangularizar(M, n, pasos)
    if intercambios is None:
        pasos.append("det(A) = 0")
        return pasos
    diagonal = [M[i][i] for i in range(n)]
    producto = Fraction(1)
    for v in diagonal:
        producto = producto * v
    pasos.append("Producto de la diagonal: "
                 + " · ".join(formato(v) for v in diagonal)
                 + " = " + formato(producto))
    pasos.append("Intercambios realizados: " + str(intercambios)
                 + "  ->  signo (-1)^" + str(intercambios) + " = "
                 + ("-1" if intercambios % 2 else "+1"))
    pasos.append("det(A) = " + formato(-producto if intercambios % 2
                                       else producto))
    return pasos


def determinante_por_reduccion(A):
    """Devuelve det(A) reduciendo A a forma triangular superior.
    Entrega (determinante, intercambios, triangular) para poder mostrarlos."""
    n = validar_cuadrada(A)
    M = [[Fraction(v) for v in fila] for fila in A]
    intercambios = _triangularizar(M, n)
    if intercambios is None:
        return Fraction(0), 0, M

    producto = Fraction(1)
    for i in range(n):
        producto = producto * M[i][i]
    return (-producto if intercambios % 2 else producto), intercambios, M


# =====================================================================
# REGLA DE CRAMER
# Resuelve A·x = b usando solo determinantes, sin reducir por filas.
# Solo sirve cuando A es cuadrada y det(A) != 0.
# =====================================================================

def sustituir_columna(A, indice, b):
    """Devuelve una copia de A con la columna 'indice' reemplazada por b.
    Es la matriz que la regla de Cramer llama Ai."""
    return [[b[i] if j == indice else A[i][j] for j in range(len(A[i]))]
            for i in range(len(A))]


def regla_de_cramer(A, b):
    """Resuelve A·x = b por la regla de Cramer: xi = det(Ai)/det(A).
    Devuelve (soluciones, det_A, dets) para poder mostrar el desarrollo.
    Lanza ValueError si A no es cuadrada, si b no tiene n entradas o si
    det(A) = 0, porque entonces no hay solucion unica."""
    n = validar_cuadrada(A)
    if len(b) != n:
        raise ValueError("El vector b debe tener " + str(n) + " entradas; "
                         "tiene " + str(len(b)) + ".")
    det_A = determinante(A)
    # Cramer divide entre det(A): si vale 0 no hay solucion unica y la
    # formula no se puede aplicar.
    if det_A == 0:
        raise ValueError("det(A) = 0: el sistema no tiene solucion unica, "
                         "asi que no se puede aplicar la regla de Cramer.")
    dets = [determinante(sustituir_columna(A, i, b)) for i in range(n)]
    return [d / det_A for d in dets], det_A, dets


def pasos_cramer(A, b):
    """Arma las lineas del desarrollo de Cramer para mostrarlas en pantalla."""
    soluciones, det_A, dets = regla_de_cramer(A, b)
    lineas = ["det(A) = " + formato(det_A) + "  (distinto de cero: hay "
              "solucion unica)", ""]
    for i, (det_i, x_i) in enumerate(zip(dets, soluciones)):
        nombre_ai = con_subindice("A" + str(i + 1))
        lineas.append(nombre_ai + ": se sustituye la columna " + str(i + 1)
                      + " de A por el vector b")
        lineas.append("   det(" + nombre_ai + ") = " + formato(det_i))
        lineas.append("   " + nombre_variable(i + 1) + " = det(" + nombre_ai
                      + ") / det(A) = " + formato(det_i) + " / "
                      + formato(det_A) + " = " + formato(x_i))
        lineas.append("")
    return lineas


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
        print("   3. Resolver un sistema por la regla de Cramer")
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
        elif opcion == "3":
            _consola_cramer()
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


def _consola_cramer():
    """Pide A y b, y resuelve el sistema con la regla de Cramer."""
    mostrar_cabecera(LOGO_DETERMINANTES)
    print("   RESOLVER A·x = b POR LA REGLA DE CRAMER")
    print("   (solo para sistemas con A cuadrada y det(A) distinto de cero)")
    print()
    try:
        n = leer_entero("   Número de ecuaciones e incógnitas (n) = ")
        print()
        A = leer_matriz("A", n, n)
        print()
        b = leer_vector("b", n)
        soluciones, det_A, _ = regla_de_cramer(A, b)
        print()
        mostrar_matriz(A, titulo="   MATRIZ A:")
        print()
        for linea in pasos_cramer(A, b):
            print("   " + linea)
        print("   SOLUCIÓN:")
        for i, x_i in enumerate(soluciones):
            print("      " + nombre_variable(i + 1) + " = " + formato(x_i))
    except ValueError as error:
        print("\n   " + str(error))
    pausa()
