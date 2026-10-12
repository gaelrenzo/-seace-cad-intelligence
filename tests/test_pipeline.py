"""
MÓDULO: tests/test_pipeline.py
Pruebas unitarias automatizadas del framework de ingeniería.
"""

import os
import pytest
from seace_cad_intelligence.core.models import ProyectoIngenieria, RequisitoTecnico
from seace_cad_intelligence.core.analyzer import EngineeringIntelligenceEngine
from seace_cad_intelligence.storage.repository import AdaptiveKnowledgeRepository
from seace_cad_intelligence.cad_bridge.parametric_flange import FlangeParametricGenerator
from seace_cad_intelligence.templates.tdr_generator import EngineeringTDRGenerator


def test_extraccion_normas():
    texto = "Se requiere brida según ASME B16.5 Clase 150 y soldadura bajo AWS D1.1, con pintura ISO 12944."
    normas = EngineeringIntelligenceEngine.extraer_normas(texto)
    assert "ASME B16.5" in normas
    assert "AWS D1.1" in normas
    assert "ISO 12944" in normas


def test_extraccion_magnitudes():
    texto = "Diámetro nominal 50 mm, presión de trabajo 150 psi y motor de 15 hp."
    reqs = EngineeringIntelligenceEngine.extraer_requisitos_tecnicos(texto)
    assert len(reqs) >= 3
    unidades = [r.unidad for r in reqs]
    assert "mm" in unidades
    assert "psi" in unidades
    assert "hp" in unidades


def test_generador_brida_asme():
    params = FlangeParametricGenerator.obtener_parametros("2")
    assert params["O"] == 152.4
    assert params["holes"] == 4
    codigo = FlangeParametricGenerator.generar_script_cadquery("2")
    assert "DIAMETRO_EXT = 152.4" in codigo
    assert "cadquery as cq" in codigo


def test_repositorio_y_tdr_generator(tmp_path):
    db_file = os.path.join(tmp_path, "test.db")
    repo = AdaptiveKnowledgeRepository(db_path=db_file)

    p = ProyectoIngenieria(
        id_referencia="TEST-001",
        fuente_origen="TEST",
        titulo_proyecto="PROYECTO DE PRUEBA ELECTROMECANICA",
        disciplina="Mecanica",
        entidad_o_cliente="CLIENTE TEST",
        presupuesto_referencial=100000.0,
        monto_adjudicado=95000.0,
        normas_identificadas=["ISO 2768-M", "ASME B31.3"]
    )
    repo.guardar_proyecto(p)
    recuperado = repo.obtener_por_id("TEST-001")
    assert recuperado is not None
    assert recuperado["monto_adjudicado"] == 95000.0

    tdr = EngineeringTDRGenerator.generar_documento_tdr(
        titulo_nuevo_proyecto="NUEVO TANQUE DE BOMBEO",
        autor="Ing. Renzo",
        disciplina="Mecanica",
        normas_aplicables=["ASME B31.3"],
        requisitos_dimensionales=[{"parametro": "Presion", "valor_nominal": 150, "unidad": "psi"}],
        proyecto_precedente=recuperado
    )
    assert "NUEVO TANQUE DE BOMBEO" in tdr
    assert "TEST-001" in tdr
