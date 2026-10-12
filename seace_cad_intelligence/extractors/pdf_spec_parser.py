"""
MÓDULO: seace_cad_intelligence/extractors/pdf_spec_parser.py
Parser especializado para expedientes técnicos, bases integradas y TDRs en PDF.
"""

import os
import re
from typing import Dict, List, Any
from ..core.analyzer import EngineeringIntelligenceEngine
from ..core.models import RequisitoTecnico


class TechnicalPDFParser:
    """Extrae el Capítulo III (Requerimientos Técnicos Mínimos) y tablas de metrados."""

    @classmethod
    def extraer_texto_completo(cls, ruta_pdf: str) -> str:
        """Extrae el contenido textual del PDF utilizando pdfplumber o pypdf."""
        if not os.path.exists(ruta_pdf):
            raise FileNotFoundError(f"Archivo PDF no encontrado: {ruta_pdf}")

        texto_acumulado = []
        try:
            import pdfplumber
            with pdfplumber.open(ruta_pdf) as pdf:
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        texto_acumulado.append(texto)
        except ImportError:
            # Fallback simple si no está instalado pdfplumber
            try:
                import pypdf
                lector = pypdf.PdfReader(ruta_pdf)
                for pagina in lector.pages:
                    texto_acumulado.append(pagina.extract_text() or "")
            except ImportError:
                print("[PDF Parser] Advertencia: Instale pdfplumber para extracción completa de PDFs.")
                return ""

        return "\n".join(texto_acumulado)

    @classmethod
    def extraer_capitulo_tecnico(cls, texto_completo: str) -> str:
        """
        Localiza la sección técnica típica de las bases del SEACE:
        'CAPÍTULO III: REQUERIMIENTO' o 'ESPECIFICACIONES TÉCNICAS'
        """
        patron = re.compile(
            r'(CAP[ÍI]TULO\s+III[:\s]+(?:REQUERIMIENTO|ESPECIFICACIONES\s+T[ÉE]CNICAS|T[ÉE]RMINOS\s+DE\s+REFERENCIA).*?)(?:CAP[ÍI]TULO\s+IV|\Z)',
            re.IGNORECASE | re.DOTALL
        )
        match = patron.search(texto_completo)
        if match:
            return match.group(1)
        # Si no detecta el encabezado exacto, retorna todo el texto para análisis heurístico
        return texto_completo

    @classmethod
    def analizar_expediente(cls, ruta_pdf: str) -> Dict[str, Any]:
        """Procesa un PDF de expediente y extrae normas, tolerancias y magnitudes."""
        texto = cls.extraer_texto_completo(ruta_pdf)
        seccion_tecnica = cls.extraer_capitulo_tecnico(texto)

        normas = EngineeringIntelligenceEngine.extraer_normas(seccion_tecnica)
        disciplina = EngineeringIntelligenceEngine.clasificar_disciplina(seccion_tecnica)
        requisitos = EngineeringIntelligenceEngine.extraer_requisitos_tecnicos(seccion_tecnica)

        return {
            "archivo": os.path.basename(ruta_pdf),
            "disciplina": disciplina,
            "normas": normas,
            "total_requisitos": len(requisitos),
            "requisitos": [r.__dict__ for r in requisitos[:30]], # Muestra de los primeros 30
            "extracto_texto": seccion_tecnica[:1500]
        }
