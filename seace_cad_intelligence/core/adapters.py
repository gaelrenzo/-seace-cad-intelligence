"""
MÓDULO: seace_cad_intelligence/core/adapters.py
Definición abstracta para conectores e ingesta adaptativa.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .models import ProyectoIngenieria


class BaseDataSourceAdapter(ABC):
    """
    Patrón Estrategia (Strategy): Todos los extractores de datos
    (SEACE OCDS, Web Scraper, Carpetas Locales, APIs de terceros)
    deben heredar de esta clase base.
    """

    @abstractmethod
    def inicializar(self, config: Dict[str, Any]) -> bool:
        """Configura credenciales, conexiones o rutas base."""
        pass

    @abstractmethod
    def extraer_proyectos(self, criterios: Dict[str, Any]) -> List[ProyectoIngenieria]:
        """
        Extrae datos y devuelve una lista normalizada de ProyectoIngenieria.
        """
        pass
