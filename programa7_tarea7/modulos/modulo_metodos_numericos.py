# -*- coding: utf-8 -*-
"""Módulo 6: métodos numéricos del Programa 7.

Incluye bisección implementada desde cero, graficación segura de funciones,
notación posicional y análisis de errores numéricos. SymPy se usa únicamente
para analizar expresiones con una lista blanca; SciPy solo contrasta la raíz.
"""

from dataclasses import dataclass
import math
import warnings

import numpy as np
import sympy as sp
from sympy.calculus.util import continuous_domain
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

import tkinter as tk
from tkinter import messagebox, ttk, font as tkfont

from modulos import (
    ACENTO, ACENTO_HOVER, BOTON_SEC, BOTON_SEC_HOVER, FONDO, LETRA_MONO,
    TARJETA, TEXTO, TEXTO_SUAVE, mostrar_cabecera, limpiar_pantalla,
    pausa, preguntar, SalirDeLaConsola,
)
from teoremas.resumen_teoremas import mostrar_teoremas


LOGO_NUMERICOS = (
    "==================================================\n"
    "       MÓDULO 6: MÉTODOS NUMÉRICOS\n"
    "  Bisección, gráficas, notación posicional y errores\n"
    "=================================================="
)

_X = sp.Symbol("x", real=True)
_FUNCIONES_PERMITIDAS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
}
_NOMBRES_PERMITIDOS = {"x", "pi", "e"} | set(_FUNCIONES_PERMITIDAS)
_TRANSFORMACIONES = standard_transformations + (implicit_multiplication_application,)
_LOCAL_DICT = {
    "x": _X,
    "pi": sp.pi,
    "e": sp.E,
    **_FUNCIONES_PERMITIDAS,
}
_SUPERSCRIPTS = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


class ErrorFuncion(ValueError):
    """Error descriptivo producido al leer o evaluar una función."""


@dataclass
class FuncionSegura:
    """Expresión validada y sus evaluadores escalar y vectorial."""

    texto: str
    expresion: sp.Expr
    evaluar: object
    evaluar_vector: object


@dataclass
class IteracionBiseccion:
    """Datos de una iteración, guardados antes de actualizar el intervalo."""

    k: int
    a: float
    b: float
    xr: float
    fa: float
    fb: float
    fr: float
    eb: float
    ea: object
    er: object


@dataclass
class ResultadoBiseccion:
    """Resultado completo del algoritmo de bisección."""

    funcion: FuncionSegura
    a_inicial: float
    b_inicial: float
    tolerancia: float
    max_iteraciones: int
    raiz: float
    fr: float
    eb: float
    estado: str
    mensaje: str
    iteraciones: list
    teoricas: int
    a_final: float
    b_final: float
    raiz_scipy: object = None
    diferencia_scipy: object = None


def _nombres_en_texto(texto):
    """Devuelve identificadores para impedir nombres no autorizados."""
    nombres = []
    actual = ""
    for caracter in texto:
        if caracter.isalpha() or caracter == "_":
            actual += caracter
        elif actual:
            nombres.append(actual)
            actual = ""
    if actual:
        nombres.append(actual)
    return nombres


def parsear_funcion(texto):
    """Convierte texto en una función segura de una sola variable real.

    No se ejecuta texto del usuario con ``eval``. Solo se aceptan los nombres
    y operaciones definidos en la lista blanca del módulo.
    """
    texto = str(texto).strip().replace("−", "-").replace("×", "*")
    if not texto:
        raise ErrorFuncion("La función no puede estar vacía.")
    if "^" in texto:
        raise ErrorFuncion("Use ** para potencias; el símbolo ^ no representa potencia en Python.")
    if any(caracter in texto for caracter in (";", "[", "]", "{", "}", "'", '"', "\\")):
        raise ErrorFuncion("La expresión contiene caracteres no permitidos.")

    desconocidos = sorted({nombre for nombre in _nombres_en_texto(texto)
                           if nombre not in _NOMBRES_PERMITIDOS})
    if desconocidos:
        raise ErrorFuncion(
            "Nombre(s) no autorizado(s): " + ", ".join(desconocidos) + ". "
            "Use x, pi, e, sin, cos, tan, exp, log, sqrt o abs."
        )
    try:
        expresion = parse_expr(
            texto,
            local_dict=_LOCAL_DICT,
            transformations=_TRANSFORMACIONES,
            evaluate=True,
        )
    except (SyntaxError, TypeError, ValueError, sp.SympifyError) as error:
        raise ErrorFuncion("No se pudo interpretar la función: " + str(error)) from error

    simbolos = expresion.free_symbols
    if simbolos - {_X}:
        raise ErrorFuncion("La función solo puede utilizar la variable x.")
    if expresion.has(sp.I, sp.zoo, sp.oo, -sp.oo, sp.nan):
        raise ErrorFuncion("La función contiene un valor no real o no finito.")
    funciones = {n.func for n in expresion.atoms(sp.Function)}
    permitidas = set(_FUNCIONES_PERMITIDAS.values())
    if not funciones <= permitidas:
        raise ErrorFuncion("La función contiene una operación no autorizada.")

    try:
        vectorizada = sp.lambdify(_X, expresion, modules="numpy")
    except Exception as error:
        raise ErrorFuncion("No se pudo preparar la evaluación segura: " + str(error)) from error

    def evaluar(valor):
        """Evalúa un valor real y rechaza resultados no definidos."""
        try:
            with np.errstate(all="ignore"):
                resultado = vectorizada(float(valor))
            arreglo = np.asarray(resultado)
            if arreglo.size != 1:
                raise ErrorFuncion("La función no produjo un único valor real.")
            numero = arreglo.reshape(-1)[0]
            if np.iscomplexobj(numero):
                if abs(float(np.imag(numero))) > 1e-12:
                    raise ErrorFuncion("La función no está definida en los reales para ese valor.")
                numero = np.real(numero)
            numero = float(numero)
            if not math.isfinite(numero):
                raise ErrorFuncion("La función no está definida o no es finita en ese valor.")
            return numero
        except ErrorFuncion:
            raise
        except (TypeError, ValueError, ZeroDivisionError, OverflowError) as error:
            raise ErrorFuncion("No se pudo evaluar la función: " + str(error)) from error

    def evaluar_vector(valores):
        """Evalúa muchos valores para la gráfica, conservando no definidos."""
        with np.errstate(all="ignore"):
            resultado = np.asarray(vectorizada(valores))
        if resultado.shape == ():
            resultado = np.full(np.asarray(valores).shape, resultado.item())
        return resultado

    return FuncionSegura(texto, expresion, evaluar, evaluar_vector)


def _comprobar_intervalo_continuo(funcion, a, b):
    """Comprueba continuidad simbólica en el intervalo cerrado."""
    intervalo = sp.Interval(sp.Float(a), sp.Float(b))
    try:
        dominio = continuous_domain(funcion.expresion, _X, intervalo)
    except Exception as error:
        raise ErrorFuncion(
            "No se pudo comprobar la continuidad del intervalo. "
            "Seleccione un intervalo donde la función esté definida."
        ) from error
    if dominio != intervalo:
        raise ErrorFuncion(
            "La función no es continua o no está definida en todo el intervalo. "
            "El cambio de signo por sí solo no garantiza una raíz."
        )
    # La comprobación numérica complementa el dominio simbólico en casos con
    # condiciones difíciles de simplificar.
    for punto in (a, b, (a + b) / 2):
        funcion.evaluar(punto)
    return True


def _teoricas_biseccion(ancho, tolerancia):
    """Calcula la cota teórica solicitada en la asignación."""
    razon = ancho / tolerancia
    if razon <= 1:
        return 0
    return max(0, math.ceil(math.log2(razon)))


def biseccion(funcion, a, b, tolerancia, max_iteraciones, contrastar=True):
    """Ejecuta bisección desde cero y devuelve toda la tabla de iteraciones."""
    if not isinstance(funcion, FuncionSegura):
        funcion = parsear_funcion(funcion)
    try:
        a = float(a)
        b = float(b)
        tolerancia = float(tolerancia)
        max_iteraciones = int(max_iteraciones)
    except (TypeError, ValueError) as error:
        raise ValueError("a, b, tolerancia y máximo deben ser numéricos.") from error
    if not all(math.isfinite(valor) for valor in (a, b, tolerancia)):
        raise ValueError("Los límites y la tolerancia deben ser finitos.")
    if a >= b:
        raise ValueError("El extremo inferior debe ser menor que el extremo superior.")
    if tolerancia <= 0:
        raise ValueError("La tolerancia absoluta debe ser positiva.")
    if max_iteraciones < 1:
        raise ValueError("El máximo de iteraciones debe ser al menos 1.")

    _comprobar_intervalo_continuo(funcion, a, b)
    fa = funcion.evaluar(a)
    fb = funcion.evaluar(b)
    if fa == 0:
        resultado = ResultadoBiseccion(
            funcion, a, b, tolerancia, max_iteraciones, a, fa, 0.0,
            "raiz_extremo", "Se encontró una raíz exacta en el extremo a.",
            [], _teoricas_biseccion(b - a, tolerancia), a, b,
        )
        return _contraste_scipy(resultado) if contrastar else resultado
    if fb == 0:
        resultado = ResultadoBiseccion(
            funcion, a, b, tolerancia, max_iteraciones, b, fb, 0.0,
            "raiz_extremo", "Se encontró una raíz exacta en el extremo b.",
            [], _teoricas_biseccion(b - a, tolerancia), a, b,
        )
        return _contraste_scipy(resultado) if contrastar else resultado
    if fa * fb >= 0:
        raise ValueError(
            "El intervalo no cumple la condición de cambio de signo. "
            "Esto no descarta raíces en otros intervalos."
        )

    teoricas = _teoricas_biseccion(b - a, tolerancia)
    filas = []
    anterior = None
    raiz = None
    fr = None
    eb = None
    estado = "maximo_iteraciones"
    mensaje = "Se alcanzó el máximo sin garantizar la tolerancia solicitada."

    for k in range(1, max_iteraciones + 1):
        # Se guardan a, b, fa y fb antes de cambiar el intervalo.
        xr = (a + b) / 2.0
        eb = (b - a) / 2.0
        fr = funcion.evaluar(xr)
        if anterior is None:
            ea, er = "—", "—"
        else:
            ea = abs(xr - anterior)
            er = "No definido" if xr == 0 else abs((xr - anterior) / xr)
        filas.append(IteracionBiseccion(k, a, b, xr, fa, fb, fr, eb, ea, er))
        raiz = xr

        if fr == 0:
            estado = "raiz_exacta"
            mensaje = "Se encontró una raíz exacta en aritmética de máquina."
            break
        if eb <= tolerancia:
            estado = "tolerancia"
            mensaje = "Se alcanzó la tolerancia absoluta solicitada."
            break
        if fa * fr < 0:
            b, fb = xr, fr
        else:
            a, fa = xr, fr
        anterior = xr

    resultado = ResultadoBiseccion(
        funcion, filas[0].a, filas[0].b, tolerancia, max_iteraciones,
        raiz, fr, eb, estado, mensaje, filas, teoricas, a, b,
    )
    return _contraste_scipy(resultado) if contrastar else resultado


def _contraste_scipy(resultado):
    """Contrasta una bisección válida con SciPy, nunca la reemplaza."""
    try:
        from scipy.optimize import bisect as scipy_bisect
        raiz = scipy_bisect(
            resultado.funcion.evaluar,
            resultado.a_inicial,
            resultado.b_inicial,
            xtol=resultado.tolerancia,
            maxiter=resultado.max_iteraciones,
        )
        resultado.raiz_scipy = float(raiz)
        resultado.diferencia_scipy = abs(resultado.raiz - resultado.raiz_scipy)
    except Exception:
        # La solución propia permanece disponible aun si SciPy no puede
        # contrastar un caso concreto o no está instalado.
        resultado.raiz_scipy = None
        resultado.diferencia_scipy = None
    return resultado


def _puntos_singulares(funcion, xmin, xmax):
    """Obtiene singularidades reales conocidas para cortar la gráfica."""
    puntos = []
    try:
        singulares = sp.singularities(funcion.expresion, _X)
        if singulares is sp.S.Complexes or singulares is sp.S.Reals:
            return puntos
        for valor in singulares:
            if getattr(valor, "is_real", False) is True:
                numero = float(valor)
                if xmin < numero < xmax and math.isfinite(numero):
                    puntos.append(numero)
    except Exception:
        pass
    return puntos


def preparar_datos_grafica(funcion, xmin, xmax, cantidad=2000):
    """Genera segmentos válidos sin unir puntos a través de asíntotas."""
    if not isinstance(funcion, FuncionSegura):
        funcion = parsear_funcion(funcion)
    xmin, xmax = float(xmin), float(xmax)
    cantidad = int(cantidad)
    if not math.isfinite(xmin) or not math.isfinite(xmax) or xmin >= xmax:
        raise ValueError("Debe cumplirse xmin < xmax y ambos límites deben ser finitos.")
    if cantidad < 1000:
        cantidad = 1000
    xs = np.linspace(xmin, xmax, cantidad)
    ys = funcion.evaluar_vector(xs)
    if np.iscomplexobj(ys):
        ys = np.where(np.abs(np.imag(ys)) <= 1e-12, np.real(ys), np.nan)
    ys = np.asarray(ys, dtype=float)
    mascara = np.isfinite(ys)
    paso = (xmax - xmin) / max(1, cantidad - 1)
    for singularidad in _puntos_singulares(funcion, xmin, xmax):
        mascara &= np.abs(xs - singularidad) > 1.5 * paso

    segmentos = []
    actual_x, actual_y = [], []
    for x_valor, y_valor, valido in zip(xs, ys, mascara):
        if valido:
            actual_x.append(float(x_valor))
            actual_y.append(float(y_valor))
        elif actual_x:
            if len(actual_x) >= 2:
                segmentos.append((np.array(actual_x), np.array(actual_y)))
            actual_x, actual_y = [], []
    if len(actual_x) >= 2:
        segmentos.append((np.array(actual_x), np.array(actual_y)))
    if not segmentos:
        raise ErrorFuncion("No hay valores reales y finitos para graficar en ese intervalo.")
    return segmentos


def crear_figura(funcion, xmin, xmax, resultado_biseccion=None, cantidad=2000):
    """Crea una figura Matplotlib con función, intervalos y raíz opcionales."""
    import matplotlib.pyplot as plt

    segmentos = preparar_datos_grafica(funcion, xmin, xmax, cantidad)
    figura, eje = plt.subplots(figsize=(9, 5.5))
    for indice, (xs, ys) in enumerate(segmentos):
        eje.plot(xs, ys, color="#0077B6", linewidth=1.8,
                 label="f(x)" if indice == 0 else None)
    eje.axhline(0, color="#555555", linewidth=0.8)
    eje.set_title("Gráfica de f(x) = " + funcion.texto)
    eje.set_xlabel("x")
    eje.set_ylabel("f(x)")
    eje.grid(True, alpha=0.3)
    if resultado_biseccion is not None:
        eje.scatter([resultado_biseccion.raiz], [resultado_biseccion.fr],
                    color="#D62828", zorder=5, label="Raíz aproximada")
        eje.axvspan(resultado_biseccion.a_inicial,
                    resultado_biseccion.b_inicial, color="#90E0EF",
                    alpha=0.22, label="Intervalo inicial")
        eje.axvspan(resultado_biseccion.a_final,
                    resultado_biseccion.b_final, color="#2A9D8F",
                    alpha=0.20, label="Intervalo final")
    eje.legend()
    figura.tight_layout()
    return figura


def _digitos_base(valor, base):
    """Devuelve los dígitos del valor absoluto en la base solicitada."""
    absoluto = abs(int(valor))
    if absoluto == 0:
        return "0"
    digitos = []
    while absoluto:
        digitos.append(str(absoluto % base))
        absoluto //= base
    return "".join(reversed(digitos))


def _expansion(digitos, base):
    """Construye la expansión posicional y los sumandos no nulos."""
    signo = "-" if digitos.startswith("-") else ""
    limpios = digitos.lstrip("-")
    terminos = []
    sumandos = []
    for posicion, digito in enumerate(limpios):
        potencia = len(limpios) - posicion - 1
        valor = int(digito) * (base ** potencia)
        terminos.append(f"{digito} · {base}{str(potencia).translate(_SUPERSCRIPTS)}")
        if valor:
            sumandos.append(str(valor))
    expansion = signo + " + ".join(terminos)
    return expansion, " + ".join(sumandos) if sumandos else "0"


def analizar_notacion(texto, base):
    """Descompone un entero y devuelve su equivalente en base 10 y 2."""
    texto = str(texto).strip().replace(" ", "")
    base = int(base)
    if base not in (2, 10):
        raise ValueError("La base debe ser 2 o 10.")
    if not texto or texto in ("+", "-"):
        raise ValueError("Debe ingresar un número entero.")
    signo = -1 if texto.startswith("-") else 1
    limpio = texto.lstrip("+-")
    if not limpio.isdigit():
        raise ValueError("Debe ingresar un número entero sin puntos decimales.")
    if base == 2 and any(digito not in "01" for digito in limpio):
        raise ValueError("En base 2 solo se permiten los dígitos 0 y 1.")
    valor = signo * int(limpio, base)
    digitos10 = ("-" if valor < 0 else "") + str(abs(valor))
    digitos2 = ("-" if valor < 0 else "") + _digitos_base(valor, 2)
    expansion_origen, suma_origen = _expansion(("-" if signo < 0 else "") + limpio, base)
    expansion10, suma10 = _expansion(digitos10, 10)
    expansion2, suma2 = _expansion(digitos2, 2)
    return {
        "base_origen": base,
        "entrada": texto,
        "valor_decimal": valor,
        "binario": digitos2,
        "decimal": digitos10,
        "expansion_origen": expansion_origen,
        "suma_origen": suma_origen,
        "expansion10": expansion10,
        "suma10": suma10,
        "expansion2": expansion2,
        "suma2": suma2,
    }


def calcular_errores(valor_verdadero, valor_aproximado):
    """Calcula errores absoluto, relativo y relativo porcentual."""
    xv, xa = float(valor_verdadero), float(valor_aproximado)
    if not math.isfinite(xv) or not math.isfinite(xa):
        raise ValueError("Los valores deben ser finitos.")
    absoluto = abs(xv - xa)
    relativo = None if xv == 0 else absoluto / abs(xv)
    return {
        "verdadero": xv,
        "aproximado": xa,
        "absoluto": absoluto,
        "relativo": relativo,
        "porcentual": None if relativo is None else relativo * 100,
    }


def propagacion_error(x, delta_x):
    """Compara la propagación lineal con el cambio real de sen(x)+x²."""
    x, delta_x = float(x), float(delta_x)
    if not math.isfinite(x) or not math.isfinite(delta_x):
        raise ValueError("x y Δx deben ser valores finitos.")
    funcion = lambda valor: math.sin(valor) + valor ** 2
    derivada = math.cos(x) + 2 * x
    aproximado = derivada * delta_x
    real = funcion(x + delta_x) - funcion(x)
    return {
        "x": x,
        "delta_x": delta_x,
        "f_x": funcion(x),
        "derivada": derivada,
        "delta_y_aproximado": aproximado,
        "delta_y_real": real,
        "diferencia": abs(aproximado - real),
    }


def diagnostico_punto_flotante():
    """Explica punto flotante y captura ejemplos de overflow y underflow."""
    advertencias = []
    with warnings.catch_warnings(record=True) as capturadas:
        warnings.simplefilter("always")
        with np.errstate(over="warn", under="warn", invalid="warn", divide="warn"):
            overflow = np.exp(np.float64(1000))
            underflow = np.exp(np.float64(-1000))
        advertencias = [str(aviso.message) for aviso in capturadas]
    return {
        "suma": 0.1 + 0.2,
        "comparacion": (0.1 + 0.2 == 0.3),
        "epsilon": float(np.finfo(float).eps),
        "overflow": overflow,
        "underflow": underflow,
        "overflow_finito": bool(np.isfinite(overflow)),
        "underflow_finito": bool(np.isfinite(underflow)),
        "advertencias": advertencias,
    }


DEFINICIONES_ERRORES = (
    "ERROR INHERENTE: incertidumbre de los datos de entrada o de su representación.\n"
    "Ejemplo: representar 0.1 en binario usando punto flotante.\n\n"
    "ERROR DE REDONDEO: se reemplaza un número por otro representable cercano.\n"
    "Ejemplo: guardar 1/3 con un número limitado de cifras.\n\n"
    "ERROR DE TRUNCAMIENTO: se detiene una serie o procedimiento aproximado.\n"
    "Ejemplo: usar pocos términos de la serie de sen(x).\n\n"
    "OVERFLOW: el resultado supera el mayor valor representable.\n"
    "Ejemplo: exp(1000) en doble precisión.\n\n"
    "UNDERFLOW: el resultado es demasiado pequeño y puede redondearse a cero.\n"
    "Ejemplo: exp(-1000) en doble precisión.\n\n"
    "ERROR DEL MODELO: el modelo matemático no representa completamente el fenómeno.\n"
    "Ejemplo: ignorar la fricción al modelar el movimiento de un objeto.\n\n"
    "El truncamiento numérico afecta el cálculo; el error de modelación afecta la\n"
    "elección de las ecuaciones y no se corrige simplemente aumentando cifras."
)


def _numero_flotante(texto, nombre):
    """Convierte un texto a float aceptando coma decimal."""
    try:
        valor = float(str(texto).strip().replace(",", "."))
    except ValueError as error:
        raise ValueError(nombre + " debe ser numérico.") from error
    if not math.isfinite(valor):
        raise ValueError(nombre + " debe ser finito.")
    return valor


def _formato_numero(valor):
    """Formato compacto para tablas y resultados."""
    if isinstance(valor, str):
        return valor
    return f"{float(valor):.10g}"


class MarcoDesplazable(tk.Frame):
    """Contenedor con barra vertical para pantallas altas o pequeñas."""

    def __init__(self, padre):
        super().__init__(padre, bg=FONDO)
        self.canvas = tk.Canvas(self, bg=FONDO, highlightthickness=0)
        self.barra_vertical = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.barra_vertical.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.barra_vertical.pack(side="right", fill="y")

        self.contenido = tk.Frame(self.canvas, bg=FONDO)
        self.ventana = self.canvas.create_window(
            (0, 0), window=self.contenido, anchor="nw"
        )
        self.contenido.bind("<Configure>", self._actualizar_region)
        self.canvas.bind("<Configure>", self._ajustar_ancho)
        self.canvas.bind("<Enter>", self._activar_rueda)
        self.canvas.bind("<Leave>", self._desactivar_rueda)

    def _actualizar_region(self, _evento=None):
        """Ajusta el área desplazable al tamaño real del contenido."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho(self, evento):
        """Hace que el contenido ocupe todo el ancho disponible."""
        self.canvas.itemconfigure(self.ventana, width=evento.width)

    def _activar_rueda(self, _evento=None):
        """Activa la rueda del mouse mientras el puntero está en el panel."""
        self.canvas.bind_all("<MouseWheel>", self._desplazar_rueda)

    def _desactivar_rueda(self, _evento=None):
        """Deja libre la rueda al salir del panel."""
        self.canvas.unbind_all("<MouseWheel>")

    def _desplazar_rueda(self, evento):
        """Desplaza varias líneas de forma cómoda en Windows."""
        self.canvas.yview_scroll(int(-evento.delta / 120), "units")

class MetodosNumericosApp:
    """Pantalla Tkinter del módulo de Métodos Numéricos."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver
        self.ultimo_biseccion = None
        self.fuente_titulo = tkfont.Font(family="Montserrat", size=21, weight="bold")
        self.fuente_body = tkfont.Font(family="Montserrat", size=10)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=10, weight="bold")
        self.marco = tk.Frame(raiz, bg=FONDO)
        self.marco.pack(fill="both", expand=True)
        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        """Configura estilos propios sin alterar los módulos anteriores."""
        estilo = ttk.Style(self.raiz)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure(
            "Numericos.TNotebook",
            background=FONDO,
            borderwidth=0,
        )
        estilo.configure(
            "Numericos.TNotebook.Tab",
            background="#DCEFF7",
            foreground=TEXTO,
            padding=(16, 8),
            font=("Montserrat", 10, "bold"),
        )
        estilo.map(
            "Numericos.TNotebook.Tab",
            background=[("selected", ACENTO)],
            foreground=[("selected", FONDO)],
        )
        estilo.configure(
            "Numericos.Treeview",
            background=TARJETA,
            fieldbackground=TARJETA,
            foreground=TEXTO,
            rowheight=27,
            font=(LETRA_MONO, 9),
        )
        estilo.configure(
            "Numericos.Treeview.Heading",
            background=ACENTO,
            foreground=FONDO,
            font=("Montserrat", 9, "bold"),
            relief="flat",
        )

    def _construir_ui(self):
        cabecera = tk.Frame(self.marco, bg=FONDO)
        cabecera.pack(fill="x", padx=28, pady=(10, 0))
        tk.Button(cabecera, text="← Volver al Menú", font=self.fuente_body,
                  bg=FONDO, fg=ACENTO, bd=0, command=self.volver_al_menu,
                  cursor="hand2").pack(side="left")
        tk.Button(cabecera, text="0. Ver Teoremas Clave", font=self.fuente_body,
                  bg=BOTON_SEC, fg=TEXTO, bd=0, padx=10, pady=5,
                  command=self._ver_teoremas).pack(side="right")
        tk.Label(self.marco, text="Módulo 6: Métodos Numéricos",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO).pack(anchor="w", padx=28, pady=(4, 0))
        tk.Label(self.marco, text="Bisección, funciones, notación posicional y errores numéricos",
                 font=self.fuente_body, bg=FONDO, fg=TEXTO_SUAVE).pack(anchor="w", padx=28, pady=(0, 8))
        self.pestanas = ttk.Notebook(self.marco, style="Numericos.TNotebook")
        self.pestanas.pack(fill="both", expand=True, padx=28, pady=(0, 22))
        self._construir_pestana_biseccion()
        self._construir_pestana_grafica()
        self._construir_pestana_posicional()
        self._construir_pestana_errores()

    def _crear_pestana(self, titulo, descripcion):
        """Crea una pestaña con descripción y desplazamiento vertical."""
        exterior = tk.Frame(self.pestanas, bg=FONDO)
        self.pestanas.add(exterior, text=titulo)
        desplazable = MarcoDesplazable(exterior)
        desplazable.pack(fill="both", expand=True)
        tk.Label(
            desplazable.contenido,
            text=descripcion,
            bg=FONDO,
            fg=TEXTO_SUAVE,
            font=self.fuente_body,
            anchor="w",
        ).pack(fill="x", padx=20, pady=(14, 2))
        return desplazable.contenido

    def _entrada(self, padre, texto, fila, columna, valor=""):
        tk.Label(padre, text=texto, bg=FONDO, fg=TEXTO,
                 font=self.fuente_body).grid(row=fila, column=columna, sticky="w", padx=8, pady=8)
        entrada = tk.Entry(padre, width=18, font=self.fuente_body,
                           relief="solid", bd=1,
                           highlightthickness=1,
                           highlightcolor="#90E0EF")
        entrada.insert(0, valor)
        entrada.grid(row=fila, column=columna + 1, sticky="ew", padx=8, pady=8)
        return entrada

    def _construir_pestana_biseccion(self):
        pestaña = self._crear_pestana(
            "A. Bisección",
            "Encuentre una raíz con una función continua y un cambio de signo válido.",
        )
        entrada = tk.Frame(pestaña, bg=TARJETA,
                           highlightbackground="#C9E3ED", highlightthickness=1)
        entrada.pack(fill="x", padx=35, pady=(18, 16))
        self.campo_funcion = self._entrada(entrada, "f(x):", 0, 0, "x**3 - 2*x - 5")
        self.campo_a = self._entrada(entrada, "a:", 1, 0, "2")
        self.campo_b = self._entrada(entrada, "b:", 1, 2, "3")
        self.campo_tol = self._entrada(entrada, "Tolerancia E:", 2, 0, "0.0001")
        self.campo_max = self._entrada(entrada, "Máximo:", 2, 2, "100")
        entrada.columnconfigure(1, weight=1)
        entrada.columnconfigure(3, weight=1)
        tk.Button(entrada, text="Ejecutar bisección", font=self.fuente_boton,
                  bg=ACENTO, fg=FONDO, relief="flat", padx=12, pady=8,
                  command=self._ejecutar_biseccion).grid(row=3, column=0, columnspan=4, pady=10)
        self.texto_biseccion = tk.Text(pestaña, height=8, wrap="word", font=(LETRA_MONO, 10),
                                      bg=TARJETA, fg=TEXTO, relief="solid", bd=1)
        self.texto_biseccion.pack(fill="x", padx=35, pady=(0, 12), ipady=8)
        tk.Label(pestaña,
                 text="La tabla registra a, b, f(a) y f(b) antes de actualizar el intervalo.",
                 bg=FONDO, fg=TEXTO_SUAVE, font=self.fuente_body).pack(anchor="w", padx=15)
        marco_tabla = tk.Frame(
            pestaña, bg=TARJETA,
            highlightbackground="#C9E3ED", highlightthickness=1,
        )
        marco_tabla.pack(fill="both", expand=True, padx=35, pady=(0, 25))
        marco_cuerpo = tk.Frame(marco_tabla, bg=TARJETA)
        marco_cuerpo.pack(fill="both", expand=True, padx=12, pady=(12, 0))
        marco_cuerpo.rowconfigure(0, weight=1)
        marco_cuerpo.columnconfigure(0, weight=1)
        columnas = ("k", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Eb", "Ea", "εa")
        self.tabla_biseccion = ttk.Treeview(
            marco_cuerpo, columns=columnas, show="headings", height=10,
            style="Numericos.Treeview",
        )
        self.tabla_biseccion.tag_configure("fila_par", background="#F1F8FB")
        self.tabla_biseccion.tag_configure("fila_impar", background=TARJETA)
        for columna in columnas:
            self.tabla_biseccion.heading(columna, text=columna)
            self.tabla_biseccion.column(columna, width=125, minwidth=90,
                                        anchor="center", stretch=False)
        barra_vertical = ttk.Scrollbar(
            marco_cuerpo, orient="vertical", command=self.tabla_biseccion.yview
        )
        barra_horizontal = ttk.Scrollbar(
            marco_tabla, orient="horizontal", command=self.tabla_biseccion.xview
        )
        self.tabla_biseccion.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        self.tabla_biseccion.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.pack(side="bottom", fill="x", padx=12, pady=(8, 12))

    def _ejecutar_biseccion(self):
        try:
            funcion = parsear_funcion(self.campo_funcion.get())
            resultado = biseccion(
                funcion,
                _numero_flotante(self.campo_a.get(), "a"),
                _numero_flotante(self.campo_b.get(), "b"),
                _numero_flotante(self.campo_tol.get(), "La tolerancia"),
                int(self.campo_max.get().strip()),
            )
        except (ValueError, ErrorFuncion) as error:
            messagebox.showerror("Datos inválidos", str(error), parent=self.raiz)
            return
        self.ultimo_biseccion = resultado
        self.texto_biseccion.configure(state="normal")
        self.texto_biseccion.delete("1.0", "end")
        texto = (
            f"Raíz aproximada: {_formato_numero(resultado.raiz)}\n"
            f"f(xr): {_formato_numero(resultado.fr)}\n"
            f"Cota Eb: {_formato_numero(resultado.eb)}\n"
            f"Iteraciones ejecutadas: {len(resultado.iteraciones)}\n"
            f"Iteraciones teóricas: {resultado.teoricas}\n"
            f"Estado: {resultado.mensaje}\n"
        )
        if resultado.raiz_scipy is not None:
            texto += (
                f"SciPy (solo contraste): {_formato_numero(resultado.raiz_scipy)}\n"
                f"Diferencia absoluta: {_formato_numero(resultado.diferencia_scipy)}\n"
            )
        else:
            texto += "SciPy no pudo realizar el contraste.\n"
        self.texto_biseccion.insert("1.0", texto)
        self.texto_biseccion.configure(state="disabled")
        for item in self.tabla_biseccion.get_children():
            self.tabla_biseccion.delete(item)
        colores_estado = {
            "tolerancia": "#E8F5E9",
            "raiz_exacta": "#E3F2FD",
            "maximo_iteraciones": "#FFF3E0",
        }
        self.texto_biseccion.configure(
            bg=colores_estado.get(resultado.estado, TARJETA)
        )
        for indice, fila in enumerate(resultado.iteraciones):
            self.tabla_biseccion.insert("", "end", tags=(
                "fila_par" if indice % 2 == 0 else "fila_impar",
            ), values=(
                fila.k, _formato_numero(fila.a), _formato_numero(fila.b),
                _formato_numero(fila.xr), _formato_numero(fila.fa),
                _formato_numero(fila.fb), _formato_numero(fila.fr),
                _formato_numero(fila.eb), _formato_numero(fila.ea),
                _formato_numero(fila.er),
            ))

    def _construir_pestana_grafica(self):
        pestaña = self._crear_pestana(
            "B. Graficador",
            "Explore funciones reales; los puntos indefinidos no se conectan entre sí.",
        )
        marco = tk.Frame(pestaña, bg=TARJETA,
                         highlightbackground="#C9E3ED", highlightthickness=1)
        marco.pack(fill="x", padx=30, pady=25)
        self.campo_grafica = self._entrada(marco, "f(x):", 0, 0, "1/(x - 1)")
        self.campo_xmin = self._entrada(marco, "x mínimo:", 1, 0, "-2")
        self.campo_xmax = self._entrada(marco, "x máximo:", 1, 2, "3")
        self.campo_puntos = self._entrada(marco, "Puntos:", 2, 0, "2000")
        marco.columnconfigure(1, weight=1)
        marco.columnconfigure(3, weight=1)
        tk.Button(marco, text="Graficar función", font=self.fuente_boton,
                  bg=ACENTO, fg=FONDO, relief="flat", padx=12, pady=8,
                  command=self._graficar).grid(row=3, column=0, columnspan=4, pady=12)
        tk.Button(marco, text="Usar última bisección", font=self.fuente_boton,
                  bg=BOTON_SEC, fg=TEXTO, relief="flat", padx=12, pady=8,
                  command=self._usar_ultima_biseccion).grid(row=4, column=0, columnspan=4, pady=4)
        tk.Label(pestaña, text="Se excluyen valores fuera del dominio y se cortan segmentos en discontinuidades.",
                 bg=FONDO, fg=TEXTO_SUAVE, font=self.fuente_body).pack(anchor="w", padx=30)

    def _usar_ultima_biseccion(self):
        """Carga en el graficador la función y el intervalo de la última bisección."""
        if self.ultimo_biseccion is None:
            messagebox.showinfo("Bisección", "Primero ejecute una bisección válida.", parent=self.raiz)
            return
        self.campo_grafica.delete(0, "end")
        self.campo_grafica.insert(0, self.ultimo_biseccion.funcion.texto)
        self.campo_xmin.delete(0, "end")
        self.campo_xmin.insert(0, str(self.ultimo_biseccion.a_inicial))
        self.campo_xmax.delete(0, "end")
        self.campo_xmax.insert(0, str(self.ultimo_biseccion.b_inicial))
        self.pestanas.select(1)

    def _graficar(self):
        try:
            funcion = parsear_funcion(self.campo_grafica.get())
            xmin = _numero_flotante(self.campo_xmin.get(), "x mínimo")
            xmax = _numero_flotante(self.campo_xmax.get(), "x máximo")
            figura = crear_figura(
                funcion, xmin, xmax,
                self.ultimo_biseccion if self.ultimo_biseccion and
                self.ultimo_biseccion.funcion.texto == funcion.texto else None,
                int(self.campo_puntos.get()),
            )
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            ventana = tk.Toplevel(self.raiz)
            ventana.title("Gráfica de función")
            canvas = FigureCanvasTkAgg(figura, master=ventana)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            ventana.geometry("920x650")
        except (ValueError, ErrorFuncion) as error:
            messagebox.showerror("No se puede graficar", str(error), parent=self.raiz)

    def _construir_pestana_posicional(self):
        pestaña = self._crear_pestana(
            "C. Notación posicional",
            "Descomponga un entero según las potencias de su base y compruebe equivalencias.",
        )
        marco = tk.Frame(pestaña, bg=TARJETA,
                         highlightbackground="#C9E3ED", highlightthickness=1)
        marco.pack(fill="x", padx=30, pady=25)
        self.campo_posicional = self._entrada(marco, "Número entero:", 0, 0, "11110011")
        self.var_base = tk.StringVar(value="2")
        tk.Label(marco, text="Base de origen:", bg=FONDO, fg=TEXTO,
                 font=self.fuente_body).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Radiobutton(marco, text="2", variable=self.var_base, value="2", bg=FONDO).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(marco, text="10", variable=self.var_base, value="10", bg=FONDO).grid(row=1, column=2, sticky="w")
        tk.Button(marco, text="Descomponer", font=self.fuente_boton, bg=ACENTO,
                  fg=FONDO, relief="flat", padx=12, pady=8,
                  command=self._analizar_posicional).grid(row=2, column=0, columnspan=4, pady=12)
        self.texto_posicional = tk.Text(pestaña, height=15, wrap="word", font=(LETRA_MONO, 11),
                                       bg=TARJETA, fg=TEXTO, relief="solid", bd=1)
        self.texto_posicional.pack(fill="both", expand=True, padx=30, pady=(0, 25))

    def _analizar_posicional(self):
        try:
            datos = analizar_notacion(self.campo_posicional.get(), int(self.var_base.get()))
        except ValueError as error:
            messagebox.showerror("Dato inválido", str(error), parent=self.raiz)
            return
        texto = (
            f"Base de origen: {datos['base_origen']}\n"
            f"Valor decimal: {datos['valor_decimal']}\n\n"
            f"Descomposición en base {datos['base_origen']}:\n"
            f"{datos['expansion_origen']}\n"
            f"Suma: {datos['suma_origen']}\n\n"
            f"Base 10: {datos['expansion10']}\n"
            f"Base 2: {datos['expansion2']}\n\n"
            f"Equivalencia: ({datos['binario']})₂ = ({datos['decimal']})₁₀"
        )
        self.texto_posicional.delete("1.0", "end")
        self.texto_posicional.insert("1.0", texto)

    def _construir_pestana_errores(self):
        pestaña = self._crear_pestana(
            "D. Errores numéricos",
            "Compare errores absolutos, relativos y la propagación mediante derivadas.",
        )
        superior = tk.Frame(pestaña, bg=TARJETA,
                            highlightbackground="#C9E3ED", highlightthickness=1)
        superior.pack(fill="x", padx=25, pady=15)
        self.campo_xv = self._entrada(superior, "Valor verdadero xv:", 0, 0, "1/3")
        self.campo_xa = self._entrada(superior, "Valor aproximado xa:", 0, 2, "0.333")
        self.campo_prop_x = self._entrada(superior, "x:", 1, 0, "0.5")
        self.campo_prop_delta = self._entrada(superior, "Δx:", 1, 2, "0.001")
        superior.columnconfigure(1, weight=1)
        superior.columnconfigure(3, weight=1)
        tk.Button(superior, text="Calcular errores y propagación", font=self.fuente_boton,
                  bg=ACENTO, fg=FONDO, relief="flat", padx=10, pady=8,
                  command=self._calcular_errores_ui).grid(row=2, column=0, columnspan=4, pady=8)
        tk.Button(superior, text="Diagnóstico de punto flotante", font=self.fuente_boton,
                  bg=BOTON_SEC, fg=TEXTO, relief="flat", padx=10, pady=8,
                  command=self._diagnostico_ui).grid(row=3, column=0, columnspan=4, pady=4)
        self.texto_errores = tk.Text(pestaña, height=22, wrap="word", font=(LETRA_MONO, 10),
                                    bg=TARJETA, fg=TEXTO, relief="solid", bd=1)
        self.texto_errores.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        self.texto_errores.insert("1.0", DEFINICIONES_ERRORES)

    def _calcular_errores_ui(self):
        try:
            errores = calcular_errores(
                _numero_flotante(self.campo_xv.get(), "xv"),
                _numero_flotante(self.campo_xa.get(), "xa"),
            )
            propagacion = propagacion_error(
                _numero_flotante(self.campo_prop_x.get(), "x"),
                _numero_flotante(self.campo_prop_delta.get(), "Δx"),
            )
        except ValueError as error:
            messagebox.showerror("Datos inválidos", str(error), parent=self.raiz)
            return
        relativo = "No definido" if errores["relativo"] is None else _formato_numero(errores["relativo"])
        porcentual = "No definido" if errores["porcentual"] is None else _formato_numero(errores["porcentual"]) + "%"
        texto = (
            DEFINICIONES_ERRORES + "\n\n"
            "CÁLCULO DE ERRORES\n"
            f"Error absoluto: {_formato_numero(errores['absoluto'])}\n"
            f"Error relativo: {relativo}\n"
            f"Error relativo porcentual: {porcentual}\n\n"
            "PROPAGACIÓN: f(x) = sen(x) + x²\n"
            f"f'(x): {_formato_numero(propagacion['derivada'])}\n"
            f"Δy aproximado: {_formato_numero(propagacion['delta_y_aproximado'])}\n"
            f"Δy real: {_formato_numero(propagacion['delta_y_real'])}\n"
            f"Diferencia absoluta: {_formato_numero(propagacion['diferencia'])}\n"
            "La aproximación por derivada es de primer orden y mejora cuando Δx es pequeño."
        )
        self.texto_errores.delete("1.0", "end")
        self.texto_errores.insert("1.0", texto)

    def _diagnostico_ui(self):
        datos = diagnostico_punto_flotante()
        texto = (
            "REPRESENTACIÓN DE PUNTO FLOTANTE\n"
            f"0.1 + 0.2 = {datos['suma']!r}\n"
            f"0.1 + 0.2 == 0.3: {datos['comparacion']}\n"
            f"Épsilon de máquina: {datos['epsilon']!r}\n"
            "Representa la distancia entre 1.0 y el siguiente float mayor.\n\n"
            f"Overflow exp(1000): {datos['overflow']!r}\n"
            f"Underflow exp(-1000): {datos['underflow']!r}\n"
            "El resultado depende del tipo de dato y del entorno.\n"
        )
        if datos["advertencias"]:
            texto += "Advertencias capturadas:\n- " + "\n- ".join(datos["advertencias"])
        self.texto_errores.delete("1.0", "end")
        self.texto_errores.insert("1.0", texto + "\n\n" + DEFINICIONES_ERRORES)

    def _ver_teoremas(self):
        mostrar_teoremas(self.raiz, "numericos", "Módulo 6: Métodos Numéricos")

    def volver_al_menu(self):
        """Regresa al menú principal."""
        self.marco.destroy()
        self.callback_volver()


def _imprimir_tabla(resultado):
    """Imprime la tabla de bisección en consola."""
    encabezados = ("k", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Eb", "Ea", "εa")
    print(" | ".join(f"{encabezado:>12}" for encabezado in encabezados))
    print("-" * 125)
    for fila in resultado.iteraciones:
        valores = (fila.k, fila.a, fila.b, fila.xr, fila.fa, fila.fb,
                   fila.fr, fila.eb, fila.ea, fila.er)
        print(" | ".join(f"{_formato_numero(valor):>12}" for valor in valores))


def _leer_float(mensaje):
    """Solicita un float hasta que el usuario escriba un valor correcto."""
    while True:
        try:
            return _numero_flotante(preguntar(mensaje), "El valor")
        except ValueError as error:
            print("   " + str(error))


def _leer_funcion():
    """Solicita una función y permite corregirla."""
    while True:
        try:
            return parsear_funcion(preguntar("   f(x) = "))
        except ErrorFuncion as error:
            print("   " + str(error))


def _menu_biseccion():
    """Ejecuta la opción de bisección en consola."""
    funcion = _leer_funcion()
    a = _leer_float("   a = ")
    b = _leer_float("   b = ")
    tolerancia = _leer_float("   Tolerancia E = ")
    while True:
        try:
            maximo = int(preguntar("   Máximo de iteraciones = ").strip())
            resultado = biseccion(funcion, a, b, tolerancia, maximo)
            break
        except (ValueError, ErrorFuncion) as error:
            print("   " + str(error))
            if "máximo" not in str(error).lower():
                a = _leer_float("   a = ")
                b = _leer_float("   b = ")
                tolerancia = _leer_float("   Tolerancia E = ")
    print("\n   " + resultado.mensaje)
    print("   Raíz aproximada:", _formato_numero(resultado.raiz))
    print("   f(xr):", _formato_numero(resultado.fr))
    print("   Cota Eb:", _formato_numero(resultado.eb))
    print("   Iteraciones teóricas:", resultado.teoricas)
    print("   Iteraciones ejecutadas:", len(resultado.iteraciones))
    if resultado.raiz_scipy is not None:
        print("   SciPy (contraste):", _formato_numero(resultado.raiz_scipy))
        print("   Diferencia absoluta:", _formato_numero(resultado.diferencia_scipy))
    _imprimir_tabla(resultado)
    return resultado


def _menu_grafica(ultimo=None):
    """Grafica una función desde consola."""
    funcion = _leer_funcion()
    xmin = _leer_float("   x mínimo = ")
    xmax = _leer_float("   x máximo = ")
    try:
        figura = crear_figura(funcion, xmin, xmax,
                              ultimo if ultimo and ultimo.funcion.texto == funcion.texto else None)
        import matplotlib.pyplot as plt
        plt.show()
        return figura
    except (ValueError, ErrorFuncion) as error:
        print("   " + str(error))
        return None


def _menu_posicional():
    """Ejecuta la opción de notación posicional en consola."""
    while True:
        try:
            texto = preguntar("   Número entero = ").strip()
            base = int(preguntar("   Base de origen (2 o 10) = ").strip())
            datos = analizar_notacion(texto, base)
            break
        except ValueError as error:
            print("   " + str(error))
    print("\n   Base de origen:", datos["base_origen"])
    print("   ", datos["expansion_origen"])
    print("   Suma:", datos["suma_origen"])
    print("   Base 10:", datos["expansion10"])
    print("   Base 2:", datos["expansion2"])
    print(f"   Equivalencia: ({datos['binario']})₂ = ({datos['decimal']})₁₀")


def _menu_errores():
    """Ejecuta cálculo de errores y propagación en consola."""
    xv = _leer_float("   Valor verdadero xv = ")
    xa = _leer_float("   Valor aproximado xa = ")
    x = _leer_float("   x para propagación = ")
    delta = _leer_float("   Δx = ")
    errores = calcular_errores(xv, xa)
    propagacion = propagacion_error(x, delta)
    print("\n   Error absoluto:", errores["absoluto"])
    print("   Error relativo:", "No definido" if errores["relativo"] is None else errores["relativo"])
    print("   Error relativo porcentual:", "No definido" if errores["porcentual"] is None else errores["porcentual"])
    print("\n   f'(x):", propagacion["derivada"])
    print("   Δy aproximado:", propagacion["delta_y_aproximado"])
    print("   Δy real:", propagacion["delta_y_real"])
    print("   Diferencia absoluta:", propagacion["diferencia"])
    datos = diagnostico_punto_flotante()
    print("\n   0.1 + 0.2 == 0.3:", datos["comparacion"])
    print("   Epsilon de máquina:", datos["epsilon"])
    print("   Overflow:", datos["overflow"], " Underflow:", datos["underflow"])
    print("\n" + DEFINICIONES_ERRORES)


def menu_consola():
    """Menú de Métodos Numéricos en consola."""
    ultimo = None
    while True:
        mostrar_cabecera(LOGO_NUMERICOS)
        print("   1. Método de Bisección")
        print("   2. Graficador de funciones")
        print("   3. Notación posicional")
        print("   4. Errores numéricos")
        print("   9. Volver al menú principal")
        opcion = preguntar("\n   Elegí una opción: ").strip()
        if opcion == "1":
            try:
                ultimo = _menu_biseccion()
            except SalirDeLaConsola:
                raise
            pausa()
        elif opcion == "2":
            _menu_grafica(ultimo)
            pausa()
        elif opcion == "3":
            _menu_posicional()
            pausa()
        elif opcion == "4":
            _menu_errores()
            pausa()
        elif opcion == "9":
            return
        else:
            print("   Opción no válida.")
            pausa()
