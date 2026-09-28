# -*- coding: utf-8 -*-
"""
=====================================================================
 RESUMEN DE TEOREMAS Y PROPIEDADES CLAVE
 Calculadora de Álgebra Lineal - Proyecto Integrador - GRUPO 2
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Segundo Corte Evaluativo - Programa 4

 Cada módulo de la calculadora ofrece la opción
     0. Ver Teoremas Clave del Módulo
 y esa opción muestra el texto que está en este archivo. Se mantiene
 aparte para que los teoremas se puedan corregir o ampliar sin tocar
 el código de los módulos.
=====================================================================
"""

import tkinter as tk


TEOREMAS = {

    "sistemas": """TEOREMAS CLAVE - MODULO 1: SISTEMAS DE ECUACIONES LINEALES

1. FORMA ESCALONADA (3 propiedades)
   a) Todas las filas distintas de cero estan ARRIBA de las filas de ceros.
   b) Cada entrada principal esta en una columna a la DERECHA de la
      entrada principal de la fila superior.
   c) Debajo de cada entrada principal, todas las entradas son cero.

2. FORMA ESCALONADA REDUCIDA (las 3 anteriores + 2 mas)
   d) La entrada principal de cada fila no nula es 1.
   e) Cada 1 principal es el UNICO valor distinto de cero de su columna.

   La forma escalonada NO es unica; la escalonada reducida SI lo es.

3. TEOREMA DE EXISTENCIA Y UNICIDAD
   Un sistema lineal es CONSISTENTE si y solo si la ultima columna de
   la matriz aumentada NO es columna pivote; es decir, si al reducir no
   aparece ninguna fila de la forma  [0 0 ... 0 | k]  con k distinto de 0.

   Si es consistente:
      - sin variables libres  -> solucion UNICA      (determinado)
      - con variables libres  -> INFINITAS soluciones (indeterminado)

4. RANGO Y VARIABLES LIBRES
   rango(A) = numero de pivotes en la matriz de coeficientes.
   numero de variables libres = n - rango(A),  con n = numero de variables.

   rango(A) = rango(A|b)  ->  consistente
   rango(A) != rango(A|b) ->  inconsistente

5. OPERACIONES ELEMENTALES POR FILAS
   Intercambio, escalamiento (por k distinto de 0) y reemplazo.
   No alteran el conjunto solucion: la matriz original y la reducida
   son equivalentes por filas y representan el mismo sistema.""",


    "vectores": """TEOREMAS CLAVE - MODULO 2: VECTORES E INDEPENDENCIA LINEAL

1. COMBINACION LINEAL (definicion)
   Dados v1, v2, ..., vk en R^n y escalares c1, c2, ..., ck, el vector
        y = c1·v1 + c2·v2 + ... + ck·vk
   se llama combinacion lineal de v1...vk con pesos c1...ck.

2. TEOREMA DE LA ECUACION VECTORIAL
   La ecuacion vectorial
        x1·a1 + x2·a2 + ... + xn·an = b
   tiene el MISMO conjunto solucion que el sistema lineal cuya matriz
   aumentada es  [a1  a2  ...  an | b].

   En particular, b se puede generar como combinacion lineal de
   a1...an SI Y SOLO SI ese sistema lineal tiene solucion.

3. TEOREMA DE INDEPENDENCIA LINEAL   <-- REQUISITO DEL PROGRAMA 4
   Un conjunto de k vectores en R^n es LINEALMENTE INDEPENDIENTE si y
   solo si la UNICA solucion de
        c1·v1 + c2·v2 + ... + ck·vk = 0
   es la trivial  c1 = c2 = ... = ck = 0  (es decir, SIN variables libres).

   Si existe alguna solucion con los coeficientes NO todos cero, el
   conjunto es LINEALMENTE DEPENDIENTE.

4. CRITERIO PRACTICO POR PIVOTES
   Se forma la matriz A cuyas COLUMNAS son los vectores y se reduce el
   sistema homogeneo [A | 0]:
        numero de pivotes = k   ->  L.I.  (no sobra ninguna columna)
        numero de pivotes < k   ->  L.D.  (hay variables libres)
   Equivalentemente:  variables libres = k - numero de pivotes.

5. SISTEMA HOMOGENEO Ax = 0
   Siempre es CONSISTENTE, porque x = 0 siempre lo satisface (solucion
   trivial). Tiene solucion NO trivial si y solo si tiene al menos una
   variable libre.

6. CONSECUENCIA POR CONTEO
   Si k > n (mas vectores que la dimension del espacio), el conjunto es
   SIEMPRE linealmente dependiente, porque el rango no puede superar n.""",


    "matrices": """TEOREMAS CLAVE - MODULO 3: ALGEBRA DE MATRICES

1. SUMA Y MULTIPLO ESCALAR
   A + B esta definida SOLO si A y B tienen el mismo tamano m×n, y se
   calcula entrada por entrada. El multiplo escalar rA multiplica cada
   entrada de A por r.

2. PRODUCTO MATRIZ-VECTOR  Ax
   Si A es m×n con columnas a1...an y x esta en R^n, entonces
        Ax = x1·a1 + x2·a2 + ... + xn·an
   es decir, Ax ES la combinacion lineal de las COLUMNAS de A usando
   como pesos las entradas de x.
   Ax esta definido solo si el numero de columnas de A es igual al
   numero de entradas de x.

3. PROPIEDADES DE LINEALIDAD DE Ax
   Para u, v en R^n y c escalar:
        A(u + v) = Au + Av        (aditividad)
        A(c·u)   = c·(Au)         (homogeneidad)

4. MULTIPLICACION DE MATRICES - REGLA FILA COLUMNA
   Si A es m×n y B es n×p, entonces AB es m×p y
        (AB)ij = ai1·b1j + ai2·b2j + ... + ain·bnj
   Esta definida SOLO si las columnas de A son iguales a las filas de B.

5. PROPIEDADES DEL PRODUCTO
   A(BC) = (AB)C           (asociativa)
   A(B + C) = AB + AC      (distributiva izquierda)
   (B + C)A = BA + CA      (distributiva derecha)
   r(AB) = (rA)B = A(rB)
   In·A = A = A·In         (identidad)

   ATENCION: en general  AB != BA.  El producto NO es conmutativo.

6. TRASPUESTA
   (A^T)^T = A
   (A + B)^T = A^T + B^T
   (rA)^T = r·A^T
   (AB)^T = B^T · A^T      (se invierte el orden)""",


    "determinantes": """TEOREMAS CLAVE - MODULO 4: DETERMINANTES Y PROPIEDADES

1. DEFINICION POR COFACTORES
   Para A de n×n, expandiendo sobre la primera fila:
        det(A) = a11·C11 + a12·C12 + ... + a1n·C1n
   donde  Cij = (-1)^(i+j) · det(Mij)  y Mij es la submatriz que queda
   al tachar la fila i y la columna j.

   Caso 2×2:   det [a b; c d] = ad - bc

2. DETERMINANTE Y TIPO DE MATRIZ
   Si A es triangular (superior o inferior) o diagonal, det(A) es el
   PRODUCTO de los elementos de la diagonal.
   det(In) = 1.   Si A tiene una fila o columna de ceros, det(A) = 0.

3. EFECTO DE LAS OPERACIONES ELEMENTALES
   Intercambiar dos filas       ->  el determinante cambia de SIGNO.
   Multiplicar una fila por k   ->  el determinante se multiplica por k.
   Sumar a una fila un multiplo
   de otra (reemplazo)          ->  el determinante NO cambia.

4. PROPIEDADES DEL PRODUCTO
   det(AB) = det(A)·det(B)
   det(A^T) = det(A)
   det(rA) = r^n · det(A)   para A de n×n

5. CRITERIO DE INVERTIBILIDAD
   A es INVERTIBLE  si y solo si  det(A) != 0.
   Equivalentemente: A es invertible si y solo si sus columnas son
   linealmente independientes, y si y solo si A tiene n pivotes.

   Si det(A) = 0, la matriz es SINGULAR (no tiene inversa).

   NOTA: la matriz inversa se implementa en el siguiente programa.""",
}


def texto_teoremas(modulo):
    """Devuelve el resumen de teoremas del módulo pedido."""
    return TEOREMAS.get(modulo, "No hay teoremas registrados para este módulo.")


def mostrar_teoremas(raiz, modulo, titulo="Teoremas Clave del Módulo"):
    """Abre una ventana con el resumen de teoremas del módulo.

    Es la opción '0. Ver Teoremas Clave del Módulo' que pide la Tarea 4,
    adaptada a la interfaz gráfica: en lugar de imprimirse en consola,
    el resumen se despliega en una ventana con su propia barra de
    desplazamiento.
    """
    ventana = tk.Toplevel(raiz)
    ventana.title(titulo)
    ventana.configure(bg="#FFFFFF")
    ventana.geometry("820x600")

    tk.Label(ventana, text=titulo, font=("Montserrat", 15, "bold"),
             bg="#FFFFFF", fg="#0077B6").pack(anchor="w", padx=18, pady=(14, 8))

    marco = tk.Frame(ventana, bg="#FFFFFF")
    marco.pack(fill="both", expand=True, padx=18, pady=(0, 14))

    barra = tk.Scrollbar(marco)
    barra.pack(side="right", fill="y")

    caja = tk.Text(marco, wrap="word", font=("Consolas", 10),
                   bg="#FFFFFF", fg="#000000", relief="solid", bd=1,
                   yscrollcommand=barra.set, padx=12, pady=10)
    caja.pack(side="left", fill="both", expand=True)
    barra.configure(command=caja.yview)

    caja.insert("1.0", texto_teoremas(modulo))
    caja.configure(state="disabled")

    tk.Button(ventana, text="Cerrar", font=("Montserrat", 11, "bold"),
              bg="#0077B6", fg="#FFFFFF", relief="flat", cursor="hand2",
              padx=20, pady=8, command=ventana.destroy).pack(pady=(0, 14))

    ventana.transient(raiz)
    return ventana
