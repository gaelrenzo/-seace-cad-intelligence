"""
MÓDULO: seace_cad_intelligence/cad_bridge/export_manager.py
Coordinador de exportación de código CAD según especificaciones del proyecto.
"""

import os
from typing import Dict, Any
from .parametric_flange import FlangeParametricGenerator
from .parametric_shaft import SteppedShaftParametricGenerator
from .parametric_chassis import StructuralSkidParametricGenerator


class CADCodeExporter:
    """Fábrica y exportador de scripts CAD paramétricos."""

    @classmethod
    def generar_codigo(cls, tipo_componente: str, params: Dict[str, Any] = None) -> str:
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

        else:
            raise ValueError(f"Componente '{tipo_componente}' no reconocido. Tipos disponibles: brida, eje, skid.")

    @classmethod
    def guardar_script(cls, tipo_componente: str, ruta_salida: str, params: Dict[str, Any] = None) -> str:
        codigo = cls.generar_codigo(tipo_componente, params)
        os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(codigo)
        print(f"[CAD Exporter] Script paramétrico guardado en: {ruta_salida}")
        return ruta_salida
