# -*- coding: utf-8 -*-
"""Módulo 8: método abierto de Newton-Raphson (Programa 9).

Aproxima una raíz de f(x) = 0 a partir de un único valor inicial x0 usando
la fórmula  x(i+1) = x(i) - f(x(i)) / f'(x(i)).  La derivada se obtiene de
forma simbólica con SymPy sobre la expresión ya validada por el parser del
Módulo 6, se controla el error de cada iteración, se verifica que f'(x(i))
no sea cero ni demasiado pequeña y se informa el residuo |f(x_aprox)| al
final, porque cumplir el criterio de error no garantiza haber hallado una
raíz (Sesión 22, diapositiva 11).

Temas de clase: Sesión 22 (métodos abiertos, Newton-Raphson, derivada
numérica y convergencia) y Sesión 18 (error aproximado y criterio de paro).

Elaborado por el Grupo #2: Marian Alejandra Guillén Castillo,
Chelsea Yosmara Quintanilla Blandón, José Cristo Carvallo Herrera y
Gabriela Suyen Espinoza Rodríguez.

Librerías autorizadas por el enunciado: SymPy para la derivada simbólica,
NumPy para evaluar, Pandas para la tabla y Matplotlib para las gráficas.
El método está programado por el equipo: NO se usa scipy.optimize.newton
para producir la solución principal, solo como contraste opcional.
"""

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd
import sympy as sp

import tkinter as tk
from tkinter import messagebox, ttk, font as tkfont

from modulos import (
    ACENTO, BOTON_SEC, FONDO, LETRA_MONO, TARJETA, TEXTO, TEXTO_SUAVE,
    limpiar_pantalla, mostrar_cabecera, pausa, preguntar,
)
from modulos.modulo_metodos_numericos import (
    ErrorFuncion,
    FuncionSegura,
    parsear_funcion,
    preparar_datos_grafica,
    _numero_flotante,
    _SUPERSCRIPTS,
    _X,
)
from teoremas.resumen_teoremas import mostrar_teoremas, texto_teoremas

# Para rotular x0, x1, x2... con el subindice pequeno en la grafica.
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


LOGO_NEWTON = (
    "==================================================\n"
    "       MODULO 8: METODO DE NEWTON-RAPHSON\n"
    "  Metodo abierto: raices, derivada y convergencia\n"
    "=================================================="
)

# Valores por defecto que se muestran al usuario (el enunciado pide que si
# hay predeterminados, se vean claramente en pantalla).
TOLERANCIA_POR_DEFECTO = 1e-4          # epsilon_s de los ejemplos de clase
MAX_ITERACIONES_POR_DEFECTO = 50

# Debajo de este valor se considera que f'(x) es "cero o muy pequeña": no se
# divide, porque el paso se dispararía (ejemplo x^10 - 1 con x0 = 0.5, donde
# f'(0.5) = 0.0195 lanza la iteración hasta 51.65).
DERIVADA_MINIMA = 1e-12

# Si la aproximación se va más allá de esto, la iteración está divergiendo
# (ejemplo arctan(x) con x0 = 2: -3.54, 13.95, -279.3, ...).
LIMITE_DIVERGENCIA = 1e12


# =====================================================================
# BLOQUE 1: DERIVADA SIMBÓLICA
# =====================================================================

def _funcion_desde_expresion(expresion, texto=None):
    """Arma una FuncionSegura a partir de una expresión de SymPy ya validada.

    Se usa para la derivada: no se vuelve a pasar por el parser de texto
    porque f'(x) puede contener formas (como sign(x)) que el parser no
    acepta escritas a mano, aunque sí son el resultado legítimo de derivar.
    """
    try:
        vectorizada = sp.lambdify(_X, expresion, modules="numpy")
    except Exception as error:
        raise ErrorFuncion("No se pudo preparar la derivada: " + str(error)) from error

    def evaluar(valor):
        """Evalúa la expresión en un punto y rechaza resultados no reales."""
        try:
            with np.errstate(all="ignore"):
                resultado = vectorizada(float(valor))
            numero = np.asarray(resultado).reshape(-1)[0]
            if np.iscomplexobj(numero):
                if abs(float(np.imag(numero))) > 1e-12:
                    raise ErrorFuncion("La derivada no es real en ese valor.")
                numero = np.real(numero)
            numero = float(numero)
            if not math.isfinite(numero):
                raise ErrorFuncion("La derivada no está definida en ese valor.")
            return numero
        except ErrorFuncion:
            raise
        except (TypeError, ValueError, ZeroDivisionError, OverflowError) as error:
            raise ErrorFuncion("No se pudo evaluar la derivada: " + str(error)) from error

    def evaluar_vector(valores):
        """Evalúa muchos valores de una vez, para las rectas tangentes."""
        with np.errstate(all="ignore"):
            resultado = np.asarray(vectorizada(valores))
        if resultado.shape == ():
            resultado = np.full(np.asarray(valores).shape, resultado.item())
        return resultado

    return FuncionSegura(texto or sp.sstr(expresion), expresion,
                         evaluar, evaluar_vector)


def derivar(funcion):
    """Devuelve f'(x) como FuncionSegura, derivando con SymPy.

    Recibe la función ya parseada (o el texto). La derivada se calcula de
    forma ANALÍTICA, no numérica: es lo que pide el enunciado y lo que hace
    el profesor en los ejemplos (f(x) = e^(-x) - x  ->  f'(x) = -e^(-x) - 1).
    """
    if not isinstance(funcion, FuncionSegura):
        funcion = parsear_funcion(funcion)
    # Se deja la derivada tal como la entrega sp.diff, sin simplify ni
    # cancel: así sale escrita igual que en la pizarra del profesor
    # (-exp(-x) - 1), mientras que "ordenarla" la vuelve ilegible
    # ((-exp(x) - 1)*exp(-x)) y además simplify es lento en expresiones
    # grandes.
    derivada = sp.diff(funcion.expresion, _X)
    return _funcion_desde_expresion(derivada)


# =====================================================================
# BLOQUE 2: ESTRUCTURAS DE DATOS DE UNA CORRIDA
# =====================================================================

@dataclass
class IteracionNewton:
    """Una fila de la tabla, con las columnas que pide la Sesión 22.

    i | x_i | f(x_i) | f'(x_i) | x_(i+1) | error_absoluto | error_relativo
    El error relativo es None cuando x_(i+1) = 0, porque la fórmula
    dividiría entre cero; en ese caso solo se informa el absoluto.
    """

    i: int
    x_i: float
    f_xi: float
    df_xi: float
    x_siguiente: object
    error_absoluto: object
    error_relativo: object


@dataclass
class ResultadoNewton:
    """Resultado completo de la corrida del método."""

    funcion: FuncionSegura
    derivada: FuncionSegura
    x0: float
    tolerancia: float
    max_iteraciones: int
    criterio: str            # "absoluto" o "relativo"
    raiz: object             # None si el proceso se detuvo sin aproximación
    residuo: object          # |f(x_aprox)|
    iteraciones: list
    estado: str              # convergencia | derivada_nula | max_iteraciones | divergencia
    mensaje: str


# Textos del estado final, para no repetirlos en la ventana y en la consola.
MENSAJES_ESTADO = {
    "convergencia": "Convergencia alcanzada: se cumplió el criterio de parada.",
    "derivada_nula": "Proceso detenido: f'(x) es cero o demasiado cercana a "
                     "cero, no se puede dividir.",
    "max_iteraciones": "Se alcanzó el máximo de iteraciones sin cumplir la "
                       "tolerancia; el método no convergió.",
    "divergencia": "Proceso detenido: las aproximaciones se están alejando "
                   "(divergencia).",
}


# =====================================================================
# BLOQUE 3: EL MÉTODO (algoritmo de la Sesión 22, diapositiva 10)
# =====================================================================

def _errores(x_siguiente, x_i):
    """Calcula el error aproximado absoluto y el relativo porcentual.

    Absoluto:  ea = |x(i+1) - x(i)|
    Relativo:  ea(%) = |(x(i+1) - x(i)) / x(i+1)| * 100, solo si x(i+1) != 0.
    Si x(i+1) = 0 el relativo no existe y se devuelve None en vez de dividir
    entre cero, tal como exige el enunciado.
    """
    absoluto = abs(x_siguiente - x_i)
    if x_siguiente == 0:
        return absoluto, None
    return absoluto, abs((x_siguiente - x_i) / x_siguiente) * 100.0


def _cumple_criterio(absoluto, relativo, tolerancia, criterio):
    """Dice si el error alcanzado ya es menor que la tolerancia pedida."""
    if criterio == "relativo" and relativo is not None:
        return relativo < tolerancia
    # Si se pidió el relativo pero x(i+1) = 0, se cae al absoluto para no
    # quedarse iterando sin criterio.
    return absoluto < tolerancia


def newton_raphson(funcion, x0, tolerancia=TOLERANCIA_POR_DEFECTO,
                   max_iteraciones=MAX_ITERACIONES_POR_DEFECTO,
                   criterio="absoluto", derivada=None):
    """Aproxima una raíz de f(x) = 0 por el método de Newton-Raphson.

    Sigue el algoritmo de la Sesión 22: evalúa f y f', valida que f' no sea
    cero ni muy pequeña, aplica la fórmula, calcula el error, registra la
    fila y se detiene por tolerancia o por máximo de iteraciones. Devuelve
    un ResultadoNewton con todas las filas y el residuo final.
    """
    if not isinstance(funcion, FuncionSegura):
        funcion = parsear_funcion(funcion)
    if derivada is None:
        derivada = derivar(funcion)

    x0 = float(x0)
    tolerancia = float(tolerancia)
    max_iteraciones = int(max_iteraciones)
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")
    if max_iteraciones < 1:
        raise ValueError("El máximo de iteraciones debe ser al menos 1.")
    if criterio not in ("absoluto", "relativo"):
        raise ValueError("El criterio debe ser 'absoluto' o 'relativo'.")

    filas = []
    x_i = x0
    raiz = None
    estado = "max_iteraciones"

    for i in range(1, max_iteraciones + 1):
        f_xi = funcion.evaluar(x_i)
        df_xi = derivada.evaluar(x_i)

        # Paso 2 del algoritmo: antes de dividir se valida la derivada.
        if abs(df_xi) <= DERIVADA_MINIMA:
            filas.append(IteracionNewton(i, x_i, f_xi, df_xi, None, None, None))
            raiz = x_i
            estado = "derivada_nula"
            break

        x_siguiente = x_i - f_xi / df_xi

        # Una tangente casi plana puede lanzar la iteración lejísimos.
        if not math.isfinite(x_siguiente) or abs(x_siguiente) > LIMITE_DIVERGENCIA:
            filas.append(IteracionNewton(i, x_i, f_xi, df_xi, x_siguiente,
                                         None, None))
            raiz = x_siguiente if math.isfinite(x_siguiente) else x_i
            estado = "divergencia"
            break

        absoluto, relativo = _errores(x_siguiente, x_i)
        filas.append(IteracionNewton(i, x_i, f_xi, df_xi, x_siguiente,
                                     absoluto, relativo))
        raiz = x_siguiente

        if _cumple_criterio(absoluto, relativo, tolerancia, criterio):
            estado = "convergencia"
            break

        x_i = x_siguiente

    # Paso 6: se sustituye la aproximación final en la función ORIGINAL.
    # El residuo no es el error de la raíz, pero delata los casos en que el
    # error aproximado se hizo pequeño sin haber llegado a una raíz.
    residuo = None
    if raiz is not None:
        try:
            residuo = abs(funcion.evaluar(raiz))
        except ErrorFuncion:
            residuo = None

    return ResultadoNewton(
        funcion=funcion,
        derivada=derivada,
        x0=x0,
        tolerancia=tolerancia,
        max_iteraciones=max_iteraciones,
        criterio=criterio,
        raiz=raiz,
        residuo=residuo,
        iteraciones=filas,
        estado=estado,
        mensaje=MENSAJES_ESTADO[estado],
    )


# =====================================================================
# BLOQUE 4: TABLA DE ITERACIONES (pandas) Y RESUMEN FINAL
# =====================================================================

# Columnas con los mismos nombres y el mismo orden que la tabla de la
# Sesión 22 (diapositivas 13 y 16), más la columna del error relativo
# porcentual que pide el enunciado de la Tarea 9.
ENCABEZADOS = ["i", "x_i", "f(x_i)", "f'(x_i)", "x_(i+1)", "ea", "ea (%)"]


def _cientifica(valor, cifras=2):
    """Escribe un número chico como 8.32 × 10⁻⁴, igual que en clase.

    Dos decimales en la mantisa es justo el formato que usa el profesor en
    las tablas de la Sesión 22 (8.32 × 10⁻⁴, 1.25 × 10⁻⁷).
    """
    mantisa, exponente = f"{valor:.{cifras}e}".split("e")
    mantisa = mantisa.rstrip("0").rstrip(".")
    return mantisa + " × 10" + str(int(exponente)).translate(_SUPERSCRIPTS)


def _celda(valor, decimales=6, es_error=False):
    """Formatea una celda de la tabla.

    Los valores normales van con decimales fijos (0.566311, como el
    profesor). Los errores muy pequeños pasan a notación científica para
    que no se vean como 0.000001 y se pierda la magnitud real.
    """
    if valor is None:
        return "—"
    if es_error and valor != 0 and abs(valor) < 1e-3:
        return _cientifica(valor)
    return f"{valor:.{decimales}f}"


def tabla_iteraciones(resultado):
    """Devuelve el DataFrame NUMÉRICO con una fila por iteración.

    Se usa para cálculos o para exportar; lo que se muestra en pantalla
    sale de tabla_formateada(), que aplica el formato de clase.
    """
    filas = [{
        "i": it.i,
        "x_i": it.x_i,
        "f(x_i)": it.f_xi,
        "f'(x_i)": it.df_xi,
        "x_(i+1)": it.x_siguiente,
        "ea": it.error_absoluto,
        "ea (%)": it.error_relativo,
    } for it in resultado.iteraciones]
    return pd.DataFrame(filas, columns=ENCABEZADOS)


def tabla_formateada(resultado, decimales=6):
    """DataFrame de texto, ya con el formato que se muestra al usuario."""
    filas = [{
        "i": str(it.i),
        "x_i": _celda(it.x_i, decimales),
        "f(x_i)": _celda(it.f_xi, decimales),
        "f'(x_i)": _celda(it.df_xi, decimales),
        "x_(i+1)": _celda(it.x_siguiente, decimales),
        "ea": _celda(it.error_absoluto, decimales, es_error=True),
        "ea (%)": _celda(it.error_relativo, decimales, es_error=True),
    } for it in resultado.iteraciones]
    return pd.DataFrame(filas, columns=ENCABEZADOS)


def texto_tabla(resultado, decimales=6):
    """La tabla alineada como texto, para la consola y el panel de la ventana."""
    tabla = tabla_formateada(resultado, decimales)
    if tabla.empty:
        return "No se realizó ninguna iteración."
    return tabla.to_string(index=False, justify="center")


def residuo_sospechoso(resultado, limite=1e-6):
    """Avisa si el error se hizo chico pero la función no se acercó a cero.

    Es el caso contra el que protege la diapositiva 11: una convergencia
    lenta u oscilatoria puede dar un ea pequeño mientras la aproximación
    sigue lejos de una raíz. Por eso se informa el residuo |f(x)|.
    """
    return (resultado.estado == "convergencia"
            and resultado.residuo is not None
            and resultado.residuo > limite)


def resumen(resultado, decimales=6):
    """Devuelve la lista de pares (etiqueta, valor) del resumen final.

    Incluye todo lo que pide la sección 4.3 del enunciado: la función y su
    derivada, la aproximación final, el número de iteraciones, el error
    alcanzado, el residuo y el estado del proceso.
    """
    ultima = resultado.iteraciones[-1] if resultado.iteraciones else None
    if resultado.criterio == "relativo":
        criterio = "|ea(%)| < " + f"{resultado.tolerancia:g}" + " %  (error relativo porcentual)"
        error_final = ultima.error_relativo if ultima else None
    else:
        criterio = "|ea| < " + f"{resultado.tolerancia:g}" + "  (error absoluto)"
        error_final = ultima.error_absoluto if ultima else None

    # Se dice "raíz aproximada", nunca "raíz exacta": el enunciado lo pide
    # explícitamente y una aproximación numérica no es un punto exacto.
    datos = [
        ("Función f(x)", resultado.funcion.texto),
        ("Derivada f'(x)", resultado.derivada.texto),
        ("Valor inicial x0", f"{resultado.x0:.{decimales}f}"),
        ("Tolerancia", f"{resultado.tolerancia:g}"),
        ("Criterio de parada", criterio),
        ("Máximo de iteraciones", str(resultado.max_iteraciones)),
        ("Iteraciones realizadas", str(len(resultado.iteraciones))),
        # Solo se llama "raíz aproximada" cuando el método realmente
        # convergió; si se cortó por derivada nula, divergencia o máximo de
        # iteraciones, lo que queda es apenas la última aproximación.
        ("Raíz aproximada" if resultado.estado == "convergencia"
         else "Última aproximación",
         "—" if resultado.raiz is None
         else f"{resultado.raiz:.{decimales + 4}f}"),
        ("Error alcanzado", _celda(error_final, decimales, es_error=True)),
        ("Residuo |f(x_aprox)|", _celda(resultado.residuo, decimales, es_error=True)),
        ("Estado", resultado.mensaje),
    ]
    if residuo_sospechoso(resultado):
        datos.append(("Advertencia",
                      "El error aproximado cumplió la tolerancia, pero el "
                      "residuo no se acercó a cero: la aproximación podría "
                      "no estar sobre una raíz."))
    return datos


def texto_resumen(resultado, decimales=6):
    """El resumen final como texto alineado, para consola e informe."""
    datos = resumen(resultado, decimales)
    ancho = max(len(etiqueta) for etiqueta, _ in datos)
    return "\n".join(etiqueta.ljust(ancho) + " : " + str(valor)
                     for etiqueta, valor in datos)


# =====================================================================
# BLOQUE 5: GRÁFICA DE f(x) CON LAS RECTAS TANGENTES
# =====================================================================

COLOR_FUNCION = "#0077B6"      # la curva f(x)
COLOR_TANGENTE = "#E07A1F"     # las rectas tangentes de cada iteración
COLOR_APROXIMACION = "#023E8A" # los puntos x0, x1, x2, ... sobre el eje
COLOR_RAIZ = "#D62828"         # la aproximación final


def rango_grafica(resultado, margen=0.35, ancho_maximo=50.0):
    """Calcula el intervalo [xmin, xmax] donde conviene dibujar f(x).

    Se toma el recorrido de las aproximaciones y se le agrega un margen.
    Si el método divergió, ese recorrido puede ser enorme (arctan con
    x0 = 2 llega a -279) y la curva quedaría aplastada contra el eje; en
    ese caso se encuadra la zona donde empezó y terminó el método.
    """
    valores = [resultado.x0]
    for iteracion in resultado.iteraciones:
        valores.append(iteracion.x_i)
        valores.append(iteracion.x_siguiente)
    valores = [v for v in valores if v is not None and math.isfinite(v)]
    if not valores:
        return resultado.x0 - 2.0, resultado.x0 + 2.0

    xmin, xmax = min(valores), max(valores)
    if xmax - xmin > ancho_maximo:
        centro = resultado.raiz
        if centro is None or not math.isfinite(centro):
            centro = resultado.x0
        semiancho = max(1.0, abs(centro - resultado.x0) * 1.5)
        xmin, xmax = centro - semiancho, centro + semiancho

    ancho = xmax - xmin
    if ancho <= 0:
        # Todas las aproximaciones cayeron en el mismo punto.
        return xmin - 1.0, xmax + 1.0
    return xmin - margen * ancho, xmax + margen * ancho


def _tangentes_dibujables(resultado, maximo):
    """Elige las iteraciones que se pueden dibujar como recta tangente.

    Se descartan las que no produjeron x(i+1) (derivada nula) y se limita
    la cantidad: con 42 iteraciones el dibujo se vuelve ilegible.
    """
    utiles = [it for it in resultado.iteraciones
              if it.x_siguiente is not None
              and math.isfinite(it.x_siguiente)
              and math.isfinite(it.f_xi)]
    return utiles[:maximo]


def crear_figura_newton(resultado, xmin=None, xmax=None, cantidad=2000,
                        max_tangentes=4):
    """Crea la figura de Matplotlib que pide la sección 4.3 del enunciado.

    Dibuja f(x), el eje horizontal, las aproximaciones obtenidas y las
    rectas tangentes de las primeras iteraciones. Cada tangente va del
    punto de tangencia (x(i), f(x(i))) hasta su corte con el eje x, que
    es justamente x(i+1): así se ve de dónde sale la fórmula.
    """
    import matplotlib.pyplot as plt

    if xmin is None or xmax is None:
        xmin, xmax = rango_grafica(resultado)

    segmentos = preparar_datos_grafica(resultado.funcion, xmin, xmax, cantidad)
    figura, eje = plt.subplots(figsize=(9, 5.5))
    for indice, (xs, ys) in enumerate(segmentos):
        eje.plot(xs, ys, color=COLOR_FUNCION, linewidth=1.8,
                 label="f(x) = " + resultado.funcion.texto if indice == 0 else None)
    eje.axhline(0, color="#555555", linewidth=0.8)

    tangentes = _tangentes_dibujables(resultado, max_tangentes)
    for numero, iteracion in enumerate(tangentes):
        # Recta tangente  y = f(x(i)) + f'(x(i))·(x - x(i)).
        # Dibujada entre el punto de tangencia y su raíz, que es x(i+1).
        eje.plot([iteracion.x_i, iteracion.x_siguiente],
                 [iteracion.f_xi, 0.0],
                 color=COLOR_TANGENTE, linewidth=1.1, linestyle="--",
                 label="Rectas tangentes" if numero == 0 else None)
        # Línea punteada vertical que baja de la curva al eje.
        eje.plot([iteracion.x_i, iteracion.x_i], [0.0, iteracion.f_xi],
                 color=COLOR_TANGENTE, linewidth=0.7, linestyle=":")
        eje.plot([iteracion.x_i], [iteracion.f_xi], marker="o",
                 color=COLOR_TANGENTE, markersize=4)
        eje.annotate("x" + str(numero).translate(_SUBINDICES),
                     (iteracion.x_i, 0.0), textcoords="offset points",
                     xytext=(0, -14), ha="center", fontsize=9,
                     color=COLOR_APROXIMACION)

    # Las aproximaciones sobre el eje horizontal.
    puntos = [it.x_i for it in resultado.iteraciones if math.isfinite(it.x_i)]
    if puntos:
        eje.scatter(puntos, [0.0] * len(puntos), s=22,
                    color=COLOR_APROXIMACION, zorder=4,
                    label="Aproximaciones")

    if resultado.raiz is not None and math.isfinite(resultado.raiz):
        etiqueta = ("Raíz aproximada" if resultado.estado == "convergencia"
                    else "Última aproximación")
        eje.scatter([resultado.raiz], [0.0], s=70, color=COLOR_RAIZ,
                    zorder=5, label=etiqueta)

    eje.set_title("Newton-Raphson sobre f(x) = " + resultado.funcion.texto)
    eje.set_xlabel("x")
    eje.set_ylabel("f(x)")
    eje.grid(True, alpha=0.3)
    eje.legend(loc="best", fontsize=9)
    figura.tight_layout()
    return figura


def guardar_figura(resultado, ruta, **opciones):
    """Guarda la gráfica en un archivo PNG, para las evidencias del informe."""
    import matplotlib
    matplotlib.use("Agg", force=False)
    figura = crear_figura_newton(resultado, **opciones)
    figura.savefig(ruta, dpi=150)
    import matplotlib.pyplot as plt
    plt.close(figura)
    return ruta


# =====================================================================
# BLOQUE 6: INTERFAZ GRÁFICA DEL MÓDULO (Tkinter)
# =====================================================================

class NewtonApp:
    """Pantalla Tkinter del método de Newton-Raphson."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver
        self.ultimo = None            # último ResultadoNewton calculado

        self.fuente_titulo = tkfont.Font(family="Montserrat", size=21, weight="bold")
        self.fuente_body = tkfont.Font(family="Montserrat", size=10)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=10, weight="bold")

        self.marco = tk.Frame(raiz, bg=FONDO)
        self.marco.pack(fill="both", expand=True)
        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        """Estilo propio de la tabla, sin tocar el de los módulos anteriores."""
        estilo = ttk.Style(self.raiz)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Newton.Treeview", background=TARJETA,
                         fieldbackground=TARJETA, foreground=TEXTO,
                         rowheight=27, font=(LETRA_MONO, 9))
        estilo.configure("Newton.Treeview.Heading", background=ACENTO,
                         foreground=FONDO, font=("Montserrat", 9, "bold"),
                         relief="flat")

    # ---------- armado de la pantalla ----------
    def _construir_ui(self):
        cabecera = tk.Frame(self.marco, bg=FONDO)
        cabecera.pack(fill="x", padx=28, pady=(10, 0))
        tk.Button(cabecera, text="← Volver al Menú", font=self.fuente_body,
                  bg=FONDO, fg=ACENTO, bd=0, cursor="hand2",
                  command=self.volver_al_menu).pack(side="left")
        tk.Button(cabecera, text="0. Ver Teoremas Clave", font=self.fuente_body,
                  bg=BOTON_SEC, fg=TEXTO, bd=0, padx=10, pady=5,
                  command=self._ver_teoremas).pack(side="right")

        tk.Label(self.marco, text="Módulo 8: Método de Newton-Raphson",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).pack(anchor="w", padx=28, pady=(4, 0))
        tk.Label(self.marco,
                 text="Método abierto: parte de un solo valor inicial x0 y usa "
                      "la derivada simbólica para acercarse a la raíz.",
                 font=self.fuente_body, bg=FONDO, fg=TEXTO_SUAVE
                 ).pack(anchor="w", padx=28, pady=(0, 8))

        self._construir_entrada()
        self._construir_resumen()
        self._construir_tabla()

    def _entrada(self, padre, texto, fila, columna, valor=""):
        """Etiqueta + casilla de texto, con los colores fijados a mano.

        Los colores se escriben explícitamente porque si no Tkinter los
        hereda del sistema y, con Windows en modo oscuro, la letra sale
        blanca sobre fondo blanco.
        """
        tk.Label(padre, text=texto, bg=TARJETA, fg=TEXTO,
                 font=self.fuente_body).grid(row=fila, column=columna,
                                             sticky="w", padx=8, pady=8)
        casilla = tk.Entry(padre, width=18, font=self.fuente_body,
                           relief="solid", bd=1, highlightthickness=1,
                           highlightcolor="#90E0EF", bg="#FFFFFF", fg=TEXTO,
                           insertbackground=TEXTO, selectbackground="#CAF0F8",
                           selectforeground=TEXTO)
        casilla.insert(0, valor)
        casilla.grid(row=fila, column=columna + 1, sticky="ew", padx=8, pady=8)
        return casilla

    def _construir_entrada(self):
        """Tarjeta con f(x), x0, tolerancia, máximo de iteraciones y criterio."""
        tarjeta = tk.Frame(self.marco, bg=TARJETA,
                           highlightbackground="#C9E3ED", highlightthickness=1)
        tarjeta.pack(fill="x", padx=35, pady=(6, 12))

        self.campo_funcion = self._entrada(tarjeta, "f(x):", 0, 0, "exp(-x) - x")
        self.campo_x0 = self._entrada(tarjeta, "Valor inicial x0:", 1, 0, "0")
        self.campo_tolerancia = self._entrada(
            tarjeta, "Tolerancia:", 1, 2, str(TOLERANCIA_POR_DEFECTO))
        self.campo_maximo = self._entrada(
            tarjeta, "Máximo de iteraciones:", 2, 0,
            str(MAX_ITERACIONES_POR_DEFECTO))

        tk.Label(tarjeta, text="Criterio de parada:", bg=TARJETA, fg=TEXTO,
                 font=self.fuente_body).grid(row=2, column=2, sticky="w",
                                             padx=8, pady=8)
        self.variable_criterio = tk.StringVar(value="absoluto")
        ttk.Combobox(tarjeta, textvariable=self.variable_criterio, width=16,
                     state="readonly", font=self.fuente_body,
                     values=("absoluto", "relativo")
                     ).grid(row=2, column=3, sticky="ew", padx=8, pady=8)

        tarjeta.columnconfigure(1, weight=1)
        tarjeta.columnconfigure(3, weight=1)

        # Los valores predeterminados quedan a la vista, como pide el enunciado.
        tk.Label(tarjeta,
                 text="Predeterminados: tolerancia " + str(TOLERANCIA_POR_DEFECTO)
                      + ", máximo " + str(MAX_ITERACIONES_POR_DEFECTO)
                      + " iteraciones, criterio por error absoluto "
                      "|x(i+1) - x(i)|. Use ** para potencias.",
                 bg=TARJETA, fg=TEXTO_SUAVE, font=self.fuente_body,
                 wraplength=760, justify="left"
                 ).grid(row=3, column=0, columnspan=4, sticky="w", padx=8)

        botones = tk.Frame(tarjeta, bg=TARJETA)
        botones.grid(row=4, column=0, columnspan=4, pady=10)
        tk.Button(botones, text="Ejecutar Newton-Raphson",
                  font=self.fuente_boton, bg=ACENTO, fg=FONDO, relief="flat",
                  padx=12, pady=8, cursor="hand2",
                  command=self._ejecutar).pack(side="left", padx=6)
        tk.Button(botones, text="Ver gráfica", font=self.fuente_boton,
                  bg=BOTON_SEC, fg=TEXTO, relief="flat", padx=12, pady=8,
                  cursor="hand2", command=self._ver_grafica
                  ).pack(side="left", padx=6)

    def _construir_resumen(self):
        """Recuadro de texto con el resumen final del proceso."""
        self.texto_resumen = tk.Text(self.marco, height=9, wrap="word",
                                     font=(LETRA_MONO, 10), bg=TARJETA,
                                     fg=TEXTO, relief="solid", bd=1)
        self.texto_resumen.pack(fill="x", padx=35, pady=(0, 10), ipady=6)
        self.texto_resumen.insert("1.0",
                                  "Ingrese f(x) y el valor inicial x0, y presione "
                                  "«Ejecutar Newton-Raphson».")
        self.texto_resumen.configure(state="disabled")

    def _construir_tabla(self):
        """Tabla de iteraciones con las columnas de la Sesión 22."""
        tk.Label(self.marco,
                 text="Cada fila guarda los valores ANTES de avanzar: por eso "
                      "x(i+1) de una fila es x(i) de la siguiente.",
                 bg=FONDO, fg=TEXTO_SUAVE, font=self.fuente_body
                 ).pack(anchor="w", padx=38)

        marco_tabla = tk.Frame(self.marco, bg=TARJETA,
                               highlightbackground="#C9E3ED",
                               highlightthickness=1)
        marco_tabla.pack(fill="both", expand=True, padx=35, pady=(2, 25))
        cuerpo = tk.Frame(marco_tabla, bg=TARJETA)
        cuerpo.pack(fill="both", expand=True, padx=12, pady=(12, 0))
        cuerpo.rowconfigure(0, weight=1)
        cuerpo.columnconfigure(0, weight=1)

        self.tabla = ttk.Treeview(cuerpo, columns=tuple(ENCABEZADOS),
                                  show="headings", height=10,
                                  style="Newton.Treeview")
        self.tabla.tag_configure("fila_par", background="#F1F8FB")
        self.tabla.tag_configure("fila_impar", background=TARJETA)
        anchos = {"i": 50, "x_i": 140, "f(x_i)": 140, "f'(x_i)": 140,
                  "x_(i+1)": 140, "ea": 130, "ea (%)": 130}
        for columna in ENCABEZADOS:
            self.tabla.heading(columna, text=columna)
            self.tabla.column(columna, width=anchos[columna], minwidth=50,
                              anchor="center", stretch=False)
        barra_v = ttk.Scrollbar(cuerpo, orient="vertical",
                                command=self.tabla.yview)
        barra_h = ttk.Scrollbar(marco_tabla, orient="horizontal",
                                command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_v.set,
                             xscrollcommand=barra_h.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.pack(side="bottom", fill="x", padx=12, pady=(8, 12))

    # ---------- acciones ----------
    def _leer_datos(self):
        """Lee y valida lo que escribió el usuario antes de calcular."""
        funcion = parsear_funcion(self.campo_funcion.get())
        x0 = _numero_flotante(self.campo_x0.get(), "El valor inicial x0")
        tolerancia = _numero_flotante(self.campo_tolerancia.get(),
                                      "La tolerancia")
        try:
            maximo = int(str(self.campo_maximo.get()).strip())
        except ValueError:
            raise ValueError("El máximo de iteraciones debe ser un entero.")
        return funcion, x0, tolerancia, maximo, self.variable_criterio.get()

    def _ejecutar(self):
        """Corre el método y vuelca el resumen y la tabla en pantalla."""
        try:
            funcion, x0, tolerancia, maximo, criterio = self._leer_datos()
            resultado = newton_raphson(funcion, x0, tolerancia, maximo, criterio)
        except (ValueError, ErrorFuncion) as error:
            messagebox.showerror("Datos inválidos", str(error), parent=self.raiz)
            return

        self.ultimo = resultado
        self._mostrar_resumen(resultado)
        self._llenar_tabla(resultado)

    # Un color de fondo por estado, para que se vea de lejos cómo terminó.
    COLORES_ESTADO = {
        "convergencia": "#E8F5E9",
        "derivada_nula": "#FDECEA",
        "divergencia": "#FDECEA",
        "max_iteraciones": "#FFF3E0",
    }

    def _mostrar_resumen(self, resultado):
        self.texto_resumen.configure(state="normal")
        self.texto_resumen.delete("1.0", "end")
        self.texto_resumen.insert("1.0", texto_resumen(resultado))
        self.texto_resumen.configure(
            state="disabled",
            bg=self.COLORES_ESTADO.get(resultado.estado, TARJETA))

    def _llenar_tabla(self, resultado):
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)
        tabla = tabla_formateada(resultado)
        for indice, fila in tabla.iterrows():
            self.tabla.insert("", "end",
                              tags=("fila_par" if indice % 2 == 0
                                    else "fila_impar",),
                              values=tuple(fila[columna]
                                           for columna in ENCABEZADOS))

    def _ver_grafica(self):
        """Abre la gráfica en una ventana aparte, con opción de guardarla."""
        if self.ultimo is None:
            messagebox.showinfo("Sin datos",
                                "Primero ejecute el método para tener qué graficar.",
                                parent=self.raiz)
            return
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            figura = crear_figura_newton(self.ultimo)
        except (ValueError, ErrorFuncion, ImportError) as error:
            messagebox.showerror("No se pudo graficar", str(error),
                                 parent=self.raiz)
            return

        ventana = tk.Toplevel(self.raiz)
        ventana.title("Newton-Raphson: f(x) y rectas tangentes")
        ventana.configure(bg=FONDO)
        ventana.geometry("940x680")
        lienzo = FigureCanvasTkAgg(figura, master=ventana)
        lienzo.draw()
        lienzo.get_tk_widget().pack(fill="both", expand=True)

        def guardar():
            """Guarda la figura como PNG para las evidencias del informe."""
            from tkinter import filedialog
            ruta = filedialog.asksaveasfilename(
                parent=ventana, defaultextension=".png",
                filetypes=[("Imagen PNG", "*.png")],
                initialfile="newton_raphson.png")
            if ruta:
                figura.savefig(ruta, dpi=150)

        tk.Button(ventana, text="Guardar imagen", font=self.fuente_boton,
                  bg=ACENTO, fg=FONDO, relief="flat", padx=12, pady=6,
                  cursor="hand2", command=guardar).pack(pady=8)

    def _ver_teoremas(self):
        mostrar_teoremas(self.raiz, "newton",
                         "Módulo 8: Método de Newton-Raphson")

    def volver_al_menu(self):
        self.marco.destroy()
        self.callback_volver()


# =====================================================================
# BLOQUE 7: MENÚ DE CONSOLA DEL MÓDULO (MODO CLI)
# =====================================================================

def _leer_funcion_consola():
    """Pide f(x) hasta que la expresión sea válida."""
    while True:
        try:
            return parsear_funcion(preguntar("   f(x) = "))
        except ErrorFuncion as error:
            print("   " + str(error))


def _leer_numero_consola(mensaje, por_defecto=None):
    """Pide un número; con ENTER se toma el valor predeterminado."""
    while True:
        crudo = preguntar(mensaje).strip()
        if not crudo and por_defecto is not None:
            return por_defecto
        try:
            return _numero_flotante(crudo, "El valor")
        except ValueError as error:
            print("   " + str(error))


def _consola_newton():
    """Corre el método desde la consola y muestra tabla y resumen."""
    mostrar_cabecera(LOGO_NEWTON)
    print("   METODO DE NEWTON-RAPHSON")
    print("   Escriba la funcion con ** para potencias: x**3 - 2*x - 5")
    print()
    try:
        funcion = _leer_funcion_consola()
        x0 = _leer_numero_consola("   Valor inicial x0 = ")
        tolerancia = _leer_numero_consola(
            "   Tolerancia [ENTER = " + str(TOLERANCIA_POR_DEFECTO) + "] = ",
            TOLERANCIA_POR_DEFECTO)
        maximo = int(_leer_numero_consola(
            "   Maximo de iteraciones [ENTER = "
            + str(MAX_ITERACIONES_POR_DEFECTO) + "] = ",
            MAX_ITERACIONES_POR_DEFECTO))
        criterio = preguntar("   Criterio (absoluto/relativo) [ENTER = absoluto] = ").strip()
        criterio = criterio if criterio in ("absoluto", "relativo") else "absoluto"

        resultado = newton_raphson(funcion, x0, tolerancia, maximo, criterio)
        print()
        print("   f'(x) = " + resultado.derivada.texto)
        print()
        for linea in texto_tabla(resultado).split("\n"):
            print("   " + linea)
        print()
        for linea in texto_resumen(resultado).split("\n"):
            print("   " + linea)
    except (ValueError, ErrorFuncion) as error:
        print("\n   " + str(error))
    pausa()


def menu_consola():
    """Menú de texto del módulo de Newton-Raphson."""
    while True:
        mostrar_cabecera(LOGO_NEWTON)
        print("   0. Ver Teoremas Clave del Modulo")
        print("   1. Aproximar una raiz por Newton-Raphson")
        print("   9. Volver al menu principal")
        print()
        opcion = preguntar("   Elegi una opcion: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("newton"))
            pausa()
        elif opcion == "1":
            _consola_newton()
        else:
            print("   Opcion no valida.")
            pausa()
