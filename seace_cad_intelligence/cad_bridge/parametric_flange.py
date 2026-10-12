"""
MÓDULO: seace_cad_intelligence/cad_bridge/parametric_flange.py
Generador paramétrico de Bridas bajo norma ASME B16.5 / ISO 7005.
"""

from typing import Dict, Any


class FlangeParametricGenerator:
    """
    Modelo matemático y paramétrico de Brida Slip-On / Welding Neck ASME B16.5 (Clase 150).
    Dimensiones en milímetros según tabla estandarizada.
    """

    # Dimensiones estándar ASME B16.5 Clase 150 (en mm)
    # [O: Diámetro exterior, C: Círculo de pernos, t: Espesor, d_hole: Diám. barrenos, holes: N° barrenos, d_bore: Diám. interior]
    TABLA_ASME_B16_5_CLASE_150: Dict[str, Dict[str, float]] = {
        "1/2": {"O": 88.9,  "C": 60.3,  "t": 11.1, "d_hole": 15.9, "holes": 4, "d_bore": 22.2},
        "1":   {"O": 108.0, "C": 79.4,  "t": 14.3, "d_hole": 15.9, "holes": 4, "d_bore": 34.9},
        "2":   {"O": 152.4, "C": 120.7, "t": 19.1, "d_hole": 19.1, "holes": 4, "d_bore": 62.0},
        "3":   {"O": 190.5, "C": 152.4, "t": 23.8, "d_hole": 19.1, "holes": 4, "d_bore": 90.7},
        "4":   {"O": 228.6, "C": 190.5, "t": 23.8, "d_hole": 19.1, "holes": 8, "d_bore": 116.1},
        "6":   {"O": 279.4, "C": 241.3, "t": 25.4, "d_hole": 22.2, "holes": 8, "d_bore": 170.7},
    }

    @classmethod
    def obtener_parametros(cls, nps: str = "2") -> Dict[str, float]:
        """Retorna las dimensiones dimensionalmente exactas según tamaño nominal."""
        if nps not in cls.TABLA_ASME_B16_5_CLASE_150:
            raise ValueError(f"NPS '{nps}' no está en la tabla estándar. Disponibles: {list(cls.TABLA_ASME_B16_5_CLASE_150.keys())}")
        return cls.TABLA_ASME_B16_5_CLASE_150[nps]

    @classmethod
    def generar_script_cadquery(cls, nps: str = "2") -> str:
        """Genera el código ejecutable de CadQuery listo para compilar a STEP/STL."""
        p = cls.obtener_parametros(nps)
        return f'''"""
Generador paramétrico de Brida ASME B16.5 Clase 150 NPS {nps}"
Validación dimensional: Exactitud bajo estándar internacional ASME.
"""
import cadquery as cq

# Parámetros nominales en mm
DIAMETRO_EXT = {p["O"]}
CIRCULO_PERNOS = {p["C"]}
ESPESOR = {p["t"]}
DIAMETRO_BARRENO = {p["d_hole"]}
NUM_BARRENOS = {int(p["holes"])}
DIAMETRO_INTERIOR = {p["d_bore"]}

# Construcción de geometría sólida
brida = (
    cq.Workplane("XY")
    .circle(DIAMETRO_EXT / 2.0)
    .extrude(ESPESOR)
    # Agujero pasante de tubería (Bore)
    .faces(">Z").workplane()
    .circle(DIAMETRO_INTERIOR / 2.0)
    .cutThruAll()
    # Distribución polar de pernos
    .faces(">Z").workplane()
    .polarArray(radius=CIRCULO_PERNOS / 2.0, startAngle=0, angle=360, count=NUM_BARRENOS)
    .circle(DIAMETRO_BARRENO / 2.0)
    .cutThruAll()
)

# Exportar a formato estándar interoperable
# cq.exporters.export(brida, "brida_asme_{nps.replace('/', '_')}_clase150.step")
'''
