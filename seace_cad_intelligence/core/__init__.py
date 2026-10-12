"""Módulo Core: Modelos, contratos y analizadores del framework."""
from .models import ProyectoIngenieria, RequisitoTecnico, DocumentoAdjunto
from .adapters import BaseDataSourceAdapter
from .analyzer import EngineeringIntelligenceEngine

__all__ = [
    "ProyectoIngenieria",
    "RequisitoTecnico",
    "DocumentoAdjunto",
    "BaseDataSourceAdapter",
    "EngineeringIntelligenceEngine",
]
