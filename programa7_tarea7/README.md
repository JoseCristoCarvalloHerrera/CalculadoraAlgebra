# Programa 7 - Métodos Numéricos

Calculadora de Álgebra Lineal del Grupo 2, integrada con cuatro opciones nuevas:

1. Método de Bisección implementado desde cero.
2. Graficador seguro de funciones.
3. Notación posicional en base 10 y base 2.
4. Errores numéricos y propagación del error.

## Instalación

Desde esta carpeta:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

```bash
python main.py              # Interfaz Tkinter
python main.py --consola    # Menú de consola
python main.py --pruebas    # Pruebas de módulos anteriores y Programa 7
```

SymPy analiza las funciones con una lista blanca de símbolos y operaciones;
no se utiliza `eval()` directamente con texto del usuario. SciPy aparece
únicamente como contraste externo de la raíz: la bisección principal está
programada en `modulos/modulo_metodos_numericos.py`.

## Funciones permitidas

Se admite `x`, `pi`, `e`, `sin`, `cos`, `tan`, `exp`, `log`, `ln`, `sqrt`,
`abs`, operaciones aritméticas y potencias con `**`. El símbolo `^` se rechaza
porque no representa potencia en Python.
