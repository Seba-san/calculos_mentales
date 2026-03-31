"""
generar_circuito_v2.py
=======================
Versión 2 — mejoras:
  • Notación científica con \\cdot (evita el doble \\times)
  • Sin página inicial ni hoja separadora entre lotes
  • Tarjetas de sensor con layout bicolor (\\tcblower) → sin solapamiento
  • Coeficientes no enteros (0.25, 0.5, 1.5, 2.5, 7.5…)
  • Nuevos generadores: conversión de unidades SI y regla de tres
  • Distribución equitativa entre 4 categorías de operación
  • Errores tipo "ceguera de datos" (desplazamiento de coma decimal)

Uso:
    python generar_circuito_v2.py
Compilar:
    pdflatex circuito_triage.tex
"""

import random
import math
import os
import time
random.seed(time.time())

#SEED       = 42
#random.seed(SEED)
NUM_CARDS  = 40
ERROR_RATE = 0.30
OUTPUT     = "circuito_triage.tex"


# ══════════════════════════════════════════════════════════════════
#  AUXILIARES NUMÉRICOS Y LaTeX
# ══════════════════════════════════════════════════════════════════

def fmt_sci(val: float, sig: int = 2) -> str:
    """
    Notación científica con \\cdot entre mantisa y potencia.
    Así  5 \\times 3 \\cdot 10^{-3}  es inequívoco
    (el primer \\times es el operador, el \\cdot el de la notación).
    """
    if val == 0:
        return "0"
    exp  = int(math.floor(math.log10(abs(val))))
    mant = round(val / 10**exp, sig - 1)
    if mant == int(mant):
        mant = int(mant)
    if exp == 0:
        return str(mant)
    return rf"{mant} \cdot 10^{{{exp}}}"


def fmt_num(val: float) -> str:
    """Decimal limpio sin notación científica de Python."""
    if val == 0:
        return "0"
    return f"{val:.6g}"


# ══════════════════════════════════════════════════════════════════
#  UNIDADES SI  (sin paquete siunitx — renderizado manual en math)
# ══════════════════════════════════════════════════════════════════

# Prefijo: (clave_interna, factor, LaTeX-en-modo-math)
_PFX = [
    ("micro", 1e-6, r"\mu"),
    ("milli", 1e-3, r"\mathrm{m}"),
    ("",      1.0,  ""),
    ("kilo",  1e3,  r"\mathrm{k}"),
    ("mega",  1e6,  r"\mathrm{M}"),
]
_PFX_IDX = {p[0]: i for i, p in enumerate(_PFX)}

# Unidad: (clave_interna, LaTeX-en-modo-math)
_UNIT = {
    "A":  r"\mathrm{A}",
    "W":  r"\mathrm{W}",
    "V":  r"\mathrm{V}",
    "Ohm": r"\Omega",
    "Hz": r"\mathrm{Hz}",
    "Pa": r"\mathrm{Pa}",
}
_UNIT_KEYS = list(_UNIT.keys())


def render_unit(pfx_key: str, unit_key: str) -> str:
    """
    Combina prefijo + unidad para uso dentro de $...$.
    Fusiona \\mathrm{} adyacentes: \\mathrm{m}\\mathrm{A} → \\mathrm{mA}.
    """
    pfx_tex  = next(p[2] for p in _PFX if p[0] == pfx_key)
    unit_tex = _UNIT[unit_key]
    # Fusionar \mathrm{x} + \mathrm{y}  →  \mathrm{xy}  (ej. mA, kHz, MPa)
    MR = r'\mathrm{'        # prefijo real de la cadena LaTeX
    if pfx_tex.startswith(MR) and unit_tex.startswith(MR):
        p_inner = pfx_tex[len(MR):-1]   # extrae 'm', 'k', 'M', ...
        u_inner = unit_tex[len(MR):-1]  # extrae 'A', 'W', 'Hz', ...
        return rf'\mathrm{{{p_inner}{u_inner}}}'
    return pfx_tex + unit_tex


#NICE_VALS = [
    0.1, 0.25, 0.5, 1, 1.5, 2, 2.5, 5,
    10, 25, 50, 100, 150, 250, 500, 1000, 1500, 2000, 2500,
#]

# Valores de componentes y suministros reales
NICE_VALS = [
    12, 24, 48, 110, 220, 380, 440,     # Voltajes industriales
    15, 33, 47, 68, 100, 150, 220, 330, 470, 680, # Valores comunes de componentes
    0.33, 0.47, 0.68, 1.2, 2.2, 4.7     # Valores en escala pequeña
]

# ══════════════════════════════════════════════════════════════════
#  GENERADORES DE OPERACIONES
# ══════════════════════════════════════════════════════════════════

# Coeficientes no sólo enteros
#COEFS = [0.25, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5, 8]
# Valores basados en la serie E12 (resistencias/capacitores) y constantes de ingeniería
# Esto obliga a redondear mentalmente (ej: 4.7 es "casi 5", 8.2 es "un poco más de 8")
COEFS = [
    1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2,  # Serie E12
    3.14, 1.41, 1.73, 9.8, 0.707, 2.71                       # pi, sqrt(2), sqrt(3), g, sin(45), e
]


# ── Categoría 1: Divisiones decimales / fracciones con potencias ──

def gen_division_decimales() -> dict:
    """Cociente de decimales pequeños. Ej: 0.015 / 0.006"""
    exp_n = random.choice([-3, -2, -1])
    exp_d = random.choice([-3, -2, -1])
    c_n   = random.choice(COEFS)
    c_d   = random.choice([0.5, 1, 2, 2.5, 4, 5])
    nv, dv = c_n * 10**exp_n, c_d * 10**exp_d
    return {
        "latex":  rf"\dfrac{{{fmt_num(nv)}}}{{{fmt_num(dv)}}}",
        "result": nv / dv,
        "scale":  "huge",
    }


def gen_fraccion_potencias() -> dict:
    """Fracción con potencias de 10. Ej: (2.5 × 10^{-2}) / (5 × 10^3)"""
    en = random.choice([-4, -3, -2, -1, 0, 1, 2, 3])
    ed = random.choice([-4, -3, -2, -1, 0, 1, 2, 3])
    while en == 0 and ed == 0:
        ed = random.choice([-3, -2, -1, 1, 2, 3])
    cn = random.choice([1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 15, 20])
    cd = random.choice([2, 4, 5, 8, 10, 20, 25, 50])
    nv, dv = cn * 10**en, cd * 10**ed

    def term(c, e):
        if e == 0:   return fmt_num(c)
        if c == 1:   return rf"10^{{{e}}}"
        return rf"{fmt_num(c)} \times 10^{{{e}}}"

    return {
        "latex":  rf"\dfrac{{{term(cn, en)}}}{{{term(cd, ed)}}}",
        "result": nv / dv,
        "scale":  "huge",
    }


# ── Categoría 2: Multiplicaciones con notación científica ─────────

def gen_mult_sci_entero() -> dict:
    """
    Entero × coef·10^exp.
    Ej:  50 × 2.5·10^{-4}
    El \\cdot separa la mantisa de la potencia;
    el \\times separa el factor entero del número científico.
    """
    ent  = random.choice([2, 3, 4, 5, 6, 8, 10, 20, 50, 100])
    coef = random.choice(COEFS)
    exp  = random.choice([-5, -4, -3, -2, -1, 2, 3, 4, 5])
    sv   = coef * 10**exp
    return {
        "latex":  rf"{fmt_num(ent)} \times {fmt_sci(sv)}",
        "result": ent * sv,
        "scale":  "huge",
    }


def gen_mult_doble_sci() -> dict:
    """
    Dos factores en notación científica.
    Ej:  (1.5·10^{-3}) × (4·10^2)
    """
    c1 = random.choice(COEFS)
    e1 = random.choice([-5, -4, -3, -2, -1, 0, 1, 2])
    c2 = random.choice(COEFS)
    e2 = random.choice([-5, -4, -3, -2, -1, 0, 1, 2])
    v1, v2 = c1 * 10**e1, c2 * 10**e2
    return {
        "latex":  rf"({fmt_sci(v1)}) \times ({fmt_sci(v2)})",
        "result": v1 * v2,
        "scale":  "huge",
    }


# ── Categoría 3: Conversión de unidades SI ────────────────────────

def gen_unit_conversion() -> dict:
    """
    Conversión de prefijo.
    Ej:  250 μA → mA   |   1.5 kΩ → Ω
    """
    unit = random.choice(_UNIT_KEYS)

    # Dos prefijos distintos, como máximo 2 escalones de distancia
    while True:
        i, j = random.sample(range(len(_PFX)), 2)
        if abs(i - j) <= 2:
            break

    src_pfx, src_f, _ = _PFX[i]
    tgt_pfx, tgt_f, _ = _PFX[j]

    val_src = random.choice(NICE_VALS)
    result  = round(val_src * src_f / tgt_f, 12)

    src_tex = render_unit(src_pfx, unit)
    tgt_tex = render_unit(tgt_pfx, unit)

    return {
        "latex":  (
            rf"{fmt_num(val_src)}\,{src_tex}"
            rf" \;\longrightarrow\; {tgt_tex}"
        ),
        "result": result,
        "scale":  "huge", # large
    }



# ── Categoría 4: Regla de tres proporcional ───────────────────────

def gen_proportionality() -> dict:
    """
    Regla de tres directa.
    Formato visual:
        A  →  B
        C  →  ?
    """
    factor = random.choice([0.1, 0.2, 0.25, 0.5, 2, 4, 5, 10, 20, 100])
    A = random.choice([0.02, 0.05, 0.1, 0.2, 0.4, 0.5, 1, 2, 4, 5, 10])
    B = round(A * factor, 8)
    C = round(A * random.choice([0.1, 0.25, 0.5, 2, 4, 5, 10]), 8)
    result = round(C * factor, 8)

    return {
        "latex": (
            r"\begin{array}{r@{\;\longrightarrow\;}l}"
            rf"  {fmt_num(A)} & {fmt_num(B)} \\"
            rf"  {fmt_num(C)} & ?"
            r"\end{array}"
        ),
        "result": result,
        "scale":  "huge", # large
    }


# ── Dispatcher: 25 % por categoría ───────────────────────────────

def generate_operation() -> dict:
    cat = random.randint(0, 3)
    if cat == 0:
        return random.choice([gen_division_decimales,
                               gen_fraccion_potencias])()
    elif cat == 1:
        return random.choice([gen_mult_sci_entero,
                               gen_mult_doble_sci])()
    elif cat == 2:
        return gen_unit_conversion()
    else:
        return gen_proportionality()


# ══════════════════════════════════════════════════════════════════
#  LÓGICA DEL JUEGO — LOTES A y B
# ══════════════════════════════════════════════════════════════════

def apply_error(val: float) -> float:
    """
    Error tipo 'ceguera de datos': desplaza la coma decimal
    1 ó 2 posiciones (×10, ÷10, ×100, ÷100).
    Simula confusión de prefijo SI o error de unidad.
    """
    return val * random.choice([10, 100, 0.1, 0.01])


def build_lote_a_old(n: int) -> list:
    cards = []
    for _ in range(n):
        op = generate_operation()
        cards.append({
            "lote":   "A",
            "latex":  op["latex"],
            "result": op["result"],
            "scale":  op["scale"],
        })
    return cards

def build_lote_a(n: int) -> list:
    cards = []
    used_latex = set() # Para no repetir
    while len(cards) < n:
        op = generate_operation()
        if op["latex"] not in used_latex:
            used_latex.add(op["latex"])
            cards.append({
                "lote":   "A",
                "latex":  op["latex"],
                "result": op["result"],
                "scale":  op["scale"],
            })
    return cards


def build_lote_b_old(n: int, rate: float = ERROR_RATE) -> list:
    n_err   = round(n * rate)
    flags   = [True] * n_err + [False] * (n - n_err)
    random.shuffle(flags)
    cards   = []
    for has_err in flags:
        op = generate_operation()
        tv = op["result"]
        sv = apply_error(tv) if has_err else tv
        cards.append({
            "lote":       "B",
            "latex":      op["latex"],
            "result":     tv,
            "sensor_val": sv,
            "has_error":  has_err,
            "scale":      op["scale"],
        })
    return cards


def build_lote_b(n: int, rate: float = ERROR_RATE) -> list:
    n_err = round(n * rate)
    flags = [True] * n_err + [False] * (n - n_err)
    random.shuffle(flags)
    
    cards = []
    used_latex = set()
    for has_err in flags:
        # Intentar generar una operación única
        while True:
            op = generate_operation()
            if op["latex"] not in used_latex:
                used_latex.add(op["latex"])
                break
        
        tv = op["result"]
        sv = apply_error(tv) if has_err else tv
        cards.append({
            "lote":       "B",
            "latex":      op["latex"],
            "result":     tv,
            "sensor_val": sv,
            "has_error":  has_err,
            "scale":      op["scale"],
        })
    return cards


# ══════════════════════════════════════════════════════════════════
#  PREÁMBULO LaTeX
# ══════════════════════════════════════════════════════════════════

PREAMBLE = r"""% circuito_triage.tex  —  generado con generar_circuito_v2.py
% Compilar con:  pdflatex circuito_triage.tex
\documentclass[a4paper]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[a4paper,
  top=6mm, bottom=6mm, left=6mm, right=6mm,
  includehead=false, includefoot=false]{geometry}
\usepackage{amsmath}
\usepackage{array}          % columnas @{} en tabular y array
\usepackage{tikz}
\usepackage[most]{tcolorbox}

\pagestyle{empty}

% ── Dimensiones de tarjeta ────────────────────────────────────────
%   Ancho útil  ≈ 210−12 = 198 mm  →  2 col →  99 mm  (usamos 98)
%   Alto útil   ≈ 297−12 = 285 mm  →  4 fil →  71 mm  (usamos 70)
\newlength{\cardW}  \setlength{\cardW}{98mm}
\newlength{\cardH}  \setlength{\cardH}{70mm}

% ── Recuadro de corte punteado ────────────────────────────────────
\newcommand{\cutframe}[1]{%
  \begin{tikzpicture}
    \draw[black!35, dashed, line width=0.35pt]
      (0,0) rectangle (\cardW,\cardH);
    \node[inner sep=0pt] at (0.5\cardW,0.5\cardH) {#1};
  \end{tikzpicture}%
}
"""

# ══════════════════════════════════════════════════════════════════
#  ESTILOS tcolorbox (blanco y negro)
# ══════════════════════════════════════════════════════════════════

_BASE = (
    "enhanced, colback=white, colframe=black, arc=3pt, "
    "width=\\cardW-2.5mm, height=\\cardH-2.5mm"
)

STYLE_A = _BASE + (
    ", boxrule=0.7pt"
    ", halign=center, valign=center"
)

# Tarjetas B: bicolor split con \tcblower  ──────────────────────
# upper  → operación (centrada vertical)
# lower  → resultado del sensor (centrada vertical)
# Línea de separación gris clara entre las dos mitades
_BASE_B_OLD = (
    _BASE
    + ", bicolor, colback=white, colbacklower=white" # 
    + ", halign=center,       valign=center"
    + ", halign lower=center, valign lower=center"
    + ", segmentation style={solid, black!30, line width=0.6pt}" # Línea divisora visible
)

_BASE_B = (
    _BASE
    + ", halign=center,       valign=center"
    + ", halign lower=center, valign lower=center"
    + ", segmentation style={solid, black!30, line width=0.6pt}"
)

STYLE_B_OK  = _BASE_B + ", boxrule=0.7pt"
STYLE_B_ERR = _BASE_B + ", boxrule=0.7pt"


# ══════════════════════════════════════════════════════════════════
#  RENDERIZADORES DE TARJETA
# ══════════════════════════════════════════════════════════════════

def _op_size(scale: str, upper: bool) -> str:
    """
    upper=True  → tamaño para la operación en tarjeta Lote A (grande)
    upper=False → tamaño para la operación en tarjeta Lote B (algo menor)
    """
    return r"\Huge"
    return r"\Huge" if scale == "huge" else r"\Large"
    if upper:
        return r"\Huge"  if scale == "huge" else r"\Large"
    else:
        return r"\LARGE" if scale == "huge" else r"\large"


def tex_card_a(card: dict) -> str:
    """Tarjeta Lote A: solo la operación matemática."""
    sz = _op_size(card.get("scale", "huge"), upper=True)
    inner = (
        rf"\begin{{tcolorbox}}[{STYLE_A}]"
        "\n"
        rf"  {{{sz} $\displaystyle {card['latex']}$}}"
        "\n"
        r"\end{tcolorbox}"
    )
    return rf"\cutframe{{{inner}}}" + "\n"


def tex_card_b_old(card: dict) -> str:
    """
    Tarjeta Lote B: operación (mitad superior) +
    resultado del sensor (mitad inferior).
    El uso de \\tcblower evita solapamiento entre las dos zonas.
    """
    scale  = card.get("scale", "huge")
    op_sz  = _op_size(scale, upper=False)
    sensor = fmt_sci(card["sensor_val"], sig=2)
    style  = STYLE_B_ERR if card["has_error"] else STYLE_B_OK

    inner = (
        rf"\begin{{tcolorbox}}[{style}]"
        "\n"
        rf"  {{{op_sz} $\displaystyle {card['latex']}$}}"
        "\n"
        r"\tcblower"
        "\n"
        r"  {\small\bfseries Resultado del Sensor:}\\[5pt]"
        "\n"
        rf"  {{\Huge\bfseries ${sensor}$}}"
        "\n"
        r"\end{tcolorbox}"
    )
    return rf"\cutframe{{{inner}}}" + "\n"

def tex_card_b(card: dict) -> str:
    """
    Generates Lote B cards with the label in the corner and centered number.
    Fixes the 'No shape named lower' error by using 'segmentation' node.
    """
    sz     = r"\Huge"
    sensor = fmt_sci(card["sensor_val"], sig=2)
    style  = STYLE_B_ERR if card["has_error"] else STYLE_B_OK

    # Etiqueta para el resultado
    label_latex = r"{\scriptsize\bfseries Resultado del Sensor:}"
    
    # CAMBIO CLAVE: Usamos (segmentation.south west) en lugar de (lower.north west)
    overlay_cmd = rf"overlay={{\node[anchor=north west, xshift=2.5mm, yshift=-1.5mm] at (segmentation.south west) {{{label_latex}}};}}"

    inner = (
        rf"\begin{{tcolorbox}}[{style}, {overlay_cmd}]"
        "\n"
        # Parte superior: Altura fija de 30mm para la ecuación
        rf"  \begin{{minipage}}[c][30mm][c]{{\linewidth}}"
        rf"    \centering {sz} $\displaystyle {card['latex']}$\par"
        rf"  \end{{minipage}}"
        "\n"
        r"\tcblower"
        "\n"
        # Parte inferior: Altura fija de 30mm para el valor del sensor
        rf"  \begin{{minipage}}[c][30mm][c]{{\linewidth}}"
        rf"    \centering {{{sz}\bfseries ${sensor}$}}"
        rf"  \end{{minipage}}"
        "\n"
        r"\end{tcolorbox}"
    )
    return rf"\cutframe{{{inner}}}" + "\n"


# ══════════════════════════════════════════════════════════════════
#  MAQUETACIÓN: grilla 2 × 4  (8 tarjetas por página)
# ══════════════════════════════════════════════════════════════════

def cards_to_latex(cards: list) -> str:
    """
    Vuelca la lista de tarjetas en una grilla 2×4.
    \\newpage solo ENTRE páginas → nunca se genera hoja en blanco.
    """
    per_page = 8
    per_row  = 2
    chunks   = [cards[i:i + per_page] for i in range(0, len(cards), per_page)]
    lines    = []

    for idx, chunk in enumerate(chunks):
        cells = [
            tex_card_a(c) if c["lote"] == "A" else tex_card_b(c)
            for c in chunk
        ]
        # Relleno para completar la última fila
        while len(cells) % per_row != 0:
            cells.append(
                r"\begin{tikzpicture}"
                r"\useasboundingbox (0,0) rectangle (\cardW,\cardH);"
                r"\end{tikzpicture}" + "\n"
            )

        lines.append(r"{\centering")
        lines.append(r"\begin{tabular}{@{}cc@{}}")
        rows = [cells[i:i + per_row] for i in range(0, len(cells), per_row)]
        for row in rows:
            lines.append("  " + " & ".join(c.rstrip() for c in row) + r" \\[0pt]")
        lines.append(r"\end{tabular}\par}")

        # \newpage solo entre páginas, NUNCA al final del último bloque
        if idx < len(chunks) - 1:
            lines.append(r"\newpage")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
#  ENSAMBLADO DEL DOCUMENTO
# ══════════════════════════════════════════════════════════════════

def build_document(lote_a: list, lote_b: list) -> str:
    n_err = sum(1 for c in lote_b if c["has_error"])
    header = (
        f"% Lote A: {len(lote_a)} tarjetas (solo operación)\n"
        f"% Lote B: {len(lote_b)} tarjetas "
        f"({n_err} con error de magnitud, "
        f"{len(lote_b) - n_err} correctas)\n"
    )
    body_a = cards_to_latex(lote_a)
    body_b = cards_to_latex(lote_b)

    return (
        header
        + PREAMBLE
        + r"\begin{document}" + "\n"
        + body_a
        + "\n\\newpage\n"   # único salto entre Lote A y Lote B
        + body_b
        + "\n"
        + r"\end{document}" + "\n"
    )


# ══════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════

def main():
    print("Generando operaciones...")
    lote_a = build_lote_a(NUM_CARDS)
    lote_b = build_lote_b(NUM_CARDS)

    n_err = sum(1 for c in lote_b if c["has_error"])
    print(f"  Lote A: {len(lote_a)} tarjetas")
    print(f"  Lote B: {len(lote_b)} tarjetas "
          f"({n_err} con error, {len(lote_b)-n_err} correctas)")

    print(f"\nEscribiendo {OUTPUT}...")
    doc = build_document(lote_a, lote_b)
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(doc)

    kb = os.path.getsize(OUTPUT) / 1024
    print(f"  → {OUTPUT}  ({kb:.1f} KB)")
    print("\nCompilar con:  pdflatex circuito_triage.tex")


if __name__ == "__main__":
    main()
