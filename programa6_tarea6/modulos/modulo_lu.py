# -*- coding: utf-8 -*-
"""
Módulo 5 de la Calculadora de Álgebra Lineal: Factorización LU.

Obtiene la factorización A = L·U mediante operaciones elementales de
reemplazo de fila (Fᵢ ← Fᵢ − l·Fⱼ), donde L es una matriz triangular
inferior m×m con unos en la diagonal que guarda los multiplicadores de
eliminación y U es la forma escalonada de A (m×n). Con la factorización
verifica L·U = A y, para matrices cuadradas n×n, resuelve A·x = b en dos
etapas: sustitución hacia adelante (L·y = b) y hacia atrás (U·x = y).

Temas de clase: eliminación de Gauss (Sesión 5) y factorización de
matrices (Sesión 12). Reutiliza el motor de reducción por filas y el
producto matricial ya programados en la Calculadora.

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
    BOTON_SEC, BOTON_SEC_HOVER, CELDA_FONDO, LETRA_MONO, MAX_DIMENSION,
    a_numero, formato, formato_matriz, con_subindice,
    _validar_matriz, _leer_dimensiones, LOGO_LU,
    mostrar_cabecera, limpiar_pantalla, leer_entero, leer_matriz,
    leer_vector, mostrar_matriz, pausa, preguntar,
)
from modulos.modulo_sistemas import escalonar
from modulos.modulo_matrices import multiplicar_matrices
from modulos.modulo_determinantes import validar_cuadrada
from teoremas.resumen_teoremas import mostrar_teoremas, texto_teoremas


# El mensaje exacto que pide el enunciado cuando hace falta pivoteo.
MENSAJE_SIN_PERMUTACION = (
    "La matriz no admite Factorización LU sin permutación "
    "(requiere pivoteo parcial PA = LU)"
)


# =====================================================================
# BLOQUE 1: CÁLCULO DE LA FACTORIZACIÓN (funciones puras)
# =====================================================================

def factorizar_lu(A):
    """Factoriza A = L·U sin pivoteo y devuelve (L, U, pasos).

    Recibe la matriz A (m×n) como listas anidadas. Reduce A a su forma
    escalonada U aplicando únicamente operaciones de reemplazo de fila
    Fᵢ ← Fᵢ − l·Fⱼ y registra cada multiplicador l = a_eliminar/pivote en
    la posición (i, j) de L. L es triangular inferior m×m con unos en la
    diagonal. Si un pivote diagonal es cero y haría falta intercambiar
    filas, lanza ValueError con el mensaje de pivoteo parcial.
    """
    _validar_matriz(A, "A")
    filas, columnas = _leer_dimensiones(A)

    # U arranca como copia de A; L arranca como la identidad m×m.
    U = [[Fraction(valor) for valor in fila] for fila in A]
    L = [[Fraction(0)] * filas for _ in range(filas)]
    for i in range(filas):
        L[i][i] = Fraction(1)

    pasos = ["Matriz A original:"]
    pasos.extend(formato_matriz(A))
    pasos.append("")

    fila_pivote = 0
    for col in range(columnas):
        if fila_pivote >= filas:
            break

        pivote = U[fila_pivote][col]
        if pivote == 0:
            # Si hay un valor abajo en esta columna, habría que intercambiar
            # filas, y eso cambia la factorización salvo que se arrastre P.
            hay_valor_abajo = any(U[f][col] != 0
                                  for f in range(fila_pivote + 1, filas))
            if hay_valor_abajo:
                raise ValueError(MENSAJE_SIN_PERMUTACION)
            # Columna sin pivote: se salta y se sigue con la siguiente.
            continue

        # Generar ceros por debajo con reemplazo de fila.
        for f in range(fila_pivote + 1, filas):
            if U[f][col] != 0:
                multiplicador = U[f][col] / pivote
                # Se registra el multiplicador en L ANTES de alterar la fila
                # de U, porque ésa es justamente la entrada que se elimina.
                L[f][fila_pivote] = multiplicador
                U[f] = [U[f][c] - multiplicador * U[fila_pivote][c]
                        for c in range(columnas)]
                pasos.append(
                    "l(" + str(f + 1) + "," + str(fila_pivote + 1) + ") = "
                    + formato(multiplicador) + "   ->   F" + str(f + 1)
                    + " = F" + str(f + 1) + " - (" + formato(multiplicador)
                    + ")·F" + str(fila_pivote + 1))
                pasos.extend(formato_matriz(U))
                pasos.append("")

        fila_pivote += 1

    return L, U, pasos


def verificar_factorizacion(A, L, U):
    """Comprueba L·U = A multiplicando las dos matrices.

    Devuelve (producto, se_cumple), donde producto es L·U ya calculado
    (lista anidada) y se_cumple indica si coincide con A.
    """
    producto = multiplicar_matrices(L, U)
    se_cumple = producto == [[Fraction(valor) for valor in fila] for fila in A]
    return producto, se_cumple


def resolver_lu(A, b):
    """Resuelve A·x = b para A cuadrada usando su factorización LU.

    Recibe A (n×n) y b (n componentes). Halla y resolviendo L·y = b y luego
    x resolviendo U·x = y, ambos por reducción sobre la matriz aumentada.
    Devuelve un diccionario con L, U, y, x, los pasos de cada etapa, el
    producto A·x y si la solución satisface el sistema.
    """
    n = validar_cuadrada(A)
    if len(b) != n:
        raise ValueError("El vector b debe tener " + str(n)
                         + " componentes (una por fila de A).")

    L, U, pasos_factorizacion = factorizar_lu(A)

    # Si algún pivote de la diagonal de U es cero, A es singular (det = 0)
    # y el sistema no tiene solución única.
    for i in range(n):
        if U[i][i] == 0:
            raise ValueError("La matriz A es singular (un pivote de U es cero); "
                             "no tiene solución única por LU.")

    # Etapa 1: L·y = b, reduciendo la aumentada [L | b].
    aumentada_L = [[Fraction(L[i][j]) for j in range(n)]
                   + [Fraction(b[i])] for i in range(n)]
    pasos_adelante, _ = escalonar(aumentada_L, n)
    y = [aumentada_L[i][n] for i in range(n)]

    # Etapa 2: U·x = y, reduciendo la aumentada [U | y].
    aumentada_U = [[Fraction(U[i][j]) for j in range(n)]
                   + [y[i]] for i in range(n)]
    pasos_atras, _ = escalonar(aumentada_U, n)
    x = [aumentada_U[i][n] for i in range(n)]

    # Comprobación final: A·x debe reproducir el vector b.
    A_fraccion = [[Fraction(valor) for valor in fila] for fila in A]
    producto_ax = multiplicar_matrices(A_fraccion, [[x[i]] for i in range(n)])
    b_columna = [[Fraction(b[i])] for i in range(n)]
    return {
        "L": L, "U": U, "y": y, "x": x,
        "pasos_factorizacion": pasos_factorizacion,
        "pasos_adelante": pasos_adelante,
        "pasos_atras": pasos_atras,
        "producto_ax": [fila[0] for fila in producto_ax],
        "solucion_correcta": producto_ax == b_columna,
    }


def formato_vector(v):
    """Muestra un vector como una tupla de componentes entre paréntesis."""
    return "( " + ", ".join(formato(valor) for valor in v) + " )"


# =====================================================================
# BLOQUE 2: INTERFAZ GRÁFICA DEL MÓDULO (Tkinter)
# =====================================================================

class LUApp:
    """Pantalla del módulo de Factorización LU y solución de A·x = b."""

    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver

        self.var_filas = tk.StringVar(value="3")
        self.var_columnas = tk.StringVar(value="3")
        self.celdas_A = {}
        self.celdas_b = {}

        self.fuente_titulo = tkfont.Font(family="Montserrat", size=22, weight="bold")
        self.fuente_sub = tkfont.Font(family="Montserrat", size=11)
        self.fuente_body = tkfont.Font(family="Montserrat", size=11)
        self.fuente_encab = tkfont.Font(family="Montserrat", size=11, weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11)
        self.fuente_boton = tkfont.Font(family="Montserrat", size=11, weight="bold")

        self.marco_principal = tk.Frame(self.raiz, bg=FONDO)
        self.marco_principal.pack(fill="both", expand=True)

        self.lineas_resultado = []
        self.lineas_pasos = []
        self.mostrando_pasos = False

        self._construir_ui()
        self._construir_grids()

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
                 text="Módulo 5: Factorización LU y solución Ax = b",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO
                 ).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal,
                 text="A = L·U por reemplazo de filas, verificación L·U = A y "
                      "doble sustitución para resolver A·x = b.",
                 font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE
                 ).grid(row=2, column=0, columnspan=2, sticky="w", padx=34, pady=(0, 12))

        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)

        # ---- panel izquierdo (entrada) ----
        panel_izq = tk.Frame(self.marco_principal, bg=FONDO)
        panel_izq.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))
        self.frame_izq = panel_izq

        self._llenar_tarjeta_A(self.frame_izq)
        self._llenar_tarjeta_b(self.frame_izq)

        tk.Button(self.frame_izq, text="Factorizar y resolver",
                  font=self.fuente_boton, bg=ACENTO, fg=FONDO, relief="flat",
                  cursor="hand2", padx=12, pady=10, activebackground=ACENTO_HOVER,
                  activeforeground=FONDO, command=self._al_factorizar
                  ).pack(fill="x", pady=(4, 0))

        # ---- panel derecho (resultados) ----
        panel_der = tk.Frame(self.marco_principal, bg=FONDO)
        panel_der.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))
        tarjeta_res = self._crear_tarjeta(panel_der)
        tarjeta_res.pack(fill="both", expand=True)

        cab_res = tk.Frame(tarjeta_res, bg=TARJETA)
        cab_res.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cab_res, text="Resultado", font=self.fuente_encab,
                 bg=TARJETA, fg=TEXTO_SUAVE).pack(side="left")
        self.boton_procedimiento = tk.Button(
            cab_res, text="Ver procedimiento", font=self.fuente_body,
            bg=BOTON_SEC, fg=TEXTO, bd=0, relief="flat", cursor="hand2",
            padx=12, pady=4, activebackground=BOTON_SEC_HOVER,
            activeforeground=TEXTO, command=self._alternar_procedimiento)

        marco_texto = tk.Frame(tarjeta_res, bg=TARJETA)
        marco_texto.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        barra = ttk.Scrollbar(marco_texto)
        barra.pack(side="right", fill="y")
        self.texto_resultado = tk.Text(
            marco_texto, wrap="word", font=self.fuente_mono, bg=TARJETA,
            fg=TEXTO, relief="flat", bd=0, yscrollcommand=barra.set,
            highlightthickness=0)
        self.texto_resultado.pack(side="left", fill="both", expand=True)
        barra.configure(command=self.texto_resultado.yview)
        self.texto_resultado.insert(
            "1.0", "Ingresa la matriz A y el vector b, y presiona «Factorizar y resolver».")
        self.texto_resultado.configure(state="disabled")

    def _crear_tarjeta(self, padre):
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC,
                        highlightthickness=1, bd=0)

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
        tk.Label(cont, text="Matriz A", font=self.fuente_sub, bg=TARJETA,
                 fg=TEXTO, anchor="w").grid(row=0, column=0, columnspan=5,
                                            sticky="w", pady=(0, 8))
        tk.Label(cont, text="Filas", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_filas,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._reconstruir_entradas
                   ).grid(row=1, column=1, sticky="w", padx=(0, 16))
        tk.Label(cont, text="Columnas", font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 6))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_columnas,
                   font=self.fuente_body, width=4, justify="center", bg="#FFFFFF",
                   fg=TEXTO, relief="solid", bd=1, highlightthickness=0,
                   command=self._reconstruir_entradas
                   ).grid(row=1, column=3, sticky="w")

        def aplicar():
            self._leer_dimension(self.var_filas, 3)
            self._leer_dimension(self.var_columnas, 3)
            self._reconstruir_entradas()

        tk.Button(cont, text="✓", font=self.fuente_body, bg=ACENTO, fg=FONDO,
                  relief="flat", cursor="hand2", padx=6, pady=2,
                  activebackground=ACENTO_HOVER, activeforeground=FONDO,
                  command=aplicar
                  ).grid(row=1, column=4, sticky="w", padx=(12, 0))

        self.frame_A = tk.Frame(tarjeta, bg=TARJETA)
        self.frame_A.pack(fill="both", expand=True, padx=18, pady=(0, 8))

    def _llenar_tarjeta_b(self, padre):
        tarjeta = self._crear_tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 10))
        tk.Label(cont, text="Vector b (términos independientes)",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).pack(fill="x")
        tk.Label(cont, text="Una componente por fila de A. Se usa para resolver "
                            "A·x = b cuando A es cuadrada.",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 justify="left", wraplength=380, anchor="w").pack(fill="x", pady=(0, 6))
        self.frame_b = tk.Frame(cont, bg=TARJETA)
        self.frame_b.pack(anchor="w", pady=(2, 0))

    def _reconstruir_entradas(self):
        self._construir_grids()

    def _construir_grids(self):
        previos_A = {c: v.get() for c, v in self.celdas_A.items()}
        previos_b = {i: v.get() for i, v in self.celdas_b.items()}

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
                tk.Entry(self.frame_A, textvariable=var, font=self.fuente_mono,
                         width=6, justify="center", relief="solid", bd=1,
                         bg=CELDA_FONDO).grid(row=i + 1, column=j, padx=3, pady=2)

        for hijo in self.frame_b.winfo_children():
            hijo.destroy()
        self.celdas_b.clear()
        for i in range(m):
            var = tk.StringVar(value=previos_b.get(i, ""))
            self.celdas_b[i] = var
            tk.Entry(self.frame_b, textvariable=var, font=self.fuente_mono,
                     width=10, justify="center", relief="solid", bd=1,
                     bg=CELDA_FONDO).grid(row=i, column=0, pady=2)

    def _leer_matriz(self, celdas, m, n, nombre):
        matriz = []
        for i in range(m):
            fila = []
            for j in range(n):
                try:
                    fila.append(a_numero(celdas[(i, j)].get()))
                except ValueError:
                    raise ValueError("Revisa la matriz " + nombre + ", celda fila "
                                     + str(i + 1) + ", columna " + str(j + 1) + ".")
            matriz.append(fila)
        return matriz

    def _leer_b(self, m):
        b = []
        for i in range(m):
            try:
                b.append(a_numero(self.celdas_b[i].get()))
            except ValueError:
                raise ValueError("Revisa el vector b, componente " + str(i + 1) + ".")
        return b

    def _al_factorizar(self):
        try:
            self._construir_grids()
            m = self._leer_dimension(self.var_filas, 3)
            n = self._leer_dimension(self.var_columnas, 3)
            A = self._leer_matriz(self.celdas_A, m, n, "A")

            L, U, pasos = factorizar_lu(A)
            _, correcta = verificar_factorizacion(A, L, U)

            lineas = ["FACTORIZACIÓN A = L·U", ""]
            if correcta:
                lineas.append("La factorización es correcta (L · U == A).")
            else:
                lineas.append("¡Atención! L · U no coincide con A.")
            lineas += ["", "Matriz L:", *formato_matriz(L), "",
                       "Matriz U:", *formato_matriz(U)]

            pasos_completos = list(pasos)

            if m == n:
                b = self._leer_b(m)
                datos = resolver_lu(A, b)
                lineas += ["", "Vector intermedio y = " + formato_vector(datos["y"]),
                           "Vector solución   x = " + formato_vector(datos["x"]), ""]
                if datos["solucion_correcta"]:
                    lineas.append("Comprobación exitosa: A · x == b")
                else:
                    lineas.append("¡Atención! A · x no coincide con b")
                pasos_completos += ["", "--- SUSTITUCIÓN HACIA ADELANTE: L·y = b ---", ""]
                pasos_completos += datos["pasos_adelante"]
                pasos_completos += ["", "--- SUSTITUCIÓN HACIA ATRÁS: U·x = y ---", ""]
                pasos_completos += datos["pasos_atras"]
            else:
                lineas += ["", "A es " + str(m) + "×" + str(n)
                           + "; la solución por LU se resuelve solo para A cuadrada."]

            self._mostrar(lineas, pasos_completos)
        except ValueError as error:
            self._mostrar_error(str(error))

    def _mostrar(self, lineas, pasos):
        self.lineas_resultado = lineas
        self.lineas_pasos = pasos or []
        self.mostrando_pasos = False
        self.boton_procedimiento.configure(text="Ver procedimiento")
        if self.lineas_pasos:
            self.boton_procedimiento.pack(side="right")
        else:
            self.boton_procedimiento.pack_forget()
        self._render()

    def _render(self):
        texto = list(self.lineas_resultado)
        if self.mostrando_pasos and self.lineas_pasos:
            texto += ["", "=" * 46, "DESARROLLO PASO A PASO", "=" * 46, ""]
            texto += self.lineas_pasos
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.insert("1.0", "\n".join(texto))
        self.texto_resultado.configure(state="disabled")

    def _alternar_procedimiento(self):
        if not self.lineas_pasos:
            return
        self.mostrando_pasos = not self.mostrando_pasos
        self.boton_procedimiento.configure(
            text="Ocultar procedimiento" if self.mostrando_pasos
            else "Ver procedimiento")
        self._render()

    def _mostrar_error(self, mensaje):
        messagebox.showerror("Operación no válida", mensaje)

    def _ver_teoremas(self):
        mostrar_teoremas(self.raiz, "lu", "Módulo 5: Factorización LU")

    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()


# =====================================================================
# BLOQUE 3: MENÚ DE CONSOLA DEL MÓDULO 5 (MODO CLI)
# =====================================================================

def menu_consola():
    """Menú de texto del Módulo 5: Factorización LU y solución A·x = b."""
    while True:
        mostrar_cabecera(LOGO_LU)
        print("   0. Ver Teoremas Clave del Módulo")
        print("   1. Factorizar A = L·U y resolver A·x = b")
        print("   9. Volver al menú principal")
        print()
        opcion = preguntar("   Elegí una opción: ").strip()

        if opcion == "9":
            return
        elif opcion == "0":
            limpiar_pantalla()
            print(texto_teoremas("lu"))
            pausa()
        elif opcion == "1":
            _consola_lu()
        else:
            print("   Opción no válida.")
            pausa()


def _consola_lu():
    """Pide A y b, muestra la factorización LU y resuelve el sistema."""
    mostrar_cabecera(LOGO_LU)
    print("   FACTORIZACIÓN LU Y SOLUCIÓN A·x = b")
    print()
    try:
        m = leer_entero("   Número de filas de A (m) = ")
        n = leer_entero("   Número de columnas de A (n) = ")
        print()
        A = leer_matriz("A", m, n)
        print()
        b = leer_vector("b", m)

        L, U, _ = factorizar_lu(A)
        _, correcta = verificar_factorizacion(A, L, U)

        print()
        mostrar_matriz(L, titulo="   MATRIZ L (triangular inferior):")
        print()
        mostrar_matriz(U, titulo="   MATRIZ U (forma escalonada):")
        print()
        if correcta:
            print("   La factorización es correcta (L · U == A).")
        else:
            print("   ¡Atención! L · U no coincide con A.")

        if m == n:
            datos = resolver_lu(A, b)
            print()
            print("   Vector intermedio y = " + formato_vector(datos["y"]))
            print("   Vector solución   x = " + formato_vector(datos["x"]))
            print()
            if datos["solucion_correcta"]:
                print("   Comprobación exitosa: A · x == b")
            else:
                print("   ¡Atención! A · x no coincide con b")
        else:
            print()
            print("   A es " + str(m) + "×" + str(n)
                  + "; la solución por LU se resuelve solo para A cuadrada.")
    except ValueError as error:
        print("\n   " + str(error))
    pausa()
