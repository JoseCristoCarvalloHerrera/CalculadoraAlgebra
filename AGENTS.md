# AGENTS.md

University deliverable (Álgebra Lineal, MTM0120, UAM, Grupo 2): a linear-algebra calculator in pure Python 3 + Tkinter. Code, UI text, and comments are in Spanish.

## Layout: one folder per submission
- `programa1_tarea1/`, `programa3_tarea3/` — single-file scripts (`Programa N_Grupo2.py`).
- `programa4_tarea4/`, `programa5_tarea5/` — modular packages (`modulos/` + `teoremas/`).
- There is **no** `programa2`.
- `programa5_tarea5/` is the integrated final app. Program 4 and 5 both define the same module files but they have **diverged** (program 5 adds inverse, determinants, properties). Earlier folders are frozen submissions for their own grading — do not "sync" them from each other or assume a fix belongs in more than one. Only touch the folder the task names.

## Hard constraint (grading requirement, repeated in every file header)
- Standard library only: `fractions`, `tkinter`, `math`.
- Do **not** introduce NumPy/SciPy, nor `math`'s linear-algebra helpers.
- The math engine uses `Fraction` everywhere for exact results; avoid float arithmetic.

## Running — you must be inside the task folder
Imports are package-relative (`from modulos import ...`), so the working directory matters.
- GUI: `python main.py` (tarea5) or `python "Programa 4_Grupo2.py"` (tarea4).
- Console CLI: `python main.py --consola` (alias `--cli`); same flags work for tarea4's `Programa 4_Grupo2.py`.
- Self-tests: `python main.py --pruebas` (tarea5), `python "Programa 4_Grupo2.py" --pruebas` (tarea4).
- File names contain spaces — quote them in shells.

## Architecture
- `modulos/modulo_sistemas.py` owns the Gauss / Gauss-Jordan row-reduction engine; other modules reuse it (independence, combination, inverse, determinant-via-reduction all reduce to it).
- `modulos/__init__.py` — UI palette constants, `a_numero` / `formato` (Fraction parse/format), matrix validators, ASCII logos, CLI input helpers (`preguntar`, `leer_matriz`, `SalirDeLaConsola`).
- Other modules: `modulo_vectores.py` (vectors, L.I./L.D., A·x), `modulo_matrices.py` (matrix ops, transpose, inverse by Gauss-Jordan and by adjugate), `modulo_determinantes.py` (cofactors, Sarrus, reduction).
- `teoremas/resumen_teoremas.py` backs each module's "Ver Teoremas Clave" screen.
- GUI and CLI share the exact same math functions; only input/display differ, so a computation change affects both.
- `MAX_DIMENSION = 8` (`modulos/__init__.py`).
- Source is UTF-8 and prints Unicode subscripts/symbols (₀₁₂, ·); `modulos/__init__.py` reconfigures stdout to UTF-8.

## Tests
- No pytest/unittest. `--pruebas` runs `ejecutar_pruebas()`, the de-facto test suite, printing `[  OK  ]`/`[FALLA]` per case and exiting non-zero if any check fails.
- Run it after any math change; success ends with "Todas las comprobaciones pasaron".
- **Currently broken on `origin/main`**: `ejecutar_pruebas()` raises `ValueError: too many values to unpack` at `programa5_tarea5/main.py:472` because `comprobar_inversa()` now returns 3 values `(A·A⁻¹, A⁻¹·A, se_cumple)` but the test still unpacks 2. Fix the unpack before trusting a green/red signal.

## Git
- Shared team repo (`github.com/JoseCristoCarvalloHerrera/CalculadoraAlgebra`). Members work on their own branch (`Cristo`, `Chel`, `Gabi`, `marian-dev`) and merge via PR. Commit on a branch, not directly on `main`.
- `origin/main` is the source of truth. The local `main` ref is stale (behind `origin/main`) and is missing `programa5_tarea5/`; the integrated tarea-5 app lives on `origin/main` and the `Cristo`/`Chel` branches. Verify against `origin/main`, not local `main`.
- `__pycache__/*.pyc` are generated and gitignored — never commit them.
