# -*- coding: utf-8 -*-
"""
Módulo 5 de la Calculadora de Álgebra Lineal: Factorización LU.

Obtiene la factorización A = L·U mediante operaciones elementales de
reemplazo de fila (Fᵢ ← Fᵢ − l·Fⱼ), donde L es una matriz triangular
inferior m×m con unos en la diagonal que guarda los multiplicadores de
eliminación y U es la forma escalonada de A (m×n). Con la factorización
verifica L·U = A y, para matrices cuadradas n×n, resuelve A·x = b en dos
etapas: sustitución hacia adelante (L·y = b) y hacia atrás (U·x = y).

Temas de clase: eliminación de Gauss (Sesión 5) y factorización de
matrices (Sesión 12). Reutiliza el motor de reducción por filas y el
producto matricial ya programados en la Calculadora.

Elaborado por el Grupo #2: Marian Alejandra Guillén Castillo,
Chelsea Yosmara Quintanilla Blandón, José Cristo Carvallo Herrera y
Gabriela Suyen Espinoza Rodríguez.

Restricción cumplida: solo Python estándar (fractions, tkinter).
No se usan NumPy, SciPy ni funciones de álgebra lineal de math.
"""

from fractions import Fraction
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

from modulos import (
    FONDO, TARJETA, TEXTO, TEXTO_SUAVE, ACENTO, ACENTO_HOVER,
    BOTON_SEC, BOTON_SEC_HOVER, CELDA_FONDO, EXITO, ERROR, ADVERTENCIA,
    LETRA_MONO, MAX_DIMENSION,
    a_numero, formato, formato_matriz, con_subindice,
    _validar_matriz, _leer_dimensiones, LOGO_LU,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_matriz,
    leer_vector, mostrar_matriz, pausa, preguntar,
)
from modulos.modulo_sistemas import escalonar
from modulos.modulo_matrices import multiplicar_matrices
from modulos.modulo_determinantes import validar_cuadrada
from teoremas.resumen_teoremas import mostrar_teoremas, texto_teoremas


# El mensaje exacto que pide el enunciado cuando hace falta pivoteo.
MENSAJE_SIN_PERMUTACION = (
    "La matriz no admite Factorización LU sin permutación "
    "(requiere pivoteo parcial PA = LU)"
)


# =====================================================================
# BLOQUE 1: CÁLCULO DE LA FACTORIZACIÓN (funciones puras)
# =====================================================================

def factorizar_lu(A):
    """Factoriza A = L·U sin pivoteo y devuelve (L, U, pasos).

    Recibe la matriz A (m×n) como listas anidadas. Reduce A a su forma
    escalonada U aplicando únicamente operaciones de reemplazo de fila
    Fᵢ ← Fᵢ − l·Fⱼ y registra cada multiplicador l = a_eliminar/pivote en
    la posición (i, j) de L. L es triangular inferior m×m con unos en la
    diagonal. Si un pivote diagonal es cero y haría falta intercambiar
    filas, lanza ValueError con el mensaje de pivoteo parcial.
    """
    _validar_matriz(A, "A")
    filas, columnas = _leer_dimensiones(A)

    # U arranca como copia de A; L arranca como la identidad m×m.
    U = [[Fraction(valor) for valor in fila] for fila in A]
    L = [[Fraction(0)] * filas for _ in range(filas)]
    for i in range(filas):
        L[i][i] = Fraction(1)

    pasos = ["Matriz A original:"]
    pasos.extend(formato_matriz(A))
    pasos.append("")

    fila_pivote = 0
    for col in range(columnas):
        if fila_pivote >= filas:
            break

        pivote = U[fila_pivote][col]
        if pivote == 0:
            # Si hay un valor abajo en esta columna, habría que intercambiar
            # filas, y eso cambia la factorización salvo que se arrastre P.
            hay_valor_abajo = any(U[f][col] != 0
                                  for f in range(fila_pivote + 1, filas))
            if hay_valor_abajo:
                raise ValueError(MENSAJE_SIN_PERMUTACION)
            # Columna sin pivote: se salta y se sigue con la siguiente.
            continue

        # Generar ceros por debajo con reemplazo de fila.
        for f in range(fila_pivote + 1, filas):
            if U[f][col] != 0:
                multiplicador = U[f][col] / pivote
                # Se registra el multiplicador en L ANTES de alterar la fila
                # de U, porque ésa es justamente la entrada que se elimina.
                L[f][fila_pivote] = multiplicador
                U[f] = [U[f][c] - multiplicador * U[fila_pivote][c]
                        for c in range(columnas)]
                pasos.append(
                    "l(" + str(f + 1) + "," + str(fila_pivote + 1) + ") = "
                    + formato(multiplicador) + "   ->   F" + str(f + 1)
                    + " = F" + str(f + 1) + " - (" + formato(multiplicador)
                    + ")·F" + str(fila_pivote + 1))
                pasos.extend(formato_matriz(U))
                pasos.append("")

        fila_pivote += 1

    return L, U, pasos


def verificar_factorizacion(A, L, U):
    """Comprueba L·U = A multiplicando las dos matrices.

    Devuelve (producto, se_cumple), donde producto es L·U ya calculado
    (lista anidada) y se_cumple indica si coincide con A.
    """
    producto = multiplicar_matrices(L, U)
    se_cumple = producto == [[Fraction(valor) for valor in fila] for fila in A]
    return producto, se_cumple


def _producto_visible(a, b):
    """Escribe un producto con los dos factores entre paréntesis, para que
    se vea de dónde sale cada término: (-1)·(3)."""
    return "(" + formato(a) + ")·(" + formato(b) + ")"


def _unir_suma(valores):
    """Une valores con signos + y − legibles: 4 + 3 − 1."""
    return " + ".join(formato(valor) for valor in valores).replace("+ -", "- ")


def _lineas_cuentas_factorizacion(A, L, U):
    """Cuentas fila-columna del producto L·U, una línea por entrada.

    Se usa dentro de las tarjetas de la interfaz; devuelve solo las cuentas,
    sin encabezados ni matrices, para no repetir la respuesta.
    """
    producto = multiplicar_matrices(L, U)
    filas, columnas = _leer_dimensiones(A)
    comun = len(L[0])               # columnas de L = filas de U
    lineas = []
    for i in range(filas):
        for j in range(columnas):
            terminos = [_producto_visible(L[i][k], U[k][j])
                        for k in range(comun)]
            valores = [L[i][k] * U[k][j] for k in range(comun)]
            lineas.append(
                "(L·U)[" + str(i + 1) + "][" + str(j + 1) + "] = "
                + " + ".join(terminos).replace("+ -", "- ")
                + " = " + _unir_suma(valores)
                + " = " + formato(producto[i][j]))
    return lineas


def _lineas_comparacion_factorizacion(A, L, U):
    """Compara L·U con A entrada por entrada. Devuelve (lineas, se_cumple)."""
    producto = multiplicar_matrices(L, U)
    filas, columnas = _leer_dimensiones(A)
    izquierdas = ["a[" + str(i + 1) + "][" + str(j + 1) + "] = "
                  + formato(A[i][j])
                  for i in range(filas) for j in range(columnas)]
    derechas = ["(L·U)[" + str(i + 1) + "][" + str(j + 1) + "] = "
                + formato(producto[i][j])
                for i in range(filas) for j in range(columnas)]
    ancho = max(len(texto) for texto in izquierdas + derechas) + 4

    lineas = ["Comparación entrada por entrada:"]
    se_cumple = True
    posicion = 0
    for i in range(filas):
        for j in range(columnas):
            coincide = producto[i][j] == Fraction(A[i][j])
            se_cumple = se_cumple and coincide
            marca = "✓" if coincide else "✗"
            lineas.append("    " + izquierdas[posicion].ljust(ancho)
                          + derechas[posicion].ljust(ancho) + marca)
            posicion += 1
    return lineas, se_cumple


def _lineas_cuentas_solucion(A, x, b):
    """Cuentas fila-vector del producto A·x, una línea por componente."""
    filas, columnas = _leer_dimensiones(A)
    producto = [sum((A[i][j] * x[j] for j in range(columnas)), Fraction(0))
                for i in range(filas)]
    lineas = []
    for i in range(filas):
        terminos = [_producto_visible(A[i][j], x[j]) for j in range(columnas)]
        valores = [A[i][j] * x[j] for j in range(columnas)]
        coincide = producto[i] == Fraction(b[i])
        marca = "✓" if coincide else "✗"
        lineas.append(
            "(A·x)[" + str(i + 1) + "] = "
            + " + ".join(terminos).replace("+ -", "- ")
            + " = " + _unir_suma(valores)
            + " = " + formato(producto[i])
            + "    |  b[" + str(i + 1) + "] = " + formato(b[i])
            + "    " + marca)
    return lineas


def pasos_comprobar_factorizacion(A, L, U):
    """Desarrolla la multiplicación L·U entrada por entrada y la compara con A.

    Devuelve una lista de líneas con la regla fila-columna, la cuenta de cada
    entrada del producto, la matriz L·U, la matriz A, la comparación posición
    por posición (✓/✗) y el veredicto. Sirve para VER que la factorización es
    correcta en lugar de dar por hecho el mensaje.
    """
    _validar_matriz(A, "A")
    _validar_matriz(L, "L")
    _validar_matriz(U, "U")
    producto = multiplicar_matrices(L, U)

    lineas = ["=" * 60, "COMPROBACIÓN 1: A = L · U", "=" * 60, ""]
    lineas.append("Regla fila-columna: (L·U)[i][j] = Σₖ L[i][k]·U[k][j]")
    lineas.append("")
    lineas += _lineas_cuentas_factorizacion(A, L, U)
    lineas += ["", "Matriz L·U:", *formato_matriz(producto), "",
               "Matriz A:", *formato_matriz(A), ""]

    comparacion, se_cumple = _lineas_comparacion_factorizacion(A, L, U)
    lineas += comparacion
    lineas.append("")
    if se_cumple:
        lineas.append("La factorización es correcta (L · U == A).")
    else:
        lineas.append("¡Atención! L · U no coincide con A.")
    return lineas


def pasos_comprobar_solucion(A, x, b):
    """Desarrolla el producto A·x fila por fila y lo compara con b.

    Devuelve una lista de líneas con la regla fila-vector, la cuenta de cada
    componente, el vector calculado A·x, el vector original b, la comparación
    (✓/✗) y el veredicto. Sirve para VER que A·x = b es cierto.
    """
    _validar_matriz(A, "A")
    filas, columnas = _leer_dimensiones(A)
    if len(x) != columnas:
        raise ValueError("El vector x debe tener " + str(columnas)
                         + " componente(s), igual al número de columnas de A.")
    if len(b) != filas:
        raise ValueError("El vector b debe tener " + str(filas)
                         + " componente(s), igual al número de filas de A.")

    producto = [sum((A[i][j] * x[j] for j in range(columnas)), Fraction(0))
                for i in range(filas)]

    lineas = ["=" * 60, "COMPROBACIÓN 2: A · x = b", "=" * 60, ""]
    lineas.append("Solución x = " + formato_vector(x))
    lineas.append("Vector b   = " + formato_vector(b))
    lineas.append("")
    lineas.append("Regla fila-vector: (A·x)[i] = Σⱼ A[i][j]·x[j]")
    lineas.append("")
    lineas += _lineas_cuentas_solucion(A, x, b)

    lineas += ["", "Vector calculado A·x = " + formato_vector(producto),
               "Vector original   b  = " + formato_vector(b), ""]
    if producto == [Fraction(valor) for valor in b]:
        lineas.append("Comprobación exitosa: A · x == b")
    else:
        lineas.append("¡Atención! A · x no coincide con b")
    return lineas


def resolver_lu(A, b):
    """Resuelve A·x = b para A cuadrada usando su factorización LU.

    Recibe A (n×n) y b (n componentes). Halla y resolviendo L·y = b y luego
    x resolviendo U·x = y, ambos por reducción sobre la matriz aumentada.
    Devuelve un diccionario con L, U, y, x, los pasos de cada etapa, el
    producto A·x y si la solución satisface el sistema.
    """
    n = validar_cuadrada(A)
    if len(b) != n:
        raise ValueError("El vector b debe tener " + str(n)
                         + " componentes (una por fila de A).")

    L, U, pasos_factorizacion = factorizar_lu(A)

    # Si algún pivote de la diagonal de U es cero, A es singular (det = 0)
    # y el sistema no tiene solución única.
    for i in range(n):
        if U[i][i] == 0:
            raise ValueError("La matriz A es singular (un pivote de U es cero); "
                             "no tiene solución única por LU.")

    # Etapa 1: L·y = b, reduciendo la aumentada [L | b].
    aumentada_L = [[Fraction(L[i][j]) for j in range(n)]
                   + [Fraction(b[i])] for i in range(n)]
    pasos_adelante, _ = escalonar(aumentada_L, n)
    y = [aumentada_L[i][n] for i in range(n)]

    # Etapa 2: U·x = y, reduciendo la aumentada [U | y].
    aumentada_U = [[Fraction(U[i][j]) for j in range(n)]
                   + [y[i]] for i in range(n)]
    pasos_atras, _ = escalonar(aumentada_U, n)
    x = [aumentada_U[i][n] for i in range(n)]

    # Comprobación final: A·x debe reproducir el vector b.
    A_fraccion = [[Fraction(valor) for valor in fila] for fila in A]
    producto_ax = multiplicar_matrices(A_fraccion, [[x[i]] for i in range(n)])
    b_columna = [[Fraction(b[i])] for i in range(n)]
    return {
        "L": L, "U": U, "y": y, "x": x,
        "pasos_factorizacion": pasos_factorizacion,
        "pasos_adelante": pasos_adelante,
        "pasos_atras": pasos_atras,
        "producto_ax": [fila[0] for fila in producto_ax],
        "solucion_correcta": producto_ax == b_columna,
    }


def formato_vector(v):
    """Muestra un vector como una tupla de componentes entre paréntesis."""
    return "( " + ", ".join(formato(valor) for valor in v) + " )"


# =====================================================================
# BLOQUE 2: INTERFAZ GRÁFICA DEL MÓDULO (Tkinter)
# =====================================================================

class LUApp:
    """Pantalla del módulo de Factorización LU y solución de A·x = b."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver

        self.var_filas = tk.StringVar(value="3")
        self.var_columnas = tk.StringVar(value="3")
        self.celdas_A = {}
        self.celdas_b = {}

        self.fuente_titulo = tkfont.Font(family="Montserrat", size=22, weight="bold")
        self.fuente_sub = tkfont.Font(family="Montserrat", size=11)
        self.fuente_body = tkfont.Font(family="Montserrat", size=11)
        self.fuente_encab = tkfont.Font(family="Montserrat", size=11, weight="bold")
        self.fuente_big = tkfont.Font(family="Montserrat", size=16, weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=11, weight="bold")

        self.marco_principal = tk.Frame(self.raiz, bg=FONDO)
        self.marco_principal.pack(fill="both", expand=True)

        self.ultimo_calculo = None
        self.etiquetas_ajustables = []
        self.mostrando_pasos = False
        self.mostrando_comprobacion_lu = False
        self.mostrando_comprobacion_ax = False

        self._construir_ui()
        self._construir_grids()

    def _construir_ui(self):
        cabecera = tk.Frame(self.marco_principal, bg=FONDO)
        cabecera.grid(row=0, column=0, columnspan=2, sticky="ew",
                      padx=34, pady=(10, 0))
        cabecera.columnconfigure(1, weight=1)

        tk.Button(cabecera, text="← Volver al Menú", font=self.fuente_body,
                  bg=FONDO, fg=ACENTO, bd=0, relief="flat", cursor="hand2",
                  activeforeground=ACENTO_HOVER, command=self.volver_al_menu
                  ).grid(row=0, column=0, sticky="nw", pady=(4, 0))

        tk.Button(cabecera, text="0. Ver Teoremas Clave del Módulo",
                  font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO, bd=0,
                  relief="flat", cursor="hand2", padx=12, pady=5,
                  activebackground=BOTON_SEC_HOVER, command=self._ver_teoremas
                  ).grid(row=0, column=2, sticky="ne", pady=(4, 0))

        tk.Label(self.marco_principal,
                 text="Módulo 5: Factorización LU y solución Ax = b",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal,
                 text="A = L·U por reemplazo de filas, verificación L·U = A y "
                      "doble sustitución para resolver A·x = b.",
                 font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE
                 ).grid(row=2, column=0, columnspan=2, sticky="w", padx=34, pady=(0, 12))

        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)

        # ---- panel izquierdo (entrada) ----
        panel_izq = tk.Frame(self.marco_principal, bg=FONDO)
        panel_izq.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))
        self.frame_izq = panel_izq

        self._llenar_tarjeta_A(self.frame_izq)
        self._llenar_tarjeta_b(self.frame_izq)

        tk.Button(self.frame_izq, text="Factorizar y resolver",
                  font=self.fuente_boton, bg=ACENTO, fg=FONDO, relief="flat",
                  cursor="hand2", padx=12, pady=10, activebackground=ACENTO_HOVER,
                  activeforeground=FONDO, command=self._al_factorizar
                  ).pack(fill="x", pady=(4, 0))

        # ---- panel derecho (resultados) ----
        panel_der = tk.Frame(self.marco_principal, bg=FONDO)
        panel_der.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))
        tarjeta_res = self._crear_tarjeta(panel_der)
        tarjeta_res.pack(fill="both", expand=True)

        cab_res = tk.Frame(tarjeta_res, bg=TARJETA)
        cab_res.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cab_res, text="Resultado", font=self.fuente_encab,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        # Los botones viven en un marco propio para que su orden no cambie
        # al mostrarlos u ocultarlos.
        self.marco_botones_resultado = tk.Frame(cab_res, bg=TARJETA)
        self.marco_botones_resultado.pack(side="right")
        self.boton_procedimiento = self._boton_resultado(
            "Ver procedimiento", self._alternar_procedimiento)
        self.boton_comprobar_lu = self._boton_resultado(
            "Ver L·U = A", self._alternar_comprobacion_lu)
        self.boton_comprobar_ax = self._boton_resultado(
            "Ver A·x = b", self._alternar_comprobacion_ax)

        # El resultado se pinta con tarjetas dentro de un lienzo desplazable,
        # igual que en el módulo de Operaciones Matriciales.
        self.lienzo_resultado = tk.Canvas(tarjeta_res, bg=TARJETA,
                                          highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(tarjeta_res, orient="vertical",
                                             command=self.lienzo_resultado.yview)
        self.lienzo_resultado.configure(yscrollcommand=self.barra_resultado.set)
        self.frame_resultado = tk.Frame(self.lienzo_resultado, bg=TARJETA)
        self._ventana_res = self.lienzo_resultado.create_window(
            (0, 0), window=self.frame_resultado, anchor="nw")

        def al_cambiar_tamano(evento):
            self.lienzo_resultado.itemconfig(self._ventana_res, width=evento.width)
            self._ajustar_textos(evento.width)

        self.lienzo_resultado.bind("<Configure>", al_cambiar_tamano)
        self.frame_resultado.bind(
            "<Configure>",
            lambda e: self.lienzo_resultado.configure(
                scrollregion=self.lienzo_resultado.bbox("all")))
        self._activar_rueda(self.lienzo_resultado)

        self.lienzo_resultado.pack(side="left", fill="both", expand=True,
                                   padx=(12, 0), pady=(0, 12))
        self.barra_resultado.pack(side="right", fill="y", padx=(0, 6), pady=(0, 12))
        self._mostrar_bienvenida()

    def _crear_tarjeta(self, padre):
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC,
                        highlightthickness=1, bd=0)

    def _boton_resultado(self, texto, accion):
        """Botón pequeño de la cabecera del panel de resultados."""
        return tk.Button(self.marco_botones_resultado, text=texto,
                         font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO, bd=0,
                         relief="flat", cursor="hand2", padx=10, pady=4,
                         activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO,
                         command=accion)

    def _activar_rueda(self, lienzo):
        """Permite desplazar el panel de resultados con la rueda del ratón."""
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

    # ---------- piezas visuales del panel de resultados ----------
    def _texto_ajustable(self, etiqueta):
        """Registra una etiqueta para reajustar su ancho al redimensionar."""
        self.etiquetas_ajustables.append(etiqueta)
        return etiqueta

    def _ajustar_textos(self, ancho_disponible=None):
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(160, ancho_disponible - 70)
        for etiqueta in list(self.etiquetas_ajustables):
            try:
                if etiqueta.winfo_exists():
                    etiqueta.configure(wraplength=ancho)
            except tk.TclError:
                pass

    def _finalizar_render(self):
        """Recalcula el área desplazable y ajusta los textos al ancho actual."""
        self.raiz.update_idletasks()
        self.lienzo_resultado.configure(
            scrollregion=self.lienzo_resultado.bbox("all"))
        self._ajustar_textos()

    def _mostrar_bienvenida(self):
        """Mensaje inicial antes de factorizar."""
        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = []
        aviso = tk.Label(
            self.frame_resultado,
            text="Ingresa la matriz A y el vector b, y presiona "
                 "«Factorizar y resolver» para ver aquí la factorización "
                 "A = L · U y, si A es cuadrada, la solución A · x = b.",
            font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
            justify="left", anchor="nw")
        aviso.pack(fill="both", expand=True, padx=18, pady=16)
        self._texto_ajustable(aviso)
        self._finalizar_render()

    def _sub_tarjeta(self, padre, titulo, color):
        """Tarjeta con su título, como las secciones de Operaciones Matriciales."""
        sub = tk.Frame(padre, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(6, 4), anchor="n")
        tk.Label(sub, text=titulo, font=self.fuente_encab, bg=TARJETA,
                 fg=color, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        return sub

    def _banner(self, padre, texto, color):
        """Franja de color con el título grande del resultado."""
        marco = tk.Frame(padre, bg=color, padx=14, pady=10)
        marco.pack(fill="x", pady=(0, 6))
        self._texto_ajustable(
            tk.Label(marco, text=texto, font=self.fuente_big, bg=color,
                     fg=FONDO, justify="left", anchor="w")).pack(fill="x")

    def _bloque_matriz(self, padre, etiqueta, M, nota=""):
        """Muestra una matriz en bloque, con el mismo aspecto que el módulo
        de Operaciones Matriciales."""
        tk.Label(padre, text=etiqueta, font=self.fuente_sub, bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x", pady=(4, 0))
        if nota:
            self._texto_ajustable(
                tk.Label(padre, text=nota, font=self.fuente_body, bg=TARJETA,
                         fg=TEXTO_SUAVE, anchor="w", justify="left")).pack(fill="x")
        self._texto_ajustable(
            tk.Label(padre, text="\n".join(formato_matriz(M)),
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w")).pack(fill="x", pady=(2, 6))

    def _bloque_vector(self, padre, etiqueta, vector):
        """Muestra un vector como ( v₁, v₂, … ) en monoespaciado."""
        self._texto_ajustable(
            tk.Label(padre, text=etiqueta + " " + formato_vector(vector),
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w")).pack(fill="x", pady=2)

    def _veredicto(self, padre, texto, color):
        self._texto_ajustable(
            tk.Label(padre, text=texto, font=self.fuente_encab, bg=TARJETA,
                     fg=color, anchor="w", justify="left")).pack(fill="x",
                                                                 pady=(4, 2))

    def _recuadro_cuentas(self, padre, titulo, lineas):
        """Recuadro monoespaciado con el desarrollo detallado."""
        tk.Label(padre, text=titulo, font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE, anchor="w").pack(fill="x", pady=(6, 2))
        marco = tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC,
                         highlightthickness=1, bd=0)
        marco.pack(fill="x", pady=(0, 8))
        self._texto_ajustable(
            tk.Label(marco, text="\n".join(lineas), font=self.fuente_mono,
                     bg=TARJETA, fg=TEXTO, justify="left", anchor="w")
        ).pack(fill="x", padx=10, pady=8)

    def _leer_dimension(self, variable, por_defecto):
        try:
            valor = int(variable.get())
        except Exception:
            valor = por_defecto
        valor = max(1, min(MAX_DIMENSION, valor))
        variable.set(str(valor))
        return valor

    def _llenar_tarjeta_A(self, padre):
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cont, text="Matriz A", font=self.fuente_sub, bg=TARJETA,
                 fg=TEXTO, anchor="w").grid(row=0, column=0, columnspan=5,
                                            sticky="w", pady=(0, 8))
        tk.Label(cont, text="Filas", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_filas,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._reconstruir_entradas
                   ).grid(row=1, column=1, sticky="w", padx=(0, 16))
        tk.Label(cont, text="Columnas", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_columnas,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._reconstruir_entradas
                   ).grid(row=1, column=3, sticky="w")

        def aplicar():
            self._leer_dimension(self.var_filas, 3)
            self._leer_dimension(self.var_columnas, 3)
            self._reconstruir_entradas()

        tk.Button(cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO,
                  relief="flat", cursor="hand2", padx=6, pady=2,
                  activebackground=ACENTO_HOVER, activeforeground=FONDO,
                  command=aplicar
                  ).grid(row=1, column=4, sticky="w", padx=(12, 0))

        self.frame_A = tk.Frame(tarjeta, bg=TARJETA)
        self.frame_A.pack(fill="both", expand=True, padx=18, pady=(0, 8))

    def _llenar_tarjeta_b(self, padre):
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 10))
        tk.Label(cont, text="Vector b (términos independientes)",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).pack(fill="x")
        tk.Label(cont, text="Una componente por fila de A. Se usa para resolver "
                            "A·x = b cuando A es cuadrada.",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 justify="left", wraplength=380, anchor="w").pack(fill="x", pady=(0, 6))
        self.frame_b = tk.Frame(cont, bg=TARJETA)
        self.frame_b.pack(anchor="w", pady=(2, 0))

    def _reconstruir_entradas(self):
        self._construir_grids()

    def _construir_grids(self):
        previos_A = {c: v.get() for c, v in self.celdas_A.items()}
        previos_b = {i: v.get() for i, v in self.celdas_b.items()}

        m = self._leer_dimension(self.var_filas, 3)
        n = self._leer_dimension(self.var_columnas, 3)

        for hijo in self.frame_A.winfo_children():
            hijo.destroy()
        self.celdas_A.clear()
        for j in range(n):
            tk.Label(self.frame_A, text=con_subindice("a" + str(j + 1)),
                     font=self.fuente_encab, bg=TARJETA, fg=TEXTO
                     ).grid(row=0, column=j, padx=3, pady=(0, 4))
        for i in range(m):
            for j in range(n):
                var = tk.StringVar(value=previos_A.get((i, j), ""))
                self.celdas_A[(i, j)] = var
                tk.Entry(self.frame_A, textvariable=var, font=self.fuente_mono,
                         width=6, justify="center", relief="solid", bd=1,
                         bg=CELDA_FONDO).grid(row=i + 1, column=j, padx=3, pady=2)

        for hijo in self.frame_b.winfo_children():
            hijo.destroy()
        self.celdas_b.clear()
        for i in range(m):
            var = tk.StringVar(value=previos_b.get(i, ""))
            self.celdas_b[i] = var
            tk.Entry(self.frame_b, textvariable=var, font=self.fuente_mono,
                     width=10, justify="center", relief="solid", bd=1,
                     bg=CELDA_FONDO).grid(row=i, column=0, pady=2)

    def _leer_matriz(self, celdas, m, n, nombre):
        matriz = []
        for i in range(m):
            fila = []
            for j in range(n):
                try:
                    fila.append(a_numero(celdas[(i, j)].get()))
                except ValueError:
                    raise ValueError("Revisa la matriz " + nombre + ", celda fila "
                                     + str(i + 1) + ", columna " + str(j + 1) + ".")
            matriz.append(fila)
        return matriz

    def _leer_b(self, m):
        b = []
        for i in range(m):
            try:
                b.append(a_numero(self.celdas_b[i].get()))
            except ValueError:
                raise ValueError("Revisa el vector b, componente " + str(i + 1) + ".")
        return b

    def _al_factorizar(self):
        try:
            self._construir_grids()
            m = self._leer_dimension(self.var_filas, 3)
            n = self._leer_dimension(self.var_columnas, 3)
            A = self._leer_matriz(self.celdas_A, m, n, "A")

            L, U, pasos = factorizar_lu(A)
            _, correcta = verificar_factorizacion(A, L, U)

            datos = None
            b = None
            aviso = ""
            pasos_completos = list(pasos)

            if m == n:
                b = self._leer_b(m)
                try:
                    datos = resolver_lu(A, b)
                except ValueError as error_singular:
                    # A cuadrada pero singular: la factorización y L·U = A se
                    # pueden ver igual; solo A·x = b carece de solución única.
                    aviso = "No se puede resolver A·x = b: " + str(error_singular)
                if datos is not None:
                    pasos_completos += ["", "--- SUSTITUCIÓN HACIA ADELANTE: L·y = b ---", ""]
                    pasos_completos += datos["pasos_adelante"]
                    pasos_completos += ["", "--- SUSTITUCIÓN HACIA ATRÁS: U·x = y ---", ""]
                    pasos_completos += datos["pasos_atras"]
            else:
                aviso = ("A es " + str(m) + "×" + str(n)
                         + "; la solución por LU se resuelve solo para A cuadrada.")

            self._mostrar_resultado(A, L, U, correcta, datos, b,
                                    pasos_completos, aviso)
        except ValueError as error:
            self._mostrar_error(str(error))

    def _mostrar_resultado(self, A, L, U, correcta, datos, b, pasos, aviso=""):
        """Fija la respuesta principal y prepara las secciones de comprobación."""
        self.ultimo_calculo = {
            "A": A, "L": L, "U": U, "correcta": correcta,
            "datos": datos, "b": b, "pasos": pasos or [], "aviso": aviso,
        }
        self.mostrando_pasos = False
        self.mostrando_comprobacion_lu = False
        self.mostrando_comprobacion_ax = False
        self._acomodar_botones()

        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = []

        # La respuesta principal vive en su propio marco y nunca se destruye
        # al abrir o cerrar comprobaciones: éstas se agregan debajo.
        self.frame_base = tk.Frame(self.frame_resultado, bg=TARJETA)
        self.frame_base.pack(fill="x")
        self.frame_secciones = tk.Frame(self.frame_resultado, bg=TARJETA)
        self.frame_secciones.pack(fill="x")
        self._dibujar_base()
        self._dibujar_secciones()
        self._finalizar_render()

    def _dibujar_base(self):
        """Respuesta principal: factorización LU y, si se puede, solución."""
        calculo = self.ultimo_calculo

        sub = self._sub_tarjeta(self.frame_base, "RESULTADO", ACENTO)
        self._banner(sub, "FACTORIZACIÓN A = L · U", ACENTO)
        if calculo["correcta"]:
            self._veredicto(sub, "La factorización es correcta (L · U == A).",
                            EXITO)
        else:
            self._veredicto(sub, "¡Atención! L · U no coincide con A.", ERROR)
        self._bloque_matriz(sub, "Matriz L:", calculo["L"],
                            "Triangular inferior con unos en la diagonal.")
        self._bloque_matriz(sub, "Matriz U:", calculo["U"],
                            "Forma escalonada obtenida por reemplazo de filas.")

        if calculo["datos"] is not None:
            datos = calculo["datos"]
            sub = self._sub_tarjeta(self.frame_base, "SOLUCIÓN DEL SISTEMA",
                                    EXITO)
            self._banner(sub, "A · x = b", EXITO)
            self._bloque_vector(sub, "Vector intermedio y =", datos["y"])
            self._bloque_vector(sub, "Vector solución   x =", datos["x"])
            if datos["solucion_correcta"]:
                self._veredicto(sub, "Comprobación exitosa: A · x == b", EXITO)
            else:
                self._veredicto(sub, "¡Atención! A · x no coincide con b", ERROR)
        elif calculo["aviso"]:
            sub = self._sub_tarjeta(self.frame_base, "AVISO", ADVERTENCIA)
            self._texto_ajustable(
                tk.Label(sub, text=calculo["aviso"], font=self.fuente_body,
                         bg=TARJETA, fg=ADVERTENCIA, justify="left",
                         anchor="w")).pack(fill="x", pady=(2, 8))

    def _dibujar_secciones(self):
        """Dibuja debajo de la respuesta solo las comprobaciones abiertas."""
        if self.ultimo_calculo is None:
            return
        for hijo in self.frame_secciones.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = [etiqueta
                                     for etiqueta in self.etiquetas_ajustables
                                     if etiqueta.winfo_exists()]

        if self.mostrando_comprobacion_lu:
            self._seccion_comprobacion_lu()
        if self.mostrando_comprobacion_ax:
            self._seccion_comprobacion_ax()
        if self.mostrando_pasos:
            self._seccion_procedimiento()

    def _seccion_comprobacion_lu(self):
        """Tarjeta «A = L · U»: matrices y cuentas de la multiplicación."""
        calculo = self.ultimo_calculo
        A, L, U = calculo["A"], calculo["L"], calculo["U"]

        sub = self._sub_tarjeta(self.frame_secciones,
                                "COMPROBACIÓN A = L · U", ACENTO)
        if calculo["correcta"]:
            self._banner(sub, "L · U == A", EXITO)
        else:
            self._banner(sub, "L · U ≠ A", ERROR)

        self._bloque_matriz(sub, "Matriz L:", L)
        self._bloque_matriz(sub, "Matriz U:", U)
        self._bloque_matriz(sub, "Producto L · U:", multiplicar_matrices(L, U))
        self._bloque_matriz(sub, "Matriz A:", A)

        comparacion, _ = _lineas_comparacion_factorizacion(A, L, U)
        self._recuadro_cuentas(sub, "Comparación entrada por entrada:",
                               comparacion)
        self._recuadro_cuentas(sub, "Cuentas con la regla fila-columna:",
                               _lineas_cuentas_factorizacion(A, L, U))

    def _seccion_comprobacion_ax(self):
        """Tarjeta «A · x = b»: vectores y cuentas de la multiplicación."""
        calculo = self.ultimo_calculo
        datos = calculo["datos"]
        A, b = calculo["A"], calculo["b"]

        sub = self._sub_tarjeta(self.frame_secciones,
                                "COMPROBACIÓN A · x = b", EXITO)
        if datos["solucion_correcta"]:
            self._banner(sub, "A · x == b", EXITO)
        else:
            self._banner(sub, "A · x ≠ b", ERROR)

        self._bloque_matriz(sub, "Matriz A:", A)
        self._bloque_vector(sub, "Vector solución   x =", datos["x"])
        self._bloque_vector(sub, "Producto A · x =", datos["producto_ax"])
        self._bloque_vector(sub, "Vector original   b =", b)
        self._recuadro_cuentas(sub, "Cuentas con la regla fila-vector:",
                               _lineas_cuentas_solucion(A, datos["x"], b))

    def _seccion_procedimiento(self):
        """Tarjeta con la eliminación y las dos sustituciones."""
        sub = self._sub_tarjeta(self.frame_secciones,
                                "DESARROLLO PASO A PASO", TEXTO_SUAVE)
        self._recuadro_cuentas(sub, "Eliminación y sustituciones:",
                               self.ultimo_calculo["pasos"])

    def _acomodar_botones(self):
        """Muestra solo los botones que tienen contenido y actualiza rótulos."""
        for boton in (self.boton_procedimiento, self.boton_comprobar_lu,
                      self.boton_comprobar_ax):
            boton.pack_forget()

        calculo = self.ultimo_calculo
        if calculo is not None:
            if calculo["pasos"]:
                self.boton_procedimiento.pack(side="left", padx=(0, 6))
            if calculo["L"]:
                self.boton_comprobar_lu.pack(side="left", padx=(0, 6))
            if calculo["datos"] is not None:
                self.boton_comprobar_ax.pack(side="left")

        self.boton_procedimiento.configure(
            text="Ocultar procedimiento" if self.mostrando_pasos
            else "Ver procedimiento")
        self.boton_comprobar_lu.configure(
            text="Ocultar L·U = A" if self.mostrando_comprobacion_lu
            else "Ver L·U = A")
        self.boton_comprobar_ax.configure(
            text="Ocultar A·x = b" if self.mostrando_comprobacion_ax
            else "Ver A·x = b")

    def _alternar_procedimiento(self):
        if self.ultimo_calculo is None or not self.ultimo_calculo["pasos"]:
            return
        self.mostrando_pasos = not self.mostrando_pasos
        self._acomodar_botones()
        self._dibujar_secciones()
        self._finalizar_render()

    def _alternar_comprobacion_lu(self):
        """Muestra u oculta el desarrollo de la multiplicación L·U."""
        if self.ultimo_calculo is None:
            return
        self.mostrando_comprobacion_lu = not self.mostrando_comprobacion_lu
        self._acomodar_botones()
        self._dibujar_secciones()
        self._finalizar_render()

    def _alternar_comprobacion_ax(self):
        """Muestra u oculta el desarrollo de la multiplicación A·x."""
        if self.ultimo_calculo is None or self.ultimo_calculo["datos"] is None:
            return
        self.mostrando_comprobacion_ax = not self.mostrando_comprobacion_ax
        self._acomodar_botones()
        self._dibujar_secciones()
        self._finalizar_render()

    def _mostrar_error(self, mensaje):
        messagebox.showerror("Operación no válida", mensaje)

    def _ver_teoremas(self):
        mostrar_teoremas(self.raiz, "lu", "Módulo 5: Factorización LU")

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


# =====================================================================
# BLOQUE 3: MENÚ DE CONSOLA DEL MÓDULO 5 (MODO CLI)
# =====================================================================

def menu_consola():
    """Menú de texto del Módulo 5: Factorización LU y solución A·x = b."""
    while True:
        mostrar_cabecera(LOGO_LU)
        print("   0. Ver Teoremas Clave del Módulo")
        print("   1. Factorizar A = L·U y resolver A·x = b")
        print("   9. Volver al menú principal")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("lu"))
            pausa()
        elif opcion == "1":
            _consola_lu()
        else:
            print("   Opción no válida.")
            pausa()


def _consola_lu():
    """Pide A y b, muestra la factorización LU y resuelve el sistema."""
    mostrar_cabecera(LOGO_LU)
    print("   FACTORIZACIÓN LU Y SOLUCIÓN A·x = b")
    print()
    try:
        m = leer_entero("   Número de filas de A (m) = ")
        n = leer_entero("   Número de columnas de A (n) = ")
        print()
        A = leer_matriz("A", m, n)
        print()
        b = leer_vector("b", m)

        L, U, _ = factorizar_lu(A)

        print()
        mostrar_matriz(L, titulo="   MATRIZ L (triangular inferior):")
        print()
        mostrar_matriz(U, titulo="   MATRIZ U (forma escalonada):")
        print()
        # Mismo desarrollo que muestra el botón «Ver L·U = A» de la ventana.
        for linea in pasos_comprobar_factorizacion(A, L, U):
            print("   " + linea)

        if m == n:
            datos = resolver_lu(A, b)
            print()
            print("   Vector intermedio y = " + formato_vector(datos["y"]))
            print("   Vector solución   x = " + formato_vector(datos["x"]))
            print()
            # Mismo desarrollo que muestra el botón «Ver A·x = b».
            for linea in pasos_comprobar_solucion(A, datos["x"], b):
                print("   " + linea)
        else:
            print()
            print("   A es " + str(m) + "×" + str(n)
                  + "; la solución por LU se resuelve solo para A cuadrada.")
    except ValueError as error:
        print("\n   " + str(error))
    pausa()
