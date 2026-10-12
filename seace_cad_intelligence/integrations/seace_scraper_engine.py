"""
MÓDULO: seace_cad_intelligence/integrations/seace_scraper_engine.py
Motor de scraping batch inspirado en Ed1123/seace-scraper.
Gestiona colas de búsqueda por matriz de parámetros (parameters.csv)
y automatiza la descarga de fichas y documentos de selección.
"""

import os
import csv
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..core.models import ProyectoIngenieria


@dataclass
class ParametroScrapingBatch:
    anio: str
    objeto: str
    palabra_clave: str
    departamento: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None


class BatchSEACEScraperEngine:
    """
    Orquestador de consultas por lotes.
    Permite definir un archivo de parámetros tipo 'parameters.csv'
    para barrer sistemáticamente múltiples convocatorias del SEACE.
    """

    @classmethod
    def cargar_matriz_parametros(cls, ruta_csv: str) -> List[ParametroScrapingBatch]:
        """Carga la matriz de parámetros de búsqueda desde un archivo CSV."""
        if not os.path.exists(ruta_csv):
            raise FileNotFoundError(f"Archivo de matriz de parámetros no encontrado: {ruta_csv}")

        parametros: List[ParametroScrapingBatch] = []
        with open(ruta_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parametros.append(ParametroScrapingBatch(
                    anio=row.get("anio", "2025").strip(),
                    objeto=row.get("objeto", "Obra").strip(),
                    palabra_clave=row.get("palabra_clave", "").strip(),
                    departamento=row.get("departamento", "").strip() or None,
                    fecha_inicio=row.get("fecha_inicio", "").strip() or None,
                    fecha_fin=row.get("fecha_fin", "").strip() or None
                ))
        return parametros

    @classmethod
    def generar_plantilla_parametros(cls, ruta_salida: str = "parameters_template.csv"):
        """Crea un archivo CSV de ejemplo con parámetros típicos para ingeniería."""
        with open(ruta_salida, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["anio", "objeto", "palabra_clave", "departamento", "fecha_inicio", "fecha_fin"])
            writer.writerow(["2025", "Obra", "ELECTROMECANICO", "LIMA", "01/01/2025", "31/12/2025"])
            writer.writerow(["2025", "Obra", "ESTRUCTURA METALICA", "AREQUIPA", "", ""])
            writer.writerow(["2024", "Bien", "TRANSFORMADOR DE POTENCIA", "PUNO", "", ""])
            writer.writerow(["2024", "Servicio", "MANTENIMIENTO DE BOMBAS", "CUSCO", "", ""])
        print(f"[SEACE Batch Engine] Plantilla de parámetros generada en: {ruta_salida}")
        return ruta_salida
