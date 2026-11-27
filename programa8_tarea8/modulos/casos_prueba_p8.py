# -*- coding: utf-8 -*-
"""casos_prueba_p8.py - Los tres casos obligatorios del Programa 8."""
from modulos.modulo_iterativos import ejecutar_y_mostrar

CASOS = {
    1: {
        "titulo": "CASO 1: Convergencia (diagonal estrictamente dominante)",
        "objetivo": "Comprobar que Jacobi y Gauss-Seidel convergen y comparar iteraciones/solucion.",
        "A": [[10, -1, 2, 0], [-1, 11, -1, 3], [2, -1, 10, -1], [0, 3, -1, 8]],
        "b": [6, 25, -11, 15], "x0": [0, 0, 0, 0],
        "tol": 1e-8, "max_iter": 100, "reordenar": False,
    },
    2: {
        "titulo": "CASO 2: Reordenamiento de filas (hay un cero en la diagonal)",
        "objetivo": "Mostrar que reordenar las ecuaciones deja una diagonal dominante y permite continuar.",
        "A": [[0, 5, 1], [4, 1, 0], [1, 1, 6]],
        "b": [7, 9, 15], "x0": [0, 0, 0],
        "tol": 1e-8, "max_iter": 100, "reordenar": True,
    },
    3: {
        "titulo": "CASO 3: No convergencia (sin dominancia diagonal, sin reordenar)",
        "objetivo": "Observar divergencia/advertencia. No cumplir la condicion suficiente no basta "
                    "para afirmar divergencia; aqui ademas el radio espectral de la iteracion es > 1.",
        "A": [[1, 2], [3, 1]],
        "b": [3, 4], "x0": [0, 0],
        "tol": 1e-8, "max_iter": 50, "reordenar": False,
    },
}


def ejecutar_caso(indice):
    """indice = 0, 1 o 2 (consola)."""
    c = CASOS[indice + 1]
    print("\n" + "=" * 70)
    print(c["titulo"])
    print("Objetivo:", c["objetivo"])
    print("=" * 70)
    ejecutar_y_mostrar(c["A"], c["b"], c["x0"], c["tol"], c["max_iter"],
                       c["reordenar"], f"caso{indice + 1}")