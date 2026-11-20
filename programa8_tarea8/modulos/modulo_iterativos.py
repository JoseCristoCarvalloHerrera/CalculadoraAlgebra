# -*- coding: utf-8 -*-
"""
modulo_iterativos.py  -  PROGRAMA 8
Metodos iterativos para Ax = b: Jacobi y Gauss-Seidel.

Estructura (igual que los demas modulos: motor matematico + pantalla + consola):
    1. Validaciones              validar_entradas, diagonal_dominante, ...
    2. Reordenamiento de filas   buscar_reordenamiento
    3. Metodos                   jacobi, gauss_seidel
    4. Proceso completo          ejecutar, texto_resultado, crear_figura
    5. Consola                   menu_consola
    6. Ventana Tkinter           IterativosApp
"""
import os
import tkinter as tk
from fractions import Fraction
from tkinter import messagebox

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

# Colores y utilidades de consola del proyecto (si se prueba el archivo solo,
# se usan valores por defecto para que no falle).
try:
    from modulos import (FONDO, TARJETA, TEXTO, TEXTO_SUAVE, ACENTO, ACENTO_HOVER,
                         LETRA_MONO, mostrar_cabecera, limpiar_pantalla, pausa,
                         preguntar, LOGO_PRINCIPAL)
except ImportError:
    FONDO, TARJETA, TEXTO, TEXTO_SUAVE = "#1e1e2e", "#2a2a3c", "#e6e6e6", "#a0a0b0"
    ACENTO, ACENTO_HOVER, LETRA_MONO = "#4fc3f7", "#81d4fa", ("Consolas", 10)
    LOGO_PRINCIPAL = ""
    mostrar_cabecera = lambda logo: print(logo)
    limpiar_pantalla = lambda: None
    pausa = lambda: input("   Presione Enter para continuar...")
    preguntar = input

LIMITE_DIVERGENCIA = 1e12          # si el error supera esto, se corta el proceso
CARPETA_EVIDENCIAS = "evidencias"  # aqui se guardan las graficas (.png)


# ======================================================================
# 1. VALIDACIONES
# ======================================================================
def validar_entradas(A, b, x0, tol, max_iter):
    """Valida dimensiones, tolerancia y maximo de iteraciones.
    Devuelve los datos convertidos; lanza ValueError si algo esta mal."""
    try:
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float).reshape(-1)
        x0 = np.array(x0, dtype=float).reshape(-1)
        tol = float(tol)
    except (ValueError, TypeError):
        raise ValueError("Todos los datos deben ser numericos.")

    if A.ndim != 2 or A.shape[0] != A.shape[1] or A.shape[0] == 0:
        raise ValueError("A debe ser una matriz cuadrada n x n.")
    n = A.shape[0]
    if b.shape != (n,):
        raise ValueError(f"b debe tener {n} componentes (tiene {b.size}).")
    if x0.shape != (n,):
        raise ValueError(f"x0 debe tener {n} componentes (tiene {x0.size}).")
    if not (np.all(np.isfinite(A)) and np.all(np.isfinite(b)) and np.all(np.isfinite(x0))):
        raise ValueError("A, b y x0 no pueden contener valores no finitos (nan/inf).")
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError("La tolerancia debe ser un decimal positivo (ej. 0.000001).")
    if int(max_iter) != max_iter or max_iter <= 0:
        raise ValueError("El maximo de iteraciones debe ser un entero positivo.")
    return A, b, x0, tol, int(max_iter)


def diagonal_dominante(A):
    """|a_ii| > suma_{j!=i} |a_ij| en cada fila (dominancia ESTRICTA por filas)."""
    diag = np.abs(np.diag(A))
    resto = np.abs(A).sum(axis=1) - diag
    por_fila = diag > resto
    return bool(por_fila.all()), por_fila


def ceros_en_diagonal(A):
    return [i for i in range(len(A)) if A[i, i] == 0]


# ======================================================================
# 2. REORDENAMIENTO DE FILAS (backtracking)
# ======================================================================
def buscar_reordenamiento(A):
    """Busca una permutacion de filas: primero diagonal estrictamente dominante;
    si no existe, al menos diagonal sin ceros. Devuelve (perm, tipo) o (None, None).
    perm[j] = fila original que queda en la posicion j."""
    n = len(A)
    absA = np.abs(A)
    suma = absA.sum(axis=1)

    def cond_estricta(r, j):
        return absA[r, j] > suma[r] - absA[r, j]

    def cond_no_cero(r, j):
        return A[r, j] != 0

    def bt(j, usadas, perm, cond):
        if j == n:
            return perm
        candidatas = [r for r in range(n) if r not in usadas and cond(r, j)]
        candidatas.sort(key=lambda r: -absA[r, j])      # prueba primero pivotes grandes
        for r in candidatas:
            res = bt(j + 1, usadas | {r}, perm + [r], cond)
            if res is not None:
                return res
        return None

    for cond, tipo in ((cond_estricta, "diagonal estrictamente dominante"),
                       (cond_no_cero, "diagonal sin ceros (no dominante)")):
        perm = bt(0, frozenset(), [], cond)
        if perm is not None:
            return perm, tipo
    return None, None


def diagnostico_diagonal(A):
    """Resume el estado de la diagonal y si hay un reordenamiento util."""
    ceros = ceros_en_diagonal(A)
    dominante, por_fila = diagonal_dominante(A)
    perm = tipo = None
    if ceros or not dominante:
        perm, tipo = buscar_reordenamiento(A)
        # Si no hay ceros y no se logra dominancia, reordenar no aporta nada.
        if perm is not None and (perm == list(range(len(A)))
                                 or (not ceros and "no dominante" in tipo)):
            perm = tipo = None
    return {"ceros": ceros, "dominante": dominante, "por_fila": por_fila,
            "perm": perm, "tipo": tipo}


# ======================================================================
# 3. METODOS ITERATIVOS
# ======================================================================
def _iterar(A, b, x0, tol, max_iter, metodo):
    """Nucleo comun. Criterio de parada igual para ambos:
        error = ||x(k) - x(k-1)||_inf <= tol      (tambien se guarda el residuo)"""
    n = len(b)
    x = x0.copy()
    filas = []
    estado = None
    with np.errstate(all="ignore"):
        for k in range(1, max_iter + 1):
            if metodo == "Jacobi":
                # TODOS los componentes nuevos usan solo valores de x(k-1)
                x_new = (b - (A @ x - np.diag(A) * x)) / np.diag(A)
            else:
                # Gauss-Seidel: cada x_new[i] se usa de inmediato en las filas siguientes
                x_new = x.copy()
                for i in range(n):
                    s = A[i] @ x_new - A[i, i] * x_new[i]
                    x_new[i] = (b[i] - s) / A[i, i]

            error = np.max(np.abs(x_new - x))
            residuo = np.max(np.abs(A @ x_new - b))
            filas.append([k, *x_new, error, residuo])
            x = x_new

            if not np.isfinite(error) or error > LIMITE_DIVERGENCIA:
                estado = "divergencia"
                break
            if error <= tol:
                estado = "convergencia"
                break
    if estado is None:
        estado = "max_iter"

    columnas = ["k"] + [f"x{i + 1}" for i in range(n)] + ["error", "residuo"]
    tabla = pd.DataFrame(filas, columns=columnas)
    tabla["k"] = tabla["k"].astype(int)

    mensajes = {
        "convergencia": "Convergencia alcanzada (error <= tolerancia).",
        "max_iter": "Se alcanzo el maximo de iteraciones SIN llegar a la tolerancia (posible no convergencia).",
        "divergencia": "ADVERTENCIA: el error crecio sin control / aparecieron valores no finitos. El metodo diverge.",
    }
    return {"metodo": metodo, "x": x, "iteraciones": len(tabla), "estado": estado,
            "mensaje": mensajes[estado], "error_final": float(tabla["error"].iloc[-1]),
            "residuo_final": float(tabla["residuo"].iloc[-1]), "tabla": tabla}


def jacobi(A, b, x0, tol, max_iter):
    return _iterar(A, b, x0, tol, max_iter, "Jacobi")


def gauss_seidel(A, b, x0, tol, max_iter):
    return _iterar(A, b, x0, tol, max_iter, "Gauss-Seidel")


def solucion_referencia(A, b):
    """numpy.linalg.solve: solo VALIDA los resultados, no sustituye a los metodos.
    (Tambien se puede usar el modulo de Gauss-Jordan de la calculadora.)"""
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return None


# ======================================================================
# 4. PROCESO COMPLETO, TEXTO Y GRAFICA
# ======================================================================
def ejecutar(A, b, x0, tol, max_iter, reordenar=False):
    """Hace todo el proceso SIN imprimir ni cerrar el programa. Devuelve un dict:
        error  -> texto si no se pudo ejecutar (validacion, ceros sin arreglo), o None
        log    -> lineas informativas (diagonal, reordenamiento)
        rj, rg -> resultados de Jacobi y Gauss-Seidel
        ref    -> solucion de referencia (o None)"""
    res = {"error": None, "log": [], "rj": None, "rg": None, "ref": None, "A": None, "b": None}
    try:
        A, b, x0, tol, max_iter = validar_entradas(A, b, x0, tol, max_iter)
    except ValueError as e:
        res["error"] = f"[ERROR de validacion] {e}"
        return res

    log = res["log"]
    d = diagnostico_diagonal(A)
    log.append("--- Revision de la diagonal ---")
    if d["ceros"]:
        log.append(f"Hay ceros en la diagonal principal (posiciones {[i + 1 for i in d['ceros']]}).")
    filas_ok = [i + 1 for i in range(len(A)) if d["por_fila"][i]]
    log.append("Diagonal estrictamente dominante por filas: "
               + ("SI" if d["dominante"] else "NO") + f" (filas que cumplen: {filas_ok})")
    if not d["dominante"]:
        log.append("Nota: la dominancia es condicion SUFICIENTE, no necesaria; su ausencia "
                   "no implica por si sola que el metodo diverja.")

    if d["perm"] is not None:
        log.append(f"Reordenamiento posible -> filas {[p + 1 for p in d['perm']]}: {d['tipo']}.")
        if reordenar:
            A, b = A[d["perm"]], b[d["perm"]]
            log.append("Reordenamiento APLICADO. Matriz reordenada:")
            log.append(np.array2string(A, precision=6))
        else:
            log.append("Reordenamiento NO aplicado: se usa el orden original.")
    elif d["ceros"]:
        log.append("No existe un reordenamiento de filas que elimine los ceros de la diagonal.")
    elif not d["dominante"]:
        log.append("No se encontro un reordenamiento que logre diagonal dominante; "
                   "se continua con el orden original.")

    if ceros_en_diagonal(A):
        res["error"] = ("[ERROR] Hay ceros en la diagonal: no se puede iniciar Jacobi / "
                        "Gauss-Seidel (division entre cero).")
        return res

    res["A"], res["b"] = A, b
    res["rj"] = jacobi(A, b, x0, tol, max_iter)
    res["rg"] = gauss_seidel(A, b, x0, tol, max_iter)
    res["ref"] = solucion_referencia(A, b)
    return res


def _texto_metodo(r):
    t = [f"\n===== {r['metodo']} =====",
         r["tabla"].to_string(index=False, float_format=lambda v: f"{v:.8g}"),
         f"\nEstado: {r['mensaje']}",
         f"Iteraciones usadas : {r['iteraciones']}"]
    if np.all(np.isfinite(r["x"])):
        t.append("Solucion aproximada: " + np.array2string(r["x"], precision=8))
    t.append(f"Error final  ||x(k)-x(k-1)||_inf : {r['error_final']:.3e}")
    t.append(f"Residuo final ||Ax-b||_inf        : {r['residuo_final']:.3e}")
    return "\n".join(t)


def texto_resultado(res):
    """Convierte el resultado de ejecutar() en texto (sirve para consola y ventana)."""
    partes = list(res["log"])
    if res["error"]:
        partes.append(res["error"])
        return "\n".join(partes)
    rj, rg, ref = res["rj"], res["rg"], res["ref"]
    partes += [_texto_metodo(rj), _texto_metodo(rg), "\n===== COMPARACION Y VALIDACION ====="]
    ok_j, ok_g = rj["estado"] == "convergencia", rg["estado"] == "convergencia"
    if ok_j and ok_g:
        if rj["iteraciones"] != rg["iteraciones"]:
            mejor = rj if rj["iteraciones"] < rg["iteraciones"] else rg
            otro = rg if mejor is rj else rj
            partes.append(f"Menos iteraciones: {mejor['metodo']} "
                          f"({mejor['iteraciones']} vs {otro['iteraciones']}).")
        else:
            partes.append(f"Ambos necesitaron {rj['iteraciones']} iteraciones.")
        partes.append(f"||x_Jacobi - x_GaussSeidel||_inf = {np.max(np.abs(rj['x'] - rg['x'])):.3e}")
    else:
        partes.append("No se comparan iteraciones: al menos un metodo no convergio.")
    if ref is not None:
        for r, ok in ((rj, ok_j), (rg, ok_g)):
            if ok:
                partes.append(f"{r['metodo']:<13}: ||x - x_ref||_inf = "
                              f"{np.max(np.abs(r['x'] - ref)):.3e} | residuo = {r['residuo_final']:.3e}")
        partes.append("Solucion de referencia (numpy.linalg.solve): " + np.array2string(ref, precision=8))
    else:
        partes.append("A es singular: no hay solucion de referencia unica.")
    return "\n".join(partes)


def crear_figura(res, fig=None):
    """Grafica error vs iteracion (escala log) para ambos metodos.
    Devuelve la Figure o None si no hay datos validos."""
    if res["rj"] is None:
        return None
    if fig is None:
        fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    hay = False
    for r, estilo in ((res["rj"], "o-"), (res["rg"], "s--")):
        err = r["tabla"]["error"].to_numpy()
        ks = r["tabla"]["k"].to_numpy()
        m = np.isfinite(err)
        if m.any():
            ax.semilogy(ks[m], np.maximum(err[m], 1e-18), estilo, label=r["metodo"], markersize=4)
            hay = True
    if not hay:
        return None
    ax.set_xlabel("Iteracion k")
    ax.set_ylabel("Error  ||x(k) - x(k-1)||inf")
    ax.set_title("Jacobi vs Gauss-Seidel")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def guardar_figura(fig, nombre):
    os.makedirs(CARPETA_EVIDENCIAS, exist_ok=True)
    ruta = os.path.join(CARPETA_EVIDENCIAS, f"{nombre}.png")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    return ruta


# ======================================================================
# 5. MODO CONSOLA
# ======================================================================
def _numero(texto):
    """Acepta decimales y fracciones: 2.5, -3, 1/4."""
    return float(Fraction(texto.strip()))


def _leer_vector(mensaje, n):
    while True:
        try:
            v = [_numero(t) for t in preguntar(mensaje).replace(",", " ").split()]
            if len(v) == n:
                return v
            print(f"   Deben ser exactamente {n} valores.")
        except (ValueError, ZeroDivisionError):
            print("   Entrada no valida, intente de nuevo.")


def ejecutar_y_mostrar(A, b, x0, tol, max_iter, reordenar, nombre):
    """Ejecuta, imprime el texto y muestra/guarda la grafica (modo consola)."""
    res = ejecutar(A, b, x0, tol, max_iter, reordenar)
    print(texto_resultado(res))
    fig = crear_figura(res)
    if fig is not None:
        print("\nGrafica guardada en:", guardar_figura(fig, nombre))
        import matplotlib.pyplot as plt          # solo para ABRIR la ventana de la grafica
        plt.figure(figsize=(8, 5))
        crear_figura(res, plt.gcf())
        plt.show()
    return res


def _ingresar_en_consola():
    try:
        n = int(preguntar("   Tamano n de la matriz A (n x n): "))
        if n < 1:
            raise ValueError
    except ValueError:
        print("   n debe ser un entero positivo.")
        return
    print("   Ingrese A fila por fila (valores separados por espacio):")
    A = [_leer_vector(f"     Fila {i + 1}: ", n) for i in range(n)]
    b = _leer_vector("   Vector b: ", n)
    x0 = _leer_vector("   Vector inicial x0: ", n)
    try:
        tol = float(preguntar("   Tolerancia (ej. 0.000001): "))
        max_iter = int(preguntar("   Maximo de iteraciones: "))
    except ValueError:
        print("   [ERROR] Tolerancia decimal y maximo entero, por favor.")
        return
    reordenar = preguntar("   Reordenar filas si es posible? (s/n): ").strip().lower() == "s"
    ejecutar_y_mostrar(A, b, x0, tol, max_iter, reordenar, "sistema_usuario")


def menu_consola():
    from modulos.casos_prueba_p8 import ejecutar_caso
    while True:
        mostrar_cabecera(LOGO_PRINCIPAL)
        print("   METODOS ITERATIVOS: JACOBI Y GAUSS-SEIDEL\n")
        print("   1. Resolver un sistema (ingresar datos)")
        print("   2. Caso de prueba 1 (convergencia)")
        print("   3. Caso de prueba 2 (reordenamiento)")
        print("   4. Caso de prueba 3 (advertencia / no convergencia)")
        print("   9. Volver al menu principal\n")
        op = preguntar("   Elija una opcion: ").strip()
        if op == "9":
            return
        elif op == "1":
            _ingresar_en_consola()
        elif op in ("2", "3", "4"):
            ejecutar_caso(int(op) - 2)
        else:
            print("   Opcion no valida.")
        pausa()


# ======================================================================
# 6. VENTANA TKINTER
# ======================================================================
class IterativosApp:
    """Pantalla del Modulo 6: Jacobi y Gauss-Seidel."""

    def __init__(self, raiz, callback_volver):
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self._Canvas = FigureCanvasTkAgg
        self.raiz = raiz
        self.callback_volver = callback_volver
        self.entradas_A, self.entradas_b, self.entradas_x0 = [], [], []
        self.canvas_widget = None

        self.frame = tk.Frame(raiz, bg=FONDO)
        self.frame.pack(fill="both", expand=True)

        # --- encabezado ---
        cab = tk.Frame(self.frame, bg=FONDO)
        cab.pack(fill="x", padx=16, pady=(12, 4))
        tk.Button(cab, text="< Volver al menu", bg=TARJETA, fg=TEXTO, relief="flat",
                  cursor="hand2", command=self.callback_volver).pack(side="left")
        tk.Label(cab, text="Jacobi y Gauss-Seidel  (Ax = b)", font=("Montserrat", 18, "bold"),
                 bg=FONDO, fg=TEXTO).pack(side="left", padx=20)

        cuerpo = tk.Frame(self.frame, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=16, pady=8)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        # --- panel izquierdo: datos ---
        izq = tk.Frame(cuerpo, bg=TARJETA)
        izq.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        fila_n = tk.Frame(izq, bg=TARJETA)
        fila_n.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(fila_n, text="n =", bg=TARJETA, fg=TEXTO).pack(side="left")
        self.var_n = tk.IntVar(value=3)
        tk.Spinbox(fila_n, from_=2, to=8, width=3, textvariable=self.var_n).pack(side="left", padx=4)
        tk.Button(fila_n, text="Crear tabla", bg=ACENTO, fg=FONDO, relief="flat", cursor="hand2",
                  command=self.crear_tabla).pack(side="left", padx=6)

        self.marco_tabla = tk.Frame(izq, bg=TARJETA)
        self.marco_tabla.pack(padx=10, pady=6)

        opc = tk.Frame(izq, bg=TARJETA)
        opc.pack(fill="x", padx=10, pady=4)
        tk.Label(opc, text="Tolerancia:", bg=TARJETA, fg=TEXTO).grid(row=0, column=0, sticky="w")
        self.var_tol = tk.StringVar(value="0.000001")
        tk.Entry(opc, textvariable=self.var_tol, width=12).grid(row=0, column=1, padx=6, pady=2)
        tk.Label(opc, text="Max. iteraciones:", bg=TARJETA, fg=TEXTO).grid(row=1, column=0, sticky="w")
        self.var_max = tk.StringVar(value="100")
        tk.Entry(opc, textvariable=self.var_max, width=12).grid(row=1, column=1, padx=6, pady=2)
        self.var_reord = tk.BooleanVar(value=True)
        tk.Checkbutton(opc, text="Reordenar filas si es posible", variable=self.var_reord,
                       bg=TARJETA, fg=TEXTO, selectcolor=FONDO, activebackground=TARJETA,
                       activeforeground=TEXTO).grid(row=2, column=0, columnspan=2, sticky="w", pady=4)

        tk.Button(izq, text="Resolver (Jacobi y Gauss-Seidel)", bg=ACENTO, fg=FONDO,
                  font=("Montserrat", 11, "bold"), relief="flat", cursor="hand2", pady=8,
                  activebackground=ACENTO_HOVER, command=self.resolver).pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(izq, text="Casos de prueba:", bg=TARJETA, fg=TEXTO_SUAVE).pack(anchor="w", padx=10, pady=(8, 0))
        fila_c = tk.Frame(izq, bg=TARJETA)
        fila_c.pack(fill="x", padx=10, pady=(2, 10))
        for i, txt in enumerate(("Caso 1", "Caso 2", "Caso 3")):
            tk.Button(fila_c, text=txt, bg=FONDO, fg=TEXTO, relief="flat", cursor="hand2",
                      command=lambda k=i + 1: self.cargar_caso(k)).pack(side="left", expand=True, fill="x", padx=2)

        # --- panel derecho: resultados y grafica ---
        der = tk.Frame(cuerpo, bg=FONDO)
        der.grid(row=0, column=1, sticky="nsew")
        der.rowconfigure(0, weight=3)
        der.rowconfigure(1, weight=2)
        der.columnconfigure(0, weight=1)

        marco_txt = tk.Frame(der, bg=FONDO)
        marco_txt.grid(row=0, column=0, sticky="nsew")
        self.texto = tk.Text(marco_txt, wrap="none", bg=TARJETA, fg=TEXTO,
                             font=("Consolas", 10), relief="flat", height=14)
        sy = tk.Scrollbar(marco_txt, command=self.texto.yview)
        sx = tk.Scrollbar(marco_txt, orient="horizontal", command=self.texto.xview)
        self.texto.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.texto.pack(fill="both", expand=True)

        self.marco_grafica = tk.Frame(der, bg=FONDO)
        self.marco_grafica.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.crear_tabla()
        self.cargar_caso(1)

    # ---------- tabla de entradas ----------
    def crear_tabla(self):
        try:
            n = int(self.var_n.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Dato invalido", "n debe ser un entero entre 2 y 8.")
            return
        n = max(2, min(8, n))
        for w in self.marco_tabla.winfo_children():
            w.destroy()
        self.entradas_A, self.entradas_b, self.entradas_x0 = [], [], []
        tk.Label(self.marco_tabla, text="Matriz A", bg=TARJETA, fg=TEXTO_SUAVE).grid(row=0, column=0, columnspan=n)
        tk.Label(self.marco_tabla, text="b", bg=TARJETA, fg=TEXTO_SUAVE).grid(row=0, column=n + 1)
        tk.Label(self.marco_tabla, text="x0", bg=TARJETA, fg=TEXTO_SUAVE).grid(row=0, column=n + 2)
        for i in range(n):
            fila = []
            for j in range(n):
                e = tk.Entry(self.marco_tabla, width=6, justify="center")
                e.grid(row=i + 1, column=j, padx=1, pady=1)
                e.insert(0, "0")
                fila.append(e)
            self.entradas_A.append(fila)
            tk.Label(self.marco_tabla, text="|", bg=TARJETA, fg=TEXTO_SUAVE).grid(row=i + 1, column=n)
            eb = tk.Entry(self.marco_tabla, width=6, justify="center")
            eb.grid(row=i + 1, column=n + 1, padx=1)
            eb.insert(0, "0")
            self.entradas_b.append(eb)
            ex = tk.Entry(self.marco_tabla, width=6, justify="center")
            ex.grid(row=i + 1, column=n + 2, padx=(6, 1))
            ex.insert(0, "0")
            self.entradas_x0.append(ex)

    def _poner(self, entrada, valor):
        entrada.delete(0, "end")
        entrada.insert(0, str(valor))

    def cargar_caso(self, k):
        from modulos.casos_prueba_p8 import CASOS
        c = CASOS[k]
        self.var_n.set(len(c["A"]))
        self.crear_tabla()
        for i, fila in enumerate(c["A"]):
            for j, v in enumerate(fila):
                self._poner(self.entradas_A[i][j], v)
            self._poner(self.entradas_b[i], c["b"][i])
            self._poner(self.entradas_x0[i], c["x0"][i])
        self.var_tol.set(str(c["tol"]))
        self.var_max.set(str(c["max_iter"]))
        self.var_reord.set(bool(c["reordenar"]))
        self.texto.delete("1.0", "end")
        self.texto.insert("end", f"{c['titulo']}\nObjetivo: {c['objetivo']}\n\n"
                                 "Datos cargados. Presione 'Resolver'.")
        self._nombre = f"caso{k}"

    # ---------- resolver ----------
    def resolver(self):
        try:
            A = [[_numero(e.get()) for e in fila] for fila in self.entradas_A]
            b = [_numero(e.get()) for e in self.entradas_b]
            x0 = [_numero(e.get()) for e in self.entradas_x0]
            tol = float(self.var_tol.get())
            max_iter = int(self.var_max.get())
        except (ValueError, ZeroDivisionError):
            messagebox.showerror("Dato invalido",
                                 "Revise los datos: numeros (o fracciones como 1/2), tolerancia decimal "
                                 "y maximo de iteraciones entero.")
            return
        try:
            res = ejecutar(A, b, x0, tol, max_iter, self.var_reord.get())
            self.texto.delete("1.0", "end")
            self.texto.insert("end", texto_resultado(res))
            self._mostrar_grafica(res)
        except Exception as error:                      # la calculadora nunca se cierra sola
            messagebox.showerror("Error inesperado", str(error))

    def _mostrar_grafica(self, res):
        if self.canvas_widget is not None:
            self.canvas_widget.destroy()
            self.canvas_widget = None
        fig = crear_figura(res, Figure(figsize=(6, 3.2)))
        if fig is None:
            return
        guardar_figura(fig, getattr(self, "_nombre", "sistema_usuario"))
        canvas = self._Canvas(fig, master=self.marco_grafica)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)