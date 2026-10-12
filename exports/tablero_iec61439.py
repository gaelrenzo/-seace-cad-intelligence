"""
Gabinete Eléctrico Paramétrico con build123d
Norma: IEC 61439-1/2
"""
from build123d import *

alto = 1200.0
ancho = 800.0
prof = 400.0
t = 2.0

with BuildPart() as gabinete:
    # Carcasa
    Box(ancho, prof, alto)
    # Vaciado frontal
    with BuildPart(mode=Mode.SUBTRACT):
        with Locations(Location((0, t, 0))):
            Box(ancho - 2 * t, prof, alto - 2 * t)

# export_step(gabinete.part, "gabinete_build123d.step")
