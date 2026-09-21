# -*- coding: utf-8 -*-
"""
=====================================================================
 PROGRAMA 3 - GRUPO 2
 Calculadora de Álgebra Lineal - Proyecto Integrador
 Operaciones Algebraicas en R^n, Combinación Lineal y Ecuaciones Matriciales
 Aplicación de escritorio (Tkinter) - Python estándar
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Primer Corte Evaluativo


 Descripción general:
   - El programa solicita el número de ecuaciones (m) y de variables (n).
   - Pide los coeficientes de la matriz A y los términos independientes b,
     formando la matriz aumentada [ A | b ].
   - Aplica eliminación por filas (Gauss) con pivoteo parcial, mostrando la
     matriz en cada paso representativo.
   - Clasifica el sistema (Consistente Determinado / Consistente
     Indeterminado / Inconsistente).
   - Halla las variables (si aplica) mediante sustitución regresiva.
   - Comprueba la solución sustituyendo los valores en el sistema original.

 Módulo de vectores en R^n (Programa 3):
   - Suma y resta de vectores, y multiplicación de un vector por un escalar.
   - Determina si un vector b es combinación lineal de un conjunto de
     vectores {v1, v2, ..., vk}, mostrando los pesos cuando lo es
     (por ejemplo: b = 3·v1 + 2·v2).
   - Determina si un conjunto de vectores es linealmente independiente y,
     cuando es dependiente, halla la relación de dependencia explícita
     (por ejemplo: 2·v1 + 3·v2 - v3 = 0) asignando valor a las variables
     libres del sistema homogéneo.
   - Producto matriz-vector A·x por la regla fila-vector + su lectura como
     combinación de columnas.
   - Todo esto se apoya en el mismo motor de eliminación por filas: por el
     teorema de la ecuación vectorial, preguntar si b es combinación lineal
     de v1...vk equivale a resolver el sistema de matriz aumentada
     [ v1  v2  ...  vk | b ].
   - El módulo muestra el procedimiento completo (Gauss-Jordan paso a paso)
     y verifica cada resultado por sustitución.

 Módulo de operaciones matriciales básicas (Programa 3):
   - Suma y resta de matrices, validando que tengan las mismas
     dimensiones m×n.
   - Multiplicación de una matriz por un escalar.
   - Multiplicación de matrices A(m×n) · B(n×p) con bucles anidados,
     validando que las columnas de A sean iguales a las filas de B.


 Restricción cumplida:
   - Solo se usa Python estándar (tkinter, math, fractions). NO se usan
     NumPy, SciPy ni funciones integradas de álgebra lineal de math.
=====================================================================
"""


import sys
from fractions import Fraction
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont


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
# BLOQUE 1B: INTÉRPRETE DE ECUACIONES
# Esta sección lee lo que escribimos en la caja de texto
# (ej. "2x - y = 5") y lo convierte automáticamente en una matriz.
# Así evitamos tener que ingresar número por número en la cuadrícula.
# =====================================================================
ORDEN_LETRAS = ["x", "y", "z", "w", "u", "v", "s", "t"]
EQUIVALENCIAS = {
    "−": "-", "–": "-", "—": "-", "×": "*", "·": "*",
    "≡": "=", "＝": "=", "₀": "0", "₁": "1", "₂": "2",
    "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7",
    "₈": "8", "₉": "9",
}
LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"


def _partir_variable(texto):
    if texto == "": return None
    corte = 0
    while corte < len(texto) and texto[corte] in LETRAS:
        corte += 1
    if corte == 0: return None
    letras = texto[:corte]
    digitos = texto[corte:]
    for caracter in digitos:
        if caracter not in DIGITOS: return None
    return letras, digitos


def _buscar_variable_al_final(cuerpo):
    final = len(cuerpo)
    posicion = final
    while posicion > 0 and cuerpo[posicion - 1] in DIGITOS:
        posicion -= 1
    fin_letras = posicion
    while posicion > 0 and cuerpo[posicion - 1] in LETRAS:
        posicion -= 1
    if posicion == fin_letras: return None
    letras = cuerpo[posicion:fin_letras]
    digitos = cuerpo[fin_letras:final]
    return posicion, letras, digitos


def _normalizar(linea):
    for original, reemplazo in EQUIVALENCIAS.items():
        linea = linea.replace(original, reemplazo)
    linea = linea.replace("*", "").replace("_", "")
    return "".join(linea.split())


def _trocear(lado):
    if lado == "": return []
    if lado[0] not in "+-": lado = "+" + lado
    terminos, actual = [], lado[0]
    for caracter in lado[1:]:
        if caracter in "+-":
            terminos.append(actual)
            actual = caracter
        else:
            actual += caracter
    terminos.append(actual)
    return terminos


def _numero_del_termino(texto, termino, numero_linea):
    try:
        return a_numero(texto)
    except ValueError as error:
        raise ValueError(f"Ecuación {numero_linea}, término «{termino}»: {error}")


def _leer_termino(termino, numero_linea):
    signo = -1 if termino[0] == "-" else 1
    cuerpo = termino[1:]
    if cuerpo == "": raise ValueError(f"Ecuación {numero_linea}: hay un signo suelto.")
    hallazgo = _buscar_variable_al_final(cuerpo)
    if hallazgo is None:
        return signo * _numero_del_termino(cuerpo, termino, numero_linea), None
    inicio, letras, digitos = hallazgo
    nombre = letras.lower() + digitos
    texto_coeficiente = cuerpo[:inicio]
    if texto_coeficiente == "":
        coeficiente = Fraction(1)
    elif texto_coeficiente.endswith("/"):
        raise ValueError(f"Ecuación {numero_linea}: falta el denominador en «{termino}».")
    else:
        coeficiente = _numero_del_termino(texto_coeficiente, termino, numero_linea)
    return signo * coeficiente, nombre


def _ordenar_variables(nombres):
    con_numero, sin_numero = [], []
    for nombre in nombres:
        letra, digitos = _partir_variable(nombre)
        if digitos: con_numero.append((letra, int(digitos), nombre))
        else: sin_numero.append((letra, nombre))
    con_numero.sort(key=lambda dato: (dato[0], dato[1]))
    def clave_letra(dato):
        letra = dato[0]
        if letra in ORDEN_LETRAS: return (0, ORDEN_LETRAS.index(letra))
        return (1, letra)
    sin_numero.sort(key=clave_letra)
    return [dato[2] for dato in con_numero] + [dato[1] for dato in sin_numero]


def interpretar_ecuaciones(texto):
    """Convierte el bloque de texto con ecuaciones a la matriz A y el vector b."""
    lineas = [linea for linea in texto.splitlines() if linea.strip() != ""]
    if not lineas: raise ValueError("No se escribió ninguna ecuación.")
    ecuaciones, nombres = [], set()


    for indice, linea_original in enumerate(lineas, start=1):
        linea = _normalizar(linea_original)
        if linea.count("=") != 1:
            raise ValueError(f"Ecuación {indice}: debe llevar exactamente un signo '='.")
        izquierda, derecha = linea.split("=")
        if izquierda == "" or derecha == "":
            raise ValueError(f"Ecuación {indice}: falta un lado de la igualdad.")


        coeficientes, constante = {}, Fraction(0)
        for lado, orientacion in ((izquierda, 1), (derecha, -1)):
            for termino in _trocear(lado):
                valor, nombre = _leer_termino(termino, indice)
                if nombre is None:
                    constante -= orientacion * valor
                else:
                    coeficientes[nombre] = coeficientes.get(nombre, Fraction(0)) + orientacion * valor
                    nombres.add(nombre)


        if not coeficientes: raise ValueError(f"Ecuación {indice}: no tiene ninguna variable.")
        ecuaciones.append((coeficientes, constante))


    orden = _ordenar_variables(nombres)
    A, b = [], []
    for coeficientes, constante in ecuaciones:
        A.append([coeficientes.get(nombre, Fraction(0)) for nombre in orden])
        b.append(constante)
    return A, b, orden




# =====================================================================
# BLOQUE 2: ESCALONAMIENTO Y REDUCCIÓN (MÉTODO DE GAUSS-JORDAN)
# Aquí está la lógica principal. Primero hacemos ceros hacia abajo
# (Fase 1: Gauss) y luego nos regresamos haciendo ceros hacia arriba
# (Fase 2: Jordan) hasta llegar a la Matriz Identidad. Todo esto
# guardando el texto paso a paso para el procedimiento.
# =====================================================================
def intercambiar_filas(matriz, i, j):
    """Cambia la fila i por la j."""
    matriz[i], matriz[j] = matriz[j], matriz[i]
    return f"Intercambio de filas: F{i+1} <-> F{j+1}"


def reemplazar_fila(matriz, destino, factor, origen):
    """Hace cero el número restando filas."""
    matriz[destino] = [matriz[destino][c] - factor * matriz[origen][c] for c in range(len(matriz[destino]))]
    return f"Anular en F{destino+1}: F{destino+1} = F{destino+1} - ({formato(factor)}) * F{origen+1}"


def escalonar(matriz, col_barra=None):
    """Lleva la matriz a su forma escalonada reducida (Identidad)."""
    pasos = []
    filas = len(matriz)
    columnas = len(matriz[0])
    fila_pivote = 0
    pivotes = []


    pasos.append("--- FASE 1: MÉTODO DE GAUSS (Ceros debajo de los pivotes) ---")
    pasos.append("")


    for col in range(columnas - 1): # Nos detenemos antes del vector b
        if fila_pivote >= filas: break


        fila_no_nula = None
        for f in range(fila_pivote, filas):
            if matriz[f][col] != 0:
                fila_no_nula = f
                break
       
        if fila_no_nula is None:
            continue


        if fila_no_nula != fila_pivote:
            pasos.append(intercambiar_filas(matriz, fila_pivote, fila_no_nula))
            pasos.extend(formato_matriz(matriz, col_barra))
            pasos.append("")


        # Normalizar: Convertir el pivote a 1
        pivote_val = matriz[fila_pivote][col]
        if pivote_val != 1:
            matriz[fila_pivote] = [x / pivote_val for x in matriz[fila_pivote]]
            pasos.append(f"Convertir pivote a 1: F{fila_pivote+1} = F{fila_pivote+1} / ({formato(pivote_val)})")
            pasos.extend(formato_matriz(matriz, col_barra))
            pasos.append("")


        # Generar ceros por debajo
        for f in range(fila_pivote + 1, filas):
            if matriz[f][col] != 0:
                factor = matriz[f][col]
                pasos.append(reemplazar_fila(matriz, f, factor, fila_pivote))
                pasos.extend(formato_matriz(matriz, col_barra))
                pasos.append("")


        pivotes.append((fila_pivote, col))
        fila_pivote += 1


    # Bajar filas nulas al final
    f = fila_pivote
    while f < filas:
        if all(valor == 0 for valor in matriz[f]):
            siguiente = None
            for g in range(f + 1, filas):
                if any(valor != 0 for valor in matriz[g]):
                    siguiente = g
                    break
            if siguiente is None: break
            pasos.append(intercambiar_filas(matriz, f, siguiente))
            pasos.extend(formato_matriz(matriz, col_barra))
            pasos.append("")
        f += 1


    # Fase 2 (Gauss-Jordan) -> Ceros por encima de la diagonal
    if len(pivotes) > 0:
        pasos.append("--- FASE 2: GAUSS-JORDAN (Ceros arriba de los pivotes) ---")
        pasos.append("")
        hubo_operaciones_arriba = False
       
        # Recorremos los pivotes de abajo hacia arriba
        for i in range(len(pivotes)-1, -1, -1):
            f_piv, c_piv = pivotes[i]
            for f_arriba in range(f_piv - 1, -1, -1):
                if matriz[f_arriba][c_piv] != 0:
                    factor = matriz[f_arriba][c_piv]
                    pasos.append(reemplazar_fila(matriz, f_arriba, factor, f_piv))
                    pasos.extend(formato_matriz(matriz, col_barra))
                    pasos.append("")
                    hubo_operaciones_arriba = True
                   
        if not hubo_operaciones_arriba:
            pasos.append("La matriz ya estaba completamente reducida.")
            pasos.append("")


    return pasos, pivotes


def entrada_principal(fila):
    """Busca el primer elemento distinto de cero en una fila."""
    for c, valor in enumerate(fila):
        if valor != 0: return c
    return None


def es_escalonada(matriz):
    """Verificador usado por las pruebas automáticas para confirmar que el algoritmo no falló."""
    principales = [entrada_principal(fila) for fila in matriz]
    vista_nula = False
    for p in principales:
        if p is None:
            vista_nula = True
        elif vista_nula:
            return False, "hay una fila no nula debajo de una fila de ceros"
    anterior = -1
    for p in principales:
        if p is None: continue
        if p <= anterior: return False, "las entradas principales no forman escalera"
        anterior = p
    return True, ""




# =====================================================================
# BLOQUE 4: CLASIFICACIÓN Y SUSTITUCIÓN REGRESIVA
# Una vez que la matriz está escalonada, el programa revisa si tiene
# solución única, infinitas (variables libres) o si es inconsistente
# (detectando una fila de ceros igualada a un número). También
# arma la sustitución explícita de la comprobación final.
# =====================================================================


def resolver_sistema(m, n, A, b):
    A = [[Fraction(valor) for valor in fila] for fila in A]
    b = [Fraction(valor) for valor in b]
    aumentada = [A[i][:] + [b[i]] for i in range(m)]


    pasos = ["Matriz aumentada inicial [A|b]:"]
    pasos.extend(formato_matriz(aumentada, n))
    pasos.append("")


    pasos_escalonamiento, pivotes = escalonar(aumentada, n)
    if pasos_escalonamiento:
        pasos.extend(pasos_escalonamiento)
    else:
        pasos.append("La matriz ya estaba en forma escalonada; no hizo falta ninguna operación.")
   
    pasos.append("Forma Escalonada Reducida Final:")
    pasos.extend(formato_matriz(aumentada, n))


    # --- EXTRACCIÓN ---
    pivotes_variables = [(f, c) for f, c in pivotes if c < n]
    rango_A = len(pivotes_variables)
   
    columnas_pivote = [c + 1 for _, c in pivotes_variables]
    vars_basicas = [nombre_variable(c + 1) for _, c in pivotes_variables]
   
    # Identificar variables libres
    vars_libres_idx = [c for c in range(n) if c not in [col - 1 for col in columnas_pivote]]
    vars_libres = [nombre_variable(c + 1) for c in vars_libres_idx]
    cantidad_libres = len(vars_libres)


    # Formatear listas a texto
    str_cols_pivote = ", ".join(map(str, columnas_pivote)) if columnas_pivote else "Ninguna"
    str_vars_basicas = ", ".join(vars_basicas) if vars_basicas else "Ninguna"
    str_vars_libres = ", ".join(vars_libres) if vars_libres else "Ninguna"


    fila_inconsistente = -1
    for i, fila in enumerate(aumentada):
        if all(valor == 0 for valor in fila[:n]) and fila[n] != 0:
            fila_inconsistente = i
            break


    # --- ESTRUCTURA BASE DEL RESULTADO ---
    resultado = {
        "pasos": pasos,
        "escalonada": [fila[:] for fila in aumentada],
        "homogeneo": all(valor == 0 for valor in b),
        "variables_libres": vars_libres_idx,
        "solucion": None,
        "m": m,
        "n": n,
       
        # Aquí van los datos listos para que Tkinter arme la tabla gráfica:
        "datos_resumen": [
            ("Total variables (n)", str(n)),
            ("Rango matriz (r)", str(rango_A)),
            ("Columnas Pivote", str_cols_pivote),
            ("Variables básicas", str_vars_basicas),
            ("Variables libres", str_vars_libres),
            ("Cálculo (n - r)", f"{n} - {rango_A} = {cantidad_libres} variable(s)")
        ]
    }


    # CASO 1: SIN SOLUCIÓN
    if fila_inconsistente != -1:
        valor_k = formato(aumentada[fila_inconsistente][n])
        resultado["clasificacion"] = "Inconsistente"
        resultado["descripcion"] = f"> Sistema sin solución. Contradicción en la fila {fila_inconsistente+1} (0 = {valor_k})."
        resultado["verificacion"] = "No hay solución vectorial ni parametrizada porque el sistema es inconsistente."
        return resultado


    # CASO 2: INFINITAS SOLUCIONES (Generador de Parametrizada y Vectorial)
    if vars_libres_idx:
        parametrizada = ["--- SOLUCIÓN GENERAL (PARAMETRIZADA) ---"]
        vectorial_const = []
        vectorial_vars = {v: [] for v in vars_libres_idx}
       
        for c in range(n):
            if c in vars_libres_idx:
                parametrizada.append(f"{nombre_variable(c+1)} = {nombre_variable(c+1)}  <-- (Libre)")
                vectorial_const.append("0")
                for v in vars_libres_idx:
                    vectorial_vars[v].append("1" if v == c else "0")
            else:
                f = next(fila for fila, col in pivotes_variables if col == c)
                termino_ind = aumentada[f][n]
                eq_params = []
               
                for v in vars_libres_idx:
                    coef = -aumentada[f][v]
                    if coef != 0:
                        eq_params.append(f"{formato(coef)}·{nombre_variable(v+1)}")
                        vectorial_vars[v].append(formato(coef))
                    else:
                        vectorial_vars[v].append("0")
               
                str_params = " + ".join(eq_params).replace("+ -", "- ")
                if termino_ind != 0 or not str_params:
                    texto_eq = f"{nombre_variable(c+1)} = {formato(termino_ind)}" + (f" + {str_params}" if str_params else "")
                else:
                    texto_eq = f"{nombre_variable(c+1)} = {str_params}"
                parametrizada.append(texto_eq.replace("+ -", "- "))
                vectorial_const.append(formato(termino_ind))
       
        # Armar la Forma Vectorial renglón por renglón
        lineas_vectorial = ["\n--- SOLUCIÓN GENERAL (FORMA VECTORIAL) ---"]
        for i in range(n):
            linea = f"[{nombre_variable(i+1)}] = [{vectorial_const[i]:>4}]"
            for v in vars_libres_idx:
                linea += f" + {nombre_variable(v+1)} * [{vectorial_vars[v][i]:>4}]"
            lineas_vectorial.append(linea)


        texto_infinito = "\n".join(parametrizada) + "\n" + "\n".join(lineas_vectorial)


        resultado["clasificacion"] = "Consistente Indeterminado"
        resultado["descripcion"] = "▶ Sistema con infinitas soluciones."
        resultado["verificacion"] = texto_infinito
        return resultado


    # CASO 3: SOLUCIÓN ÚNICA
    solucion = sustitucion_regresiva(aumentada, n, pivotes_variables)
    resultado["clasificacion"] = "Consistente Determinado"
    resultado["descripcion"] = "▶ Sistema con solución única. Sin variables libres."
    resultado["solucion"] = solucion
   
    texto_verificacion = verificar(m, n, A, b, solucion)
    resultado["verificacion"] = texto_verificacion
   
    resultado["pasos"].append("")
    resultado["pasos"].append("========================================")
    resultado["pasos"].append("COMPROBACIÓN DEL SISTEMA (PASO FINAL):")
    resultado["pasos"].append("========================================")
    resultado["pasos"].extend(texto_verificacion.split("\n"))
   
    return resultado




def sustitucion_regresiva(aumentada, n, pivotes_variables):
    """Despeja las variables de abajo hacia arriba."""
    x = [Fraction(0)] * n
    for fila_p, col_p in reversed(pivotes_variables):
        total = aumentada[fila_p][n]
        for c in range(col_p + 1, n):
            total -= aumentada[fila_p][c] * x[c]
        x[col_p] = total / aumentada[fila_p][col_p]
    return x


def verificar(m, n, A, b, solucion):
    """Reemplaza los resultados en el sistema original armando la ecuación paso a paso."""
    lineas = ["Sustituyendo explícitamente los valores hallados en las ecuaciones originales:"]
    todo_correcto = True
   
    for i in range(m):
        total = Fraction(0)
        partes_ecuacion = []
       
        for j in range(n):
            coeficiente = A[i][j]
            valor = solucion[j]
            total += coeficiente * valor
           
            # Crea la visual: (Coeficiente)(Valor)
            if coeficiente != 0:
                partes_ecuacion.append(f"({formato(coeficiente)})({formato(valor)})")
            else:
                partes_ecuacion.append(f"(0)({formato(valor)})")
               
        ecuacion_visual = " + ".join(partes_ecuacion).replace("+ -", "- ")
        correcta = (total == b[i])
        todo_correcto = todo_correcto and correcta
       
        lineas.append(f"   Ec{i+1}: {ecuacion_visual} = {formato(b[i])}")
        lineas.append(f"        {formato(total)} = {formato(b[i])}   ->   { 'CORRECTO' if correcta else '❌ FALLO'}")
        lineas.append("")
       
    lineas.append("-" * 46)
    lineas.append("La solución satisface todas las ecuaciones." if todo_correcto else "La solución NO satisface el sistema.")
    return "\n".join(lineas)


EJEMPLOS = {
    "unica": {"titulo": "Solución única", "ecuaciones": "x1 + x2 + x3 = 6\n2x1 - x2 + x3 = 3\nx1 + 2x2 - x3 = 2"},
    "infinitas": {"titulo": "Infinitas", "ecuaciones": "x1 + x2 + x3 = 1\n2x1 + 2x2 + 2x3 = 2"},
    "sin_solucion": {"titulo": "Sin solución", "ecuaciones": "x1 - 2x2 + x3 = 4\n2x1 - 4x2 + 2x3 = 5\n3x1 + x2 - x3 = 2"},
}
# Sistema que aparece escrito en la caja al abrir la calculadora, como
# guía del formato que se espera.
SISTEMA_INICIAL = ("x1 + x2 + x3 = 6\n"
                   "2x1 - x2 + x3 = 3\n"
                   "x1 + 2x2 - x3 = 2")




# =====================================================================
# BLOQUE 6: LA INTERFAZ GRÁFICA (PANTALLAS)
# Aquí construimos toda la parte visual usando Tkinter: el menú de
# inicio, la cuadrícula que se adapta a las dimensiones, los botones
# y la zona donde se imprimen los resultados ordenados.
# =====================================================================
# =====================================================================
# BLOQUE V1: MÓDULO DE VECTORES EN R^n
# =====================================================================

def validar_dimensiones(u, v):
    """Comprueba que dos vectores tengan el mismo número de entradas."""
    if len(u) != len(v):
        raise ValueError(
            "No se pueden operar: un vector está en R^" + str(len(u))
            + " y el otro en R^" + str(len(v))
            + ". Ambos deben tener el mismo número de entradas."
        )


def sumar_vectores(u, v):
    """Suma dos vectores de R^n entrada por entrada."""
    validar_dimensiones(u, v)
    resultado = []
    for i in range(len(u)):
        resultado.append(u[i] + v[i])
    return resultado


def escalar_por_vector(c, u):
    """Multiplica un vector por un escalar."""
    resultado = []
    for entrada in u:
        resultado.append(c * entrada)
    return resultado


def restar_vectores(u, v):
    """Resta dos vectores: u - v = u + (-1)v."""
    validar_dimensiones(u, v)
    return sumar_vectores(u, escalar_por_vector(-1, v))


def vectores_como_columnas(vectores):
    """Acomoda una lista de vectores como las COLUMNAS de una matriz."""
    filas = len(vectores[0])
    columnas = len(vectores)
    matriz = []
    for i in range(filas):
        fila = []
        for j in range(columnas):
            fila.append(vectores[j][i])
        matriz.append(fila)
    return matriz


def es_combinacion_lineal(b, vectores):
    """Determina si b es combinación lineal de los vectores dados."""
    if len(vectores) == 0:
        raise ValueError("Debe indicar al menos un vector.")
    for v in vectores:
        validar_dimensiones(b, v)
    A = vectores_como_columnas(vectores)
    resultado = resolver_sistema(len(b), len(vectores), A, list(b))
    if resultado["clasificacion"] == "Inconsistente":
        return (False, None, resultado)
    return (True, resultado["solucion"], resultado)


def son_linealmente_independientes(vectores):
    """Determina si un conjunto de vectores es linealmente independiente."""
    if len(vectores) == 0:
        raise ValueError("Debe indicar al menos un vector.")
    for v in vectores:
        validar_dimensiones(vectores[0], v)
    A = vectores_como_columnas(vectores)
    vector_cero = [0] * len(vectores[0])
    resultado = resolver_sistema(len(vectores[0]), len(vectores), A, vector_cero)
    independientes = (len(resultado["variables_libres"]) == 0)
    return (independientes, resultado)


def formato_vector(v):
    """Devuelve un vector como texto: ( 3, -1, 1/2 )."""
    return "( " + ",  ".join(formato(x) for x in v) + " )"


def _formato_suma_lineal(coefs, nombre_base="v"):
    """Construye el texto de una combinación lineal, por ejemplo
    '3·v₁ + 2·v₂ − v₃'. Recibe la lista de coeficientes y el nombre base
    de las variables ('v', 'a', 'x', ...). Escribe el signo + o − según
    el signo de cada coeficiente y omite el coeficiente si es 1 ó −1."""
    terminos = []
    for i, c in enumerate(coefs):
        if c == 0:
            continue
        nombre = con_subindice(nombre_base + str(i + 1))
        if c > 0:
            signo = " + " if terminos else ""
        else:
            signo = " − " if terminos else "−"
        c_abs = abs(c)
        if c_abs == 1:
            terminos.append(signo + nombre)
        else:
            terminos.append(signo + formato(c_abs) + "·" + nombre)
    return "".join(terminos) if terminos else "0"


def _mcd(a, b):
    """Máximo común divisor de enteros positivos (algoritmo de Euclides)."""
    a, b = abs(int(a)), abs(int(b))
    while b:
        a, b = b, a % b
    return a


def _coeficientes_enteros(coefs):
    """Convierte coeficientes racionales en enteros equivalentes y mínimos.
    Multiplica por el mínimo común múltiplo de los denominadores y luego
    simplifica dividiendo entre el máximo común divisor. Así la relación de
    dependencia se muestra con los números enteros más pequeños posibles."""
    mcm = 1
    for c in coefs:
        if c == 0:
            continue
        d = c.denominator
        mcm = mcm // _mcd(mcm, d) * d
    enteros = [c * mcm for c in coefs]
    g = 0
    for v in enteros:
        g = _mcd(g, v.numerator)
    if g > 1:
        enteros = [v / g for v in enteros]
    return enteros


def _normalizar_signo_coeficientes(coefs):
    """Multiplica por −1 la lista si el primer coeficiente no nulo es
    negativo, para mostrar la relación con el primer término positivo."""
    primero = next((c for c in coefs if c != 0), 0)
    if primero < 0:
        return [-c for c in coefs]
    return coefs


def relacion_de_dependencia(vectores):
    """Encuentra la(s) relación(es) de dependencia lineal del conjunto
    {v₁, ..., vₖ} cuando es linealmente dependiente.

    Método: se resuelve el sistema homogéneo
    c₁v₁ + ... + cₖvₖ = 0 reduciendo [v₁ ... vₖ | 0]. Cada variable libre
    recibe el valor 1 (y las demás libres 0); su solución proporciona una
    relación no trivial. Devuelve una lista de relaciones; cada relación es
    una lista de coeficientes enteros [c₁, ..., cₖ] con Σ cᵢvᵢ = 0.
    Si el conjunto es independiente, devuelve una lista vacía."""
    if len(vectores) == 0:
        raise ValueError("Debe indicar al menos un vector.")
    for v in vectores:
        validar_dimensiones(vectores[0], v)
    k = len(vectores)
    A = vectores_como_columnas(vectores)
    aumentada = [fila[:] + [Fraction(0)] for fila in A]
    _, pivotes = escalonar(aumentada, k)
    columnas_libres = [c for c in range(k) if c not in [c for _, c in pivotes]]
    if not columnas_libres:
        return []
    relaciones = []
    for libre in columnas_libres:
        coef = [Fraction(0)] * k
        coef[libre] = Fraction(1)
        for fila_p, col in pivotes:
            # En la forma escalonada reducida, la ecuación de la fila pivote es:
            #   x_col + (aumentada[fila_p][libre])·x_libre + ... = 0
            # Por eso el coeficiente de x_col queda: -aumentada[fila_p][libre].
            coef[col] = -aumentada[fila_p][libre]
        coef = _normalizar_signo_coeficientes(_coeficientes_enteros(coef))
        relaciones.append(coef)
    return relaciones


def matriz_por_vector(A, x):
    """Calcula el producto matriz-vector A·x por la REGLA FILA-VECTOR:
    la entrada i del resultado es el producto escalar de la
    fila i de A con el vector x,
        b[i] = A[i][0]·x[0] + A[i][1]·x[1] + ... + A[i][n-1]·x[n-1].
    Requiere que el número de COLUMNAS de A sea igual al número de ENTRADAS
    de x; si no, la operación no está definida."""
    if not A or not x:
        raise ValueError("Debe ingresar la matriz A y el vector x.")
    if not A[0]:
        raise ValueError("La matriz A no puede tener filas vacías.")
    n_columnas = len(A[0])
    if n_columnas != len(x):
        raise ValueError(
            "No se puede calcular A·x: la matriz A tiene " + str(n_columnas)
            + " columna(s) pero el vector x tiene " + str(len(x))
            + " entrada(s); deben coincidir."
        )
    resultado = []
    for fila in A:
        total = Fraction(0)
        for j in range(n_columnas):
            total = total + fila[j] * x[j]
        resultado.append(total)
    return resultado


# =====================================================================
# BLOQUE M1: OPERACIONES MATRICIALES BÁSICAS
# Suma, resta, escalar y multiplicación A(m×n) · B(n×p) con bucles
# anidados. Solo se usa Python estándar; cada función documenta el
# procedimiento algebraico equivalente.
# =====================================================================

def _es_matriz_valida(M):
    """Verifica que M sea una lista no vacía de listas del mismo ancho."""
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


def validar_operables_suma(A, B):
    """Exige que A y B tengan las mismas dimensiones m×n para sumar/restar."""
    ma, na = _leer_dimensiones(A)
    mb, nb = _leer_dimensiones(B)
    if ma != mb or na != nb:
        raise ValueError(
            "No se pueden sumar/restar: las dimensiones son distintas. "
            "A es " + str(ma) + "×" + str(na) + " mientras que B es "
            + str(mb) + "×" + str(nb) + ". Para sumar, ambas han de ser "
            "del mismo tamaño m×n."
        )


def sumar_matrices(A, B):
    """Suma dos matrices del mismo tamaño m×n.
    Método algebraico equivalente: la entrada (i, j) del resultado es
    C[i][j] = A[i][j] + B[i][j], con i de 1 a m y j de 1 a n."""
    _validar_matriz(A, "A")
    _validar_matriz(B, "B")
    validar_operables_suma(A, B)
    m, n = _leer_dimensiones(A)
    resultado = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(A[i][j] + B[i][j])
        resultado.append(fila)
    return resultado


def restar_matrices(A, B):
    """Resta dos matrices del mismo tamaño: A - B = A + (-1)·B.
    Método algebraico equivalente: C[i][j] = A[i][j] - B[i][j]."""
    _validar_matriz(A, "A")
    _validar_matriz(B, "B")
    validar_operables_suma(A, B)
    m, n = _leer_dimensiones(A)
    resultado = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(A[i][j] - B[i][j])
        resultado.append(fila)
    return resultado


def escalar_por_matriz(c, A):
    """Multiplica una matriz por un escalar.
    Método algebraico equivalente: cada entrada se multiplica por c,
    C[i][j] = c · A[i][j]."""
    _validar_matriz(A, "A")
    m, n = _leer_dimensiones(A)
    resultado = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(c * A[i][j])
        resultado.append(fila)
    return resultado


def validar_multiplicables(A, B):
    """Exige que el número de columnas de A sea igual al de filas de B."""
    _, nA = _leer_dimensiones(A)
    mB, _ = _leer_dimensiones(B)
    if nA != mB:
        raise ValueError(
            "No se puede multiplicar A·B: las columnas de A (" + str(nA)
            + ") deben ser iguales a las filas de B (" + str(mB)
            + "). Como A es m×n, A se multiplica a la derecha solo por "
            "matrices de tamaño n×p."
        )


def multiplicar_matrices(A, B):
    """Multiplica dos matrices A(m×n) · B(n×p), devolviendo C de tamaño m×p.
    Método algebraico equivalente (regla fila-columna) con TRES bucles
    anidados:
        para i en 1..m:                    # filas de A
            para j en 1..p:                # columnas de B
                C[i][j] = 0
                para k en 1..n:            # término común col(A)=fil(B)
                    C[i][j] = C[i][j] + A[i][k]·B[k][j]
    Es decir, el elemento (i, j) de C es el producto escalar de la fila i
    de A por la columna j de B."""
    _validar_matriz(A, "A")
    _validar_matriz(B, "B")
    validar_multiplicables(A, B)
    m, n = _leer_dimensiones(A)
    _, p = _leer_dimensiones(B)
    resultado = []
    for i in range(m):
        fila = []
        for j in range(p):
            total = Fraction(0)
            for k in range(n):
                total = total + A[i][k] * B[k][j]
            fila.append(total)
        resultado.append(fila)
    return resultado


def pasos_multiplicar_matrices(A, B):
    """Genera el texto explicativo del producto A·B mostrando la regla
    fila-columna (producto escalar) para cada entrada del resultado."""
    _validar_matriz(A, "A")
    _validar_matriz(B, "B")
    validar_multiplicables(A, B)
    m, n = _leer_dimensiones(A)
    _, p = _leer_dimensiones(B)
    lineas = ["Regla fila-columna:  C[i][j] = Σₖ A[i][k]·B[k][j]", ""]
    for i in range(m):
        for j in range(p):
            terminos = []
            for k in range(n):
                terminos.append(f"({formato(A[i][k])})({formato(B[k][j])})")
            lista = " + ".join(terminos).replace("+ -", "- ")
            lineas.append(f"C[{i+1}][{j+1}] = {lista}")
    lineas.append("")
    lineas.append("Se usan tres bucles anidados: filas de A, columnas de "
                  "B y el índice común k (col de A = fila de B).")
    return "\n".join(lineas)


def resolver_ecuacion_matricial(y, matrices):
    """Resuelve la ECUACIÓN MATRICIAL
        x₁·v₁ + x₂·v₂ + … + xₖ·vₖ = y
    donde cada vⱼ es una matriz m×n y y es otra matriz m×n.

    Procedimiento algebraico equivalente: la igualdad matricial equivale a
    igualar entrada a entrada. Para cada posición (i, j) se obtiene una
    ecuación lineal
        x₁·v₁[i][j] + x₂·v₂[i][j] + … + xₖ·vₖ[i][j] = y[i][j].
    Se 'aplastan' las m·n entradas de cada matriz para formar las columnas
    de la matriz de coeficientes y se resuelve el sistema de m·n ecuaciones
    con k incógnitas mediante Gauss-Jordan (reutiliza resolver_sistema).

    Devuelve la misma estructura que es_combinacion_lineal:
    (es_combinacion, pesos, resultado)."""
    _validar_matriz(y, "y")
    if not matrices:
        raise ValueError("Debe indicar al menos una matriz v (k ≥ 1).")
    tamano_y = _leer_dimensiones(y)
    for M in matrices:
        _validar_matriz(M, "v")
        if _leer_dimensiones(M) != tamano_y:
            raise ValueError("Todas las matrices vⱼ y la matriz y deben tener "
                             "las mismas dimensiones m×n.")
    b = [valor for fila in y for valor in fila]
    columnas = [[valor for fila in M for valor in fila] for M in matrices]
    return es_combinacion_lineal(b, columnas)


# =====================================================================
# BLOQUE V2: PANTALLA DEL MÓDULO DE VECTORES (Tkinter)
# =====================================================================

class VectoresApp:
    """Pantalla del módulo de vectores en R^n."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver

        self.var_n = tk.StringVar(value="3")   # entradas por vector
        self.var_k = tk.StringVar(value="2")   # cantidad de vectores
        self.var_escalar = tk.StringVar(value="2")
        self.celdas = {}        # (fila, columna) -> StringVar de los vectores
        self.celdas_y = {}      # fila -> StringVar del objetivo y

        self.fuente_titulo = tkfont.Font(family="Montserrat", size=22, weight="bold")
        self.fuente_sub = tkfont.Font(family="Montserrat", size=11)
        self.fuente_body = tkfont.Font(family="Montserrat", size=11)
        self.fuente_encab = tkfont.Font(family="Montserrat", size=11, weight="bold")
        self.fuente_big = tkfont.Font(family="Montserrat", size=16, weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=11, weight="bold")

        self.marco_principal = tk.Frame(self.raiz, bg=FONDO)
        self.marco_principal.pack(fill="both", expand=True)

        self.procedimiento_visible = False
        self.ultimo_resultado = None
        self.etiquetas_ajustables = []
        self.aviso_vacio = None

        self._construir_ui()
        self._construir_grid_vectores()

    # ---------- armado de la pantalla ----------
    def _construir_ui(self):
        tk.Button(self.marco_principal, text="← Volver al Menú", font=self.fuente_body,
                  bg=FONDO, fg=ACENTO, bd=0, relief="flat", cursor="hand2",
                  activeforeground=ACENTO_HOVER, command=self.volver_al_menu
                  ).grid(row=0, column=0, columnspan=2, sticky="w", padx=34, pady=(10, 0))

        tk.Label(self.marco_principal, text="Módulo de Vectores en Rⁿ",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal,
                 text="Sumar, restar, multiplicar por escalar y resolver\n"
                      "x₁v₁ + … + xₖvₖ = y (detecta si y es combinación lineal\n"
                      "y si los vectores son dependientes o independientes)",
                 font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE
                 ).grid(row=2, column=0, columnspan=2, sticky="w", padx=34, pady=(0, 12))

        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)

        # ---- panel izquierdo (entrada de datos) con scroll propio ----
        panel_izq = tk.Frame(self.marco_principal, bg=FONDO)
        panel_izq.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))
        panel_izq.rowconfigure(0, weight=1)
        panel_izq.columnconfigure(0, weight=1)

        self.lienzo_izq = tk.Canvas(panel_izq, bg=FONDO, highlightthickness=0)
        self.barra_izq = ttk.Scrollbar(panel_izq, orient="vertical",
                                       command=self.lienzo_izq.yview)
        self.lienzo_izq.configure(yscrollcommand=self.barra_izq.set)
        self.frame_izq = tk.Frame(self.lienzo_izq, bg=FONDO)
        self._ventana_izq = self.lienzo_izq.create_window((0, 0),
                                                          window=self.frame_izq, anchor="nw")
        self.frame_izq.bind("<Configure>",
                            lambda e: self.lienzo_izq.configure(
                                scrollregion=self.lienzo_izq.bbox("all")))
        self.lienzo_izq.bind("<Configure>",
                             lambda e: self.lienzo_izq.itemconfig(self._ventana_izq,
                                                                  width=e.width))
        self._activar_rueda(self.lienzo_izq)
        self.lienzo_izq.grid(row=0, column=0, sticky="nsew")
        self.barra_izq.grid(row=0, column=1, sticky="ns")

        # Tarjetas apiladas dentro del panel con scroll
        tarjeta_vect = self._crear_tarjeta(self.frame_izq)
        tarjeta_vect.pack(fill="x", pady=(0, 10))
        self._llenar_cabecera(tarjeta_vect)

        # ---- panel derecho: resultados ----
        panel_der = tk.Frame(self.marco_principal, bg=FONDO)
        panel_der.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))
        tarjeta_res = self._crear_tarjeta(panel_der)
        tarjeta_res.pack(fill="both", expand=True)

        cabecera = tk.Frame(tarjeta_res, bg=TARJETA)
        cabecera.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cabecera, text="Resultado", font=self.fuente_encab,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        self.boton_procedimiento = tk.Button(cabecera, text="Ver procedimiento",
                                             font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO,
                                             bd=0, relief="flat", cursor="hand2", padx=12, pady=4,
                                             activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO,
                                             command=self._alternar_procedimiento)

        self.aviso_vacio = tk.Label(tarjeta_res,
                                    text="Completa los vectores y elige una operación.\n"
                                         "Puedes usar enteros, decimales o fracciones.",
                                    font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                                    justify="left", anchor="nw", padx=18, pady=14)
        self.aviso_vacio.pack(fill="both", expand=True)

        self.lienzo_resultado = tk.Canvas(tarjeta_res, bg=TARJETA, highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(tarjeta_res, orient="vertical",
                                             command=self.lienzo_resultado.yview)
        self.lienzo_resultado.configure(yscrollcommand=self.barra_resultado.set)
        self.frame_resultado = tk.Frame(self.lienzo_resultado, bg=TARJETA)
        self._ventana_res = self.lienzo_resultado.create_window((0, 0),
                                                                window=self.frame_resultado,
                                                                anchor="nw")

        def al_cambiar_tamano(evento):
            self.lienzo_resultado.itemconfig(self._ventana_res, width=evento.width)
            self._ajustar_textos(evento.width)

        self.lienzo_resultado.bind("<Configure>", al_cambiar_tamano)
        self.frame_resultado.bind("<Configure>",
                                  lambda e: self.lienzo_resultado.configure(
                                      scrollregion=self.lienzo_resultado.bbox("all")))
        self._activar_rueda(self.lienzo_resultado)

    def _activar_rueda(self, lienzo):
        """Hace que la rueda del ratón mueva el scroll del lienzo indicado."""
        def al_girar(evento):
            if evento.num == 4:
                lienzo.yview_scroll(-1, "units")
            elif evento.num == 5:
                lienzo.yview_scroll(1, "units")
            else:
                lienzo.yview_scroll(-1 * (evento.delta // 120), "units")
        def al_entrar(_evento):
            lienzo.bind_all("<MouseWheel>", al_girar)
            lienzo.bind_all("<Button-4>", al_girar)
            lienzo.bind_all("<Button-5>", al_girar)
        def al_salir(_evento):
            lienzo.unbind_all("<MouseWheel>")
            lienzo.unbind_all("<Button-4>")
            lienzo.unbind_all("<Button-5>")
        lienzo.bind("<Enter>", al_entrar)
        lienzo.bind("<Leave>", al_salir)

    def _llenar_cabecera(self, tarjeta):
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))

        tk.Label(cont, text="Vectores — cada columna es un vector y la última (y), el objetivo",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        tk.Label(cont, text="Entradas (n)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_n,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._construir_grid_vectores
                   ).grid(row=1, column=1, sticky="w", padx=(0, 16))

        tk.Label(cont, text="Vectores (k)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_k,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._construir_grid_vectores
                   ).grid(row=1, column=3, sticky="w")

        def aplicar():
            self._leer_dimension(self.var_n, 3)
            self._leer_dimension(self.var_k, 3)
            self._construir_grid_vectores()

        self.boton_mas_vectores = tk.Button(
            cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO,
            relief="flat", cursor="hand2", padx=6, pady=2,
            activebackground=ACENTO_HOVER, activeforeground=FONDO,
            command=aplicar)
        self.boton_mas_vectores.grid(row=1, column=4, sticky="w", padx=(12, 0))

        botones = tk.Frame(tarjeta, bg=TARJETA)
        botones.pack(fill="x", padx=18, pady=(4, 8))
        acciones = [
            ("v₁ + v₂", self._al_sumar),
            ("v₁ − v₂", self._al_restar),
            ("x · v₁", self._al_escalar),
            ("Resolver x₁v₁ + … + xₖvₖ = y", self._al_combinacion),
            ("Limpiar", self._limpiar_vectores),
        ]
        for i, (texto, accion) in enumerate(acciones):
            tk.Button(botones, text=texto, font=("Montserrat", 10, "bold"),
                      bg=BOTON_SEC, fg=TEXTO, relief="flat", cursor="hand2",
                      padx=8, pady=7, activebackground=BOTON_SEC_HOVER,
                      command=accion).grid(row=i // 2, column=i % 2,
                                           sticky="ew", padx=3, pady=3)
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        fila_esc = tk.Frame(tarjeta, bg=TARJETA)
        fila_esc.pack(fill="x", padx=18, pady=(0, 6))
        tk.Label(fila_esc, text="Escalar x =", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        tk.Entry(fila_esc, textvariable=self.var_escalar, font=self.fuente_mono,
                 width=6, justify="center", relief="solid", bd=1
                 ).pack(side="left", padx=6)

        self.frame_vectores = tk.Frame(tarjeta, bg=TARJETA)
        self.frame_vectores.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        tk.Label(tarjeta, text=AYUDA_NUMERO, font=("Montserrat", 9),
                 bg=TARJETA, fg=TEXTO_SUAVE, wraplength=420, justify="left"
                 ).pack(anchor="w", padx=18, pady=(0, 12))

    def _limpiar_vectores(self):
        """Vacía todas las casillas de vectores y del objetivo y."""
        for variable in (list(self.celdas.values()) + list(self.celdas_y.values())):
            variable.set("")

    def _crear_tarjeta(self, padre):
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC,
                        highlightthickness=1, bd=0)

    # ---------- cuadrícula de vectores ----------
    def _leer_dimension(self, variable, por_defecto):
        try:
            valor = int(variable.get())
        except ValueError:
            valor = por_defecto
        valor = max(1, min(MAX_DIMENSION, valor))
        variable.set(str(valor))
        return valor

    def _construir_grid_vectores(self):
        n = self._leer_dimension(self.var_n, 3)
        k = self._leer_dimension(self.var_k, 2)

        previos = {c: v.get() for c, v in self.celdas.items()}
        previos_y = {c: v.get() for c, v in self.celdas_y.items()}
        for hijo in self.frame_vectores.winfo_children():
            hijo.destroy()
        self.celdas = {}
        self.celdas_y = {}

        for j in range(k):
            tk.Label(self.frame_vectores, text=con_subindice("v" + str(j + 1)),
                     font=self.fuente_encab, bg=TARJETA, fg=TEXTO
                     ).grid(row=0, column=j, padx=3, pady=(0, 4))
        tk.Label(self.frame_vectores, text="y", font=self.fuente_encab,
                 bg=TARJETA, fg=ACENTO).grid(row=0, column=k + 1, padx=(14, 3), pady=(0, 4))

        for i in range(n):
            for j in range(k):
                var = tk.StringVar(value=previos.get((i, j), ""))
                self.celdas[(i, j)] = var
                tk.Entry(self.frame_vectores, textvariable=var, font=self.fuente_mono,
                         width=6, justify="center", relief="solid", bd=1,
                         bg=CELDA_FONDO).grid(row=i + 1, column=j, padx=3, pady=2)
            var_y = tk.StringVar(value=previos_y.get(i, ""))
            self.celdas_y[i] = var_y
            tk.Entry(self.frame_vectores, textvariable=var_y, font=self.fuente_mono,
                     width=6, justify="center", relief="solid", bd=1,
                     bg=CELDA_FONDO).grid(row=i + 1, column=k + 1, padx=(14, 3), pady=2)

    # ---------- lectura de datos ----------
    def _leer_vectores(self):
        n = self._leer_dimension(self.var_n, 3)
        k = self._leer_dimension(self.var_k, 2)
        vectores = []
        for j in range(k):
            v = []
            for i in range(n):
                v.append(a_numero(self.celdas[(i, j)].get()))
            vectores.append(v)
        return vectores

    def _leer_y(self):
        n = self._leer_dimension(self.var_n, 3)
        return [a_numero(self.celdas_y[i].get()) for i in range(n)]

    # ---------- acciones ----------
    def _al_sumar(self):
        try:
            vs = self._leer_vectores()
            if len(vs) < 2:
                raise ValueError("Se necesitan al menos 2 vectores para sumar.")
            r = sumar_vectores(vs[0], vs[1])
            detalle = ("(" + formato_vector(vs[0]) + ") + (" + formato_vector(vs[1])
                       + ")\nse suma entrada por entrada:\n= "
                       + formato_vector(r))
            self._mostrar("v₁ + v₂", formato_vector(r), detalle)
        except ValueError as e:
            self._mostrar_error(str(e))

    def _al_restar(self):
        try:
            vs = self._leer_vectores()
            if len(vs) < 2:
                raise ValueError("Se necesitan al menos 2 vectores para restar.")
            r = restar_vectores(vs[0], vs[1])
            detalle = ("(" + formato_vector(vs[0]) + ") − (" + formato_vector(vs[1])
                       + ")\nv₁ − v₂ = v₁ + (−1)·v₂ (propiedad iv de Rⁿ):\n= "
                       + formato_vector(r))
            self._mostrar("v₁ − v₂", formato_vector(r), detalle)
        except ValueError as e:
            self._mostrar_error(str(e))

    def _al_escalar(self):
        try:
            c = a_numero(self.var_escalar.get())
            vs = self._leer_vectores()
            r = escalar_por_vector(c, vs[0])
            detalle = ("(" + formato(c) + ") · (" + formato_vector(vs[0])
                       + ")\ncada entrada se multiplica por el escalar:\n= "
                       + formato_vector(r))
            self._mostrar(formato(c) + " · v₁", formato_vector(r), detalle)
        except ValueError as e:
            self._mostrar_error(str(e))

    def _al_combinacion(self):
        """Resuelve x₁v₁ + … + xₖvₖ = y (combinación lineal) y, en el mismo
        resultado, muestra si los vectores son linealmente dependientes o
        independientes y por qué."""
        try:
            vs = self._leer_vectores()
            y_obj = self._leer_y()
            k = len(vs)
            es_cl, pesos, resultado = es_combinacion_lineal(y_obj, vs)
            independientes, res_ind = son_linealmente_independientes(vs)

            if not es_cl:
                titulo = "NO ES COMBINACIÓN LINEAL"
                texto = "El sistema [v₁ … vₖ | y] es inconsistente."
                detalle = ("No existen coeficientes x₁…xₖ tales que y = Σ xᵢvᵢ.\n"
                           "⟹ y ∉ Gen{v₁, …, vₖ}.")
                color = ERROR
            elif resultado["clasificacion"] == "Consistente Determinado":
                titulo = "SÍ ES COMBINACIÓN LINEAL"
                texto = "y = " + _formato_suma_lineal(pesos, "v")
                detalle = "Pesos únicos:   " + "    ".join(
                    con_subindice("x" + str(i + 1)) + " = " + formato(p)
                    for i, p in enumerate(pesos))
                color = EXITO
            else:
                libres = [con_subindice("x" + str(c + 1))
                          for c in resultado["variables_libres"]]
                titulo = "SÍ ES COMBINACIÓN LINEAL (INFINITAS FORMAS)"
                texto = "Variables libres: " + "  ".join(libres)
                detalle = resultado["verificacion"]
                color = ADVERTENCIA

            homog = " + ".join(
                con_subindice("c" + str(i + 1)) + "·"
                + con_subindice("v" + str(i + 1)) for i in range(k)) + " = 0"
            if independientes:
                nota_dep = ("\n\n{DEPENDENCIA LINEAL DEL CONJUNTO}\n\n"
                            "Ecuación homogénea:\n   " + homog + "\n\n"
                            "Al reducir [v₁ … vₖ | 0] se llega a la identidad: "
                            "pivotes = k y\nninguna variable libre, así que la "
                            "única solución es:\n   c₁ = c₂ = … = cₖ = 0\n\n"
                            "⟹ Los vectores son LINEALMENTE INDEPENDIENTES.\n"
                            "Por eso, si y es combinación, los coeficientes "
                            "resultan ÚNICOS.")
            else:
                relaciones = relacion_de_dependencia(vs)
                if relaciones:
                    rel_txt = "\n".join(
                        "   " + _formato_suma_lineal(rel, "v") + " = 0"
                        for rel in relaciones)
                else:
                    rel_txt = ("   existen coeficientes c₁…cₖ no todos nulos\n"
                               "   con " + homog)
                nota_dep = ("\n\n{DEPENDENCIA LINEAL DEL CONJUNTO}\n\n"
                            "Ecuación homogénea:\n   " + homog + "\n\n"
                            "Al reducir [v₁ … vₖ | 0] quedan variables libres.\n"
                            "Relación de dependencia encontrada:\n" + rel_txt
                            + "\n\n"
                            "⟹ Los vectores son LINEALMENTE DEPENDIENTES.\n"
                            "Por eso, si y es combinación, hay INFINITAS formas "
                            "de escribirla.")

            detalle = detalle + nota_dep

            pasos_totales = list(resultado["pasos"])
            pasos_totales.append("")
            pasos_totales.append("DEPENDENCIA LINEAL (SISTEMA HOMOGÉNEO [v₁ … vₖ | 0]):")
            pasos_totales.extend(res_ind["pasos"])

            self._mostrar(titulo, texto, detalle, color=color,
                          pasos=pasos_totales)
        except ValueError as e:
            self._mostrar_error(str(e))

    # ---------- panel de resultado ----------
    def _limpiar_resultado(self):
        """Destruye el aviso inicial, muestra el scroll y borra resultados."""
        if self.aviso_vacio is not None:
            try:
                self.aviso_vacio.destroy()
            except Exception:
                pass
            self.aviso_vacio = None
            self.lienzo_resultado.pack(side="left", fill="both", expand=True,
                                       padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))
        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = []
        self.procedimiento_visible = False

    def _texto_ajustable(self, etiqueta):
        self.etiquetas_ajustables.append(etiqueta)
        return etiqueta

    def _ajustar_textos(self, ancho_disponible=None):
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(240, ancho_disponible - 56)
        for etiqueta in self.etiquetas_ajustables:
            try:
                etiqueta.configure(wraplength=ancho)
            except tk.TclError:
                pass

    def _mostrar(self, titulo, texto, detalle="", color=ACENTO, pasos=None):
        """Muestra un resultado con su título coloreado y la descripción.
        Si pasos contiene el procedimiento Gauss-Jordan, se puede mostrar
        u ocultar con el botón «Ver procedimiento»."""
        if self.aviso_vacio is not None:
            try:
                self.aviso_vacio.destroy()
            except Exception:
                pass
            self.aviso_vacio = None
            self.lienzo_resultado.pack(side="left", fill="both", expand=True,
                                       padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))

        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = []
        self.ultimo_resultado = {"titulo": titulo, "texto": texto, "pasos": pasos}
        self.procedimiento_visible = False

        if pasos:
            self.boton_procedimiento.pack(side="right")
            self.boton_procedimiento.configure(text="Ver procedimiento")
        else:
            self.boton_procedimiento.pack_forget()

        tk.Label(self.frame_resultado, text=titulo, font=self.fuente_encab,
                 bg=color, fg="#FFFFFF", padx=12, pady=8, anchor="w"
                 ).pack(fill="x", pady=(0, 10))
        self._texto_ajustable(
            tk.Label(self.frame_resultado, text=texto, font=self.fuente_big,
                     bg=TARJETA, fg=TEXTO, wraplength=440, justify="left"
                     )).pack(anchor="w", pady=(0, 8))
        if detalle:
            self._texto_ajustable(
                tk.Label(self.frame_resultado, text=detalle,
                         font=self.fuente_mono, bg=TARJETA, fg=TEXTO_SUAVE,
                         wraplength=440, justify="left", anchor="w"
                         )).pack(anchor="w", pady=(0, 4))

        self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA)
        tk.Label(self.sub_procedimiento, text="PROCESO DE ELIMINACIÓN (GAUSS-JORDAN)",
                 font=self.fuente_encab, bg=TARJETA, fg=TEXTO_SUAVE, anchor="w"
                 ).pack(fill="x", padx=2, pady=(6, 2))
        texto_proc = "\n".join(pasos) if pasos else "(sin procedimiento)"
        self._texto_ajustable(
            tk.Label(self.sub_procedimiento, text=texto_proc,
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w"
                     )).pack(fill="x", pady=(0, 10))

        self.raiz.update_idletasks()
        self._ajustar_textos()

    def _alternar_procedimiento(self):
        if not self.ultimo_resultado or not self.ultimo_resultado.get("pasos"):
            return
        if self.procedimiento_visible:
            self.sub_procedimiento.pack_forget()
            self.boton_procedimiento.configure(text="Ver procedimiento")
            self.procedimiento_visible = False
        else:
            self.sub_procedimiento.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
            self.boton_procedimiento.configure(text="Ocultar procedimiento")
            self.procedimiento_visible = True
        self.raiz.update_idletasks()
        self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all"))

    def _mostrar_error(self, mensaje):
        self._mostrar("Revisá los datos", mensaje, "", color=ERROR, pasos=None)

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


class MenuPrincipal:
    """Pantalla inicial del sistema para elegir el módulo."""
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Calculadora de Álgebra Lineal - Proyecto UAM")
        self.raiz.configure(bg=FONDO)
       
        # La ventana se adapta a la pantalla del equipo: pide el tamaño
        # cómodo, pero nunca más de lo que cabe. Con un tamaño fijo pequeño
        # la matriz queda cortada y había que desplazarse para verla.
        ancho = min(1300, self.raiz.winfo_screenwidth() - 80)
        alto = min(840, self.raiz.winfo_screenheight() - 120)
        self.raiz.geometry(f"{max(1120, ancho)}x{max(700, alto)}")
        self.raiz.minsize(1120, 700)
        self._centrar_ventana()
       
        self.frame_menu = tk.Frame(self.raiz, bg=FONDO)
        self.frame_menu.pack(fill="both", expand=True)
       
        tk.Label(self.frame_menu, text="¡Bienvenido a la mejor Calculadora!", font=("Montserrat", 26, "bold"), bg=FONDO, fg=TEXTO).pack(pady=(150, 10))
        tk.Label(self.frame_menu, text="Proyecto de Álgebra Lineal", font=("Montserrat", 16), bg=FONDO, fg=TEXTO_SUAVE).pack(pady=(0, 40))
        tk.Label(self.frame_menu, text="Selecciona el módulo en el que quieres trabajar:", font=("Montserrat", 13), bg=FONDO, fg=TEXTO).pack(pady=(0, 20))
       
        btn_matrices = tk.Button(self.frame_menu, text="Ecuaciones Matriciales (Ax = b)", font=("Montserrat", 13, "bold"),
                                 bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                 activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_calculadora)
        btn_matrices.pack(pady=10)

        btn_vectores = tk.Button(self.frame_menu, text="Vectores en ℝⁿ", font=("Montserrat", 13, "bold"),
                                 bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                 activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_vectores)
        btn_vectores.pack(pady=10)

        btn_matriz_ops = tk.Button(self.frame_menu, text="Operaciones Matriciales", font=("Montserrat", 13, "bold"),
                                   bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                   activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_matrices_ops)
        btn_matriz_ops.pack(pady=10)


        tk.Label(self.frame_menu, text="Desarrollado por Grupo 2 • Universidad Americana (UAM)", font=("Montserrat", 10), bg=FONDO, fg=TEXTO_SUAVE).pack(side="bottom", pady=40)


    def abrir_calculadora(self):
        self.frame_menu.pack_forget()
        CalculadoraApp(self.raiz, callback_volver=self.mostrar_menu)
       
    def abrir_vectores(self):
        self.frame_menu.pack_forget()
        VectoresApp(self.raiz, callback_volver=self.mostrar_menu)

    def abrir_matrices_ops(self):
        self.frame_menu.pack_forget()
        MatricesOpsApp(self.raiz, callback_volver=self.mostrar_menu)

    def mostrar_menu(self):
        for widget in self.raiz.winfo_children():
            widget.destroy()
        self.__init__(self.raiz)


    def _centrar_ventana(self):
        self.raiz.update_idletasks()
        ancho = self.raiz.winfo_width()
        alto = self.raiz.winfo_height()
        x = max(0, (self.raiz.winfo_screenwidth() - ancho) // 2)
        y = max(0, (self.raiz.winfo_screenheight() - alto) // 2)
        self.raiz.geometry(f"+{x}+{y}")




class CalculadoraApp:
    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver
       
        self.var_m = tk.StringVar(value="3")
        self.var_n = tk.StringVar(value="3")
        self.celdas = {}
        self.entradas = {}
        self.filas_actuales = 0
        self.columnas_actuales = 0
        self.procedimiento_visible = False
        self.ultimo_resultado = None
        self.etiquetas_ajustables = []
        self.celda_con_error = None   # casilla marcada por un valor inválido


        self.fuente_titulo = tkfont.Font(family="Montserrat", size=22, weight="bold")
        self.fuente_sub = tkfont.Font(family="Montserrat", size=11)
        self.fuente_body = tkfont.Font(family="Montserrat", size=11)
        self.fuente_encab = tkfont.Font(family="Montserrat", size=11, weight="bold")
        self.fuente_big = tkfont.Font(family="Montserrat", size=17, weight="bold")
        self.fuente_cartel = tkfont.Font(family="Montserrat", size=15, weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=12, weight="bold")


        self.marco_principal = tk.Frame(self.raiz, bg=FONDO)
        self.marco_principal.pack(fill="both", expand=True)


        self._construir_ui()
        self._construir_grid_matriz()


    def _construir_ui(self):
        btn_volver = tk.Button(self.marco_principal, text="← Volver al Menú", font=self.fuente_body,
                               bg=FONDO, fg=ACENTO, bd=0, relief="flat", cursor="hand2", activeforeground=ACENTO_HOVER, command=self.volver_al_menu)
        btn_volver.grid(row=0, column=0, sticky="w", padx=34, pady=(10, 0))


        tk.Label(self.marco_principal, text="Ecuaciones Matriciales (Ax = b)",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal, text="Resolver sistemas Ax = b por eliminación por filas (Gauss-Jordan)", font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE).grid(row=2, column=0, columnspan=2, sticky="w", padx=34, pady=(0, 14))


        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)


        panel_izq = tk.Frame(self.marco_principal, bg=FONDO)
        panel_izq.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))


        tarjeta_ecuaciones = self._crear_tarjeta(panel_izq)
        tarjeta_ecuaciones.pack(side="top", fill="x", pady=(0, 10))
        self._llenar_ecuaciones(tarjeta_ecuaciones)


        self.boton_resolver = tk.Button(panel_izq, text="Resolver Sistema", font=self.fuente_boton, bg=ACENTO, fg=FONDO, cursor="hand2", relief="flat", padx=18, pady=12, activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self._al_resolver)
        self.boton_resolver.pack(side="bottom", fill="x", pady=(10, 0))


        tarjeta_matriz = self._crear_tarjeta(panel_izq)
        tarjeta_matriz.pack(side="top", fill="both", expand=True)
        self._llenar_cabecera_matriz(tarjeta_matriz)


        contenedor_matriz = tk.Frame(tarjeta_matriz, bg=TARJETA)
        contenedor_matriz.pack(fill="both", expand=True, padx=(6, 6), pady=(0, 10))
        contenedor_matriz.rowconfigure(0, weight=1)
        contenedor_matriz.columnconfigure(0, weight=1)


        lienzo_matriz = tk.Canvas(contenedor_matriz, bg=TARJETA, highlightthickness=0, width=400, height=150)
        barra_v = ttk.Scrollbar(contenedor_matriz, orient="vertical", command=lienzo_matriz.yview)
        barra_h = ttk.Scrollbar(contenedor_matriz, orient="horizontal", command=lienzo_matriz.xview)
        lienzo_matriz.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
       
        self.frame_matriz = tk.Frame(lienzo_matriz, bg=TARJETA)
        lienzo_matriz.create_window((0, 0), window=self.frame_matriz, anchor="nw")
        self.frame_matriz.bind("<Configure>", lambda e: lienzo_matriz.configure(scrollregion=lienzo_matriz.bbox("all")))
        self.lienzo_matriz = lienzo_matriz
        self._activar_rueda(lienzo_matriz)


        lienzo_matriz.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")


        panel_der = tk.Frame(self.marco_principal, bg=FONDO)
        panel_der.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))


        tarjeta_resultado = self._crear_tarjeta(panel_der)
        tarjeta_resultado.pack(fill="both", expand=True)


        cabecera = tk.Frame(tarjeta_resultado, bg=TARJETA)
        cabecera.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cabecera, text="Resultado", font=self.fuente_sub, bg=TARJETA, fg=TEXTO).pack(side="left")


        self.boton_procedimiento = tk.Button(cabecera, text="Ver procedimiento", font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO, bd=0, relief="flat", cursor="hand2", padx=12, pady=4, activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO, command=self._alternar_procedimiento)


        self.aviso_vacio = tk.Label(tarjeta_resultado, text="Complete las dimensiones y la matriz aumentada a la izquierda,\ny luego pulse «Resolver Sistema».", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, justify="left", anchor="nw", padx=18, pady=14)
        self.aviso_vacio.pack(fill="both", expand=True)


        self.lienzo_resultado = tk.Canvas(tarjeta_resultado, bg=TARJETA, highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(tarjeta_resultado, orient="vertical", command=self.lienzo_resultado.yview)
        self.lienzo_resultado.configure(yscrollcommand=self.barra_resultado.set)


        self.frame_resultado = tk.Frame(self.lienzo_resultado, bg=TARJETA)
        ventana_resultado = self.lienzo_resultado.create_window((0, 0), window=self.frame_resultado, anchor="nw")
       
        def al_cambiar_tamano(evento):
            self.lienzo_resultado.itemconfig(ventana_resultado, width=evento.width)
            self._ajustar_textos(evento.width)


        self.lienzo_resultado.bind("<Configure>", al_cambiar_tamano)
        self.frame_resultado.bind("<Configure>", lambda e: self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all")))
        self._activar_rueda(self.lienzo_resultado)
       
    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


    def _ajustar_textos(self, ancho_disponible=None):
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(240, ancho_disponible - 56)
        for etiqueta in self.etiquetas_ajustables:
            try: etiqueta.configure(wraplength=ancho)
            except tk.TclError: pass


    def _texto_ajustable(self, etiqueta):
        self.etiquetas_ajustables.append(etiqueta)
        return etiqueta


    def _activar_rueda(self, lienzo):
        def al_girar(evento):
            if evento.num == 4: lienzo.yview_scroll(-1, "units")
            elif evento.num == 5: lienzo.yview_scroll(1, "units")
            else: lienzo.yview_scroll(-1 * (evento.delta // 120), "units")
        def al_entrar(_evento):
            lienzo.bind_all("<MouseWheel>", al_girar)
            lienzo.bind_all("<Button-4>", al_girar)
            lienzo.bind_all("<Button-5>", al_girar)
        def al_salir(_evento):
            lienzo.unbind_all("<MouseWheel>")
            lienzo.unbind_all("<Button-4>")
            lienzo.unbind_all("<Button-5>")
        lienzo.bind("<Enter>", al_entrar)
        lienzo.bind("<Leave>", al_salir)


    def _crear_tarjeta(self, padre):
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC, highlightthickness=1, bd=0)


    def _llenar_ecuaciones(self, tarjeta):
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 14))


        tk.Label(cont, text="Sistema de ecuaciones", font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w").pack(fill="x", pady=(0, 2))
        tk.Label(cont, text="Una ecuación por línea; las que falten valen 0.", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, anchor="w", justify="left", wraplength=420).pack(fill="x", pady=(0, 6))
       
        self.caja_ecuaciones = tk.Text(cont, height=4, font=self.fuente_mono, bg=FONDO, fg=TEXTO, relief="solid", bd=1, highlightthickness=1, highlightbackground=BOTON_SEC, highlightcolor=ACENTO, wrap="none", padx=8, pady=6)
        self.caja_ecuaciones.pack(fill="x")
        self.caja_ecuaciones.insert("1.0", SISTEMA_INICIAL)


        botones = tk.Frame(cont, bg=TARJETA)
        botones.pack(fill="x", pady=(8, 0))
       
        self._boton_secundario(botones, "Convertir a matriz", self._convertir_ecuaciones, 0, 0)
        self._boton_secundario(botones, "Borrar", self._borrar_ecuaciones, 0, 1)


        self.aviso_ecuaciones = tk.Label(cont, text="", font=self.fuente_body, bg=TARJETA, fg=EXITO, anchor="w")
        self.aviso_ecuaciones.pack(fill="x", pady=(4, 0))


    def _borrar_ecuaciones(self):
        self.caja_ecuaciones.delete("1.0", "end")
        self.aviso_ecuaciones.configure(text="")


    def _convertir_ecuaciones(self):
        try:
            texto = self.caja_ecuaciones.get("1.0", "end")
            A, b, nombres = interpretar_ecuaciones(texto)
            filas, columnas = len(A), len(nombres)
           
            if filas > MAX_DIMENSION or columnas > MAX_DIMENSION:
                raise ValueError(f"El sistema es muy grande. El límite es {MAX_DIMENSION}x{MAX_DIMENSION}.")


            self.var_m.set(str(filas))
            self.var_n.set(str(columnas))
            self._construir_grid_matriz()
            self._limpiar_celdas()
           
            for i in range(filas):
                for j in range(columnas):
                    self.celdas[(i, j)].set(formato(A[i][j]))
                self.celdas[(i, columnas)].set(formato(b[i]))


            self.aviso_ecuaciones.configure(fg=EXITO, text=f"Listo: {filas} ecuaciones y {columnas} variables detectadas.")
        except ValueError as error:
            self.aviso_ecuaciones.configure(fg=ERROR, text=str(error))
        except Exception as error:
            self.aviso_ecuaciones.configure(fg=ERROR, text=f"Error inesperado: {error}")


    def _boton_secundario(self, padre, texto, accion, fila=0, columna=0):
        boton = tk.Button(padre, text=texto, font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO, bd=0, relief="flat", cursor="hand2", padx=10, pady=4, activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO, command=accion)
        boton.grid(row=fila, column=columna, sticky="w", padx=(0, 8), pady=(0, 4))
        return boton


    def _llenar_cabecera_matriz(self, tarjeta):
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))


        tk.Label(cont, text="Matriz aumentada [A | b] — ingrese los coeficientes", font=self.fuente_sub, bg=TARJETA, fg=TEXTO).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))


        tk.Label(cont, text="Ecuaciones (m)", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 8))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_m, width=4, justify="center", bg=FONDO, fg=TEXTO, relief="solid", bd=1, highlightthickness=1, highlightbackground=BOTON_SEC, highlightcolor=ACENTO, command=self._construir_grid_matriz).grid(row=1, column=1, sticky="w", padx=(0, 18))


        tk.Label(cont, text="Variables (n)", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 8))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_n, width=4, justify="center", bg=FONDO, fg=TEXTO, relief="solid", bd=1, highlightthickness=1, highlightbackground=BOTON_SEC, highlightcolor=ACENTO, command=self._construir_grid_matriz).grid(row=1, column=3, sticky="w")

        def crecer_sistema():
            self._leer_dimension(self.var_m, 3)
            self._leer_dimension(self.var_n, 3)
            self._construir_grid_matriz()

        self.boton_mas_sistema = tk.Button(cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO, relief="flat", cursor="hand2", padx=6, pady=2, activebackground=ACENTO_HOVER, activeforeground=FONDO, command=crecer_sistema)
        self.boton_mas_sistema.grid(row=1, column=4, sticky="w", padx=(12, 0))


        botones = tk.Frame(cont, bg=TARJETA)
        botones.grid(row=2, column=0, columnspan=5, sticky="w", pady=(8, 0))
        self._boton_secundario(botones, "Limpiar", self._limpiar_celdas, 0, 0)


    def _leer_dimension(self, variable, por_defecto):
        try: valor = int(str(variable.get()).strip())
        except: valor = por_defecto
        valor = max(1, min(MAX_DIMENSION, valor))
        variable.set(str(valor))
        return valor


    def _construir_grid_matriz(self):
        m = self._leer_dimension(self.var_m, 3)
        n = self._leer_dimension(self.var_n, 3)
        valores_previos = {clave: var.get() for clave, var in self.celdas.items()}


        for hijo in self.frame_matriz.winfo_children(): hijo.destroy()
        self.celdas, self.entradas = {}, {}
        self.filas_actuales, self.columnas_actuales = m, n


        # **** La matriz se dibuja como una tabla continua ****
        # Las casillas no llevan borde propio: entre ellas se intercalan
        # marcos de un píxel que hacen de líneas. Las columnas pares de la
        # cuadrícula son líneas y las impares son casillas; lo mismo con
        # las filas. Así se ve como una matriz escrita a mano y no como
        # cuadritos sueltos.
        #
        #   columna 0      borde izquierdo        fila 0        encabezados
        #   columna 2j+1   casillas de la col. j  fila 1        borde superior
        #   columna 2n     barra que separa A|b   fila 2i+2     ecuación i+1
        #   columna 2n+2   borde derecho          fila 2m+1     borde inferior


        total_columnas = n + 1
        columna_celda = lambda j: 2 * j + 1
        filas_del_marco = 2 * m + 1


        # Encabezados de columna, por encima del marco
        for j in range(n):
            tk.Label(self.frame_matriz, text=nombre_variable(j+1), font=self.fuente_sub,
                     bg=TARJETA, fg=TEXTO_SUAVE).grid(row=0, column=columna_celda(j), pady=(0, 4))
        tk.Label(self.frame_matriz, text="b", font=self.fuente_sub,
                 bg=TARJETA, fg=ACENTO).grid(row=0, column=columna_celda(n), pady=(0, 4))


        # Líneas verticales: bordes, separadores y la barra de [A|b]
        for j in range(total_columnas + 1):
            es_barra_ab = (j == n)
            tk.Frame(self.frame_matriz,
                     width=3 if es_barra_ab else 1,
                     bg=BARRA_AB if es_barra_ab else LINEA_MATRIZ
                     ).grid(row=1, column=2 * j, rowspan=filas_del_marco, sticky="ns")


        # Líneas horizontales: bordes e intermedios
        for i in range(m + 1):
            for j in range(total_columnas):
                tk.Frame(self.frame_matriz, height=1, bg=LINEA_MATRIZ
                         ).grid(row=2 * i + 1, column=columna_celda(j), sticky="ew")


        # Casillas de entrada, pegadas unas a otras
        for i in range(m):
            for j in range(total_columnas):
                variable = tk.StringVar(value=valores_previos.get((i, j), ""))
                self.celdas[(i, j)] = variable
                entrada = tk.Entry(self.frame_matriz, textvariable=variable,
                                   font=self.fuente_mono, width=6, justify="center",
                                   relief="flat", bd=0, highlightthickness=0,
                                   bg=CELDA_FONDO, fg=TEXTO, insertbackground=TEXTO)
                entrada.grid(row=2 * i + 2, column=columna_celda(j), sticky="nsew", ipady=4)
                entrada.bind("<Return>", lambda e: self._al_resolver())
                clave = (i, j)
                entrada.bind("<FocusIn>", lambda e, c=clave: self._pintar_celda(c, True))
                entrada.bind("<FocusOut>", lambda e, c=clave: self._pintar_celda(c, False))
                entrada.bind("<KeyRelease>", lambda e, c=clave: self._al_teclear(c))
                self.entradas[clave] = entrada


    def _pintar_celda(self, clave, enfocada):
        """Resalta la casilla activa. Como las casillas ya no tienen borde
        propio, sin esto se pierde de vista dónde está el cursor. No toca
        la casilla marcada con error."""
        if clave == self.celda_con_error:
            return
        entrada = self.entradas.get(clave)
        if entrada is not None:
            entrada.configure(bg=CELDA_FOCO if enfocada else CELDA_FONDO)


    def _al_teclear(self, clave):
        """Quita la marca de error en cuanto el usuario corrige la casilla."""
        if clave == self.celda_con_error:
            self.celda_con_error = None
            entrada = self.entradas.get(clave)
            if entrada is not None:
                entrada.configure(bg=CELDA_FOCO)


    def _limpiar_celdas(self):
        for variable in self.celdas.values(): variable.set("")
        self._restaurar_bordes()


    def _al_resolver(self):
        try:
            m, n = self.filas_actuales, self.columnas_actuales
            A, b = [], []
            for i in range(m):
                fila = []
                for j in range(n):
                    try: fila.append(a_numero(self.celdas[(i, j)].get()))
                    except ValueError as error:
                        self._mostrar_error(f"Revisa la casilla fila {i+1}, columna {nombre_variable(j+1)}.", i, j)
                        return
                A.append(fila)
                try: b.append(a_numero(self.celdas[(i, n)].get()))
                except ValueError as error:
                    self._mostrar_error(f"Revisa el vector 'b' de la fila {i+1}.", i, n)
                    return


            self._restaurar_bordes()
            resultado = resolver_sistema(m, n, A, b)
            self.ultimo_resultado = resultado
            self._mostrar_resultado(resultado)


        except Exception as error:
            messagebox.showerror("Error inesperado", f"Ocurrió un problema:\n{error}")


    def _restaurar_bordes(self):
        """Devuelve todas las casillas a su color de fondo normal."""
        self.celda_con_error = None
        for entrada in self.entradas.values():
            entrada.configure(bg=CELDA_FONDO)


    def _mostrar_error(self, mensaje, fila, columna):
        """Avisa del error y pinta de rojo claro la casilla con el problema.
        Como las casillas ya no tienen borde propio, el error se señala con
        el color de fondo."""
        self._restaurar_bordes()
        entrada = self.entradas.get((fila, columna))
        if entrada:
            self.celda_con_error = (fila, columna)
            entrada.configure(bg=CELDA_ERROR)
            entrada.focus_set()
            entrada.selection_range(0, "end")
        messagebox.showerror("Entrada inválida", mensaje)


    def _limpiar_resultado(self):
        if self.aviso_vacio and self.aviso_vacio.winfo_manager():
            self.aviso_vacio.destroy()
            self.aviso_vacio = None
            self.lienzo_resultado.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))
        for hijo in self.frame_resultado.winfo_children(): hijo.destroy()
        self.etiquetas_ajustables = []


    def _sub_tarjeta(self, titulo, color):
        sub = tk.Frame(self.frame_resultado, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
        tk.Label(sub, text=titulo, font=self.fuente_encab, bg=TARJETA, fg=color, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        return sub


    def _mostrar_resultado(self, resultado):
        self._limpiar_resultado()
        self.boton_procedimiento.pack(side="right")


        clasificacion = resultado["clasificacion"]
        color = EXITO if clasificacion == "Consistente Determinado" else ADVERTENCIA if clasificacion == "Consistente Indeterminado" else ERROR


        # ================= RESULTADO =================
        sub = self._sub_tarjeta("CLASIFICACIÓN DEL SISTEMA", TEXTO_SUAVE)
        cartel = tk.Frame(sub, bg=color, padx=14, pady=10)
        cartel.pack(fill="x", pady=(0, 4))
        self._texto_ajustable(tk.Label(cartel, text=clasificacion.upper(), font=self.fuente_cartel, bg=color, fg=FONDO)).pack(fill="x")
        self._texto_ajustable(tk.Label(sub, text=resultado["descripcion"], font=self.fuente_body, bg=TARJETA, fg=TEXTO)).pack(fill="x", pady=(0, 6))


        # --- TABLA DE DATOS (TEOREMA DE ROUCHÉ) ---
        marco_tabla = tk.Frame(sub, bg="#00bcd4", bd=1)
        marco_tabla.pack(pady=10)


        for i, (campo, valor) in enumerate(resultado["datos_resumen"]):
            celda_izq = tk.Label(marco_tabla, text=campo, bg="#e0f7fa", fg="black",
                                 width=20, anchor="w", padx=8, pady=5,
                                 borderwidth=1, relief="solid", font=("Arial", 10))
            celda_izq.grid(row=i, column=0, sticky="nsew")
           
            celda_der = tk.Label(marco_tabla, text=valor, bg="white", fg="black",
                                 width=35, anchor="center", padx=8, pady=5,
                                 borderwidth=1, relief="solid", font=("Arial", 10))
            celda_der.grid(row=i, column=1, sticky="nsew")


        if resultado["solucion"] is not None:
            sub2 = self._sub_tarjeta("SOLUCIÓN DEL SISTEMA", ACENTO)
            contenedor = tk.Frame(sub2, bg=FONDO, padx=12, pady=10)
            contenedor.pack(fill="x", pady=(0, 8))
            texto_solucion = "     ".join(f"{nombre_variable(i+1)} = {formato(v)}" for i, v in enumerate(resultado["solucion"]))
            self._texto_ajustable(tk.Label(contenedor, text=texto_solucion, font=self.fuente_big, bg=FONDO, fg=TEXTO)).pack(fill="x")
       
        elif clasificacion == "Consistente Indeterminado":
            sub2 = self._sub_tarjeta("VARIABLES LIBRES", ADVERTENCIA)
            nombres = "   ".join(nombre_variable(c+1) for c in resultado["variables_libres"])
            tk.Label(sub2, text="Soluciones dadas en función de:", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE).pack(fill="x")
            self._texto_ajustable(tk.Label(sub2, text=nombres, font=self.fuente_big, bg=TARJETA, fg=TEXTO)).pack(fill="x", pady=(4, 8))


        sub3 = self._sub_tarjeta("VERIFICACIÓN AUTOMÁTICA", EXITO)
        self._texto_ajustable(tk.Label(sub3, text=resultado["verificacion"], font=self.fuente_mono, bg=TARJETA, fg=TEXTO, justify="left", anchor="w")).pack(fill="x", pady=(0, 8))


        # ================= PROCEDIMIENTO =================
        self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA)
        tk.Label(self.sub_procedimiento, text="PROCESO DE ELIMINACIÓN (GAUSS-JORDAN)", font=self.fuente_encab, bg=TARJETA, fg=TEXTO_SUAVE, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
       
        self._texto_ajustable(tk.Label(self.sub_procedimiento, text="\n".join(resultado["pasos"]), font=self.fuente_mono, bg=TARJETA, fg=TEXTO, justify="left", anchor="w")).pack(fill="x", pady=(0, 10))


        self.procedimiento_visible = False
        self.boton_procedimiento.configure(text="Ver procedimiento")
        self.lienzo_resultado.yview_moveto(0)
        self.raiz.update_idletasks()
        self._ajustar_textos()


    def _alternar_procedimiento(self):
        if not self.ultimo_resultado: return
        if self.procedimiento_visible:
            self.sub_procedimiento.pack_forget()
            self.boton_procedimiento.configure(text="Ver procedimiento")
            self.procedimiento_visible = False
        else:
            self.sub_procedimiento.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
            self.boton_procedimiento.configure(text="Ocultar procedimiento")
            self.procedimiento_visible = True
        self.raiz.update_idletasks()
        self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all"))


# =====================================================================
# BLOQUE M2: PANTALLA DE OPERACIONES MATRICIALES (Tkinter)
# =====================================================================

class MatricesOpsApp:
    """Pantalla del módulo de operaciones matriciales básicas:
    suma, resta, multiplicación por escalar y producto A·B, siempre
    validando las dimensiones de las matrices."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver

        self.var_ma = tk.StringVar(value="2")   # filas de A
        self.var_na = tk.StringVar(value="2")   # columnas de A
        self.var_mb = tk.StringVar(value="2")   # filas de B
        self.var_nb = tk.StringVar(value="2")   # columnas de B
        self.var_escalar = tk.StringVar(value="2")
        self.celdas_A = {}
        self.celdas_B = {}
        self.celda_con_error = None

        self.fuente_titulo = tkfont.Font(family="Montserrat", size=22, weight="bold")
        self.fuente_sub = tkfont.Font(family="Montserrat", size=11)
        self.fuente_body = tkfont.Font(family="Montserrat", size=11)
        self.fuente_encab = tkfont.Font(family="Montserrat", size=11, weight="bold")
        self.fuente_big = tkfont.Font(family="Montserrat", size=16, weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=11, weight="bold")

        self.marco_principal = tk.Frame(self.raiz, bg=FONDO)
        self.marco_principal.pack(fill="both", expand=True)

        self.procedimiento_visible = False
        self.ultimo_resultado = None
        self.sub_procedimiento = None
        self.etiquetas_ajustables = []
        self.aviso_vacio = None
        self.botones_mas = {}

        self._construir_ui()
        self._construir_grids()

    def _construir_ui(self):
        tk.Button(self.marco_principal, text="← Volver al Menú", font=self.fuente_body,
                  bg=FONDO, fg=ACENTO, bd=0, relief="flat", cursor="hand2",
                  activeforeground=ACENTO_HOVER, command=self.volver_al_menu
                  ).grid(row=0, column=0, columnspan=2, sticky="w", padx=34, pady=(10, 0))

        tk.Label(self.marco_principal, text="Módulo de Operaciones Matriciales",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal,
                 text="Sumar, restar, multiplicar por escalar y producto A·B "
                      "(se validan siempre las dimensiones)",
                 font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE
                 ).grid(row=2, column=0, columnspan=2, sticky="w", padx=34, pady=(0, 12))

        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)

        # ---- panel izquierdo (entrada) con scroll ----
        panel_izq = tk.Frame(self.marco_principal, bg=FONDO)
        panel_izq.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))
        panel_izq.rowconfigure(0, weight=1)
        panel_izq.columnconfigure(0, weight=1)

        self.lienzo_izq = tk.Canvas(panel_izq, bg=FONDO, highlightthickness=0)
        self.barra_izq = ttk.Scrollbar(panel_izq, orient="vertical",
                                       command=self.lienzo_izq.yview)
        self.lienzo_izq.configure(yscrollcommand=self.barra_izq.set)
        self.frame_izq = tk.Frame(self.lienzo_izq, bg=FONDO)
        self._ventana_izq = self.lienzo_izq.create_window((0, 0),
                                                          window=self.frame_izq, anchor="nw")
        self.frame_izq.bind("<Configure>",
                            lambda e: self.lienzo_izq.configure(
                                scrollregion=self.lienzo_izq.bbox("all")))
        self.lienzo_izq.bind("<Configure>",
                             lambda e: self.lienzo_izq.itemconfig(self._ventana_izq,
                                                                  width=e.width))
        self._activar_rueda(self.lienzo_izq)
        self.lienzo_izq.grid(row=0, column=0, sticky="nsew")
        self.barra_izq.grid(row=0, column=1, sticky="ns")

        tarjeta_A = self._llenar_cabecera_matriz("Matriz A", self.var_ma, self.var_na,
                                                 self.frame_izq, "A")
        self.frame_A = tk.Frame(tarjeta_A, bg=TARJETA)
        self.frame_A.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        tarjeta_B = self._llenar_cabecera_matriz("Matriz B", self.var_mb, self.var_nb,
                                                 self.frame_izq, "B")
        self.frame_B = tk.Frame(tarjeta_B, bg=TARJETA)
        self.frame_B.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        self._llenar_botones(self.frame_izq)

        # ---- panel derecho (resultados) ----
        panel_der = tk.Frame(self.marco_principal, bg=FONDO)
        panel_der.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))
        tarjeta_res = self._crear_tarjeta(panel_der)
        tarjeta_res.pack(fill="both", expand=True)

        cabecera = tk.Frame(tarjeta_res, bg=TARJETA)
        cabecera.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cabecera, text="Resultado", font=self.fuente_encab,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        self.boton_procedimiento = tk.Button(cabecera, text="Ver procedimiento",
                                             font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO,
                                             bd=0, relief="flat", cursor="hand2", padx=12, pady=4,
                                             activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO,
                                             command=self._alternar_procedimiento)

        self.aviso_vacio = tk.Label(tarjeta_res,
                                    text="Completa las matrices A y B y elige una operación.\n"
                                         "Puedes usar enteros, decimales o fracciones.",
                                    font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                                    justify="left", anchor="nw", padx=18, pady=14)
        self.aviso_vacio.pack(fill="both", expand=True)

        self.lienzo_resultado = tk.Canvas(tarjeta_res, bg=TARJETA, highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(tarjeta_res, orient="vertical",
                                             command=self.lienzo_resultado.yview)
        self.lienzo_resultado.configure(yscrollcommand=self.barra_resultado.set)
        self.frame_resultado = tk.Frame(self.lienzo_resultado, bg=TARJETA)
        self._ventana_res = self.lienzo_resultado.create_window((0, 0),
                                                                window=self.frame_resultado,
                                                                anchor="nw")

        def al_cambiar_tamano(evento):
            self.lienzo_resultado.itemconfig(self._ventana_res, width=evento.width)
            self._ajustar_textos(evento.width)

        self.lienzo_resultado.bind("<Configure>", al_cambiar_tamano)
        self.frame_resultado.bind("<Configure>",
                                  lambda e: self.lienzo_resultado.configure(
                                      scrollregion=self.lienzo_resultado.bbox("all")))
        self._activar_rueda(self.lienzo_resultado)

    def _crear_tarjeta(self, padre):
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC,
                        highlightthickness=1, bd=0)

    def _activar_rueda(self, lienzo):
        def al_girar(evento):
            if evento.num == 4:
                lienzo.yview_scroll(-1, "units")
            elif evento.num == 5:
                lienzo.yview_scroll(1, "units")
            else:
                lienzo.yview_scroll(-1 * (evento.delta // 120), "units")
        def al_entrar(_evento):
            lienzo.bind_all("<MouseWheel>", al_girar)
            lienzo.bind_all("<Button-4>", al_girar)
            lienzo.bind_all("<Button-5>", al_girar)
        def al_salir(_evento):
            lienzo.unbind_all("<MouseWheel>")
            lienzo.unbind_all("<Button-4>")
            lienzo.unbind_all("<Button-5>")
        lienzo.bind("<Enter>", al_entrar)
        lienzo.bind("<Leave>", al_salir)

    def _leer_dimension(self, variable, por_defecto):
        try:
            valor = int(variable.get())
        except Exception:
            valor = por_defecto
        valor = max(1, min(MAX_DIMENSION, valor))
        variable.set(str(valor))
        return valor

    def _llenar_cabecera_matriz(self, titulo, var_m, var_n, padre, letra):
        """Construye una tarjeta con título, spinboxes de dimensiones y un
        botón pequeño «＋» que agrega una fila y una columna a la vez.
        Devuelve la tarjeta (la cuadrícula se dibuja en self.frame_*)."""
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cont, text=titulo, font=self.fuente_sub, bg=TARJETA, fg=TEXTO,
                 anchor="w").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))
        tk.Label(cont, text="Filas", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=var_m,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._construir_grids).grid(row=1, column=1, sticky="w", padx=(0, 16))
        tk.Label(cont, text="Columnas", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=var_n,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._construir_grids).grid(row=1, column=3, sticky="w")

        def aplicar():
            self._leer_dimension(var_m, 2)
            self._leer_dimension(var_n, 2)
            self._construir_grids()

        self.botones_mas[letra] = tk.Button(
            cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO,
            relief="flat", cursor="hand2", padx=6, pady=2,
            activebackground=ACENTO_HOVER, activeforeground=FONDO, command=aplicar)
        self.botones_mas[letra].grid(row=0, column=4, sticky="e", padx=(8, 0), pady=(0, 8))
        return tarjeta

    def _construir_grids(self):
        """Redibuja las cuadrículas de A y B conservando los valores previos."""
        previos_A = {c: v.get() for c, v in self.celdas_A.items()}
        previos_B = {c: v.get() for c, v in self.celdas_B.items()}

        def dibujar(frame, celdas, m, n, previos, letra):
            for hijo in frame.winfo_children():
                hijo.destroy()
            celdas.clear()
            for j in range(n):
                tk.Label(frame, text=con_subindice(letra + str(j + 1)),
                         font=self.fuente_encab, bg=TARJETA, fg=TEXTO
                         ).grid(row=0, column=j, padx=3, pady=(0, 4))
            for i in range(m):
                for j in range(n):
                    var = tk.StringVar(value=previos.get((i, j), ""))
                    celdas[(i, j)] = var
                    tk.Entry(frame, textvariable=var, font=self.fuente_mono,
                             width=6, justify="center", relief="solid", bd=1,
                             bg=CELDA_FONDO).grid(row=i + 1, column=j, padx=3, pady=2)

        ma = self._leer_dimension(self.var_ma, 2)
        na = self._leer_dimension(self.var_na, 2)
        mb = self._leer_dimension(self.var_mb, 2)
        nb = self._leer_dimension(self.var_nb, 2)
        dibujar(self.frame_A, self.celdas_A, ma, na, previos_A, "a")
        dibujar(self.frame_B, self.celdas_B, mb, nb, previos_B, "b")

    def _llenar_botones(self, padre):
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))

        fila = tk.Frame(cont, bg=TARJETA)
        fila.pack(fill="x", pady=(0, 8))
        tk.Label(fila, text="Escalar x =", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        tk.Entry(fila, textvariable=self.var_escalar, font=self.fuente_mono,
                 width=6, justify="center", relief="solid", bd=1).pack(side="left", padx=6)

        botones = tk.Frame(cont, bg=TARJETA)
        botones.pack(fill="x")
        acciones = [
            ("Sumar", self._al_sumar),
            ("Restar", self._al_restar),
            ("Multiplicar por escalar", self._al_escalar),
            ("Multiplicar matrices", self._al_producto),
            ("Limpiar", self._limpiar_matrices),
        ]
        for i, (texto, accion) in enumerate(acciones):
            tk.Button(botones, text=texto, font=("Montserrat", 10, "bold"),
                      bg=BOTON_SEC, fg=TEXTO, relief="flat", cursor="hand2",
                      padx=8, pady=7, activebackground=BOTON_SEC_HOVER,
                      command=accion).grid(row=i // 2, column=i % 2, sticky="ew", padx=3, pady=3)
        botones.columnconfigure(0, weight=1)
        botones.columnconfigure(1, weight=1)

        tk.Label(tarjeta, text=AYUDA_NUMERO, font=("Montserrat", 9),
                 bg=TARJETA, fg=TEXTO_SUAVE, wraplength=420, justify="left"
                 ).pack(anchor="w", padx=18, pady=(0, 12))

    def _leer_matriz(self, celdas, m, n, nombre):
        matriz = []
        for i in range(m):
            fila = []
            for j in range(n):
                try:
                    fila.append(a_numero(celdas[(i, j)].get()))
                except ValueError:
                    raise ValueError(
                        "Revisa la matriz " + nombre + ", celda fila "
                        + str(i + 1) + ", columna " + str(j + 1) + ".")
            matriz.append(fila)
        return matriz

    def _limpiar_matrices(self):
        for variable in (list(self.celdas_A.values()) + list(self.celdas_B.values())):
            variable.set("")

    # ---------- acciones ----------
    def _al_sumar(self):
        try:
            self._construir_grids()   # sincroniza las dimensiones escritas
            A = self._leer_matriz(self.celdas_A, self._leer_dimension(self.var_ma, 2),
                                  self._leer_dimension(self.var_na, 2), "A")
            B = self._leer_matriz(self.celdas_B, self._leer_dimension(self.var_mb, 2),
                                  self._leer_dimension(self.var_nb, 2), "B")
            C = sumar_matrices(A, B)
            self._mostrar_matriz("A + B", C,
                                 "C[i][j] = A[i][j] + B[i][j]  "
                                 "(se requiere que A y B tengan las mismas dimensiones).")
        except ValueError as e:
            self._mostrar_error(str(e))

    def _al_restar(self):
        try:
            self._construir_grids()
            A = self._leer_matriz(self.celdas_A, self._leer_dimension(self.var_ma, 2),
                                  self._leer_dimension(self.var_na, 2), "A")
            B = self._leer_matriz(self.celdas_B, self._leer_dimension(self.var_mb, 2),
                                  self._leer_dimension(self.var_nb, 2), "B")
            C = restar_matrices(A, B)
            self._mostrar_matriz("A − B", C,
                                 "C[i][j] = A[i][j] − B[i][j]  "
                                 "(A − B = A + (−1)·B).")
        except ValueError as e:
            self._mostrar_error(str(e))

    def _al_escalar(self):
        try:
            c = a_numero(self.var_escalar.get())
            self._construir_grids()
            A = self._leer_matriz(self.celdas_A, self._leer_dimension(self.var_ma, 2),
                                  self._leer_dimension(self.var_na, 2), "A")
            C = escalar_por_matriz(c, A)
            self._mostrar_matriz("x · A", C,
                                 "C[i][j] = x · A[i][j]  (cada entrada se multiplica por el escalar x).")
        except ValueError as e:
            self._mostrar_error(str(e))

    def _al_producto(self):
        try:
            self._construir_grids()
            A = self._leer_matriz(self.celdas_A, self._leer_dimension(self.var_ma, 2),
                                  self._leer_dimension(self.var_na, 2), "A")
            B = self._leer_matriz(self.celdas_B, self._leer_dimension(self.var_mb, 2),
                                  self._leer_dimension(self.var_nb, 2), "B")
            C = multiplicar_matrices(A, B)
            self._mostrar_matriz("A · B", C,
                                 "C[i][j] = Σₖ A[i][k]·B[k][j]  (regla fila-columna).",
                                 pasos=pasos_multiplicar_matrices(A, B))
        except ValueError as e:
            self._mostrar_error(str(e))

    # ---------- panel de resultados ----------
    def _ajustar_textos(self, ancho_disponible=None):
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(240, ancho_disponible - 56)
        for etiqueta in self.etiquetas_ajustables:
            try:
                etiqueta.configure(wraplength=ancho)
            except tk.TclError:
                pass

    def _texto_ajustable(self, etiqueta):
        self.etiquetas_ajustables.append(etiqueta)
        return etiqueta

    def _sub_tarjeta(self, titulo, color):
        sub = tk.Frame(self.frame_resultado, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
        tk.Label(sub, text=titulo, font=self.fuente_encab, bg=TARJETA,
                 fg=color, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        return sub

    def _mostrar_matriz(self, titulo, C, detalle="", pasos=None):
        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        if self.aviso_vacio is not None:
            self.aviso_vacio.destroy()
            self.aviso_vacio = None
            self.lienzo_resultado.pack(side="left", fill="both", expand=True,
                                       padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))
        self.etiquetas_ajustables = []
        self.procedimiento_visible = False
        self.sub_procedimiento = None

        sub = self._sub_tarjeta("RESULTADO", ACENTO)
        cartel = tk.Frame(sub, bg=ACENTO, padx=14, pady=10)
        cartel.pack(fill="x", pady=(0, 6))
        self._texto_ajustable(tk.Label(cartel, text=titulo, font=self.fuente_big,
                                       bg=ACENTO, fg=FONDO)).pack(fill="x")
        filas = _leer_dimensiones(C)
        self._texto_ajustable(tk.Label(sub, text="Matriz resultante de tamaño "
                                       + str(filas[0]) + "×" + str(filas[1]),
                                       font=self.fuente_body, bg=TARJETA,
                                       fg=TEXTO_SUAVE)).pack(fill="x", pady=(0, 4))
        self._texto_ajustable(tk.Label(sub, text="\n".join(formato_matriz(C)),
                                       font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                                       justify="left", anchor="w")).pack(fill="x", pady=(0, 6))
        if detalle:
            self._texto_ajustable(tk.Label(sub, text=detalle, font=self.fuente_body,
                                           bg=TARJETA, fg=TEXTO_SUAVE, justify="left",
                                           anchor="w", wraplength=480)).pack(fill="x",
                                                                             pady=(0, 8))

        self.ultimo_resultado = {"titulo": titulo, "matriz": C, "pasos": pasos}
        self.boton_procedimiento.configure(text="Ver procedimiento")
        if pasos:
            self.boton_procedimiento.pack(side="right")
        else:
            self.boton_procedimiento.pack_forget()

        self.lienzo_resultado.yview_moveto(0)
        self.raiz.update_idletasks()
        self._ajustar_textos()

    def _alternar_procedimiento(self):
        if not self.ultimo_resultado or not self.ultimo_resultado.get("pasos"):
            return
        if self.procedimiento_visible and self.sub_procedimiento is not None:
            self.sub_procedimiento.pack_forget()
            self.boton_procedimiento.configure(text="Ver procedimiento")
            self.procedimiento_visible = False
        else:
            self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA)
            tk.Label(self.sub_procedimiento, text="PROCEDIMIENTO DEL PRODUCTO A·B",
                     font=self.fuente_encab, bg=TARJETA, fg=TEXTO_SUAVE,
                     anchor="w").pack(fill="x", padx=2, pady=(6, 2))
            self._texto_ajustable(tk.Label(self.sub_procedimiento,
                                           text=self.ultimo_resultado["pasos"],
                                           font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                                           justify="left", anchor="w")).pack(fill="x",
                                                                             pady=(0, 10))
            self.sub_procedimiento.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
            self.boton_procedimiento.configure(text="Ocultar procedimiento")
            self.procedimiento_visible = True
        self.raiz.update_idletasks()
        self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all"))

    def _mostrar_error(self, mensaje):
        messagebox.showerror("Operación no válida", mensaje)

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


# =====================================================================
# BLOQUE 7: PRUEBAS AUTOMÁTICAS DEL ALGORITMO
# Estos son los casos de prueba internos. Nos sirven para asegurar
# que ninguna actualización que hagamos dañe la matemática del programa.
# Validan sistemas Ax=b, operaciones vectoriales y operaciones
# matriciales, y corren por detrás en la consola.
# =====================================================================


def ejecutar_pruebas():
    """Ejecuta los sistemas predefinidos y verifica que el algoritmo funciona."""
    pruebas = [
        ("Caso 1: solución única", [[1, 1, 1], [2, -1, 1], [1, 2, -1]], [6, 3, 2], "Consistente Determinado", ["1", "2", "3"]),
        ("Caso 2: infinitas", [[1, 1, 1], [2, 2, 2]], [1, 2], "Consistente Indeterminado", None),
        ("Caso 3: inconsistente", [[1, 1], [1, 1]], [1, 3], "Inconsistente", None),
        ("Clase Lay", [[1, -2, 1], [0, 2, -8], [-4, 5, 9]], [0, 8, -9], "Consistente Determinado", ["29", "16", "3"]),
        ("Actividad 1", [[2, 3, 1], [5, 3, 4], [1, 1, -1]], [1, 2, 1], "Consistente Determinado", ["2/3", "0", "-1/3"]),
        ("Inconsistente Clase", [[0, 1, -4], [2, -3, 2], [5, -8, 7]], [8, 1, 1], "Inconsistente", None),
        ("Matriz 5x5", [[1, 2, 0, 1, 1], [0, 1, 1, 0, 0], [0, 0, 1, 1, -1], [0, 0, 0, 1, 2], [0, 0, 0, 0, 1]], [4, 2, 3, 5, 1], "Consistente Determinado", ["-2", "1", "1", "3", "1"]),
        ("Homogéneo", [[1, 1, 1], [2, -1, 0]], [0, 0], "Consistente Indeterminado", None),
        ("Ceros", [[0, 0], [0, 0]], [0, 0], "Consistente Indeterminado", None),
        ("Imposible", [[0]], [7], "Inconsistente", None),
        ("Intercambio necesario", [[0, 1], [1, 0]], [2, 3], "Consistente Determinado", ["3", "2"]),
        ("Más ecuaciones", [[1, 0], [0, 1], [1, 1]], [1, 2, 3], "Consistente Determinado", ["1", "2"]),
        ("Más ecuaciones, incompatible", [[1, 0], [0, 1], [1, 1]], [1, 2, 4], "Inconsistente", None),
        ("Fracciones", [["1/2", "1/3"], ["1/4", "1/5"]], [1, 1], "Consistente Determinado", ["-8", "15"]),
        ("Más incógnitas", [[1, 2, 3]], [6], "Consistente Indeterminado", None),
    ]


    fallos = 0
    print("=" * 64)
    print("INICIANDO PRUEBAS AUTOMÁTICAS DEL ALGORITMO")
    print("=" * 64)


    for nombre, A, b, clasificacion_esperada, solucion_esperada in pruebas:
        A = [[a_numero(str(valor)) for valor in fila] for fila in A]
        b = [a_numero(str(valor)) for valor in b]
        resultado = resolver_sistema(len(A), len(A[0]), A, b)


        problemas = []
        if resultado["clasificacion"] != clasificacion_esperada:
            problemas.append(f"Clasificó como {resultado['clasificacion']} pero se esperaba {clasificacion_esperada}")
        if solucion_esperada is not None:
            obtenida = [formato(valor) for valor in resultado["solucion"]]
            if obtenida != solucion_esperada:
                problemas.append(f"Solución {obtenida} en vez de {solucion_esperada}")
       
        correcta, motivo = es_escalonada(resultado["escalonada"])
        if not correcta:
            problemas.append(f"Fallo al escalonar: {motivo}")
       
        if "FALLO" in resultado["verificacion"]:
            problemas.append("La verificación de la solución falló")


        if problemas:
            fallos += 1
            print(f"[FALLA] {nombre}")
            for p in problemas: print(f"         - {p}")
        else:
            print(f"[  OK  ] {nombre}")


    # =================================================================
    # PRUEBAS DEL MÓDULO DE VECTORES
    # =================================================================
    print("--------------------------------")
    print("PRUEBAS DEL MÓDULO DE VECTORES")
    print("--------------------------------")

    def probar(nombre, ok, detalle=""):
        nonlocal fallos
        if not ok:
            fallos += 1
            print(f"[FALLA] {nombre}   {detalle}")
        else:
            print(f"[  OK  ] {nombre}")

    def fr(valor):
        return a_numero(str(valor))

    # Combinación lineal única: ¿b=(7,4,-3) es combinación de a1 y a2?
    a1 = [fr(1), fr(-2), fr(-5)]
    a2 = [fr(2), fr(5), fr(6)]
    b5 = [fr(7), fr(4), fr(-3)]
    es_cl, pesos, res5 = es_combinacion_lineal(b5, [a1, a2])
    probar("Combinación lineal única", es_cl and pesos == [fr(3), fr(2)],
           f"pesos={pesos}")
    probar("Expresión b=3·a1+2·a2",
           _formato_suma_lineal(pesos, "v") == "3·v\u2081 + 2·v\u2082",
           f"expr={_formato_suma_lineal(pesos, 'v')}")

    # Independientes (RREF = identidad)
    v1 = [fr(1), fr(-2), fr(3)]
    v2 = [fr(2), fr(-2), fr(0)]
    v3 = [fr(0), fr(1), fr(7)]
    ind_e1, res_e1 = son_linealmente_independientes([v1, v2, v3])
    probar("Independientes (RREF = identidad)", ind_e1
           and len(res_e1["variables_libres"]) == 0)

    # Dependientes: x3 libre, relación 2v1+3v2-v3=0
    w1 = [fr(1), fr(-3), fr(0)]
    w2 = [fr(3), fr(0), fr(4)]
    w3 = [fr(11), fr(-6), fr(12)]
    ind_e2, res_e2 = son_linealmente_independientes([w1, w2, w3])
    rels = relacion_de_dependencia([w1, w2, w3])
    probar("Dependientes (x3 libre)", (not ind_e2)
           and res_e2["variables_libres"] == [2])
    probar("Relación dependencia 2v1+3v2-v3=0",
           len(rels) == 1 and rels[0] == [fr(2), fr(3), fr(-1)],
           f"rels={rels}")

    # Dependientes: columnas homogéneas, x3 libre
    p1 = [fr(1), fr(0), fr(0)]
    p2 = [fr(0), fr(1), fr(0)]
    p3 = [fr(2), fr(3), fr(0)]
    ind_p8, res_p8 = son_linealmente_independientes([p1, p2, p3])
    rels_p8 = relacion_de_dependencia([p1, p2, p3])
    probar("Columnas homogéneas dependientes", (not ind_p8)
           and res_p8["variables_libres"] == [2])
    probar("Columnas homogéneas relación correcta",
           len(rels_p8) == 1 and rels_p8[0] == [fr(2), fr(3), fr(-1)],
           f"rels={rels_p8}")

    # Producto matriz-vector A·x (regla fila-vector)
    Aprod = [[fr(1), fr(2), fr(3)], [fr(4), fr(5), fr(6)]]
    xprod = [fr(1), fr(2), fr(3)]
    bprod = matriz_por_vector(Aprod, xprod)
    probar("Producto A·x (14, 32)", bprod == [fr(14), fr(32)], f"b={bprod}")

    # Validación de dimensiones incompatibles en A·x
    try:
        matriz_por_vector([[fr(1), fr(2)]], [fr(1)])
        probar("A·x dimensiones incompatibles", False, "No lanzó ValueError")
    except ValueError:
        probar("A·x dimensiones incompatibles", True)

    # Suma / resta / escalar de vectores
    u = [fr(1), fr(2), fr(3)]
    vv = [fr(4), fr(5), fr(6)]
    probar("Suma de vectores", sumar_vectores(u, vv) == [fr(5), fr(7), fr(9)])
    probar("Resta de vectores", restar_vectores(u, vv) == [fr(-3), fr(-3), fr(-3)])
    probar("Escalar por vector", escalar_por_vector(fr(-2), u) == [fr(-2), fr(-4), fr(-6)])


    # =================================================================
    # PRUEBAS DEL MÓDULO DE OPERACIONES MATRICIALES
    # =================================================================
    print("--------------------------------")
    print("PRUEBAS DE OPERACIONES MATRICIALES")
    print("--------------------------------")

    # Suma / resta / escalar de matrices
    A1 = [[fr(1), fr(2)], [fr(3), fr(4)]]
    B1 = [[fr(5), fr(6)], [fr(7), fr(8)]]
    probar("Suma 2x2", sumar_matrices(A1, B1) == [[fr(6), fr(8)], [fr(10), fr(12)]])
    probar("Resta 2x2", restar_matrices(B1, A1) == [[fr(4), fr(4)], [fr(4), fr(4)]])
    probar("Escalar por matriz",
           escalar_por_matriz(fr(3), A1) == [[fr(3), fr(6)], [fr(9), fr(12)]])

    # Multiplicación de matrices (bucles anidados)
    probar("Producto 2x2", multiplicar_matrices(A1, B1) == [[fr(19), fr(22)], [fr(43), fr(50)]])
    A3 = [[fr(1), fr(2), fr(3)], [fr(4), fr(5), fr(6)]]
    B3 = [[fr(7), fr(8)], [fr(9), fr(10)], [fr(11), fr(12)]]
    probar("Producto 2x3 * 3x2",
           multiplicar_matrices(A3, B3) == [[fr(58), fr(64)], [fr(139), fr(154)]])
    probar("Producto 1x3 * 3x1",
           multiplicar_matrices([[fr(1), fr(2), fr(3)]], [[fr(4)], [fr(5)], [fr(6)]])
           == [[fr(32)]])

    # Dimensiones incompatibles
    try:
        sumar_matrices([[fr(1), fr(2)]], [[fr(1), fr(2), fr(3)]])
        probar("Suma dimensiones incompatibles", False, "No lanzó ValueError")
    except ValueError:
        probar("Suma dimensiones incompatibles", True)
    try:
        multiplicar_matrices([[fr(1), fr(2)]], [[fr(1), fr(2), fr(3)]])
        probar("Producto dimensiones incompatibles", False, "No lanzó ValueError")
    except ValueError:
        probar("Producto dimensiones incompatibles", True)

    # Ecuación matricial x₁v₁ + x₂v₂ + … + xₖvₖ = y (combinación de matrices)
    # Caso del ejercicio de la diapositiva: v1=(3,-2), v2=(7,3), v3=(-2,1),
    # y=(0,0). Tres vectores en R^2 => dependientes (infinitas formas).
    ec1, p1c, r1c = resolver_ecuacion_matricial(
        [[fr(0)], [fr(0)]],
        [[[fr(3)], [fr(-2)]], [[fr(7)], [fr(3)]], [[fr(-2)], [fr(1)]]])
    probar("Ecuación diapositiva (dependiente, infinitas)",
           ec1 and r1c["clasificacion"] == "Consistente Indeterminado"
           and r1c["variables_libres"] != [],
           f"clase={r1c['clasificacion']}")

    # Caso determinado: v1=(1,0), v2=(0,1), y=(3,-2)  ->  x1=3, x2=-2
    ec2, p2c, r2c = resolver_ecuacion_matricial(
        [[fr(3)], [fr(-2)]],
        [[[fr(1)], [fr(0)]], [[fr(0)], [fr(1)]]])
    probar("Ecuación 2x1 determinada (x1=3, x2=-2)",
           ec2 and p2c == [fr(3), fr(-2)] and r2c["clasificacion"] == "Consistente Determinado",
           f"pesos={p2c}")

    # Caso sin solución: v1=(1,2), v2=(2,4), y=(1,0)  -> inconsistente
    try:
        ec3, _, r3c = resolver_ecuacion_matricial(
            [[fr(1)], [fr(0)]],
            [[[fr(1)], [fr(2)]], [[fr(2)], [fr(4)]]])
        probar("Ecuación sin solución", (not ec3) and r3c["clasificacion"] == "Inconsistente")
    except ValueError as e:
        probar("Ecuación sin solución", False, str(e))

    # Caso con matrices 2x2: x1·[[1,0],[0,1]] + x2·[[0,1],[1,0]] = [[2,3],[3,2]]
    ec4, p4c, r4c = resolver_ecuacion_matricial(
        [[fr(2), fr(3)], [fr(3), fr(2)]],
        [[[fr(1), fr(0)], [fr(0), fr(1)]], [[fr(0), fr(1)], [fr(1), fr(0)]]])
    probar("Ecuación con matrices 2x2 (x1=2, x2=3)",
           ec4 and p4c == [fr(2), fr(3)] and r4c["clasificacion"] == "Consistente Determinado",
           f"pesos={p4c}")

    # Dimensiones distintas dentro de la ecuación matricial
    try:
        resolver_ecuacion_matricial(
            [[fr(2)], [fr(3)]],
            [[[fr(1), fr(1)]], [[fr(2), fr(2)]]])
        probar("Ecuación dimensiones distintas", False, "No lanzó ValueError")
    except ValueError:
        probar("Ecuación dimensiones distintas", True)


    print("=" * 64)
    if fallos == 0:
        print("¡Excelente! Todas las comprobaciones pasaron correctamente.")
    else:
        print(f"Alerta: Se encontraron {fallos} fallos matemáticos.")
    print("=" * 64)
    return fallos


# =====================================================================
# PUNTO DE ENTRADA
# Solo le decimos a Python que abra
# la ventana del menú principal y mantenga la aplicación ejecutándose.
# =====================================================================
def main():
    if "--pruebas" in sys.argv:
        sys.exit(1 if ejecutar_pruebas() else 0)


    raiz = tk.Tk()
    app = MenuPrincipal(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()