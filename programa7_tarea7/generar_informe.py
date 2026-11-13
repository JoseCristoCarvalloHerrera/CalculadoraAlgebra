# -*- coding: utf-8 -*-
"""Genera una evidencia documental inicial del Programa 7 en PDF."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from modulos.modulo_metodos_numericos import (
    analizar_notacion,
    biseccion,
    calcular_errores,
    crear_figura,
    parsear_funcion,
    propagacion_error,
)


RUTA = Path(__file__).with_name("Informe_Programa7_Grupo2.pdf")


def pagina_texto(pdf, titulo, texto, subtitulo=None):
    """Agrega una página de texto al informe."""
    figura = plt.figure(figsize=(8.27, 11.69))
    figura.text(0.5, 0.94, titulo, ha="center", va="top", fontsize=18,
                fontweight="bold", color="#0077B6")
    if subtitulo:
        figura.text(0.5, 0.90, subtitulo, ha="center", va="top", fontsize=10)
    figura.text(0.08, 0.85, texto, ha="left", va="top", fontsize=10,
                family="DejaVu Sans", linespacing=1.45)
    pdf.savefig(figura, bbox_inches="tight")
    plt.close(figura)


def main():
    """Genera portada, algoritmo y cuatro evidencias reproducibles."""
    funcion = parsear_funcion("x**3 - 2*x - 5")
    resultado = biseccion(funcion, 2, 3, 1e-4, 100)
    posicional = analizar_notacion("11110011", 2)
    errores = calcular_errores(1 / 3, 0.333)
    propagacion = propagacion_error(0.5, 0.001)

    with PdfPages(RUTA) as pdf:
        pagina_texto(
            pdf,
            "UNIVERSIDAD AMERICANA",
            "Facultad de Ingeniería y Arquitectura (FIA)\n\n"
            "Asignatura: Álgebra Lineal (MTM0120)\n\n"
            "ACTIVIDADES DE PROGRAMACIÓN EN PYTHON\n\n"
            "PROGRAMA 7\n\n"
            "Métodos Numéricos\n\n"
            "Grupo 2\n\n"
            "Marian Alejandra Guillén Castillo\n"
            "Chelsea Yosmara Quintanilla Blandón\n"
            "José Cristo Carvallo Herrera\n"
            "Gabriela Suyen Espinoza Rodríguez",
            "Informe documental y evidencias reproducibles",
        )
        pagina_texto(
            pdf,
            "Algoritmo de Bisección",
            "Entradas: f(x), a, b, tolerancia absoluta E y máximo de iteraciones.\n\n"
            "1. Se verifica a < b, E > 0 y Nmax >= 1.\n"
            "2. Se evalúan f(a) y f(b), comprobando que sean reales y finitos.\n"
            "3. Se exige continuidad en [a,b] y f(a)·f(b) < 0.\n"
            "4. En cada iteración se calcula xr = (a+b)/2.\n"
            "5. Antes de actualizar se calcula Eb = (b-a)/2 y se registra la fila.\n"
            "6. Se conserva la mitad que mantiene el cambio de signo.\n"
            "7. Se detiene por raíz exacta, Eb <= E o Nmax.\n\n"
            "Número teórico: n mínimo = ceil(log2((b-a)/E)).\n"
            "SciPy se utiliza únicamente para contrastar el resultado propio.",
            "La tabla conserva los extremos usados para calcular cada xr.",
        )

        figura = plt.figure(figsize=(11.69, 8.27))
        figura.suptitle("Evidencia 1: Bisección con tabla", fontsize=16,
                        color="#0077B6", fontweight="bold")
        datos = []
        for fila in resultado.iteraciones:
            datos.append([
                fila.k, f"{fila.a:.6f}", f"{fila.b:.6f}", f"{fila.xr:.6f}",
                f"{fila.fa:.3e}", f"{fila.fb:.3e}", f"{fila.fr:.3e}",
                f"{fila.eb:.3e}",
                fila.ea if isinstance(fila.ea, str) else f"{fila.ea:.3e}",
                fila.er if isinstance(fila.er, str) else f"{fila.er:.3e}",
            ])
        eje = figura.add_axes([0.04, 0.08, 0.92, 0.80])
        eje.axis("off")
        tabla = eje.table(
            cellText=datos,
            colLabels=["k", "a", "b", "xr", "f(a)", "f(b)", "f(xr)", "Eb", "Ea", "εa"],
            loc="center",
            cellLoc="center",
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(7)
        tabla.scale(1, 1.22)
        figura.text(
            0.05, 0.035,
            f"Raíz propia: {resultado.raiz:.10f} | E teórica: {resultado.teoricas} | "
            f"Ejecutadas: {len(resultado.iteraciones)} | "
            f"SciPy: {resultado.raiz_scipy:.10f}",
            fontsize=9,
        )
        pdf.savefig(figura)
        plt.close(figura)

        grafica = crear_figura(parsear_funcion("1/(x - 1)"), -2, 3)
        grafica.axes[0].set_title(
            "Evidencia 2: función racional sin unir la asíntota\n"
            "f(x) = 1/(x - 1)", color="#0077B6"
        )
        pdf.savefig(grafica)
        plt.close(grafica)

        pagina_texto(
            pdf,
            "Evidencia 3: Notación posicional",
            "Entrada: (11110011)₂\n\n"
            f"Descomposición:\n{posicional['expansion2']}\n\n"
            f"Suma: {posicional['suma2']}\n\n"
            f"Resultado decimal: ({posicional['decimal']})₁₀\n\n"
            "La conversión confirma que:\n"
            f"({posicional['binario']})₂ = ({posicional['decimal']})₁₀ = "
            f"{posicional['valor_decimal']}",
        )

        pagina_texto(
            pdf,
            "Evidencia 4: Errores y propagación",
            f"Valor verdadero: {errores['verdadero']}\n"
            f"Valor aproximado: {errores['aproximado']}\n"
            f"Error absoluto: {errores['absoluto']}\n"
            f"Error relativo: {errores['relativo']}\n"
            f"Error porcentual: {errores['porcentual']}\n\n"
            "f(x) = sen(x) + x²\n"
            f"f'(x): {propagacion['derivada']}\n"
            f"Δy aproximado: {propagacion['delta_y_aproximado']}\n"
            f"Δy real: {propagacion['delta_y_real']}\n"
            f"Diferencia absoluta: {propagacion['diferencia']}\n\n"
            "La aproximación mediante derivada es de primer orden y funciona mejor "
            "para perturbaciones pequeñas.",
        )

        pagina_texto(
            pdf,
            "Interpretación e instrucciones",
            "La bisección reduce el intervalo a la mitad en cada iteración y su cota "
            "Eb permite controlar el error absoluto. Un cambio de signo sin continuidad, "
            "como 1/x en [-1,1], no garantiza una raíz.\n\n"
            "Los módulos de sistemas, vectores, matrices, determinantes y LU se mantienen "
            "en la entrega integrada y se comprueban mediante --pruebas.\n\n"
            "Instalación:\n"
            "python -m pip install -r requirements.txt\n\n"
            "Ejecución:\n"
            "python main.py\n"
            "python main.py --consola\n"
            "python main.py --pruebas\n\n"
            "Librerías: NumPy, SciPy, SymPy y Matplotlib.",
        )
    print(RUTA)


if __name__ == "__main__":
    main()
