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
import sympy as sp

from modulos.modulo_metodos_numericos import (
    ErrorFuncion,
    FuncionSegura,
    parsear_funcion,
    _X,
)


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
