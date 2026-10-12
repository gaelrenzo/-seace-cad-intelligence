"""
MÓDULO: tests/test_integrations.py
Pruebas automatizadas de las integraciones con repositorios especializados:
- ocdskit (OCDS Package Bridge)
- docling / pdfplumber (Advanced Document Miner)
- seace-scraper (Batch Parameters Engine)
- build123d / cadquery (Parametric Electrical Cabinet)
"""

import os
import json
import pytest
from seace_cad_intelligence.integrations.ocdskit_bridge import OCDSPackageBridge
from seace_cad_intelligence.integrations.docling_bridge import AdvancedDocumentMiner
from seace_cad_intelligence.integrations.seace_scraper_engine import BatchSEACEScraperEngine
from seace_cad_intelligence.cad_bridge.parametric_enclosure import ElectricalEnclosureParametricGenerator
from seace_cad_intelligence.cad_bridge.export_manager import CADCodeExporter


def test_ocdskit_bridge_unpack(tmp_path):
    # Crear un release OCDS simulado según el estándar
    ocds_dummy = {
        "releases": [
            {
                "ocid": "ocds-k50g02-SEACE-2025-01",
                "id": "rel-01",
                "tender": {
                    "title": "ADQUISICION DE MOTOBOMBAS Y TUBERIAS ASME B31.3",
                    "description": "Bombas centrífugas 50 HP y bridas ASME B16.5",
                    "value": {"amount": 450000.0, "currency": "PEN"},
                    "datePublished": "2025-02-10T10:00:00Z",
                    "documents": [
                        {"title": "Bases Integradas", "url": "https://seace.gob.pe/doc1.pdf"}
                    ]
                },
                "buyer": {"name": "MUNICIPALIDAD PROVINCIAL DE PUNO"},
                "awards": [
                    {
                        "status": "active",
                        "value": {"amount": 440000.0},
                        "date": "2025-03-01",
                        "suppliers": [{"name": "HIDROINGENIERIA S.A.C.", "id": "20448899112"}]
                    }
                ]
            }
        ]
    }
    json_path = os.path.join(tmp_path, "ocds_sample.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ocds_dummy, f)

    proyectos = OCDSPackageBridge.procesar_archivo_ocds(json_path)
    assert len(proyectos) == 1
    p = proyectos[0]
    assert p.id_referencia == "ocds-k50g02-SEACE-2025-01"
    assert p.entidad_o_cliente == "MUNICIPALIDAD PROVINCIAL DE PUNO"
    assert p.postor_ganador == "HIDROINGENIERIA S.A.C."
    assert p.monto_adjudicado == 440000.0
    assert "ASME B31.3" in p.normas_identificadas
    assert "ASME B16.5" in p.normas_identificadas


def test_docling_desglose_materiales():
    texto = "Se empleará plancha de ACERO ESTRUCTURAL ASTM A36 y perfiles de ACERO INOXIDABLE AISI 304."
    mats = AdvancedDocumentMiner.desglosar_especificaciones_materiales(texto)
    assert len(mats) >= 1
    tipos = [m["tipo_material"] for m in mats]
    assert "ACERO" in tipos


def test_seace_scraper_batch_template(tmp_path):
    csv_path = os.path.join(tmp_path, "params.csv")
    BatchSEACEScraperEngine.generar_plantilla_parametros(csv_path)
    assert os.path.exists(csv_path)
    params = BatchSEACEScraperEngine.cargar_matriz_parametros(csv_path)
    assert len(params) >= 3
    assert params[0].anio == "2025"


def test_parametric_enclosure_cad():
    # CadQuery
    codigo_cq = ElectricalEnclosureParametricGenerator.generar_script_cadquery(1200, 800, 400)
    assert "IEC 61439" in codigo_cq
    assert "cadquery as cq" in codigo_cq

    # build123d
    codigo_b123 = ElectricalEnclosureParametricGenerator.generar_script_build123d(1200, 800, 400)
    assert "build123d" in codigo_b123

    # Export manager routing
    codigo_exp = CADCodeExporter.generar_codigo("tablero", {"alto": 1000}, motor="build123d")
    assert "from build123d import *" in codigo_exp
