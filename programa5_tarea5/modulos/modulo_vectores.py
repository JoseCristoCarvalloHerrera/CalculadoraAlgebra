# -*- coding: utf-8 -*-
"""
=====================================================================
 MÓDULO 2: VECTORES EN R^n E INDEPENDENCIA LINEAL
 Calculadora de Álgebra Lineal - Proyecto Integrador - GRUPO 2
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Segundo Corte Evaluativo - Programa 4

 Operaciones con vectores en R^n y el análisis de independencia
 lineal, que es el requisito central del Programa 4:
   - Suma, resta y múltiplo escalar de vectores.
   - es_combinacion_lineal(): decide si b se genera con v1...vk.
   - analizar_independencia(): construye el sistema homogéneo Ax = 0,
     lo reduce por filas, cuenta pivotes y variables libres y emite el
     veredicto explícito L.I. o L.D.
   - relacion_de_dependencia(): si son L.D., da la relación concreta.
   - VectoresApp: la pantalla Tkinter de este módulo.

 Restricción cumplida:
   - Solo se usa Python estándar (tkinter, fractions). NO se usan
     NumPy, SciPy ni funciones de álgebra lineal de math.
=====================================================================
"""

from fractions import Fraction
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

from modulos import (
    FONDO, TARJETA, TEXTO, TEXTO_SUAVE, ACENTO, ACENTO_HOVER,
    BOTON_SEC, BOTON_SEC_HOVER, CELDA_FONDO, EXITO, ADVERTENCIA, ERROR,
    LETRA_MONO, MAX_DIMENSION, AYUDA_NUMERO,
    a_numero, formato, formato_matriz, con_subindice, nombre_variable,
    _validar_matriz, _leer_dimensiones, LOGO_VECTORES,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_numero,
    leer_vector, leer_matriz, mostrar_matriz, pausa, preguntar,
)
from modulos.modulo_sistemas import resolver_sistema, escalonar
from teoremas.resumen_teoremas import mostrar_teoremas, texto_teoremas


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


def _formato_suma_lineal(coefs, nombre_base="v", ocultar_unos=True):
    """Construye el texto de una combinación lineal, por ejemplo
    '3·v₁ + 2·v₂ − v₃'. Recibe la lista de coeficientes y el nombre base
    de las variables ('v', 'a', 'x', ...). Escribe el signo + o − según
    el signo de cada coeficiente y omite el coeficiente si es 1 ó −1
    (a menos que ocultar_unos sea False, útil para mostrar los escalares)."""
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
        if c_abs == 1 and ocultar_unos:
            terminos.append(signo + nombre)
        else:
            terminos.append(signo + formato(c_abs) + "·" + nombre)
    return "".join(terminos) if terminos else "0"


def _expansion_por_columnas(coefs, columnas, nombre_base="a", resultado=None):
    """Líneas para mostrar un producto matriz-vector como combinación lineal
    explícita de las columnas: el valor de cada columna, la fórmula con los
    escalares, la suma desarrollada y el vector resultante."""
    lineas = [con_subindice(nombre_base + str(i + 1)) + " = "
              + formato_vector(columnas[i]) for i in range(len(coefs))]
    formula = _formato_suma_lineal(coefs, nombre_base, ocultar_unos=False)
    suma = " + ".join(formato_vector(col) for col in columnas)
    if resultado is not None:
        formula += " = " + suma + " = " + formato_vector(resultado)
    lineas.append(formula)
    return lineas


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
    # Se convierte todo a Fraction ANTES de reducir: si las entradas
    # llegan como enteros de Python, las divisiones del escalonamiento
    # producirían float y se perderían los valores exactos.
    aumentada = [[Fraction(valor) for valor in fila] + [Fraction(0)]
                 for fila in A]
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
    _validar_matriz(A, "A")
    if not x:
        raise ValueError("Debe ingresar el vector x.")
    _, n_columnas = _leer_dimensiones(A)
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


def vectores_iguales(a, b, tolerancia=1e-9):
    """Compara dos vectores: exacto para enteros/fracciones y con tolerancia
    solo si alguno de los valores es float, por errores de representación."""
    validar_dimensiones(a, b)
    for x, y in zip(a, b):
        if x == y:
            continue
        if isinstance(x, float) or isinstance(y, float):
            if not abs(float(x) - float(y)) <= tolerancia:
                return False
        elif x != y:
            return False
    return True


def pasos_matriz_por_vector(A, x):
    """Explica Ax usando la regla fila-vector y fracciones exactas."""
    resultado = matriz_por_vector(A, x)
    pasos = ["Producto matriz-vector Ax por regla fila-vector:"]
    for i, fila in enumerate(A):
        terminos = ["(" + formato(fila[j]) + ")·(" + formato(x[j]) + ")"
                    for j in range(len(x))]
        pasos.append("Fila " + str(i + 1) + ": " + " + ".join(terminos)
                     + " = " + formato(resultado[i]))
    return pasos


def verificar_aditividad_matriz_vector(A, u, v):
    """Verifica A(u+v)=Au+Av calculando y devolviendo ambos caminos."""
    _validar_matriz(A, "A")
    _, n = _leer_dimensiones(A)
    if len(u) != n or len(v) != n:
        raise ValueError("u y v deben tener " + str(n)
                         + " componente(s), igual al número de columnas de A.")
    u_mas_v = sumar_vectores(u, v)
    izquierda = matriz_por_vector(A, u_mas_v)
    Au = matriz_por_vector(A, u)
    Av = matriz_por_vector(A, v)
    derecha = sumar_vectores(Au, Av)
    return {
        "u_mas_v": u_mas_v,
        "izquierda": izquierda,
        "Au": Au,
        "Av": Av,
        "derecha": derecha,
        "se_cumple": vectores_iguales(izquierda, derecha),
    }


def verificar_homogeneidad_matriz_vector(A, c, u):
    """Verifica A(cu)=c(Au) mostrando los dos lados de la igualdad."""
    _validar_matriz(A, "A")
    _, n = _leer_dimensiones(A)
    if len(u) != n:
        raise ValueError("u debe tener " + str(n)
                         + " componente(s), igual al número de columnas de A.")
    cu = escalar_por_vector(c, u)
    izquierda = matriz_por_vector(A, cu)
    Au = matriz_por_vector(A, u)
    derecha = escalar_por_vector(c, Au)
    return {
        "cu": cu,
        "izquierda": izquierda,
        "Au": Au,
        "derecha": derecha,
        "se_cumple": vectores_iguales(izquierda, derecha),
    }



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
        # ---- Cabecera del módulo: volver, logotipo ASCII y teoremas ----
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
                  activebackground=BOTON_SEC_HOVER,
                  command=self._ver_teoremas
                  ).grid(row=0, column=2, sticky="ne", pady=(4, 0))


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
            ("¿L.I. o L.D.?", self._al_independencia),
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

    def _al_independencia(self):
        """Requisito central del Programa 4: analiza si el conjunto de
        vectores es Linealmente Independiente o Dependiente.

        Construye el sistema homogéneo [v₁ … v_k | 0], lo reduce por
        filas y muestra la matriz reducida, el número de pivotes, las
        variables libres y el veredicto teórico explícito."""
        try:
            vs = self._leer_vectores()
            r = analizar_independencia(vs)

            titulo = r["veredicto"]
            texto = ("Pivotes: " + str(r["cantidad_pivotes"])
                     + "     Vectores: " + str(r["k"])
                     + "     Variables libres: " + str(r["cantidad_libres"]))
            detalle = informe_independencia(vs)
            color = EXITO if r["independientes"] else ADVERTENCIA

            self._mostrar(titulo, texto, detalle, color=color,
                          pasos=r["pasos"])
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
        ancho = max(120, ancho_disponible - 56)
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

        self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA,
                                          highlightbackground=BOTON_SEC,
                                          highlightthickness=1, bd=0)
        tk.Label(self.sub_procedimiento, text="PROCESO DE ELIMINACIÓN (GAUSS-JORDAN)",
                 font=self.fuente_encab, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 6))
        texto_proc = "\n".join(pasos) if pasos else "(sin procedimiento)"
        self._texto_ajustable(
            tk.Label(self.sub_procedimiento, text=texto_proc,
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="nw"
                     )).pack(fill="x", padx=14, pady=(0, 10))

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
        self._ajustar_textos()
        self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all"))

    def _mostrar_error(self, mensaje):
        self._mostrar("Revisá los datos", mensaje, "", color=ERROR, pasos=None)


    def _ver_teoremas(self):
        """Opción '0. Ver Teoremas Clave del Módulo' que pide la Tarea 4.
        Despliega el resumen que vive en teoremas/resumen_teoremas.py."""
        mostrar_teoremas(self.raiz, "vectores", "Módulo 2: Vectores e Independencia Lineal")

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()



# =====================================================================
# BLOQUE V3: ANÁLISIS DE INDEPENDENCIA LINEAL  (REQUISITO PROGRAMA 4)
#
# Este es el requerimiento central de la Tarea 4: dado un conjunto de k
# vectores en R^n, decidir si es Linealmente Independiente (L.I.) o
# Linealmente Dependiente (L.D.) reduciendo por filas la matriz cuyas
# COLUMNAS son esos vectores.
#
# Fundamento (Sesiones 6 y 7):
#   El conjunto {v1, ..., vk} es L.I. si y solo si la única solución de
#         c1·v1 + c2·v2 + ... + ck·vk = 0
#   es la trivial c1 = c2 = ... = ck = 0. Esa ecuación es el sistema
#   homogéneo [v1 v2 ... vk | 0]. Por el teorema de la ecuación
#   homogénea, tiene solución NO trivial si y solo si queda al menos
#   una variable libre. Entonces:
#         pivotes = k   ->  sin variables libres  ->  L.I.
#         pivotes < k   ->  hay variables libres  ->  L.D.
# =====================================================================

def analizar_independencia(vectores):
    """Analiza si un conjunto de vectores de R^n es L.I. o L.D.

    Procedimiento algebraico:
      1. Se colocan los k vectores como COLUMNAS de una matriz A de n×k.
      2. Se arma el sistema homogéneo aumentado [A | 0].
      3. Se reduce por filas hasta la forma escalonada reducida.
      4. Se cuentan los pivotes que caen en columnas de variables.
      5. variables libres = k - número de pivotes.
      6. Veredicto: sin variables libres -> L.I.; con ellas -> L.D.

    Devuelve un diccionario con la matriz reducida, el número de
    pivotes, las columnas pivote, las variables libres, el veredicto y
    el procedimiento completo paso a paso.
    """
    if len(vectores) == 0:
        raise ValueError("Debe indicar al menos un vector.")
    for v in vectores:
        validar_dimensiones(vectores[0], v)

    k = len(vectores)                  # cantidad de vectores
    n = len(vectores[0])               # dimensión del espacio R^n

    # --- Paso 1 y 2: los vectores son las columnas; se agrega el 0 ---
    A = vectores_como_columnas(vectores)
    aumentada = [[Fraction(valor) for valor in fila] + [Fraction(0)]
                 for fila in A]

    pasos = []
    pasos.append("Sistema homogéneo a resolver:")
    pasos.append("   " + " + ".join(
        "c" + str(j + 1) + "·v" + str(j + 1) for j in range(k)) + " = 0")
    pasos.append("")
    pasos.append("Matriz aumentada [v₁ v₂ … vₖ | 0] "
                 "(cada vector es una COLUMNA):")
    pasos.extend(formato_matriz(aumentada, k))
    pasos.append("")

    # --- Paso 3: reducción por filas ---
    pasos_reduccion, pivotes = escalonar(aumentada, k)
    if pasos_reduccion:
        pasos.extend(pasos_reduccion)
    else:
        pasos.append("La matriz ya estaba reducida; no hizo falta operar.")
    pasos.append("")
    pasos.append("Matriz reducida final:")
    pasos.extend(formato_matriz(aumentada, k))

    # --- Paso 4 y 5: pivotes y variables libres ---
    pivotes_variables = [(f, c) for f, c in pivotes if c < k]
    columnas_pivote = [c + 1 for _, c in pivotes_variables]
    cantidad_pivotes = len(pivotes_variables)
    indices_libres = [c for c in range(k) if (c + 1) not in columnas_pivote]
    cantidad_libres = len(indices_libres)

    # --- Paso 6: veredicto ---
    independientes = (cantidad_libres == 0)
    if independientes:
        veredicto = "LINEALMENTE INDEPENDIENTES (L.I.)"
        razon = ("El número de pivotes (" + str(cantidad_pivotes)
                 + ") es igual al número de vectores (" + str(k)
                 + "), así que no hay variables libres. La única solución de "
                 "c₁v₁ + … + cₖvₖ = 0 es la trivial "
                 "c₁ = c₂ = … = cₖ = 0.")
        relaciones = []
    else:
        veredicto = "LINEALMENTE DEPENDIENTES (L.D.)"
        razon = ("El número de pivotes (" + str(cantidad_pivotes)
                 + ") es menor que el número de vectores (" + str(k)
                 + "), así que quedan " + str(cantidad_libres)
                 + " variable(s) libre(s). Existe una solución NO trivial de "
                 "c₁v₁ + … + cₖvₖ = 0, con coeficientes no todos cero.")
        relaciones = relacion_de_dependencia(vectores)

    return {
        "k": k,
        "n": n,
        "matriz_reducida": [fila[:] for fila in aumentada],
        "cantidad_pivotes": cantidad_pivotes,
        "columnas_pivote": columnas_pivote,
        "cantidad_libres": cantidad_libres,
        "variables_libres": [c + 1 for c in indices_libres],
        "independientes": independientes,
        "veredicto": veredicto,
        "razon": razon,
        "relaciones": relaciones,
        "pasos": pasos,
    }


def informe_independencia(vectores):
    """Devuelve el análisis de independencia como texto listo para
    mostrar en pantalla o imprimir en consola, con el formato exacto
    que pide la Tarea 4: matriz reducida, número de pivotes y veredicto
    teórico explícito."""
    r = analizar_independencia(vectores)
    lineas = []
    lineas.append("Conjunto de " + str(r["k"]) + " vectores en R^" + str(r["n"]))
    lineas.append("")
    lineas.append("--- MATRIZ REDUCIDA [v₁ … vₖ | 0] ---")
    lineas.extend(formato_matriz(r["matriz_reducida"], r["k"]))
    lineas.append("")
    lineas.append("--- CONTEO ---")
    lineas.append("Número de pivotes  : " + str(r["cantidad_pivotes"]))
    lineas.append("Columnas pivote    : " + (
        ", ".join(str(c) for c in r["columnas_pivote"])
        if r["columnas_pivote"] else "ninguna"))
    lineas.append("Variables libres   : " + (
        ", ".join("c" + str(c) for c in r["variables_libres"])
        if r["variables_libres"] else "ninguna"))
    lineas.append("Cálculo            : k - pivotes = " + str(r["k"]) + " - "
                  + str(r["cantidad_pivotes"]) + " = "
                  + str(r["cantidad_libres"]) + " variable(s) libre(s)")
    lineas.append("")
    lineas.append("--- VEREDICTO TEÓRICO ---")
    lineas.append(r["veredicto"])
    lineas.append("")
    lineas.append(r["razon"])
    if r["relaciones"]:
        lineas.append("")
        lineas.append("Relación de dependencia encontrada:")
        for rel in r["relaciones"]:
            lineas.append("   " + _formato_suma_lineal(rel, "v") + " = 0")
    return "\n".join(lineas)


# =====================================================================
# MENÚ DE CONSOLA DEL MÓDULO 2 (MODO CLI)
# Cabecera con logotipo ASCII y menú interno, tal como pide la Tarea 4.
# La opción 0 despliega los teoremas clave del módulo.
# =====================================================================

def menu_consola():
    """Menú de texto del Módulo 2: Vectores e Independencia Lineal."""
    while True:
        mostrar_cabecera(LOGO_VECTORES)
        print("   0. Ver Teoremas Clave del Módulo")
        print("   1. Analizar independencia lineal (L.I. / L.D.)")
        print("   2. ¿Es y combinación lineal de v1...vk?")
        print("   3. Sumar dos vectores")
        print("   4. Restar dos vectores")
        print("   5. Multiplicar un vector por un escalar")
        print("   9. Volver al menú principal")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("vectores"))
            pausa()
        elif opcion == "1":
            _consola_independencia()
        elif opcion == "2":
            _consola_combinacion()
        elif opcion in ("3", "4"):
            _consola_suma_resta(opcion == "3")
        elif opcion == "5":
            _consola_escalar()
        else:
            print("   Opción no válida.")
            pausa()


def _pedir_conjunto():
    """Pide la cantidad de vectores k y su dimensión n, y luego los lee."""
    print()
    k = leer_entero("   Cantidad de vectores (k) = ")
    n = leer_entero("   Dimensión de cada vector (n) = ")
    print()
    vectores = []
    for j in range(k):
        vectores.append(leer_vector("v" + str(j + 1), n))
    return vectores


def _consola_independencia():
    """Opción 1: el requisito central del Programa 4."""
    mostrar_cabecera(LOGO_VECTORES)
    print("   ANÁLISIS DE INDEPENDENCIA LINEAL")
    vectores = _pedir_conjunto()
    limpiar_pantalla()
    print(informe_independencia(vectores))
    print()
    ver = preguntar("   ¿Ver el procedimiento completo? (s/n): ").strip().lower()
    if ver == "s":
        print()
        for linea in analizar_independencia(vectores)["pasos"]:
            print("   " + linea)
    pausa()


def _consola_combinacion():
    """Opción 2: decide si y es combinación lineal de los vectores."""
    mostrar_cabecera(LOGO_VECTORES)
    print("   ¿ES y COMBINACIÓN LINEAL DE v1...vk?")
    vectores = _pedir_conjunto()
    print()
    y = leer_vector("y", len(vectores[0]))
    es_cl, pesos, resultado = es_combinacion_lineal(y, vectores)
    limpiar_pantalla()
    if not es_cl:
        print("   RESULTADO: y NO es combinación lineal de los vectores.")
        print("   El sistema [v1 ... vk | y] resultó inconsistente.")
    elif resultado["clasificacion"] == "Consistente Determinado":
        print("   RESULTADO: y SÍ es combinación lineal, con pesos únicos.")
        print("   y = " + _formato_suma_lineal(pesos, "v"))
    else:
        print("   RESULTADO: y SÍ es combinación lineal, de INFINITAS formas.")
        print("   El sistema es consistente indeterminado (hay variables libres).")
    pausa()


def _consola_suma_resta(es_suma):
    """Opciones 3 y 4: suma y resta de dos vectores."""
    mostrar_cabecera(LOGO_VECTORES)
    print("   " + ("SUMA" if es_suma else "RESTA") + " DE DOS VECTORES")
    print()
    n = leer_entero("   Dimensión de los vectores (n) = ")
    print()
    u = leer_vector("u", n)
    v = leer_vector("v", n)
    r = sumar_vectores(u, v) if es_suma else restar_vectores(u, v)
    print()
    print("   u " + ("+" if es_suma else "−") + " v = " + formato_vector(r))
    pausa()


def _consola_escalar():
    """Opción 5: múltiplo escalar de un vector."""
    mostrar_cabecera(LOGO_VECTORES)
    print("   MULTIPLICACIÓN DE UN VECTOR POR UN ESCALAR")
    print()
    n = leer_entero("   Dimensión del vector (n) = ")
    print()
    u = leer_vector("u", n)
    c = leer_numero("   Escalar c = ")
    print()
    print("   " + formato(c) + " · u = " + formato_vector(escalar_por_vector(c, u)))
    pausa()
