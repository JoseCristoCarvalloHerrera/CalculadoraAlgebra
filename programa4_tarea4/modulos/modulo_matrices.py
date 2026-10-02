# -*- coding: utf-8 -*-
"""
=====================================================================
 MÓDULO 3: ÁLGEBRA DE MATRICES
 Calculadora de Álgebra Lineal - Proyecto Integrador - GRUPO 2
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Segundo Corte Evaluativo - Programa 4

 Operaciones con matrices y producto matriz-vector:
   - Suma, resta y múltiplo escalar, validando dimensiones m×n.
   - multiplicar_matrices(): regla fila-columna con bucles anidados,
     validando que las columnas de A igualen las filas de B.
   - Producto Ax y verificación de las propiedades de linealidad
     A(u+v) = Au + Av  y  A(cu) = c(Au).
   - MatricesOpsApp: la pantalla Tkinter de este módulo.

 PENDIENTE para el siguiente programa: matriz traspuesta e inversa.

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
    a_numero, formato, formato_matriz, con_subindice,
    _es_matriz_valida, _validar_matriz, _leer_dimensiones, LOGO_MATRICES,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_numero,
    leer_vector, leer_matriz, mostrar_matriz, pausa, preguntar,
)
from modulos.modulo_sistemas import resolver_sistema, verificar
from modulos.modulo_vectores import (
    formato_vector, matriz_por_vector, pasos_matriz_por_vector,
    verificar_aditividad_matriz_vector, verificar_homogeneidad_matriz_vector,
    es_combinacion_lineal, _formato_suma_lineal, _expansion_por_columnas,
)
from teoremas.resumen_teoremas import mostrar_teoremas, texto_teoremas


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


def transponer_matriz(A):
    """Devuelve la transpuesta de A: si A es m×n, el resultado es n×m.

    Método algebraico equivalente: la entrada (i, j) del resultado es la
    entrada (j, i) de la original,
        (Aᵀ)[i][j] = A[j][i].
    Dicho de otro modo, las COLUMNAS de A pasan a ser las FILAS de Aᵀ.
    No hay condición de tamaño: toda matriz tiene transpuesta."""
    _validar_matriz(A, "A")
    m, n = _leer_dimensiones(A)
    resultado = []
    for j in range(n):            # recorre las COLUMNAS de A
        fila = []
        for i in range(m):        # baja por esa columna
            fila.append(A[i][j])
        resultado.append(fila)    # la columna completa se guarda como fila
    return resultado


PROPIEDADES_TRANSPUESTA = (
    "(Aᵀ)ᵀ = A",
    "(A + B)ᵀ = Aᵀ + Bᵀ",
    "(rA)ᵀ = r·Aᵀ",
    "(AB)ᵀ = Bᵀ·Aᵀ",
)


def verificar_propiedad_transpuesta(propiedad, A, B=None, r=None):
    """Comprueba numéricamente una de las cuatro propiedades de la transpuesta.

    No demuestra la propiedad: calcula el lado IZQUIERDO y el lado DERECHO
    por separado, con los datos que dé el usuario, y los compara. Devuelve
    un diccionario con los dos lados, los pasos intermedios y si coinciden.
    """
    _validar_matriz(A, "A")

    if propiedad == "(Aᵀ)ᵀ = A":
        At = transponer_matriz(A)
        izquierda = transponer_matriz(At)
        derecha = [fila[:] for fila in A]
        intermedios = [("Aᵀ", At)]

    elif propiedad == "(A + B)ᵀ = Aᵀ + Bᵀ":
        _validar_matriz(B, "B")
        validar_operables_suma(A, B)
        suma = sumar_matrices(A, B)
        izquierda = transponer_matriz(suma)
        At, Bt = transponer_matriz(A), transponer_matriz(B)
        derecha = sumar_matrices(At, Bt)
        intermedios = [("A + B", suma), ("Aᵀ", At), ("Bᵀ", Bt)]

    elif propiedad == "(rA)ᵀ = r·Aᵀ":
        if r is None:
            raise ValueError("Falta el escalar r para esta propiedad.")
        rA = escalar_por_matriz(r, A)
        izquierda = transponer_matriz(rA)
        At = transponer_matriz(A)
        derecha = escalar_por_matriz(r, At)
        intermedios = [("r·A", rA), ("Aᵀ", At)]

    elif propiedad == "(AB)ᵀ = Bᵀ·Aᵀ":
        _validar_matriz(B, "B")
        validar_multiplicables(A, B)
        AB = multiplicar_matrices(A, B)
        izquierda = transponer_matriz(AB)
        At, Bt = transponer_matriz(A), transponer_matriz(B)
        derecha = multiplicar_matrices(Bt, At)
        intermedios = [("A·B", AB), ("Aᵀ", At), ("Bᵀ", Bt)]

    else:
        raise ValueError("Propiedad no reconocida: " + str(propiedad))

    return {
        "propiedad": propiedad,
        "izquierda": izquierda,
        "derecha": derecha,
        "intermedios": intermedios,
        "se_cumple": izquierda == derecha,
    }


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
        self.var_modo_ax = tk.StringVar(value="Calcular A·x")
        self.var_prop_t = tk.StringVar(value=PROPIEDADES_TRANSPUESTA[0])
        self.var_escalar_t = tk.StringVar(value="2")
        self.var_escalar_ax = tk.StringVar(value="2")
        self.celdas_A = {}
        self.celdas_B = {}
        self.celdas_vectores_ax = {}
        self.valores_vectores_ax = {}
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
        self._construir_grid_vectores_ax()

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


        tk.Label(self.marco_principal, text="Módulo de Operaciones Matriciales",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal,
                 text="Operaciones con matrices, producto matriz-vector Ax y "
                      "propiedades de linealidad, con dimensiones validadas.",
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
        self._llenar_tarjeta_producto_vectorial(self.frame_izq)
        self._llenar_tarjeta_transpuesta(self.frame_izq)

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
                                    text="Completa A y B para operar con matrices, o usa A\n"
                                         "con un vector para calcular Ax y verificar propiedades.",
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

    def _reconstruir_entradas(self):
        """Actualiza A/B y los vectores auxiliares manteniendo lo escrito."""
        self._construir_grids()
        self._construir_grid_vectores_ax()

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
                   command=self._reconstruir_entradas).grid(row=1, column=1, sticky="w", padx=(0, 16))
        tk.Label(cont, text="Columnas", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=var_n,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._reconstruir_entradas).grid(row=1, column=3, sticky="w")

        def aplicar():
            self._leer_dimension(var_m, 2)
            self._leer_dimension(var_n, 2)
            self._reconstruir_entradas()

        self.botones_mas[letra] = tk.Button(
            cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO,
            relief="flat", cursor="hand2", padx=6, pady=2,
            activebackground=ACENTO_HOVER, activeforeground=FONDO, command=aplicar)
        self.botones_mas[letra].grid(row=0, column=4, sticky="e", padx=(8, 0), pady=(0, 8))
        return tarjeta

    def _llenar_tarjeta_producto_vectorial(self, padre):
        """Crea el formulario para Ax, aditividad y homogeneidad de Ax."""
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 8))

        tk.Label(cont, text="Producto matriz-vector y propiedades",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO,
                 anchor="w").pack(fill="x", pady=(0, 6))
        tk.Label(cont, text="Usa la matriz A ingresada arriba. La longitud de cada vector debe coincidir con sus columnas.",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 justify="left", wraplength=420, anchor="w").pack(fill="x", pady=(0, 6))

        tk.Label(cont, text="Operación", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(anchor="w")
        opciones = ("Calcular A·x",
                    "Verificar A(u + v) = Au + Av",
                    "Verificar A(cu) = c(Au)")
        selector = tk.OptionMenu(cont, self.var_modo_ax, *opciones,
                                 command=lambda _valor: self._construir_grid_vectores_ax())
        selector.configure(font=self.fuente_body, bg="#FFFFFF", fg=TEXTO,
                           activebackground=BOTON_SEC, relief="solid", bd=1,
                           highlightthickness=0, anchor="w")
        selector.pack(fill="x", pady=(2, 6))

        self.frame_escalar_ax = tk.Frame(cont, bg=TARJETA)
        tk.Label(self.frame_escalar_ax, text="Escalar c =", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        tk.Entry(self.frame_escalar_ax, textvariable=self.var_escalar_ax,
                 font=self.fuente_mono, width=7, justify="center",
                 relief="solid", bd=1).pack(side="left", padx=6)

        self.frame_vectores_ax = tk.Frame(cont, bg=TARJETA)
        self.frame_vectores_ax.pack(fill="x", pady=(4, 2))

        self.boton_calcular_ax = tk.Button(
            cont, text="Calcular / verificar", font=self.fuente_boton,
            bg=ACENTO, fg=FONDO, relief="flat", cursor="hand2",
            padx=12, pady=8, activebackground=ACENTO_HOVER,
            activeforeground=FONDO, command=self._al_producto_vectorial)
        self.boton_calcular_ax.pack(fill="x", pady=(6, 0))

    def _llenar_tarjeta_transpuesta(self, padre):
        """Tarjeta para comprobar las cuatro propiedades de la transpuesta.
        Usa las matrices A y B ya ingresadas arriba."""
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 12))

        tk.Label(cont, text="Propiedades de la transpuesta",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO,
                 anchor="w").pack(fill="x", pady=(0, 6))
        tk.Label(cont, text="Usa las matrices A y B ingresadas arriba. Se calcula cada lado por separado y se comparan.",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 justify="left", wraplength=420, anchor="w").pack(fill="x", pady=(0, 6))

        selector = tk.OptionMenu(cont, self.var_prop_t, *PROPIEDADES_TRANSPUESTA)
        selector.configure(font=self.fuente_body, bg="#FFFFFF", fg=TEXTO,
                           activebackground=BOTON_SEC, relief="solid", bd=1,
                           highlightthickness=0, anchor="w")
        selector.pack(fill="x", pady=(2, 6))

        fila_r = tk.Frame(cont, bg=TARJETA)
        fila_r.pack(fill="x", pady=(0, 6))
        tk.Label(fila_r, text="Escalar r =", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        tk.Entry(fila_r, textvariable=self.var_escalar_t, font=self.fuente_mono,
                 width=7, justify="center", relief="solid", bd=1).pack(side="left", padx=6)
        tk.Label(fila_r, text="(solo para (rA)ᵀ = r·Aᵀ)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")

        tk.Button(cont, text="Verificar propiedad", font=self.fuente_boton,
                  bg=ACENTO, fg=FONDO, relief="flat", cursor="hand2",
                  padx=12, pady=8, activebackground=ACENTO_HOVER,
                  activeforeground=FONDO,
                  command=self._al_verificar_transpuesta).pack(fill="x")

    def _roles_vectores_ax(self):
        """Devuelve los vectores que necesita la operación seleccionada."""
        modo = self.var_modo_ax.get()
        if modo == "Verificar A(u + v) = Au + Av":
            return ("u", "v")
        if modo == "Verificar A(cu) = c(Au)":
            return ("u",)
        return ("x",)

    def _construir_grid_vectores_ax(self):
        """Dibuja vectores columna de longitud igual al número de columnas de A."""
        if not hasattr(self, "frame_vectores_ax"):
            return
        for nombre, celdas in self.celdas_vectores_ax.items():
            cache = self.valores_vectores_ax.setdefault(nombre, {})
            for i, celda in celdas.items():
                cache[i] = celda.get()
        for hijo in self.frame_vectores_ax.winfo_children():
            hijo.destroy()
        self.celdas_vectores_ax = {}

        if self.var_modo_ax.get() == "Verificar A(cu) = c(Au)":
            self.frame_escalar_ax.pack(fill="x", before=self.frame_vectores_ax,
                                       pady=(2, 4))
        else:
            self.frame_escalar_ax.pack_forget()

        n = self._leer_dimension(self.var_na, 2)
        for columna, nombre in enumerate(self._roles_vectores_ax()):
            marco = tk.Frame(self.frame_vectores_ax, bg=TARJETA)
            marco.grid(row=0, column=columna, sticky="nw", padx=(0, 12))
            tk.Label(marco, text="Vector " + nombre, font=self.fuente_encab,
                     bg=TARJETA, fg=ACENTO).grid(row=0, column=0, sticky="w", pady=(0, 3))
            self.celdas_vectores_ax[nombre] = {}
            for i in range(n):
                valor_previo = self.valores_vectores_ax.get(nombre, {}).get(i, "")
                variable = tk.StringVar(value=valor_previo)
                self.celdas_vectores_ax[nombre][i] = variable
                tk.Entry(marco, textvariable=variable, font=self.fuente_mono,
                         width=7, justify="center", relief="solid", bd=1,
                         bg=CELDA_FONDO).grid(row=i + 1, column=0, pady=2)

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
            ("Transpuesta de A", self._al_transponer_a),
            ("Transpuesta de B", self._al_transponer_b),
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

    def _al_transponer_a(self):
        """Botón «Transpuesta de A»."""
        self._transponer(self.celdas_A, self.var_ma, self.var_na, "A")

    def _al_transponer_b(self):
        """Botón «Transpuesta de B»."""
        self._transponer(self.celdas_B, self.var_mb, self.var_nb, "B")

    def _al_verificar_transpuesta(self):
        """Comprueba la propiedad elegida con las matrices A y B de la pantalla."""
        try:
            self._construir_grids()
            propiedad = self.var_prop_t.get()
            A = self._leer_matriz(self.celdas_A, self._leer_dimension(self.var_ma, 2),
                                  self._leer_dimension(self.var_na, 2), "A")
            B = None
            r = None
            if propiedad in ("(A + B)ᵀ = Aᵀ + Bᵀ", "(AB)ᵀ = Bᵀ·Aᵀ"):
                B = self._leer_matriz(self.celdas_B,
                                      self._leer_dimension(self.var_mb, 2),
                                      self._leer_dimension(self.var_nb, 2), "B")
            if propiedad == "(rA)ᵀ = r·Aᵀ":
                r = a_numero(self.var_escalar_t.get())

            res = verificar_propiedad_transpuesta(propiedad, A, B, r)

            conclusion = ("Conclusión: los dos lados coinciden, se cumple "
                          + propiedad + "."
                          if res["se_cumple"] else
                          "Conclusión: los lados no coinciden; revisa los datos.")
            pasos = ["VERIFICACIÓN DE: " + propiedad, "", "Matriz A:",
                     *formato_matriz(A)]
            if B is not None:
                pasos += ["", "Matriz B:", *formato_matriz(B)]
            if r is not None:
                pasos += ["", "Escalar r = " + formato(r)]
            for titulo, M in res["intermedios"]:
                pasos += ["", titulo + ":", *formato_matriz(M)]
            pasos += ["", "LADO IZQUIERDO:", *formato_matriz(res["izquierda"]),
                      "", "LADO DERECHO:", *formato_matriz(res["derecha"]),
                      "", conclusion]

            self._mostrar_matriz("Lado izquierdo de " + propiedad,
                                 res["izquierda"], conclusion, pasos=pasos)
        except ValueError as e:
            self._mostrar_error(str(e))

    def _transponer(self, celdas, var_filas, var_columnas, nombre):
        """Transpone la matriz indicada y muestra el resultado.
        Se usa para A y para B: solo cambian las celdas que se leen."""
        try:
            self._construir_grids()
            M = self._leer_matriz(celdas, self._leer_dimension(var_filas, 2),
                                  self._leer_dimension(var_columnas, 2), nombre)
            T = transponer_matriz(M)
            self._mostrar_matriz(
                nombre + "ᵀ", T,
                "(" + nombre + "ᵀ)[i][j] = " + nombre + "[j][i]  "
                "(las columnas de " + nombre + " pasan a ser filas).")
        except ValueError as e:
            self._mostrar_error(str(e))

    def _leer_vector_ax(self, nombre):
        """Lee un vector auxiliar e informa cuál componente tiene un error."""
        n = self._leer_dimension(self.var_na, 2)
        celdas = self.celdas_vectores_ax.get(nombre, {})
        vector = []
        for i in range(n):
            try:
                vector.append(a_numero(celdas[i].get()))
            except (KeyError, ValueError):
                raise ValueError("Revisa el vector " + nombre + ", componente "
                                 + str(i + 1) + ". " + AYUDA_NUMERO)
        return vector

    def _al_producto_vectorial(self):
        """Calcula Ax o comprueba una de las dos propiedades de linealidad."""
        try:
            self._reconstruir_entradas()
            A = self._leer_matriz(self.celdas_A,
                                  self._leer_dimension(self.var_ma, 2),
                                  self._leer_dimension(self.var_na, 2), "A")
            modo = self.var_modo_ax.get()

            if modo == "Verificar A(u + v) = Au + Av":
                u = self._leer_vector_ax("u")
                v = self._leer_vector_ax("v")
                r = verificar_aditividad_matriz_vector(A, u, v)
                conclusion = ("Conclusión: se cumple A(u + v) = Au + Av; "
                              "ambos lados son iguales." if r["se_cumple"] else
                              "Conclusión: los lados no coinciden; revisa los datos.")
                detalle = (
                    "1. u + v = " + formato_vector(r["u_mas_v"]) + "\n"
                    "2. A(u + v) = " + formato_vector(r["izquierda"]) + "\n"
                    "3. Au = " + formato_vector(r["Au"]) + "\n"
                    "   Av = " + formato_vector(r["Av"]) + "\n"
                    "4. Au + Av = " + formato_vector(r["derecha"]) + "\n\n"
                    + conclusion)
                pasos = ["VERIFICACIÓN DE ADITIVIDAD: A(u + v) = Au + Av", "",
                         "Matriz A:", *formato_matriz(A),
                         "u = " + formato_vector(u),
                         "v = " + formato_vector(v), "",
                         "1. Suma de los vectores: u + v = "
                         + formato_vector(r["u_mas_v"]), "",
                         *pasos_matriz_por_vector(A, r["u_mas_v"]), "",
                         *pasos_matriz_por_vector(A, u), "",
                         *pasos_matriz_por_vector(A, v), "",
                         "Suma de resultados: Au + Av = "
                         + formato_vector(r["Au"]) + " + "
                         + formato_vector(r["Av"]) + " = "
                         + formato_vector(r["derecha"]), "", conclusion]
                self._mostrar_vector_resultado("Verificación de aditividad",
                                               r["izquierda"], detalle, pasos)
                return

            if modo == "Verificar A(cu) = c(Au)":
                u = self._leer_vector_ax("u")
                c = a_numero(self.var_escalar_ax.get())
                r = verificar_homogeneidad_matriz_vector(A, c, u)
                conclusion = ("Conclusión: se cumple A(cu) = c(Au); "
                              "ambos lados son iguales." if r["se_cumple"] else
                              "Conclusión: los lados no coinciden; revisa los datos.")
                detalle = (
                    "Escalar: c = " + formato(c) + "\n"
                    "1. cu = " + formato(c) + "·" + formato_vector(u)
                    + " = " + formato_vector(r["cu"]) + "\n"
                    "2. A(cu) = " + formato_vector(r["izquierda"]) + "\n"
                    "3. Au = " + formato_vector(r["Au"]) + "\n"
                    "4. c(Au) = " + formato(c) + "·"
                    + formato_vector(r["Au"]) + " = "
                    + formato_vector(r["derecha"]) + "\n\n" + conclusion)
                pasos = ["VERIFICACIÓN DE HOMOGENEIDAD: A(cu) = c(Au)", "",
                         "Matriz A:", *formato_matriz(A),
                         "u = " + formato_vector(u), "c = " + formato(c), "",
                         "1. Multiplicar u por c: cu = "
                         + formato_vector(r["cu"]), "",
                         *pasos_matriz_por_vector(A, r["cu"]), "",
                         *pasos_matriz_por_vector(A, u), "",
                         "Multiplicar Au por c: c(Au) = " + formato(c) + "·"
                         + formato_vector(r["Au"]) + " = "
+ formato_vector(r["derecha"]), "", conclusion]
                self._mostrar_vector_resultado("Verificación de homogeneidad",
                                               r["izquierda"], detalle, pasos)
                return

            x = self._leer_vector_ax("x")
            resultado = matriz_por_vector(A, x)
            columnas = [[fila[j] for fila in A] for j in range(len(A[0]))]
            combinacion = _formato_suma_lineal(x, "a")
            detalle = ("Cada componente es el producto de una fila de A por x.\n"
                       "Como x = " + formato_vector(x) + ", también es la combinación "
                       "lineal de las columnas de A:\nAx = " + combinacion + " = "
                       + formato_vector(resultado))
            pasos = ["PRODUCTO MATRIZ-VECTOR Ax", "", "Matriz A:",
                     *formato_matriz(A), "x = " + formato_vector(x), "",
                     *pasos_matriz_por_vector(A, x), "",
                     "COLUMNAS DE A Y COMBINACIÓN LINEAL EXPLÍCITA:",
                     *_expansion_por_columnas(x, columnas, "a", resultado),
                     "Ax = " + combinacion + " = " + formato_vector(resultado)]
            self._mostrar_vector_resultado("Producto A·x", resultado,
                                           detalle, pasos)
        except ValueError as e:
            self._mostrar_error(str(e))

    def _mostrar_vector_resultado(self, titulo, vector, detalle, pasos):
        """Presenta el resultado vectorial y mantiene el botón de desarrollo."""
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

        sub = self._sub_tarjeta("RESULTADO", EXITO)
        cartel = tk.Frame(sub, bg=EXITO, padx=14, pady=10)
        cartel.pack(fill="x", pady=(0, 6))
        self._texto_ajustable(tk.Label(cartel, text=titulo, font=self.fuente_big,
                                       bg=EXITO, fg=FONDO)).pack(fill="x")
        self._texto_ajustable(tk.Label(sub, text="Vector calculado / lado izquierdo: "
                                       + formato_vector(vector),
                                       font=self.fuente_mono, bg=TARJETA,
                                       fg=TEXTO)).pack(fill="x", pady=(0, 6))
        self._texto_ajustable(tk.Label(sub, text=detalle, font=self.fuente_mono,
                                       bg=TARJETA, fg=TEXTO_SUAVE,
                                       justify="left", anchor="w",
                                       wraplength=480)).pack(fill="x", pady=(0, 8))

        self.ultimo_resultado = {
            "titulo": titulo,
            "vector": vector,
            "pasos": pasos,
            "procedimiento_titulo": "DESARROLLO PASO A PASO",
        }
        self.boton_procedimiento.configure(text="Ver procedimiento")
        if pasos:
            self.boton_procedimiento.pack(side="right")
        else:
            self.boton_procedimiento.pack_forget()
        self.lienzo_resultado.yview_moveto(0)
        self.raiz.update_idletasks()
        self._ajustar_textos()

    # ---------- panel de resultados ----------
    def _ajustar_textos(self, ancho_disponible=None):
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(120, ancho_disponible - 56)
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

        self.ultimo_resultado = {"titulo": titulo, "matriz": C, "pasos": pasos,
                                 "procedimiento_titulo": "PROCEDIMIENTO DEL PRODUCTO A·B"}
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
            if self.sub_procedimiento is None:
                self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA,
                                                  highlightbackground=BOTON_SEC,
                                                  highlightthickness=1, bd=0)
                tk.Label(self.sub_procedimiento,
                         text=self.ultimo_resultado.get(
                             "procedimiento_titulo", "DESARROLLO PASO A PASO"),
                         font=self.fuente_encab, bg=TARJETA, fg=TEXTO,
                         anchor="w").pack(fill="x", padx=14, pady=(10, 6))
                pasos = self.ultimo_resultado["pasos"]
                texto_proc = pasos if isinstance(pasos, str) else "\n".join(pasos)
                self._texto_ajustable(
                    tk.Label(self.sub_procedimiento, text=texto_proc,
                             font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                             justify="left", anchor="nw"
                             )).pack(fill="x", padx=14, pady=(0, 10))
            self.sub_procedimiento.pack(fill="x", padx=16, pady=(8, 2), anchor="n")
            self.boton_procedimiento.configure(text="Ocultar procedimiento")
            self.procedimiento_visible = True
        self.raiz.update_idletasks()
        self._ajustar_textos()
        self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all"))

    def _mostrar_error(self, mensaje):
        messagebox.showerror("Operación no válida", mensaje)


    def _ver_teoremas(self):
        """Opción '0. Ver Teoremas Clave del Módulo' que pide la Tarea 4.
        Despliega el resumen que vive en teoremas/resumen_teoremas.py."""
        mostrar_teoremas(self.raiz, "matrices", "Módulo 3: Álgebra de Matrices")

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


# =====================================================================

# =====================================================================
# MENÚ DE CONSOLA DEL MÓDULO 3 (MODO CLI)
# =====================================================================

def menu_consola():
    """Menú de texto del Módulo 3: Álgebra de Matrices."""
    while True:
        mostrar_cabecera(LOGO_MATRICES)
        print("   0. Ver Teoremas Clave del Módulo")
        print("   1. Sumar dos matrices")
        print("   2. Restar dos matrices")
        print("   3. Multiplicar una matriz por un escalar")
        print("   4. Multiplicar dos matrices (A · B)")
        print("   5. Producto matriz-vector (A · x)")
        print("   6. Verificar A(u + v) = Au + Av")
        print("   7. Verificar A(cu) = c(Au)")
        print("   8. Transpuesta (Aᵀ) y sus propiedades")
        print("   9. Volver al menú principal")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("matrices"))
            pausa()
        elif opcion in ("1", "2", "3"):
            _consola_operacion_basica(opcion)
        elif opcion == "4":
            _consola_producto()
        elif opcion == "5":
            _consola_ax()
        elif opcion in ("6", "7"):
            _consola_propiedad(opcion == "6")
        elif opcion == "8":
            _menu_transpuesta()
        else:
            print("   Opción no válida.")
            pausa()


def _pedir_matriz(nombre):
    """Pide las dimensiones y luego las entradas de una matriz."""
    filas = leer_entero("   Filas de " + nombre + " = ")
    columnas = leer_entero("   Columnas de " + nombre + " = ")
    print()
    return leer_matriz(nombre, filas, columnas)


def _consola_operacion_basica(opcion):
    """Opciones 1, 2 y 3: suma, resta y múltiplo escalar."""
    titulos = {"1": "SUMA DE MATRICES", "2": "RESTA DE MATRICES",
               "3": "MATRIZ POR UN ESCALAR"}
    mostrar_cabecera(LOGO_MATRICES)
    print("   " + titulos[opcion])
    print()
    try:
        A = _pedir_matriz("A")
        if opcion == "3":
            c = leer_numero("   Escalar c = ")
            resultado = escalar_por_matriz(c, A)
        else:
            print()
            B = _pedir_matriz("B")
            resultado = sumar_matrices(A, B) if opcion == "1" else restar_matrices(A, B)
        print()
        mostrar_matriz(resultado, titulo="   RESULTADO:")
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _menu_transpuesta():
    """Submenú de la opción 8: calcular la transpuesta o verificar sus
    cuatro propiedades."""
    while True:
        mostrar_cabecera(LOGO_MATRICES)
        print("   TRANSPUESTA Y SUS PROPIEDADES")
        print()
        print("   1. Calcular la transpuesta de una matriz")
        print()
        print("   Verificar una propiedad:")
        for i, prop in enumerate(PROPIEDADES_TRANSPUESTA, start=2):
            print("   " + str(i) + ". " + prop)
        print()
        print("   9. Volver")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "1":
            _consola_transpuesta()
        elif opcion in ("2", "3", "4", "5"):
            _consola_propiedad_transpuesta(
                PROPIEDADES_TRANSPUESTA[int(opcion) - 2])
        else:
            print("   Opción no válida.")
            pausa()


def _consola_propiedad_transpuesta(propiedad):
    """Pide los datos que la propiedad necesita, calcula los dos lados
    por separado y los compara."""
    mostrar_cabecera(LOGO_MATRICES)
    print("   VERIFICAR:  " + propiedad)
    print()
    try:
        A = _pedir_matriz("A")
        B = None
        r = None
        if propiedad in ("(A + B)ᵀ = Aᵀ + Bᵀ", "(AB)ᵀ = Bᵀ·Aᵀ"):
            print()
            B = _pedir_matriz("B")
        if propiedad == "(rA)ᵀ = r·Aᵀ":
            r = leer_numero("   Escalar r = ")

        resultado = verificar_propiedad_transpuesta(propiedad, A, B, r)

        print()
        for titulo, M in resultado["intermedios"]:
            mostrar_matriz(M, titulo="   " + titulo + ":")
            print()
        mostrar_matriz(resultado["izquierda"], titulo="   LADO IZQUIERDO:")
        print()
        mostrar_matriz(resultado["derecha"], titulo="   LADO DERECHO:")
        print()
        if resultado["se_cumple"]:
            print("   Los dos lados coinciden: se cumple  " + propiedad)
        else:
            print("   Los lados NO coinciden. Revisá los datos ingresados.")
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _consola_transpuesta():
    """Opción 8: transpuesta de una matriz."""
    mostrar_cabecera(LOGO_MATRICES)
    print("   TRANSPUESTA DE UNA MATRIZ")
    print()
    try:
        A = _pedir_matriz("A")
        resultado = transponer_matriz(A)
        m, n = _leer_dimensiones(A)
        print()
        mostrar_matriz(A, titulo="   MATRIZ ORIGINAL A (" + str(m) + "x" + str(n) + "):")
        print()
        mostrar_matriz(resultado, titulo="   TRANSPUESTA Aᵀ (" + str(n) + "x" + str(m) + "):")
        print()
        print("   Regla: (Aᵀ)[i][j] = A[j][i]. Las columnas de A pasan a ser")
        print("   las filas de Aᵀ, por eso el tamaño se invierte.")
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _consola_producto():
    """Opción 4: producto A · B con la regla fila-columna."""
    mostrar_cabecera(LOGO_MATRICES)
    print("   MULTIPLICACIÓN DE MATRICES  A · B")
    print()
    try:
        A = _pedir_matriz("A")
        print()
        B = _pedir_matriz("B")
        resultado = multiplicar_matrices(A, B)
        print()
        mostrar_matriz(resultado, titulo="   RESULTADO A · B:")
        print()
        if preguntar("   ¿Ver el procedimiento? (s/n): ").strip().lower() == "s":
            print()
            for linea in pasos_multiplicar_matrices(A, B):
                print("   " + linea)
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _consola_ax():
    """Opción 5: producto matriz-vector A · x."""
    mostrar_cabecera(LOGO_MATRICES)
    print("   PRODUCTO MATRIZ-VECTOR  A · x")
    print()
    try:
        A = _pedir_matriz("A")
        print()
        x = leer_vector("x", len(A[0]))
        resultado = matriz_por_vector(A, x)
        print()
        print("   A · x = " + formato_vector(resultado))
        print()
        for linea in pasos_matriz_por_vector(A, x):
            print("   " + linea)
        print()
        print("   Como combinación lineal de las columnas de A:")
        print("   " + _expansion_por_columnas(x, A, "a", resultado))
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _consola_propiedad(es_aditividad):
    """Opciones 6 y 7: las propiedades de linealidad de Ax."""
    mostrar_cabecera(LOGO_MATRICES)
    print("   VERIFICAR " + ("A(u + v) = Au + Av" if es_aditividad
                             else "A(cu) = c(Au)"))
    print()
    try:
        A = _pedir_matriz("A")
        print()
        u = leer_vector("u", len(A[0]))
        if es_aditividad:
            v = leer_vector("v", len(A[0]))
            r = verificar_aditividad_matriz_vector(A, u, v)
            print()
            print("   1. u + v      = " + formato_vector(r["u_mas_v"]))
            print("   2. A(u + v)   = " + formato_vector(r["izquierda"]))
            print("   3. Au         = " + formato_vector(r["Au"]))
            print("      Av         = " + formato_vector(r["Av"]))
            print("   4. Au + Av    = " + formato_vector(r["derecha"]))
            print()
            print("   Conclusión: " + ("se cumple A(u + v) = Au + Av; ambos lados son iguales."
                                       if r["se_cumple"] else "NO se cumple."))
        else:
            c = leer_numero("   Escalar c = ")
            r = verificar_homogeneidad_matriz_vector(A, c, u)
            print()
            print("   1. c·u        = " + formato_vector(r["c_por_u"]))
            print("   2. A(c·u)     = " + formato_vector(r["izquierda"]))
            print("   3. Au         = " + formato_vector(r["Au"]))
            print("   4. c·(Au)     = " + formato_vector(r["derecha"]))
            print()
            print("   Conclusión: " + ("se cumple A(cu) = c(Au); ambos lados son iguales."
                                       if r["se_cumple"] else "NO se cumple."))
    except ValueError as error:
        print("\n   " + str(error))
    pausa()
