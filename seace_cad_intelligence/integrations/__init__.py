"""
MÓDULO: seace_cad_intelligence/integrations/__init__.py
Integraciones avanzadas con librerías y repositorios especializados:
- ocdskit: Ingestión del Estándar de Contrataciones Abiertas (OCDS).
- docling & pdfplumber: Minería profunda de tablas y especificaciones en PDFs.
- seace_scraper_engine: Motor de scraping batch con matriz de parámetros.
"""

from .ocdskit_bridge import OCDSPackageBridge
from .docling_bridge import AdvancedDocumentMiner
from .seace_scraper_engine import BatchSEACEScraperEngine

__all__ = [
    "OCDSPackageBridge",
    "AdvancedDocumentMiner",
    "BatchSEACEScraperEngine"
]
