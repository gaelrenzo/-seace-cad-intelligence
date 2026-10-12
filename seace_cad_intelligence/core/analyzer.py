"""
MÓDULO: seace_cad_intelligence/core/analyzer.py
Motor de inteligencia analítica para minería de normas y magnitudes dimensionales.
"""

import re
from typing import List, Tuple
from .models import RequisitoTecnico


class EngineeringIntelligenceEngine:
    """Analizador léxico y semántico para textos de TDRs, bases y especificaciones."""

    # Expresión regular para normas internacionales y nacionales
    PATRON_NORMAS = re.compile(
        r'\b(ISO|ASME|ASTM|IEC|IEEE|AWS|DIN|API|NTP|EN|AISC|ACI)\s*[-_./]?\s*([A-Z0-9.\-]+)\b',
        re.IGNORECASE
    )

    # Expresión regular para magnitudes dimensionales y físicas
    # Ejemplo: "50 mm", "150.5 PSI", "440 V", "2.5 HP", "3600 RPM"
    PATRON_MAGNITUDES = re.compile(
        r'(\b[a-zA-ZáéíóúÁÉÍÓÚ\s]{3,25}?)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mm|m|pulg|inch|"|psi|bar|mpa|kw|hp|v|kv|a|rpm|hz|kg|tn|gpm)\b',
        re.IGNORECASE
    )

    # Tolerancias GD&T o dimensionales estándar: ej. +/- 0.5 mm o ±0.02
    PATRON_TOLERANCIAS = re.compile(
        r'(?:±|\+/-|\+\s*0\.\d+\s*/\s*-\s*0\.\d+)\s*(\d+(?:\.\d+)?)\s*(mm|pulg|")?',
        re.IGNORECASE
    )

    @classmethod
    def extraer_normas(cls, texto: str) -> List[str]:
        """Detecta y normaliza todas las normas técnicas mencionadas en el texto."""
        if not texto:
            return []
        coincidencias = cls.PATRON_NORMAS.findall(texto)
        normas_unicas = set()
        for org, codigo in coincidencias:
            # Limpiar caracteres sobrantes
            codigo_limpio = codigo.strip(".,;:()")
            if len(codigo_limpio) >= 2:
                normas_unicas.add(f"{org.upper()} {codigo_limpio.upper()}")
        return sorted(list(normas_unicas))

    @classmethod
    def extraer_requisitos_tecnicos(cls, texto: str) -> List[RequisitoTecnico]:
        """Extrae parámetros numéricos con sus respectivas unidades físicas."""
        if not texto:
            return []
        requisitos: List[RequisitoTecnico] = []
        for prefijo, valor, unidad in cls.PATRON_MAGNITUDES.findall(texto):
            nombre_param = prefijo.strip() if prefijo and len(prefijo.strip()) > 3 else "Dimensión / Parámetro"
            # Limpieza básica
            nombre_param = re.sub(r'[\r\n\t]+', ' ', nombre_param).strip()
            
            requisitos.append(RequisitoTecnico(
                parametro=nombre_param,
                valor_nominal=float(valor),
                unidad=unidad.lower()
            ))
        return requisitos

    @classmethod
    def clasificar_disciplina(cls, texto: str) -> str:
        """Determina la disciplina técnica predominante según palabras clave."""
        texto_lower = texto.lower()
        puntajes = {
            "Mecanica": len(re.findall(r'mecanic|tuberia|valvula|bomba|reductor|brida|soldadura|acero|asme|caldereria', texto_lower)),
            "Electrica": len(re.findall(r'electric|transformador|subestacion|tablero|cable|interruptor|iec|tension|volt', texto_lower)),
            "Automatizacion": len(re.findall(r'scada|plc|control|instrumentacion|sensor|transmisor|variador|lazo', texto_lower)),
            "Civil": len(re.findall(r'concreto|cimentacion|estructura|edificacion|movimiento de tierras|muro|pavimento', texto_lower)),
        }
        disciplina_top = max(puntajes, key=puntajes.get)
        return disciplina_top if puntajes[disciplina_top] > 0 else "Multidisciplinario"
