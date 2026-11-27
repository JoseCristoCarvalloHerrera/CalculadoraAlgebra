# -*- coding: utf-8 -*-
"""casos_prueba_p9.py - Los tres casos obligatorios del Programa 9.

Cada caso deja la tabla de iteraciones, el mensaje final y la grafica en
la carpeta 'evidencias', que es lo que pide la seccion 5 del enunciado.
Los tres estan tomados de la Sesion 22 para que el desarrollo coincida
con los ejemplos de clase.
"""
import os

from modulos.modulo_newton import (
    guardar_figura,
    newton_raphson,
    texto_resumen,
    texto_tabla,
)


CARPETA_EVIDENCIAS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidencias")


CASOS = {
    1: {
        "titulo": "CASO 1: Convergencia",
        "objetivo": "Mostrar la aproximacion, el error y el residuo cuando el "
                    "metodo converge. Es el Ejemplo 1 de la Sesion 22.",
        "f": "exp(-x) - x", "x0": 0.0,
        "tol": 1e-4, "max_iter": 50, "criterio": "absoluto",
        "esperado": "4 iteraciones, raiz aproximada 0.567143",
    },
    2: {
        "titulo": "CASO 2: Derivada nula o cercana a cero",
        "objetivo": "El denominador f'(x0) vale exactamente 0, asi que la "
                    "formula no se puede aplicar. El programa debe detenerse "
                    "de forma controlada y explicar por que.",
        "f": "x**2 - 4", "x0": 0.0,
        "tol": 1e-4, "max_iter": 50, "criterio": "absoluto",
        "esperado": "se detiene en la iteracion 1 con estado derivada_nula",
    },
    3: {
        "titulo": "CASO 3: No alcanza el criterio de parada",
        "objetivo": "La iteracion oscila entre 0 y 1 sin acercarse a ninguna "
                    "raiz. El programa debe avisar que llego al maximo de "
                    "iteraciones sin converger, sin presentar un resultado "
                    "enganoso (Sesion 22, diapositiva 34).",
        "f": "x**3 - 2*x + 2", "x0": 0.0,
        "tol": 1e-4, "max_iter": 20, "criterio": "absoluto",
        "esperado": "20 iteraciones, estado max_iteraciones, residuo = 2",
    },
    4: {
        "titulo": "CASO 4 (complementario): derivada muy pequena",
        "objetivo": "f'(0.5) = 0.0195 no es cero, pero es tan pequena que la "
                    "primera iteracion salta hasta 51.65. Converge igual, "
                    "pero necesita 42 iteraciones (Sesion 22, diapositiva 35).",
        "f": "x**10 - 1", "x0": 0.5,
        "tol": 1e-4, "max_iter": 60, "criterio": "absoluto",
        "esperado": "42 iteraciones, raiz aproximada 1.0",
    },
}


def ejecutar_caso(indice, guardar=True):
    """Corre un caso (indice = 0, 1, 2 o 3) y muestra su evidencia.

    Imprime los datos de entrada, la tabla de iteraciones y el mensaje
    final; si guardar es True, deja ademas la grafica en 'evidencias'.
    Devuelve el ResultadoNewton por si el llamador quiere revisarlo.
    """
    caso = CASOS[indice + 1]
    print("\n" + "=" * 72)
    print(caso["titulo"])
    print("Objetivo:", caso["objetivo"])
    print("=" * 72)
    print("Datos de entrada: f(x) = " + caso["f"]
          + "   x0 = " + str(caso["x0"])
          + "   tolerancia = " + str(caso["tol"])
          + "   maximo = " + str(caso["max_iter"]))
    print("Resultado esperado: " + caso["esperado"])
    print()

    resultado = newton_raphson(caso["f"], caso["x0"], caso["tol"],
                               caso["max_iter"], caso["criterio"])
    print(texto_tabla(resultado))
    print()
    print(texto_resumen(resultado))

    if guardar:
        os.makedirs(CARPETA_EVIDENCIAS, exist_ok=True)
        archivo = os.path.join(CARPETA_EVIDENCIAS,
                               "caso%d_newton.png" % (indice + 1))
        try:
            guardar_figura(resultado, archivo)
            print("\nGrafica guardada en: " + archivo)
        except Exception as error:
            # Que falle la grafica no debe tumbar la corrida del caso.
            print("\nNo se pudo guardar la grafica: " + str(error))
    return resultado


def ejecutar_todos(guardar=True):
    """Corre los cuatro casos seguidos, para generar todas las evidencias."""
    return [ejecutar_caso(indice, guardar) for indice in range(len(CASOS))]
