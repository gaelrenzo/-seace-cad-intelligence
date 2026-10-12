"""
MÓDULO: seace_cad_intelligence/core/models.py
Entidades de dominio enriquecidas para ingeniería multidisciplinaria.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RequisitoTecnico:
    """Representa una restricción dimensional o parámetro técnico verificado."""
    parametro: str                          # ej: "Diámetro nominal", "Potencia", "Presión"
    valor_nominal: float                    # ej: 50.8, 15.0, 150.0
    unidad: str                             # ej: "mm", "HP", "PSI"
    tolerancia_superior: float = 0.0        # ej: +0.05
    tolerancia_inferior: float = 0.0        # ej: -0.05
    norma_asociada: Optional[str] = None    # ej: "ISO 2768-mK", "ASME B16.5"
    observaciones: Optional[str] = None


@dataclass
class DocumentoAdjunto:
    """Documento descargado o asociado al expediente técnico."""
    tipo: str                               # "Bases Integradas", "TDR", "Planos", "Resumen Ejecutivo"
    ruta_local: str
    url_origen: Optional[str] = None
    fecha_descarga: datetime = field(default_factory=datetime.now)


@dataclass
class ProyectoIngenieria:
    """Entidad principal de un proyecto (adjudicado o de referencia)."""
    id_referencia: str                      # Nomenclatura o código único de convocatoria
    fuente_origen: str                      # "SEACE", "OCDS", "EXPEDIENTE_LOCAL"
    titulo_proyecto: str
    disciplina: str                         # "Mecanica", "Electrica", "Automatizacion", "Civil", "Multidisciplinario"
    entidad_o_cliente: str
    presupuesto_referencial: float
    monto_adjudicado: float = 0.0
    postor_ganador: Optional[str] = None
    ruc_ganador: Optional[str] = None
    moneda: str = "PEN"
    fecha_convocatoria: Optional[str] = None
    fecha_adjudicacion: Optional[str] = None

    # Conocimiento técnico extraído
    normas_identificadas: List[str] = field(default_factory=list)
    requisitos: List[RequisitoTecnico] = field(default_factory=list)
    documentos: List[DocumentoAdjunto] = field(default_factory=list)
    metadatos_extra: Dict[str, Any] = field(default_factory=dict)
    fecha_registro: datetime = field(default_factory=datetime.now)

    def ratio_adjudicacion(self) -> float:
        """Calcula el porcentaje respecto al valor referencial."""
        if self.presupuesto_referencial > 0:
            return round((self.monto_adjudicado / self.presupuesto_referencial) * 100.0, 2)
        return 0.0
