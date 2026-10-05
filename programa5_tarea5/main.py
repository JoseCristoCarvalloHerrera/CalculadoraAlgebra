# -*- coding: utf-8 -*-
"""
Calculadora de Álgebra Lineal - Programa 5 - Grupo #2.

Punto de entrada del proyecto integrador. Abre el menú principal en
ventana (Tkinter) o en consola, y desde ahí se llega a los cuatro
módulos: sistemas de ecuaciones, vectores e independencia lineal,
álgebra de matrices con determinantes e inversa, y determinantes.

Temas de clase: Sesiones 1 a 11 de Álgebra Lineal (MTM0120).

Elaborado por el Grupo #2: Marian Alejandra Guillén Castillo,
Chelsea Yosmara Quintanilla Blandón, José Cristo Carvallo Herrera y
Gabriela Suyen Espinoza Rodríguez.

Modos de ejecución:
    python main.py              abre la ventana
    python main.py --consola    abre el menú de texto
    python main.py --pruebas    ejecuta las comprobaciones automáticas

Restricción cumplida: solo Python estándar (fractions, tkinter).
No se usan NumPy, SciPy ni funciones de álgebra lineal de math.
"""

import sys
import tkinter as tk
from tkinter import font as tkfont

from fractions import Fraction

from modulos import (
    FONDO, TARJETA, TEXTO, TEXTO_SUAVE, ACENTO, ACENTO_HOVER,
    LETRA_MONO, a_numero, formato, LOGO_PRINCIPAL,
)
from modulos.modulo_sistemas import (
    CalculadoraApp, resolver_sistema, escalonar, es_escalonada,
)
from modulos.modulo_vectores import (
    VectoresApp, sumar_vectores, restar_vectores, escalar_por_vector,
    es_combinacion_lineal, son_linealmente_independientes,
    relacion_de_dependencia, analizar_independencia,
    matriz_por_vector, vectores_iguales,
    verificar_aditividad_matriz_vector, verificar_homogeneidad_matriz_vector,
    _formato_suma_lineal, _expansion_por_columnas,
)
from modulos.modulo_matrices import (
    MatricesOpsApp, sumar_matrices, restar_matrices, escalar_por_matriz,
    multiplicar_matrices, resolver_ecuacion_matricial, transponer_matriz,
    inversa_gauss_jordan, inversa_por_adjunta, matriz_adjunta,
    comprobar_inversa, verificar_propiedad_inversa, PROPIEDADES_INVERSA,
)
from modulos.modulo_determinantes import (
    determinante, es_invertible, determinante_sarrus, determinante_por_reduccion,
)
from modulos import mostrar_cabecera, limpiar_pantalla, pausa, preguntar, SalirDeLaConsola
from modulos import modulo_sistemas, modulo_vectores, modulo_matrices, modulo_determinantes
from teoremas.resumen_teoremas import mostrar_teoremas


class MenuPrincipal:
    """Pantalla inicial del sistema para elegir el módulo."""
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Calculadora de Álgebra Lineal - Proyecto UAM")
        self.raiz.configure(bg=FONDO)
       
        # La ventana se adapta a la pantalla del equipo: pide el tamaño
        # cómodo, pero nunca más de lo que cabe. Con un tamaño fijo pequeño
        # la matriz queda cortada y había que desplazarse para verla.
        ancho = min(1300, self.raiz.winfo_screenwidth() - 80)
        alto = min(840, self.raiz.winfo_screenheight() - 120)
        self.raiz.geometry(f"{max(1120, ancho)}x{max(700, alto)}")
        self.raiz.minsize(1120, 700)
        self._centrar_ventana()
       
        self.frame_menu = tk.Frame(self.raiz, bg=FONDO)
        self.frame_menu.pack(fill="both", expand=True)
       
        tk.Label(self.frame_menu, text="¡Bienvenido a la mejor Calculadora!", font=("Montserrat", 26, "bold"), bg=FONDO, fg=TEXTO).pack(pady=(120, 10))
        tk.Label(self.frame_menu, text="Proyecto de Álgebra Lineal", font=("Montserrat", 16), bg=FONDO, fg=TEXTO_SUAVE).pack(pady=(0, 40))
        tk.Label(self.frame_menu, text="Selecciona el módulo en el que quieres trabajar:", font=("Montserrat", 13), bg=FONDO, fg=TEXTO).pack(pady=(0, 20))
       
        btn_matrices = tk.Button(self.frame_menu, text="Ecuaciones Matriciales (Ax = b)", font=("Montserrat", 13, "bold"),
                                 bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                 activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_calculadora)
        btn_matrices.pack(pady=10)

        btn_vectores = tk.Button(self.frame_menu, text="Vectores e Independencia Lineal", font=("Montserrat", 13, "bold"),
                                 bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                 activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_vectores)
        btn_vectores.pack(pady=10)

        btn_matriz_ops = tk.Button(self.frame_menu, text="Operaciones Matriciales", font=("Montserrat", 13, "bold"),
                                   bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                   activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_matrices_ops)
        btn_matriz_ops.pack(pady=10)

        btn_determinantes = tk.Button(self.frame_menu, text="Determinantes y Propiedades", font=("Montserrat", 13, "bold"),
                                      bg=ACENTO, fg=FONDO, width=32, pady=15, relief="flat", cursor="hand2",
                                      activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_determinantes)
        btn_determinantes.pack(pady=10)


        tk.Label(self.frame_menu, text="Desarrollado por Grupo 2 • Universidad Americana (UAM)", font=("Montserrat", 10), bg=FONDO, fg=TEXTO_SUAVE).pack(side="bottom", pady=40)


    def abrir_calculadora(self):
        self.frame_menu.pack_forget()
        CalculadoraApp(self.raiz, callback_volver=self.mostrar_menu)
       
    def abrir_vectores(self):
        self.frame_menu.pack_forget()
        VectoresApp(self.raiz, callback_volver=self.mostrar_menu)

    def abrir_matrices_ops(self):
        self.frame_menu.pack_forget()
        MatricesOpsApp(self.raiz, callback_volver=self.mostrar_menu)

    def abrir_determinantes(self):
        """El Módulo 4 se entrega con su motor de cálculo y su resumen de
        teoremas; la pantalla completa se construye en el Programa 5."""
        mostrar_teoremas(self.raiz, "determinantes",
                         "Módulo 4: Determinantes y Propiedades")

    def mostrar_menu(self):
        for widget in self.raiz.winfo_children():
            widget.destroy()
        self.__init__(self.raiz)


    def _centrar_ventana(self):
        self.raiz.update_idletasks()
        ancho = self.raiz.winfo_width()
        alto = self.raiz.winfo_height()
        x = max(0, (self.raiz.winfo_screenwidth() - ancho) // 2)
        y = max(0, (self.raiz.winfo_screenheight() - alto) // 2)
        self.raiz.geometry(f"+{x}+{y}")





# BLOQUE 7: PRUEBAS AUTOMÁTICAS DEL ALGORITMO
# Estos son los casos de prueba internos. Nos sirven para asegurar
# que ninguna actualización que hagamos dañe la matemática del programa.
# Validan sistemas Ax=b, operaciones vectoriales y operaciones
# matriciales, y corren por detrás en la consola.
# =====================================================================


def ejecutar_pruebas():
    """Ejecuta los sistemas predefinidos y verifica que el algoritmo funciona."""
    pruebas = [
        ("Caso 1: solución única", [[1, 1, 1], [2, -1, 1], [1, 2, -1]], [6, 3, 2], "Consistente Determinado", ["1", "2", "3"]),
        ("Caso 2: infinitas", [[1, 1, 1], [2, 2, 2]], [1, 2], "Consistente Indeterminado", None),
        ("Caso 3: inconsistente", [[1, 1], [1, 1]], [1, 3], "Inconsistente", None),
        ("Clase Lay", [[1, -2, 1], [0, 2, -8], [-4, 5, 9]], [0, 8, -9], "Consistente Determinado", ["29", "16", "3"]),
        ("Actividad 1", [[2, 3, 1], [5, 3, 4], [1, 1, -1]], [1, 2, 1], "Consistente Determinado", ["2/3", "0", "-1/3"]),
        ("Inconsistente Clase", [[0, 1, -4], [2, -3, 2], [5, -8, 7]], [8, 1, 1], "Inconsistente", None),
        ("Matriz 5x5", [[1, 2, 0, 1, 1], [0, 1, 1, 0, 0], [0, 0, 1, 1, -1], [0, 0, 0, 1, 2], [0, 0, 0, 0, 1]], [4, 2, 3, 5, 1], "Consistente Determinado", ["-2", "1", "1", "3", "1"]),
        ("Homogéneo", [[1, 1, 1], [2, -1, 0]], [0, 0], "Consistente Indeterminado", None),
        ("Ceros", [[0, 0], [0, 0]], [0, 0], "Consistente Indeterminado", None),
        ("Imposible", [[0]], [7], "Inconsistente", None),
        ("Intercambio necesario", [[0, 1], [1, 0]], [2, 3], "Consistente Determinado", ["3", "2"]),
        ("Más ecuaciones", [[1, 0], [0, 1], [1, 1]], [1, 2, 3], "Consistente Determinado", ["1", "2"]),
        ("Más ecuaciones, incompatible", [[1, 0], [0, 1], [1, 1]], [1, 2, 4], "Inconsistente", None),
        ("Fracciones", [["1/2", "1/3"], ["1/4", "1/5"]], [1, 1], "Consistente Determinado", ["-8", "15"]),
        ("Más incógnitas", [[1, 2, 3]], [6], "Consistente Indeterminado", None),
    ]


    fallos = 0
    print("=" * 64)
    print("INICIANDO PRUEBAS AUTOMÁTICAS DEL ALGORITMO")
    print("=" * 64)


    for nombre, A, b, clasificacion_esperada, solucion_esperada in pruebas:
        A = [[a_numero(str(valor)) for valor in fila] for fila in A]
        b = [a_numero(str(valor)) for valor in b]
        resultado = resolver_sistema(len(A), len(A[0]), A, b)


        problemas = []
        if resultado["clasificacion"] != clasificacion_esperada:
            problemas.append(f"Clasificó como {resultado['clasificacion']} pero se esperaba {clasificacion_esperada}")
        if solucion_esperada is not None:
            obtenida = [formato(valor) for valor in resultado["solucion"]]
            if obtenida != solucion_esperada:
                problemas.append(f"Solución {obtenida} en vez de {solucion_esperada}")
       
        correcta, motivo = es_escalonada(resultado["escalonada"])
        if not correcta:
            problemas.append(f"Fallo al escalonar: {motivo}")
       
        if "FALLO" in resultado["verificacion"]:
            problemas.append("La verificación de la solución falló")


        if problemas:
            fallos += 1
            print(f"[FALLA] {nombre}")
            for p in problemas: print(f"         - {p}")
        else:
            print(f"[  OK  ] {nombre}")


    # =================================================================
    # PRUEBAS DEL MÓDULO DE VECTORES
    # =================================================================
    print("--------------------------------")
    print("PRUEBAS DEL MÓDULO DE VECTORES")
    print("--------------------------------")

    def probar(nombre, ok, detalle=""):
        nonlocal fallos
        if not ok:
            fallos += 1
            print(f"[FALLA] {nombre}   {detalle}")
        else:
            print(f"[  OK  ] {nombre}")

    def fr(valor):
        return a_numero(str(valor))

    # Combinación lineal única: ¿b=(7,4,-3) es combinación de a1 y a2?
    a1 = [fr(1), fr(-2), fr(-5)]
    a2 = [fr(2), fr(5), fr(6)]
    b5 = [fr(7), fr(4), fr(-3)]
    es_cl, pesos, res5 = es_combinacion_lineal(b5, [a1, a2])
    probar("Combinación lineal única", es_cl and pesos == [fr(3), fr(2)],
           f"pesos={pesos}")
    probar("Expresión b=3·a1+2·a2",
           _formato_suma_lineal(pesos, "v") == "3·v\u2081 + 2·v\u2082",
           f"expr={_formato_suma_lineal(pesos, 'v')}")

    # Independientes (RREF = identidad)
    v1 = [fr(1), fr(-2), fr(3)]
    v2 = [fr(2), fr(-2), fr(0)]
    v3 = [fr(0), fr(1), fr(7)]
    ind_e1, res_e1 = son_linealmente_independientes([v1, v2, v3])
    probar("Independientes (RREF = identidad)", ind_e1
           and len(res_e1["variables_libres"]) == 0)

    # Dependientes: x3 libre, relación 2v1+3v2-v3=0
    w1 = [fr(1), fr(-3), fr(0)]
    w2 = [fr(3), fr(0), fr(4)]
    w3 = [fr(11), fr(-6), fr(12)]
    ind_e2, res_e2 = son_linealmente_independientes([w1, w2, w3])
    rels = relacion_de_dependencia([w1, w2, w3])
    probar("Dependientes (x3 libre)", (not ind_e2)
           and res_e2["variables_libres"] == [2])
    probar("Relación dependencia 2v1+3v2-v3=0",
           len(rels) == 1 and rels[0] == [fr(2), fr(3), fr(-1)],
           f"rels={rels}")

    # Dependientes: columnas homogéneas, x3 libre
    p1 = [fr(1), fr(0), fr(0)]
    p2 = [fr(0), fr(1), fr(0)]
    p3 = [fr(2), fr(3), fr(0)]
    ind_p8, res_p8 = son_linealmente_independientes([p1, p2, p3])
    rels_p8 = relacion_de_dependencia([p1, p2, p3])
    probar("Columnas homogéneas dependientes", (not ind_p8)
           and res_p8["variables_libres"] == [2])
    probar("Columnas homogéneas relación correcta",
           len(rels_p8) == 1 and rels_p8[0] == [fr(2), fr(3), fr(-1)],
           f"rels={rels_p8}")

    # Producto matriz-vector A·x (regla fila-vector)
    Aprod = [[fr(1), fr(2), fr(3)], [fr(4), fr(5), fr(6)]]
    xprod = [fr(1), fr(2), fr(3)]
    bprod = matriz_por_vector(Aprod, xprod)
    probar("Producto A·x (14, 32)", bprod == [fr(14), fr(32)], f"b={bprod}")

    # Validación de dimensiones incompatibles en A·x
    try:
        matriz_por_vector([[fr(1), fr(2)]], [fr(1)])
        probar("A·x dimensiones incompatibles", False, "No lanzó ValueError")
    except ValueError:
        probar("A·x dimensiones incompatibles", True)

# Verificación de la propiedad distributiva A(u+v)=Au+Av.
    A_prop = [[fr("1/2"), fr("1/3")],
              [fr("-1/3"), fr("1/2")]]
    u_prop = [fr(1), fr(0)]
    v_prop = [fr(0), fr(1)]
    aditividad = verificar_aditividad_matriz_vector(A_prop, u_prop, v_prop)
    probar("Aditividad: A(u+v)=Au+Av",
           aditividad["se_cumple"]
           and aditividad["izquierda"] == [fr("5/6"), fr("1/6")]
           and aditividad["derecha"] == aditividad["izquierda"])

    # Verificación de homogeneidad con un escalar distinto de 0 y 1.
    homogeneidad = verificar_homogeneidad_matriz_vector(
        A_prop, fr(-2), u_prop)
    probar("Homogeneidad: A(cu)=c(Au)",
           homogeneidad["se_cumple"]
           and homogeneidad["izquierda"] == [fr(-1), fr("2/3")]
           and homogeneidad["derecha"] == homogeneidad["izquierda"])

    # Producto matriz-vector 3×3 con fracciones y vista por columnas.
    A_rect = [[fr("1/2"), fr(0), fr("1/3")],
              [fr(0), fr("1/2"), fr("1/3")],
              [fr("1/3"), fr("1/3"), fr(0)]]
    x_vector = [fr(1), fr(1), fr(1)]
    Ax_vector = matriz_por_vector(A_rect, x_vector)
    probar("Producto A·x con fracciones y combinación de columnas",
           Ax_vector == [fr("5/6"), fr("5/6"), fr("2/3")]
           and _formato_suma_lineal(x_vector, "a")
           == "a₁ + a₂ + a₃")

    # Expansión explícita por columnas (escalares y sumandos vectoriales).
    columnas_rect = [[fila[j] for fila in A_rect] for j in range(3)]
    lineas_exp = _expansion_por_columnas(x_vector, columnas_rect, "a", Ax_vector)
    probar("Expansión explícita por columnas",
           lineas_exp[0] == "a₁ = ( 1/2,  0,  1/3 )"
           and lineas_exp[2] == "a₃ = ( 1/3,  1/3,  0 )"
           and lineas_exp[3] == "1·a₁ + 1·a₂ + 1·a₃ = ( 1/2,  0,  1/3 )"
           " + ( 0,  1/2,  1/3 ) + ( 1/3,  1/3,  0 ) = ( 5/6,  5/6,  2/3 )",
           f"lineas={lineas_exp}")

    # Las fracciones se comparan exactamente; float tiene resguardo de tolerancia.
    probar("Comparación exacta de fracciones",
           vectores_iguales([fr("1/3") + fr("2/3")], [fr(1)]))
    probar("Tolerancia para float externo",
           vectores_iguales([0.1 + 0.2], [0.3]))

    try:
        verificar_aditividad_matriz_vector([[fr(1), fr(2)]], [fr(1)], [fr(1)])
        probar("Validación de dimensiones en propiedad", False,
               "No lanzó ValueError")
    except ValueError:
        probar("Validación de dimensiones en propiedad", True)

    # Suma / resta / escalar de vectores
    u = [fr(1), fr(2), fr(3)]
    vv = [fr(4), fr(5), fr(6)]
    probar("Suma de vectores", sumar_vectores(u, vv) == [fr(5), fr(7), fr(9)])
    probar("Resta de vectores", restar_vectores(u, vv) == [fr(-3), fr(-3), fr(-3)])
    probar("Escalar por vector", escalar_por_vector(fr(-2), u) == [fr(-2), fr(-4), fr(-6)])


    # =================================================================
    # PRUEBAS DEL MÓDULO DE OPERACIONES MATRICIALES
    # =================================================================
    print("--------------------------------")
    print("PRUEBAS DE OPERACIONES MATRICIALES")
    print("--------------------------------")

    # Suma / resta / escalar de matrices
    A1 = [[fr(1), fr(2)], [fr(3), fr(4)]]
    B1 = [[fr(5), fr(6)], [fr(7), fr(8)]]
    probar("Suma 2x2", sumar_matrices(A1, B1) == [[fr(6), fr(8)], [fr(10), fr(12)]])
    probar("Resta 2x2", restar_matrices(B1, A1) == [[fr(4), fr(4)], [fr(4), fr(4)]])
    probar("Escalar por matriz",
           escalar_por_matriz(fr(3), A1) == [[fr(3), fr(6)], [fr(9), fr(12)]])

    # Multiplicación de matrices (bucles anidados)
    probar("Producto 2x2", multiplicar_matrices(A1, B1) == [[fr(19), fr(22)], [fr(43), fr(50)]])
    A3 = [[fr(1), fr(2), fr(3)], [fr(4), fr(5), fr(6)]]
    B3 = [[fr(7), fr(8)], [fr(9), fr(10)], [fr(11), fr(12)]]
    probar("Producto 2x3 * 3x2",
           multiplicar_matrices(A3, B3) == [[fr(58), fr(64)], [fr(139), fr(154)]])
    probar("Producto 1x3 * 3x1",
           multiplicar_matrices([[fr(1), fr(2), fr(3)]], [[fr(4)], [fr(5)], [fr(6)]])
           == [[fr(32)]])

    # Dimensiones incompatibles
    try:
        sumar_matrices([[fr(1), fr(2)]], [[fr(1), fr(2), fr(3)]])
        probar("Suma dimensiones incompatibles", False, "No lanzó ValueError")
    except ValueError:
        probar("Suma dimensiones incompatibles", True)
    try:
        multiplicar_matrices([[fr(1), fr(2)]], [[fr(1), fr(2), fr(3)]])
        probar("Producto dimensiones incompatibles", False, "No lanzó ValueError")
    except ValueError:
        probar("Producto dimensiones incompatibles", True)

    # Ecuación matricial x₁v₁ + x₂v₂ + … + xₖvₖ = y (combinación de matrices)
    # Caso del ejercicio de la diapositiva: v1=(3,-2), v2=(7,3), v3=(-2,1),
    # y=(0,0). Tres vectores en R^2 => dependientes (infinitas formas).
    ec1, p1c, r1c = resolver_ecuacion_matricial(
        [[fr(0)], [fr(0)]],
        [[[fr(3)], [fr(-2)]], [[fr(7)], [fr(3)]], [[fr(-2)], [fr(1)]]])
    probar("Ecuación diapositiva (dependiente, infinitas)",
           ec1 and r1c["clasificacion"] == "Consistente Indeterminado"
           and r1c["variables_libres"] != [],
           f"clase={r1c['clasificacion']}")

    # Caso determinado: v1=(1,0), v2=(0,1), y=(3,-2)  ->  x1=3, x2=-2
    ec2, p2c, r2c = resolver_ecuacion_matricial(
        [[fr(3)], [fr(-2)]],
        [[[fr(1)], [fr(0)]], [[fr(0)], [fr(1)]]])
    probar("Ecuación 2x1 determinada (x1=3, x2=-2)",
           ec2 and p2c == [fr(3), fr(-2)] and r2c["clasificacion"] == "Consistente Determinado",
           f"pesos={p2c}")

    # Caso sin solución: v1=(1,2), v2=(2,4), y=(1,0)  -> inconsistente
    try:
        ec3, _, r3c = resolver_ecuacion_matricial(
            [[fr(1)], [fr(0)]],
            [[[fr(1)], [fr(2)]], [[fr(2)], [fr(4)]]])
        probar("Ecuación sin solución", (not ec3) and r3c["clasificacion"] == "Inconsistente")
    except ValueError as e:
        probar("Ecuación sin solución", False, str(e))

    # Caso con matrices 2x2: x1·[[1,0],[0,1]] + x2·[[0,1],[1,0]] = [[2,3],[3,2]]
    ec4, p4c, r4c = resolver_ecuacion_matricial(
        [[fr(2), fr(3)], [fr(3), fr(2)]],
        [[[fr(1), fr(0)], [fr(0), fr(1)]], [[fr(0), fr(1)], [fr(1), fr(0)]]])
    probar("Ecuación con matrices 2x2 (x1=2, x2=3)",
           ec4 and p4c == [fr(2), fr(3)] and r4c["clasificacion"] == "Consistente Determinado",
           f"pesos={p4c}")

    # Dimensiones distintas dentro de la ecuación matricial
    try:
        resolver_ecuacion_matricial(
            [[fr(2)], [fr(3)]],
            [[[fr(1), fr(1)]], [[fr(2), fr(2)]]])
        probar("Ecuación dimensiones distintas", False, "No lanzó ValueError")
    except ValueError:
        probar("Ecuación dimensiones distintas", True)

    # --- Transpuesta de una matriz ---
    A_t = [[fr(1), fr(2), fr(3)], [fr(4), fr(5), fr(6)]]
    T = transponer_matriz(A_t)
    probar("Transpuesta 2x3 -> 3x2",
           T == [[fr(1), fr(4)], [fr(2), fr(5)], [fr(3), fr(6)]], f"obtuvo {T}")
    probar("(A^T)^T = A",
           transponer_matriz(T) == A_t)
    B_t = [[fr(0), fr(1), fr(1)], [fr(2), fr(0), fr(3)]]
    probar("(A + B)^T = A^T + B^T",
           transponer_matriz(sumar_matrices(A_t, B_t))
           == sumar_matrices(transponer_matriz(A_t), transponer_matriz(B_t)))
    probar("(rA)^T = r·A^T",
           transponer_matriz(escalar_por_matriz(fr(3), A_t))
           == escalar_por_matriz(fr(3), transponer_matriz(A_t)))
    C_t = [[fr(1), fr(0)], [fr(2), fr(-1)], [fr(0), fr(4)]]
    probar("(AB)^T = B^T·A^T  (orden invertido)",
           transponer_matriz(multiplicar_matrices(A_t, C_t))
           == multiplicar_matrices(transponer_matriz(C_t), transponer_matriz(A_t)))
    probar("det(A^T) = det(A)",
           determinante([[fr(3), fr(8)], [fr(4), fr(6)]])
           == determinante(transponer_matriz([[fr(3), fr(8)], [fr(4), fr(6)]])))



    # -----------------------------------------------------------------
    # PRUEBAS DEL PROGRAMA 4: INDEPENDENCIA LINEAL Y DETERMINANTES
    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # PRUEBAS DEL PROGRAMA 5: DETERMINANTES E INVERSA
    # -----------------------------------------------------------------
    print("--------------------------------")
    print("PRUEBAS DE INVERSA Y DETERMINANTE (PROGRAMA 5)")
    print("--------------------------------")

    A_inv = [[fr(1), fr(2), fr(3)], [fr(0), fr(1), fr(4)], [fr(5), fr(6), fr(0)]]
    esperada = [[fr(-24), fr(18), fr(5)], [fr(20), fr(-15), fr(-4)],
                [fr(-5), fr(4), fr(1)]]
    probar("Inversa por Gauss-Jordan 3x3",
           inversa_gauss_jordan(A_inv) == esperada)
    probar("Inversa por matriz adjunta 3x3",
           inversa_por_adjunta(A_inv) == esperada)
    probar("Los dos métodos dan la misma inversa",
           inversa_gauss_jordan(A_inv) == inversa_por_adjunta(A_inv))
    _, cumple_identidad = comprobar_inversa(A_inv, inversa_gauss_jordan(A_inv))
    probar("Comprobación A·A⁻¹ = I", cumple_identidad)

    A2 = [[fr(1), fr(2)], [fr(3), fr(4)]]
    probar("adj(A) de una 2x2",
           matriz_adjunta(A2) == [[fr(4), fr(-2)], [fr(-3), fr(1)]])
    probar("Inversa 2x2 con fracciones exactas",
           inversa_gauss_jordan(A2) == [[fr(-2), fr(1)],
                                        [fr("3/2"), fr("-1/2")]])

    singular = [[fr(1), fr(2), fr(3)], [fr(4), fr(5), fr(6)], [fr(7), fr(8), fr(9)]]
    for nombre, funcion in (("Gauss-Jordan", inversa_gauss_jordan),
                            ("adjunta", inversa_por_adjunta)):
        try:
            funcion(singular)
            probar("Matriz singular avisa (" + nombre + ")", False, "No lanzó ValueError")
        except ValueError:
            probar("Matriz singular avisa (" + nombre + ")", True)

    A_det = [[fr(1), fr(3), fr(-3)], [fr(2), fr(0), fr(1)], [fr(-1), fr(4), fr(-2)]]
    probar("Sarrus coincide con cofactores",
           determinante_sarrus(A_det) == determinante(A_det) == fr(-19))
    probar("Reducción coincide con cofactores (3x3)",
           determinante_por_reduccion(A_det)[0] == fr(-19))
    A4 = [[fr(2), fr(1), fr(0), fr(3)], [fr(3), fr(0), fr(-2), fr(0)],
          [fr(4), fr(-1), fr(1), fr(2)], [fr(5), fr(2), fr(0), fr(1)]]
    probar("Reducción coincide con cofactores (4x4)",
           determinante_por_reduccion(A4)[0] == determinante(A4) == fr(85))
    try:
        determinante_sarrus(A2)
        probar("Sarrus rechaza las que no son 3x3", False, "No lanzó ValueError")
    except ValueError:
        probar("Sarrus rechaza las que no son 3x3", True)

    # Las seis propiedades de las Sesiones 10 y 11, con A y B del enunciado
    B_prop = [[fr(0), fr(1)], [fr(1), fr(1)]]
    for indice, nombre in enumerate(PROPIEDADES_INVERSA):
        resultado = verificar_propiedad_inversa(indice, A2, B_prop,
                                                fila_i=1, fila_j=0, k=fr(3))
        probar("Propiedad " + str(indice + 1) + ": " + nombre,
               resultado["se_cumple"])

    print("--------------------------------")
    print("PRUEBAS DE INDEPENDENCIA LINEAL (PROGRAMA 4)")
    print("--------------------------------")

    casos_li = [
        # (nombre, vectores, esperado_independientes, pivotes, libres)
        ("Base canónica de R^3 (L.I.)",
         [[1, 0, 0], [0, 1, 0], [0, 0, 1]], True, 3, 0),
        ("Uno es múltiplo de otro (L.D.)",
         [[1, 2, 3], [2, 4, 6], [1, 1, 1]], False, 2, 1),
        ("Dos vectores no paralelos en R^2 (L.I.)",
         [[1, 0], [1, 1]], True, 2, 0),
        ("Tres vectores en R^2, siempre L.D.",
         [[1, 0], [0, 1], [3, 5]], False, 2, 1),
        ("Incluye el vector cero (L.D.)",
         [[1, 2], [0, 0]], False, 1, 1),
    ]
    for nombre, vs, esperado, piv, libres in casos_li:
        r = analizar_independencia(vs)
        ok = (r["independientes"] == esperado
              and r["cantidad_pivotes"] == piv
              and r["cantidad_libres"] == libres)
        if ok:
            print(f"[  OK  ] {nombre}")
        else:
            fallos += 1
            print(f"[ FALLO ] {nombre}: obtuvo pivotes={r['cantidad_pivotes']}, "
                  f"libres={r['cantidad_libres']}, L.I.={r['independientes']}")

    # La relación de dependencia debe anular realmente la combinación
    vs = [[1, 2, 3], [2, 4, 6], [1, 1, 1]]
    rel = relacion_de_dependencia(vs)
    if rel:
        suma = [sum(rel[0][j] * vs[j][i] for j in range(len(vs)))
                for i in range(len(vs[0]))]
        if all(valor == 0 for valor in suma):
            print("[  OK  ] La relación de dependencia anula la combinación")
        else:
            fallos += 1
            print(f"[ FALLO ] La relación no da cero: {suma}")
    else:
        fallos += 1
        print("[ FALLO ] No encontró relación de dependencia en un caso L.D.")

    print("--------------------------------")
    print("PRUEBAS DE DETERMINANTES")
    print("--------------------------------")
    casos_det = [
        ("Determinante 2x2", [[3, 8], [4, 6]], -14),
        ("Determinante 3x3", [[6, 1, 1], [4, -2, 5], [2, 8, 7]], -306),
        ("Identidad 3x3 vale 1", [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1),
        ("Triangular: producto de la diagonal",
         [[2, 7, 1], [0, 5, -3], [0, 0, 4]], 40),
        ("Matriz singular (columnas L.D.)", [[1, 2], [2, 4]], 0),
    ]
    for nombre, M, esperado in casos_det:
        obtenido = determinante(M)
        if obtenido == esperado:
            print(f"[  OK  ] {nombre}")
        else:
            fallos += 1
            print(f"[ FALLO ] {nombre}: esperaba {esperado}, obtuvo {obtenido}")

    # Coherencia entre los dos módulos: det = 0  <->  columnas L.D.
    M = [[1, 2], [2, 4]]
    columnas = [[M[i][j] for i in range(2)] for j in range(2)]
    if (determinante(M) == 0) == (not analizar_independencia(columnas)["independientes"]):
        print("[  OK  ] det(A)=0 coincide con columnas linealmente dependientes")
    else:
        fallos += 1
        print("[ FALLO ] El determinante no coincide con la independencia de columnas")

    print("=" * 64)
    if fallos == 0:
        print("¡Excelente! Todas las comprobaciones pasaron correctamente.")
    else:
        print(f"Alerta: Se encontraron {fallos} fallos matemáticos.")
    print("=" * 64)
    return fallos


# =====================================================================
# PUNTO DE ENTRADA
# Solo le decimos a Python que abra
# la ventana del menú principal y mantenga la aplicación ejecutándose.
# =====================================================================

# =====================================================================
# MENÚ PRINCIPAL EN MODO CONSOLA (CLI)
#
# La Tarea 4 pide que cada módulo tenga su cabecera con logotipo ASCII
# y un menú interno con la opción "0. Ver Teoremas Clave del Módulo".
# Eso se cumple aquí: la calculadora se puede usar de dos maneras,
#   - con la interfaz gráfica (Tkinter), que es la forma habitual, y
#   - en modo consola, que es esta, con los logotipos y los menús de
#     texto de cada módulo.
# Las dos formas usan EXACTAMENTE el mismo motor matemático; lo único
# que cambia es cómo se piden los datos y cómo se muestran.
# =====================================================================

def menu_consola():
    """Menú principal de la calculadora en modo consola."""
    while True:
        mostrar_cabecera(LOGO_PRINCIPAL)
        print("   Seleccioná el módulo en el que querés trabajar:")
        print()
        print("   1. Sistemas de Ecuaciones Lineales (SEL)")
        print("   2. Vectores e Independencia Lineal")
        print("   3. Álgebra de Matrices")
        print("   4. Determinantes y Propiedades")
        print()
        print("   8. Ejecutar las pruebas automáticas")
        print("   9. Salir")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            limpiar_pantalla()
            print("   Hasta luego. Grupo 2 - Universidad Americana (UAM)")
            print()
            return
        elif opcion == "1":
            modulo_sistemas.menu_consola()
        elif opcion == "2":
            modulo_vectores.menu_consola()
        elif opcion == "3":
            modulo_matrices.menu_consola()
        elif opcion == "4":
            modulo_determinantes.menu_consola()
        elif opcion == "8":
            limpiar_pantalla()
            ejecutar_pruebas()
            pausa()
        else:
            print("   Opción no válida.")
            pausa()


# =====================================================================
# PUNTO DE ENTRADA
# =====================================================================
def main():
    """Arranca la calculadora.

    Sin argumentos abre la interfaz gráfica. Con --consola abre el modo
    de texto con los logotipos ASCII y los menús internos de cada
    módulo. Con --pruebas corre las comprobaciones automáticas.
    """
    if "--pruebas" in sys.argv:
        sys.exit(1 if ejecutar_pruebas() else 0)

    if "--consola" in sys.argv or "--cli" in sys.argv:
        try:
            menu_consola()
        except SalirDeLaConsola:
            print("\n\n   Entrada interrumpida. Cerrando la calculadora.\n")
        return

    raiz = tk.Tk()
    MenuPrincipal(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
