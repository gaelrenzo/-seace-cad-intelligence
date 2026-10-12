"""
MÓDULO: seace_cad_intelligence/cad_bridge/export_manager.py
Coordinador de exportación de código CAD según especificaciones del proyecto.
"""

import os
from typing import Dict, Any
from .parametric_flange import FlangeParametricGenerator
from .parametric_shaft import SteppedShaftParametricGenerator
from .parametric_chassis import StructuralSkidParametricGenerator
from .parametric_enclosure import ElectricalEnclosureParametricGenerator
from .parametric_primary_line import PrimaryLineParametricGenerator


class CADCodeExporter:
    """Fábrica y exportador de scripts CAD paramétricos (CadQuery / build123d) y DXF."""

    @classmethod
    def generar_codigo(cls, tipo_componente: str, params: Dict[str, Any] = None, motor: str = "cadquery") -> str:
        params = params or {}
        tipo = tipo_componente.lower()

        if "flange" in tipo or "brida" in tipo:
            nps = str(params.get("nps", "2"))
            return FlangeParametricGenerator.generar_script_cadquery(nps)

        elif "shaft" in tipo or "eje" in tipo:
            diametros = params.get("diametros", [25.0, 40.0, 35.0])
            longitudes = params.get("longitudes", [40.0, 100.0, 50.0])
            return SteppedShaftParametricGenerator.generar_script_cadquery(diametros, longitudes)

        elif "chassis" in tipo or "skid" in tipo or "bastidor" in tipo:
            largo = float(params.get("largo", 1200.0))
            ancho = float(params.get("ancho", 600.0))
            alto = float(params.get("alto", 100.0))
            return StructuralSkidParametricGenerator.generar_script_cadquery(largo, ancho, alto)

        elif "enclosure" in tipo or "tablero" in tipo or "gabinete" in tipo:
            alto = float(params.get("alto", 1200.0))
            ancho = float(params.get("ancho", 800.0))
            prof = float(params.get("profundidad", 400.0))
            if motor.lower() == "build123d":
                return ElectricalEnclosureParametricGenerator.generar_script_build123d(alto, ancho, prof)
            return ElectricalEnclosureParametricGenerator.generar_script_cadquery(alto, ancho, prof)

        elif "poste" in tipo or "cac" in tipo:
            modelo = str(params.get("modelo", "12/400"))
            return PrimaryLineParametricGenerator.generar_script_poste_cac(modelo)

        elif "ps1" in tipo or "ps-1" in tipo or "suspension" in tipo:
            return PrimaryLineParametricGenerator.generar_script_armado_ps1()

        elif "pa1" in tipo or "pa-1" in tipo or "angulo" in tipo:
            return PrimaryLineParametricGenerator.generar_script_armado_pa1()

        elif "pr1" in tipo or "pr-1" in tipo or "retencion" in tipo:
            return PrimaryLineParametricGenerator.generar_script_armado_pr1()

        elif "sab1" in tipo or "sab-1" in tipo or "sed" in tipo:
            return PrimaryLineParametricGenerator.generar_script_armado_sab1()

        elif "retenida" in tipo or "r1" in tipo or "r-1" in tipo:
            return PrimaryLineParametricGenerator.generar_script_retenida_r1()

        else:
            raise ValueError(f"Componente '{tipo_componente}' no reconocido. Tipos disponibles: brida, eje, skid, tablero, poste, ps1, pa1, pr1, sab1, retenida.")

    @classmethod
    def guardar_script(cls, tipo_componente: str, ruta_salida: str, params: Dict[str, Any] = None) -> str:
        codigo = cls.generar_codigo(tipo_componente, params)
        os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(codigo)
        print(f"[CAD Exporter] Script paramétrico guardado en: {ruta_salida}")
        return ruta_salida

    @classmethod
    def exportar_dxf(cls, tipo_componente: str, ruta_salida: str, params: Dict[str, Any] = None) -> str:
        """Exporta archivo DXF 2D/3D directamente compatible con AutoCAD."""
        return PrimaryLineParametricGenerator.exportar_dxf_armado(tipo_componente, ruta_salida, params)

