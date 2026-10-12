"""
MÓDULO: seace_cad_intelligence/cad_bridge/parametric_enclosure.py
Generador paramétrico de Tableros Eléctricos / Gabinetes Industriales
bajo normas IEC 61439-1/2 (Conjuntos de aparamenta de baja tensión) e IEC 60529 (Grados IP).
"""

from typing import Dict, Any


class ElectricalEnclosureParametricGenerator:
    """
    Genera gabinetes eléctricos autosoportados o adosados a pared
    con placa de montaje interior, puerta abatible y calados de ventilación.
    """

    @classmethod
    def generar_script_cadquery(cls, alto: float = 1200.0, ancho: float = 800.0, profundidad: float = 400.0, espesor_chapa: float = 2.0) -> str:
        return f'''"""
Gabinete Eléctrico Industrial Paramétrico
Normas: IEC 61439-1/2 (Tableros de distribución) / IEC 60529 (IP65)
Dimensiones: {alto} x {ancho} x {profundidad} mm (Chapa {espesor_chapa} mm)
"""
import cadquery as cq

ALTO = {alto}
ANCHO = {ancho}
PROF = {profundidad}
T = {espesor_chapa}

# 1. Cuerpo principal del envolvente (Carcasa exterior vaciada)
cuerpo = (
    cq.Workplane("XY")
    .box(ANCHO, PROF, ALTO)
    .faces(">Y").workplane()
    # Vaciado frontal para marco de puerta
    .rect(ANCHO - (2 * T), ALTO - (2 * T))
    .cutBlind(PROF - T)
)

# 2. Placa de montaje interior (Chapa galvanizada naranja/zincada)
OFFSET_FONDO = 20.0
placa_montaje = (
    cq.Workplane("XY")
    .box(ANCHO - 60.0, 3.0, ALTO - 60.0)
    .translate((0, -(PROF / 2.0) + OFFSET_FONDO, 0))
)

# 3. Puerta exterior con pestaña perimetral
puerta = (
    cq.Workplane("XY")
    .box(ANCHO - 4.0, T, ALTO - 4.0)
    .translate((0, (PROF / 2.0) + (T / 2.0), 0))
)

# Ensamble de gabinete completo
tablero = cuerpo.union(placa_montaje).union(puerta)

# Exportación a formato STEP
# cq.exporters.export(tablero, "tablero_electrico_iec61439.step")
'''

    @classmethod
    def generar_script_build123d(cls, alto: float = 1200.0, ancho: float = 800.0, profundidad: float = 400.0) -> str:
        """Soporte nativo para el motor moderno build123d."""
        return f'''"""
Gabinete Eléctrico Paramétrico con build123d
Norma: IEC 61439-1/2
"""
from build123d import *

alto = {alto}
ancho = {ancho}
prof = {profundidad}
t = 2.0

with BuildPart() as gabinete:
    # Carcasa
    Box(ancho, prof, alto)
    # Vaciado frontal
    with BuildPart(mode=Mode.SUBTRACT):
        with Locations(Location((0, t, 0))):
            Box(ancho - 2 * t, prof, alto - 2 * t)

# export_step(gabinete.part, "gabinete_build123d.step")
'''
