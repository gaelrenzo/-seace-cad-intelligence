"""Módulo CAD: Generadores paramétricos y exportadores de geometría."""
from .parametric_flange import FlangeParametricGenerator
from .parametric_shaft import SteppedShaftParametricGenerator
from .parametric_chassis import StructuralSkidParametricGenerator
from .parametric_enclosure import ElectricalEnclosureParametricGenerator
from .export_manager import CADCodeExporter

__all__ = [
    "FlangeParametricGenerator",
    "SteppedShaftParametricGenerator",
    "StructuralSkidParametricGenerator",
    "ElectricalEnclosureParametricGenerator",
    "CADCodeExporter"
]
