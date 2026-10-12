"""
MÓDULO: seace_cad_intelligence/cad_bridge/parametric_chassis.py
Generador de Skid / Bastidor Estructural para equipos electromecánicos bajo AISC 360 / ISO.
"""

from typing import Dict, Any


class StructuralSkidParametricGenerator:
    """Generador paramétrico de bancada estructural para motobombas, generadores o transformadores."""

    @classmethod
    def generar_script_cadquery(cls, largo: float = 1200.0, ancho: float = 600.0, alto_perfil: float = 100.0, espesor: float = 6.0) -> str:
        return f'''"""
Generador paramétrico de Bastidor / Skid para Equipo Electromecánico
Norma: AISC 360 / NTP 350.021 (Estructuras de acero)
Dimensiones principales: {largo} x {ancho} x {alto_perfil} mm
"""
import cadquery as cq

LARGO = {largo}
ANCHO = {ancho}
ALTO_VIGA = {alto_perfil}
ESPESOR = {espesor}

# Construcción de base perimetral
skid = (
    cq.Workplane("XY")
    .box(LARGO, ANCHO, ALTO_VIGA)
    .faces(">Z").workplane()
    # Vaciado interior para simular perfiles huecos o vigas
    .rect(LARGO - (2 * ESPESOR), ANCHO - (2 * ESPESOR))
    .cutThruAll()
)

# Barrenos de anclaje a cimentación de concreto (4 esquinas)
DIST_BORDE = 50.0
DIAMETRO_PERNO = 18.0 # Pernos de anclaje de 5/8"

skid = (
    skid.faces("<Z").workplane()
    .rect(LARGO - (2 * DIST_BORDE), ANCHO - (2 * DIST_BORDE), forConstruction=True)
    .vertices()
    .circle(DIAMETRO_PERNO / 2.0)
    .cutThruAll()
)

# Exportación
# cq.exporters.export(skid, "skid_estructural.step")
'''
