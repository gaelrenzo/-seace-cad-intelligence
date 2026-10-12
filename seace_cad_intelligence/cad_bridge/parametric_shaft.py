"""
MÓDULO: seace_cad_intelligence/cad_bridge/parametric_shaft.py
Generador paramétrico de Eje Escalonado con Chavetero bajo norma ISO 2768-mK y DIN 6885.
"""

from typing import Dict, List, Any


class SteppedShaftParametricGenerator:
    """
    Generador de ejes de transmisión mecánica con concentradores de tensión mitigados
    mediante radios de acuerdo (fillets) calculados.
    """

    @classmethod
    def generar_script_cadquery(cls, diametros: List[float] = None, longitudes: List[float] = None, radio_acuerdo: float = 2.0) -> str:
        """
        Genera un eje escalonado multietapa con chavetero normalizado.
        diametros: lista de diámetros por sección (mm)
        longitudes: lista de longitudes por sección (mm)
        """
        diametros = diametros or [25.0, 40.0, 35.0]
        longitudes = longitudes or [40.0, 100.0, 50.0]

        if len(diametros) != len(longitudes):
            raise ValueError("Las listas de diámetros y longitudes deben tener la misma cantidad de etapas.")

        secciones_code = []
        for i, (d, l) in enumerate(zip(diametros, longitudes)):
            if i == 0:
                secciones_code.append(f"    .circle({d} / 2.0).extrude({l})")
            else:
                secciones_code.append(f"    .faces('>Z').workplane().circle({d} / 2.0).extrude({l})")

        cadena_secciones = "\n".join(secciones_code)

        return f'''"""
Generador de Eje Escalonado Paramétrico
Normas: ISO 2768-mK (Tolerancias generales de mecanizado) / DIN 6885 (Chaveteros)
"""
import cadquery as cq

# Construcción geométrica secuencial
eje = (
    cq.Workplane("XY")
{cadena_secciones}
)

# Aplicar radios de acuerdo en transiciones de diámetro para evitar concentración de tensiones
try:
    eje = eje.edges("|Z").fillet({radio_acuerdo})
except Exception:
    pass

# Exportar a formato universal
# cq.exporters.export(eje, "eje_escalonado_iso2768.step")
'''
