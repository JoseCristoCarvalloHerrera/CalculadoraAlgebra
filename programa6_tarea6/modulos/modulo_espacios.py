# -*- coding: utf-8 -*-
"""
Módulo 6 de la Calculadora de Álgebra Lineal: transformaciones lineales
y subespacios asociados a la matriz A.

Para la transformación T(x) = A·x calcula el NÚCLEO (las soluciones de
A·x = 0), la IMAGEN (el espacio generado por las columnas pivote de A),
el RANGO, la NULIDAD y comprueba el TEOREMA DE LA DIMENSIÓN
rango + nulidad = n. También verifica las dos propiedades que definen a
una transformación lineal, T(u+v) = T(u)+T(v) y T(c·u) = c·T(u), y si un
vector b pertenece a la imagen (es combinación lineal de las columnas).

Temas de clase: Ax = 0 y conjuntos solución (Sesión 4), independencia
lineal (Sesión 6) y transformaciones lineales (Sesión 7). Reutiliza el
motor de reducción por filas y el producto matriz-vector ya programados.

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
    BOTON_SEC, BOTON_SEC_HOVER, CELDA_FONDO, CELDA_FOCO,
    EXITO, ERROR, ADVERTENCIA, LETRA_MONO, MAX_DIMENSION,
    a_numero, formato, formato_matriz, con_subindice, nombre_variable,
    _validar_matriz, _leer_dimensiones, LOGO_ESPACIOS,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_numero,
    leer_matriz, leer_vector, mostrar_matriz, pausa, preguntar,
)
from modulos.modulo_sistemas import escalonar
from modulos.modulo_vectores import (
    matriz_por_vector, formato_vector, es_combinacion_lineal,
    verificar_aditividad_matriz_vector, verificar_homogeneidad_matriz_vector,
)
from teoremas.resumen_teoremas import mostrar_teoremas, texto_teoremas


# =====================================================================
# BLOQUE 1: CÁLCULO DEL NÚCLEO, LA IMAGEN, EL RANGO Y LA NULIDAD
# (funciones puras: no imprimen ni piden datos)
# =====================================================================

def reducir_homogeneo(A):
    """Reduce la matriz aumentada [A | 0] a su forma escalonada reducida.

    Devuelve (reducida, pivotes, columnas_libres, pasos). 'reducida' es
    solo la parte de A (sin la columna de ceros), 'pivotes' es la lista
    de pares (fila, columna) donde quedó un 1 principal y 'pasos' es el
    desarrollo de las operaciones elementales.
    """
    _validar_matriz(A, "A")
    m, n = _leer_dimensiones(A)

    # Se trabaja sobre [A | 0] porque el núcleo es el conjunto solución
    # del sistema HOMOGÉNEO A·x = 0: la columna de ceros nunca genera
    # una fila inconsistente, así que el sistema siempre es compatible.
    aumentada = [[Fraction(A[i][j]) for j in range(n)] + [Fraction(0)]
                 for i in range(m)]
    pasos, pivotes = escalonar(aumentada, n)

    reducida = [fila[:n] for fila in aumentada]
    columnas_pivote = [columna for _, columna in pivotes]
    columnas_libres = [j for j in range(n) if j not in columnas_pivote]
    return reducida, pivotes, columnas_libres, pasos


def base_del_nucleo(reducida, pivotes, columnas_libres, n):
    """Construye una base del núcleo a partir de la forma reducida.

    Hay un vector por cada VARIABLE LIBRE: se le da el valor 1 a esa
    variable, 0 a las demás libres, y cada variable básica queda
    despejada de su fila como x_pivote = −(coeficiente de la libre).
    """
    base = []
    for libre in columnas_libres:
        vector = [Fraction(0)] * n
        vector[libre] = Fraction(1)
        for fila, columna in pivotes:
            # La fila dice  x_columna + r·x_libre = 0  ->  x_columna = −r.
            vector[columna] = -reducida[fila][libre]
        base.append(vector)
    return base


def base_de_la_imagen(A, pivotes):
    """Devuelve las columnas PIVOTE de la matriz A original como vectores.

    Se toman de A y no de la forma reducida: reducir por filas cambia el
    espacio generado por las columnas, así que la base de la imagen son
    las columnas originales en las posiciones donde apareció un pivote.
    """
    m, _ = _leer_dimensiones(A)
    return [[Fraction(A[i][columna]) for i in range(m)]
            for _, columna in pivotes]


def analizar_transformacion(A):
    """Analiza T(x) = A·x y devuelve todo lo que pide el tema en un dict.

    Incluye rango, nulidad, base del núcleo, base de la imagen, si T es
    uno a uno y si es sobre, y la comprobación rango + nulidad = n.
    """
    m, n = _leer_dimensiones(A)
    reducida, pivotes, libres, pasos = reducir_homogeneo(A)
    rango = len(pivotes)
    nulidad = n - rango
    return {
        "A": A, "m": m, "n": n,
        "reducida": reducida, "pivotes": pivotes,
        "columnas_pivote": [columna + 1 for _, columna in pivotes],
        "columnas_libres": [j + 1 for j in libres],
        "rango": rango,
        "nulidad": nulidad,
        "base_nucleo": base_del_nucleo(reducida, pivotes, libres, n),
        "base_imagen": base_de_la_imagen(A, pivotes),
        # T es uno a uno si el núcleo solo contiene al vector cero, y es
        # sobre si la imagen llena todo R^m (rango igual al número de filas).
        "uno_a_uno": nulidad == 0,
        "sobre": rango == m,
        "teorema_dimension": rango + nulidad == n,
        "pasos": pasos,
    }


def pertenece_a_la_imagen(A, b):
    """Dice si b está en la imagen de T, o sea si A·x = b tiene solución.

    Pertenecer a la imagen es exactamente ser combinación lineal de las
    columnas de A, así que se reutiliza el verificador del Módulo 2.
    """
    _validar_matriz(A, "A")
    m, n = _leer_dimensiones(A)
    if len(b) != m:
        raise ValueError("El vector b debe tener " + str(m)
                         + " componente(s), igual al número de filas de A.")
    columnas = [[A[i][j] for i in range(m)] for j in range(n)]
    return es_combinacion_lineal(list(b), columnas)


# =====================================================================
# BLOQUE 2: DESARROLLOS PASO A PASO (listas de texto para mostrar)
# =====================================================================

def _producto_visible(a, b):
    """Escribe un producto con los dos factores entre paréntesis: (-1)·(3)."""
    return "(" + formato(a) + ")·(" + formato(b) + ")"


def _cuentas_producto(A, x, nombre="A·v"):
    """Cuentas de A·x fila por fila, una línea por componente."""
    _, n = _leer_dimensiones(A)
    lineas = []
    for i, fila in enumerate(A):
        terminos = [_producto_visible(fila[j], x[j]) for j in range(n)]
        total = sum((fila[j] * x[j] for j in range(n)), Fraction(0))
        lineas.append("(" + nombre + ")[" + str(i + 1) + "] = "
                      + " + ".join(terminos).replace("+ -", "- ")
                      + " = " + formato(total))
    return lineas


def pasos_comprobar_nucleo(A, base):
    """Comprueba que cada vector de la base del núcleo cumple A·v = 0.

    Devuelve (lineas, se_cumple). Es la prueba de que los vectores
    hallados pertenecen de verdad al núcleo y no solo salieron del
    algoritmo.
    """
    lineas = ["=" * 58, "COMPROBACIÓN: A · v = 0 para cada vector de la base",
              "=" * 58, ""]
    if not base:
        lineas.append("El núcleo es {0}: el único vector es el cero y")
        lineas.append("A · 0 = 0 se cumple siempre.")
        return lineas, True

    se_cumple = True
    for indice, vector in enumerate(base):
        producto = matriz_por_vector(A, vector)
        correcto = all(valor == 0 for valor in producto)
        se_cumple = se_cumple and correcto
        lineas.append(con_subindice("v" + str(indice + 1)) + " = "
                      + formato_vector(vector))
        lineas.extend("    " + linea
                      for linea in _cuentas_producto(A, vector))
        lineas.append("    A · " + con_subindice("v" + str(indice + 1))
                      + " = " + formato_vector(producto)
                      + ("   ✓ pertenece al núcleo" if correcto
                         else "   ✗ NO pertenece al núcleo"))
        lineas.append("")
    return lineas, se_cumple


def pasos_teorema_dimension(datos):
    """Escribe la comprobación del teorema de la dimensión con sus números."""
    rango, nulidad, n = datos["rango"], datos["nulidad"], datos["n"]
    lineas = ["=" * 58, "TEOREMA DE LA DIMENSIÓN", "=" * 58, "",
              "Para T: Rⁿ -> Rᵐ dada por T(x) = A·x se cumple",
              "    dim(Imagen) + dim(Núcleo) = n   (columnas de A)",
              "    rango(A) + nulidad(A) = n", ""]
    lineas.append("rango(A)   = " + str(rango)
                  + "   (columnas pivote: "
                  + (", ".join(str(c) for c in datos["columnas_pivote"])
                     or "ninguna") + ")")
    lineas.append("nulidad(A) = " + str(nulidad)
                  + "   (variables libres: "
                  + (", ".join(nombre_variable(c)
                               for c in datos["columnas_libres"]) or "ninguna")
                  + ")")
    lineas.append("")
    lineas.append("    " + str(rango) + " + " + str(nulidad) + " = "
                  + str(rango + nulidad) + "   y   n = " + str(n))
    lineas.append("")
    lineas.append("El teorema se cumple." if datos["teorema_dimension"]
                  else "¡Atención! El teorema no se cumple; revisá la matriz.")
    return lineas


def pasos_linealidad(A, u, v, escalar):
    """Desarrolla las dos propiedades que definen una transformación lineal.

    Devuelve (lineas, se_cumple) con el detalle de T(u+v) = T(u)+T(v) y
    de T(c·u) = c·T(u), reutilizando los verificadores del Módulo 2.
    """
    suma = verificar_aditividad_matriz_vector(A, u, v)
    homogenea = verificar_homogeneidad_matriz_vector(A, escalar, u)

    lineas = ["=" * 58, "T ES LINEAL: PROPIEDADES DE SUMA Y MULTIPLICACIÓN",
              "=" * 58, "",
              "u = " + formato_vector(u) + "     v = " + formato_vector(v)
              + "     c = " + formato(escalar), "",
              "1) ADITIVIDAD:  T(u + v) = T(u) + T(v)", ""]
    lineas.append("   u + v = " + formato_vector(suma["u_mas_v"]))
    lineas.extend("   " + linea
                  for linea in _cuentas_producto(A, suma["u_mas_v"], "A(u+v)"))
    lineas.append("   T(u + v) = " + formato_vector(suma["izquierda"]))
    lineas.append("   T(u) = " + formato_vector(suma["Au"])
                  + "     T(v) = " + formato_vector(suma["Av"]))
    lineas.append("   T(u) + T(v) = " + formato_vector(suma["derecha"]))
    lineas.append("   " + ("✓ Se cumple la aditividad." if suma["se_cumple"]
                           else "✗ No se cumple la aditividad."))
    lineas += ["", "2) HOMOGENEIDAD:  T(c·u) = c·T(u)", ""]
    lineas.append("   c·u = " + formato_vector(homogenea["cu"]))
    lineas.extend("   " + linea
                  for linea in _cuentas_producto(A, homogenea["cu"], "A(cu)"))
    lineas.append("   T(c·u) = " + formato_vector(homogenea["izquierda"]))
    lineas.append("   T(u) = " + formato_vector(homogenea["Au"])
                  + "     c·T(u) = " + formato_vector(homogenea["derecha"]))
    lineas.append("   " + ("✓ Se cumple la homogeneidad."
                           if homogenea["se_cumple"]
                           else "✗ No se cumple la homogeneidad."))
    se_cumple = suma["se_cumple"] and homogenea["se_cumple"]
    lineas.append("")
    if se_cumple:
        lineas.append("Se cumplen las dos propiedades: T(x) = A·x ES una "
                      "transformación lineal.")
    else:
        lineas.append("¡Atención! Alguna propiedad falló; revisá los datos.")
    return lineas, se_cumple


def pasos_pertenencia_imagen(A, b):
    """Desarrolla si b está en la imagen de T resolviendo A·x = b."""
    esta, solucion, resultado = pertenece_a_la_imagen(A, b)
    lineas = ["=" * 58, "¿b PERTENECE A LA IMAGEN DE T?", "=" * 58, "",
              "b está en la Imagen(T) si existe x con A·x = b, es decir si",
              "b es combinación lineal de las columnas de A.", "",
              "b = " + formato_vector(b), ""]
    lineas.extend(resultado["pasos"])
    lineas.append("")
    lineas.append("Clasificación del sistema [A | b]: "
                  + resultado["clasificacion"])
    if esta:
        if solucion is not None:
            lineas.append("Un vector x que lo logra: " + formato_vector(solucion))
        lineas.append("Sí: b pertenece a la Imagen de T.")
    else:
        lineas.append("No: el sistema es inconsistente, así que b NO "
                      "pertenece a la Imagen de T.")
    return lineas, esta


# =====================================================================
# BLOQUE 3: INTERFAZ GRÁFICA DEL MÓDULO (Tkinter)
# =====================================================================

class EspaciosApp:
    """Pantalla del módulo de transformaciones lineales y subespacios."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver

        self.var_filas = tk.StringVar(value="3")
        self.var_columnas = tk.StringVar(value="3")
        self.var_escalar = tk.StringVar(value="2")
        self.celdas_A = {}
        self.celdas_u = {}
        self.celdas_v = {}
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
        self.mostrando_nucleo = False
        self.mostrando_teorema = False

        self._construir_ui()
        self._construir_grids()

    # ---------- armado de la pantalla ----------
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
                 text="Módulo 6: Transformaciones Lineales y Subespacios",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).grid(row=1, column=0, columnspan=2, sticky="w",
                        padx=34, pady=(5, 4))
        tk.Label(self.marco_principal,
                 text="Para T(x) = A·x: núcleo, imagen, rango, nulidad, "
                      "teorema de la dimensión y las propiedades de linealidad.",
                 font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE
                 ).grid(row=2, column=0, columnspan=2, sticky="w",
                        padx=34, pady=(0, 12))

        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    def _construir_panel_izquierdo(self):
        """Columna de entrada: matriz A, vectores u y v, escalar c y vector b."""
        panel = tk.Frame(self.marco_principal, bg=FONDO)
        panel.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))

        lienzo = tk.Canvas(panel, bg=FONDO, highlightthickness=0)
        barra = ttk.Scrollbar(panel, orient="vertical", command=lienzo.yview)
        lienzo.configure(yscrollcommand=barra.set)
        interior = tk.Frame(lienzo, bg=FONDO)
        ventana = lienzo.create_window((0, 0), window=interior, anchor="nw")
        lienzo.bind("<Configure>",
                    lambda e: lienzo.itemconfig(ventana, width=e.width))
        interior.bind("<Configure>",
                      lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        self._activar_rueda(lienzo)
        lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.frame_izq = interior
        self._llenar_tarjeta_A(interior)
        self._llenar_tarjeta_vectores(interior)

        tk.Button(interior, text="Analizar núcleo, imagen, rango y nulidad",
                  font=self.fuente_boton, bg=ACENTO, fg=FONDO, relief="flat",
                  cursor="hand2", padx=12, pady=10, activebackground=ACENTO_HOVER,
                  activeforeground=FONDO, command=self._al_analizar
                  ).pack(fill="x", pady=(4, 6))
        self._boton_secundario(interior, "Verificar que T es lineal",
                               self._al_verificar_linealidad)
        self._boton_secundario(interior, "¿b pertenece a la imagen de T?",
                               self._al_verificar_imagen)

    def _construir_panel_derecho(self):
        """Columna de resultados, con sus botones de comprobación."""
        panel = tk.Frame(self.marco_principal, bg=FONDO)
        panel.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))
        tarjeta = self._crear_tarjeta(panel)
        tarjeta.pack(fill="both", expand=True)

        cab = tk.Frame(tarjeta, bg=TARJETA)
        cab.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cab, text="Resultado", font=self.fuente_encab,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        self.marco_botones_resultado = tk.Frame(cab, bg=TARJETA)
        self.marco_botones_resultado.pack(side="right")
        self.boton_procedimiento = self._boton_resultado(
            "Ver procedimiento", self._alternar_procedimiento)
        self.boton_nucleo = self._boton_resultado(
            "Ver A·v = 0", self._alternar_nucleo)
        self.boton_teorema = self._boton_resultado(
            "Ver teorema", self._alternar_teorema)

        self.lienzo_resultado = tk.Canvas(tarjeta, bg=TARJETA,
                                          highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(tarjeta, orient="vertical",
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
        self.barra_resultado.pack(side="right", fill="y", padx=(0, 6),
                                  pady=(0, 12))
        self._mostrar_bienvenida()

    # ---------- piezas visuales reutilizables ----------
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

    def _boton_secundario(self, padre, texto, accion):
        tk.Button(padre, text=texto, font=self.fuente_body, bg=BOTON_SEC,
                  fg=TEXTO, relief="flat", cursor="hand2", padx=10, pady=8,
                  activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO,
                  command=accion).pack(fill="x", pady=(0, 6))

    def _activar_rueda(self, lienzo):
        """Permite desplazar un panel con la rueda del ratón."""
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

    def _sub_tarjeta(self, padre, titulo, color):
        sub = tk.Frame(padre, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(6, 4), anchor="n")
        tk.Label(sub, text=titulo, font=self.fuente_encab, bg=TARJETA,
                 fg=color, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        return sub

    def _banner(self, padre, texto, color):
        marco = tk.Frame(padre, bg=color, padx=14, pady=10)
        marco.pack(fill="x", pady=(0, 6))
        self._texto_ajustable(
            tk.Label(marco, text=texto, font=self.fuente_big, bg=color,
                     fg=FONDO, justify="left", anchor="w")).pack(fill="x")

    def _bloque_matriz(self, padre, etiqueta, M, nota=""):
        tk.Label(padre, text=etiqueta, font=self.fuente_sub, bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x", pady=(4, 0))
        if nota:
            self._texto_ajustable(
                tk.Label(padre, text=nota, font=self.fuente_body, bg=TARJETA,
                         fg=TEXTO_SUAVE, anchor="w",
                         justify="left")).pack(fill="x")
        self._texto_ajustable(
            tk.Label(padre, text="\n".join(formato_matriz(M)),
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w")).pack(fill="x", pady=(2, 6))

    def _bloque_texto(self, padre, texto, color=TEXTO):
        self._texto_ajustable(
            tk.Label(padre, text=texto, font=self.fuente_body, bg=TARJETA,
                     fg=color, justify="left", anchor="w")).pack(fill="x",
                                                                 pady=2)

    def _bloque_base(self, padre, etiqueta, base, nombre, vacio):
        """Muestra una base como lista de vectores, o un aviso si está vacía."""
        tk.Label(padre, text=etiqueta, font=self.fuente_sub, bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x", pady=(4, 0))
        if not base:
            self._bloque_texto(padre, vacio, TEXTO_SUAVE)
            return
        lineas = [con_subindice(nombre + str(i + 1)) + " = " + formato_vector(v)
                  for i, v in enumerate(base)]
        self._texto_ajustable(
            tk.Label(padre, text="\n".join(lineas), font=self.fuente_mono,
                     bg=TARJETA, fg=TEXTO, justify="left",
                     anchor="w")).pack(fill="x", pady=(2, 6))

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

    # ---------- tarjetas de entrada ----------
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
        tk.Label(cont, text="Matriz A de la transformación T(x) = A·x",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))
        tk.Label(cont, text="Filas (m)", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_filas,
                   font=self.fuente_body, width=4, justify="center",
                   bg="#FFFFFF", fg=TEXTO, relief="solid", bd=1,
                   highlightthickness=0, command=self._construir_grids
                   ).grid(row=1, column=1, sticky="w", padx=(0, 16))
        tk.Label(cont, text="Columnas (n)", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION,
                   textvariable=self.var_columnas, font=self.fuente_body,
                   width=4, justify="center", bg="#FFFFFF", fg=TEXTO,
                   relief="solid", bd=1, highlightthickness=0,
                   command=self._construir_grids
                   ).grid(row=1, column=3, sticky="w")
        tk.Button(cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO,
                  relief="flat", cursor="hand2", padx=6, pady=2,
                  activebackground=ACENTO_HOVER, activeforeground=FONDO,
                  command=self._construir_grids
                  ).grid(row=1, column=4, sticky="w", padx=(12, 0))

        self.frame_A = tk.Frame(tarjeta, bg=TARJETA)
        self.frame_A.pack(fill="both", expand=True, padx=18, pady=(0, 8))

    def _llenar_tarjeta_vectores(self, padre):
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 10))
        tk.Label(cont, text="Vectores de prueba", font=self.fuente_sub,
                 bg=TARJETA, fg=TEXTO, anchor="w").pack(fill="x")
        tk.Label(cont, text="u y v tienen n componentes (se usan para la "
                            "linealidad). b tiene m componentes (se usa para "
                            "la imagen).",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 justify="left", wraplength=360, anchor="w").pack(fill="x",
                                                                  pady=(0, 6))
        tk.Label(cont, text="u =", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x")
        self.frame_u = tk.Frame(cont, bg=TARJETA)
        self.frame_u.pack(anchor="w", pady=(0, 6))
        tk.Label(cont, text="v =", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x")
        self.frame_v = tk.Frame(cont, bg=TARJETA)
        self.frame_v.pack(anchor="w", pady=(0, 6))

        fila_c = tk.Frame(cont, bg=TARJETA)
        fila_c.pack(anchor="w", pady=(0, 6))
        tk.Label(fila_c, text="escalar c =", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO).pack(side="left", padx=(0, 6))
        tk.Entry(fila_c, textvariable=self.var_escalar, font=self.fuente_mono,
                 width=8, justify="center", relief="solid", bd=1,
                 bg=CELDA_FONDO, fg=TEXTO, insertbackground=TEXTO,
                 selectbackground=CELDA_FOCO,
                 selectforeground=TEXTO).pack(side="left")

        tk.Label(cont, text="b =", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO, anchor="w").pack(fill="x")
        self.frame_b = tk.Frame(cont, bg=TARJETA)
        self.frame_b.pack(anchor="w")

    def _celda(self, padre, variable, columna, fila=0, ancho=6):
        return tk.Entry(padre, textvariable=variable, font=self.fuente_mono,
                        width=ancho, justify="center", relief="solid", bd=1,
                        bg=CELDA_FONDO, fg=TEXTO, insertbackground=TEXTO,
                        selectbackground=CELDA_FOCO, selectforeground=TEXTO
                        ).grid(row=fila, column=columna, padx=3, pady=2)

    def _construir_grids(self):
        """Dibuja las casillas de A, u, v y b según las dimensiones elegidas."""
        previos_A = {clave: var.get() for clave, var in self.celdas_A.items()}
        previos = {"u": {i: v.get() for i, v in self.celdas_u.items()},
                   "v": {i: v.get() for i, v in self.celdas_v.items()},
                   "b": {i: v.get() for i, v in self.celdas_b.items()}}

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
                self._celda(self.frame_A, var, j, fila=i + 1)

        for nombre, marco, celdas, cantidad in (
                ("u", self.frame_u, self.celdas_u, n),
                ("v", self.frame_v, self.celdas_v, n),
                ("b", self.frame_b, self.celdas_b, m)):
            for hijo in marco.winfo_children():
                hijo.destroy()
            celdas.clear()
            for i in range(cantidad):
                var = tk.StringVar(value=previos[nombre].get(i, ""))
                celdas[i] = var
                self._celda(marco, var, i, ancho=6)

    # ---------- lectura de datos ----------
    def _leer_A(self):
        m = self._leer_dimension(self.var_filas, 3)
        n = self._leer_dimension(self.var_columnas, 3)
        A = []
        for i in range(m):
            fila = []
            for j in range(n):
                try:
                    fila.append(a_numero(self.celdas_A[(i, j)].get()))
                except ValueError:
                    raise ValueError("Revisá la matriz A, fila " + str(i + 1)
                                     + ", columna " + str(j + 1) + ".")
            A.append(fila)
        return A

    def _leer_vector(self, celdas, nombre):
        vector = []
        for i in range(len(celdas)):
            try:
                vector.append(a_numero(celdas[i].get()))
            except ValueError:
                raise ValueError("Revisá el vector " + nombre + ", componente "
                                 + str(i + 1) + ".")
        return vector

    # ---------- acciones de los botones ----------
    def _al_analizar(self):
        try:
            self._construir_grids()
            datos = analizar_transformacion(self._leer_A())
            self._mostrar_analisis(datos)
        except ValueError as error:
            self._mostrar_error(str(error))

    def _al_verificar_linealidad(self):
        try:
            self._construir_grids()
            A = self._leer_A()
            u = self._leer_vector(self.celdas_u, "u")
            v = self._leer_vector(self.celdas_v, "v")
            escalar = a_numero(self.var_escalar.get())
            lineas, se_cumple = pasos_linealidad(A, u, v, escalar)
            self._mostrar_comprobacion(
                "T ES UNA TRANSFORMACIÓN LINEAL",
                "T(u+v) = T(u)+T(v)  y  T(c·u) = c·T(u)", lineas, se_cumple)
        except ValueError as error:
            self._mostrar_error(str(error))

    def _al_verificar_imagen(self):
        try:
            self._construir_grids()
            A = self._leer_A()
            b = self._leer_vector(self.celdas_b, "b")
            lineas, esta = pasos_pertenencia_imagen(A, b)
            self._mostrar_comprobacion(
                "PERTENENCIA A LA IMAGEN",
                "b " + ("SÍ" if esta else "NO") + " pertenece a Imagen(T)",
                lineas, esta)
        except ValueError as error:
            self._mostrar_error(str(error))

    # ---------- dibujo de los resultados ----------
    def _limpiar_resultado(self):
        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = []

    def _mostrar_bienvenida(self):
        self._limpiar_resultado()
        aviso = tk.Label(
            self.frame_resultado,
            text="Ingresá la matriz A y presioná «Analizar núcleo, imagen, "
                 "rango y nulidad» para ver aquí el núcleo, la imagen, el "
                 "rango, la nulidad y el teorema de la dimensión.",
            font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
            justify="left", anchor="nw")
        aviso.pack(fill="both", expand=True, padx=18, pady=16)
        self._texto_ajustable(aviso)
        self._finalizar_render()

    def _mostrar_analisis(self, datos):
        """Fija el análisis como respuesta principal y prepara las secciones."""
        self.ultimo_calculo = datos
        self.mostrando_pasos = False
        self.mostrando_nucleo = False
        self.mostrando_teorema = False
        self._acomodar_botones()

        self._limpiar_resultado()
        self.frame_base = tk.Frame(self.frame_resultado, bg=TARJETA)
        self.frame_base.pack(fill="x")
        self.frame_secciones = tk.Frame(self.frame_resultado, bg=TARJETA)
        self.frame_secciones.pack(fill="x")
        self._dibujar_base()
        self._dibujar_secciones()
        self._finalizar_render()

    def _dibujar_base(self):
        """Respuesta principal: rango, nulidad, bases y clasificación de T."""
        datos = self.ultimo_calculo
        n, m = datos["n"], datos["m"]

        sub = self._sub_tarjeta(self.frame_base, "RESULTADO", ACENTO)
        self._banner(sub, "RANGO = " + str(datos["rango"])
                     + "     NULIDAD = " + str(datos["nulidad"]), ACENTO)
        self._bloque_texto(sub, "T va de R" + str(n) + " a R" + str(m)
                           + "   (A es " + str(m) + "×" + str(n) + ")")
        self._bloque_matriz(sub, "Forma escalonada reducida de A:",
                            datos["reducida"],
                            "Columnas pivote: "
                            + (", ".join(str(c) for c in datos["columnas_pivote"])
                               or "ninguna")
                            + ".  Variables libres: "
                            + (", ".join(nombre_variable(c)
                                         for c in datos["columnas_libres"])
                               or "ninguna") + ".")

        sub = self._sub_tarjeta(self.frame_base, "NÚCLEO DE T  (A·x = 0)",
                                ACENTO)
        self._bloque_texto(sub, "nulidad(A) = dim Núcleo = n − rango = "
                           + str(n) + " − " + str(datos["rango"]) + " = "
                           + str(datos["nulidad"]))
        self._bloque_base(sub, "Base del núcleo:", datos["base_nucleo"], "v",
                          "El núcleo es {0}: solo el vector cero. No hay "
                          "variables libres, así que T es uno a uno.")

        sub = self._sub_tarjeta(self.frame_base, "IMAGEN DE T", ACENTO)
        self._bloque_texto(sub, "dim Imagen = rango(A) = "
                           + str(datos["rango"]))
        self._bloque_base(sub, "Base de la imagen (columnas pivote de A):",
                          datos["base_imagen"], "w",
                          "La imagen es {0}: A es la matriz cero.")

        sub = self._sub_tarjeta(self.frame_base, "CLASIFICACIÓN DE T", EXITO)
        self._bloque_texto(
            sub, ("T es UNO A UNO (inyectiva): el núcleo solo tiene el cero."
                  if datos["uno_a_uno"] else
                  "T NO es uno a uno: hay " + str(datos["nulidad"])
                  + " variable(s) libre(s), así que A·x = 0 tiene "
                  "soluciones distintas de cero."),
            EXITO if datos["uno_a_uno"] else ADVERTENCIA)
        self._bloque_texto(
            sub, ("T es SOBRE R" + str(m) + " (sobreyectiva): rango = "
                  + str(m) + " = número de filas."
                  if datos["sobre"] else
                  "T NO es sobre R" + str(m) + ": el rango es "
                  + str(datos["rango"]) + " y hacen falta " + str(m) + "."),
            EXITO if datos["sobre"] else ADVERTENCIA)

    def _dibujar_secciones(self):
        """Dibuja debajo de la respuesta solo las comprobaciones abiertas."""
        if self.ultimo_calculo is None:
            return
        for hijo in self.frame_secciones.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = [etiqueta
                                     for etiqueta in self.etiquetas_ajustables
                                     if etiqueta.winfo_exists()]
        datos = self.ultimo_calculo
        if self.mostrando_nucleo:
            lineas, se_cumple = pasos_comprobar_nucleo(datos["A"],
                                                       datos["base_nucleo"])
            sub = self._sub_tarjeta(self.frame_secciones,
                                    "COMPROBACIÓN A · v = 0",
                                    EXITO if se_cumple else ERROR)
            self._recuadro_cuentas(sub, "Cuentas con la regla fila-vector:",
                                   lineas)
        if self.mostrando_teorema:
            sub = self._sub_tarjeta(self.frame_secciones,
                                    "TEOREMA DE LA DIMENSIÓN", ACENTO)
            self._recuadro_cuentas(sub, "rango(A) + nulidad(A) = n:",
                                   pasos_teorema_dimension(datos))
        if self.mostrando_pasos:
            sub = self._sub_tarjeta(self.frame_secciones,
                                    "DESARROLLO PASO A PASO", TEXTO_SUAVE)
            self._recuadro_cuentas(sub, "Reducción de [A | 0]:",
                                   datos["pasos"])

    def _mostrar_comprobacion(self, titulo, resumen, lineas, correcto):
        """Pinta en el panel el resultado de una verificación suelta."""
        self.ultimo_calculo = None
        self._acomodar_botones()
        self._limpiar_resultado()
        sub = self._sub_tarjeta(self.frame_resultado, titulo,
                                EXITO if correcto else ADVERTENCIA)
        self._banner(sub, resumen, EXITO if correcto else ADVERTENCIA)
        self._recuadro_cuentas(sub, "Desarrollo completo:", lineas)
        self._finalizar_render()

    def _acomodar_botones(self):
        """Muestra solo los botones que tienen contenido y actualiza rótulos."""
        for boton in (self.boton_procedimiento, self.boton_nucleo,
                      self.boton_teorema):
            boton.pack_forget()
        if self.ultimo_calculo is not None:
            self.boton_procedimiento.pack(side="left", padx=(0, 6))
            self.boton_nucleo.pack(side="left", padx=(0, 6))
            self.boton_teorema.pack(side="left")
        self.boton_procedimiento.configure(
            text="Ocultar procedimiento" if self.mostrando_pasos
            else "Ver procedimiento")
        self.boton_nucleo.configure(
            text="Ocultar A·v = 0" if self.mostrando_nucleo
            else "Ver A·v = 0")
        self.boton_teorema.configure(
            text="Ocultar teorema" if self.mostrando_teorema
            else "Ver teorema")

    def _alternar_procedimiento(self):
        if self.ultimo_calculo is None:
            return
        self.mostrando_pasos = not self.mostrando_pasos
        self._acomodar_botones()
        self._dibujar_secciones()
        self._finalizar_render()

    def _alternar_nucleo(self):
        if self.ultimo_calculo is None:
            return
        self.mostrando_nucleo = not self.mostrando_nucleo
        self._acomodar_botones()
        self._dibujar_secciones()
        self._finalizar_render()

    def _alternar_teorema(self):
        if self.ultimo_calculo is None:
            return
        self.mostrando_teorema = not self.mostrando_teorema
        self._acomodar_botones()
        self._dibujar_secciones()
        self._finalizar_render()

    def _mostrar_error(self, mensaje):
        messagebox.showerror("Operación no válida", mensaje)

    def _ver_teoremas(self):
        mostrar_teoremas(self.raiz, "espacios",
                         "Módulo 6: Transformaciones Lineales y Subespacios")

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


# =====================================================================
# BLOQUE 4: MENÚ DE CONSOLA DEL MÓDULO 6 (MODO CLI)
# =====================================================================

def menu_consola():
    """Menú de texto del Módulo 6: núcleo, imagen, rango y nulidad."""
    while True:
        mostrar_cabecera(LOGO_ESPACIOS)
        print("   0. Ver Teoremas Clave del Módulo")
        print("   1. Núcleo, imagen, rango, nulidad y teorema de la dimensión")
        print("   2. Verificar que T(x) = A·x es lineal")
        print("   3. ¿b pertenece a la imagen de T?")
        print("   9. Volver al menú principal")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("espacios"))
            pausa()
        elif opcion == "1":
            _consola_analizar()
        elif opcion == "2":
            _consola_linealidad()
        elif opcion == "3":
            _consola_imagen()
        else:
            print("   Opción no válida.")
            pausa()


def _pedir_matriz():
    """Pide las dimensiones y la matriz A, y devuelve (A, m, n)."""
    m = leer_entero("   Número de filas de A (m) = ")
    n = leer_entero("   Número de columnas de A (n) = ")
    print()
    return leer_matriz("A", m, n), m, n


def _consola_analizar():
    """Muestra en consola el análisis completo de los subespacios de A."""
    mostrar_cabecera(LOGO_ESPACIOS)
    print("   NÚCLEO, IMAGEN, RANGO Y NULIDAD")
    print()
    try:
        A, _, _ = _pedir_matriz()
        datos = analizar_transformacion(A)
        print()
        mostrar_matriz(datos["reducida"],
                       titulo="   FORMA ESCALONADA REDUCIDA DE A:")
        print()
        print("   rango(A)   = " + str(datos["rango"]))
        print("   nulidad(A) = " + str(datos["nulidad"]))
        print()
        if datos["base_nucleo"]:
            print("   BASE DEL NÚCLEO:")
            for i, v in enumerate(datos["base_nucleo"]):
                print("      " + con_subindice("v" + str(i + 1)) + " = "
                      + formato_vector(v))
        else:
            print("   NÚCLEO = {0} (solo el vector cero): T es uno a uno.")
        print()
        print("   BASE DE LA IMAGEN (columnas pivote de A):")
        for i, w in enumerate(datos["base_imagen"]):
            print("      " + con_subindice("w" + str(i + 1)) + " = "
                  + formato_vector(w))
        print()
        for linea in pasos_teorema_dimension(datos):
            print("   " + linea)
        print()
        for linea in pasos_comprobar_nucleo(A, datos["base_nucleo"])[0]:
            print("   " + linea)
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _consola_linealidad():
    """Pide A, u, v y c y muestra las dos propiedades de linealidad."""
    mostrar_cabecera(LOGO_ESPACIOS)
    print("   T(u+v) = T(u)+T(v)   y   T(c·u) = c·T(u)")
    print()
    try:
        A, _, n = _pedir_matriz()
        print()
        u = leer_vector("u", n)
        v = leer_vector("v", n)
        escalar = leer_numero("   Escalar c = ")
        print()
        for linea in pasos_linealidad(A, u, v, escalar)[0]:
            print("   " + linea)
    except ValueError as error:
        print("\n   " + str(error))
    pausa()


def _consola_imagen():
    """Pide A y b y dice si b pertenece a la imagen de T."""
    mostrar_cabecera(LOGO_ESPACIOS)
    print("   ¿b PERTENECE A LA IMAGEN DE T?")
    print()
    try:
        A, m, _ = _pedir_matriz()
        print()
        b = leer_vector("b", m)
        print()
        for linea in pasos_pertenencia_imagen(A, b)[0]:
            print("   " + linea)
    except ValueError as error:
        print("\n   " + str(error))
    pausa()
