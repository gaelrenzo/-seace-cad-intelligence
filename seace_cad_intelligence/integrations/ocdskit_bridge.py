"""
MÓDULO: seace_cad_intelligence/integrations/ocdskit_bridge.py
Integración con el estándar OCDS (Open Contracting Data Standard) / ocdskit.
Parsea paquetes de releases (releases) y registros (records) del OECE/OSCE.
"""

import json
import os
from typing import Dict, Any, List, Optional
from ..core.models import ProyectoIngenieria, RequisitoTecnico, DocumentoAdjunto
from ..core.analyzer import EngineeringIntelligenceEngine


class OCDSPackageBridge:
    """
    Procesador compatible con la especificación OCDS 1.1 implementada en
    el Portal de Contrataciones Abiertas de Perú (contratacionesabiertas.oece.gob.pe).
    """

    @classmethod
    def procesar_archivo_ocds(cls, ruta_json: str) -> List[ProyectoIngenieria]:
        """
        Lee y decodifica un archivo JSON (Release Package o Record Package de OCDS).
        Extrae licitaciones (tender), adjudicaciones (awards) y contratos (contracts).
        """
        if not os.path.exists(ruta_json):
            raise FileNotFoundError(f"Archivo OCDS no encontrado: {ruta_json}")

        with open(ruta_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        proyectos: List[ProyectoIngenieria] = []

        # Puede ser un ReleasePackage (lista en 'releases') o RecordPackage (lista en 'records')
        releases = data.get("releases", [])
        if not releases and "records" in data:
            for rec in data["records"]:
                releases.extend(rec.get("releases", []))
                if "compiledRelease" in rec:
                    releases.append(rec["compiledRelease"])

        print(f"[OCDS Kit Bridge] Procesando {len(releases)} entregas (releases)...")

        for rel in releases:
            ocid = rel.get("ocid", rel.get("id", "N/A"))
            tender = rel.get("tender", {})
            titulo = tender.get("title") or tender.get("description") or "Sin título"
            
            # Buyer / Entidad convocante
            buyer = rel.get("buyer", {})
            entidad_nombre = buyer.get("name", "Entidad Pública del Estado")

            # Presupuesto referencial (tender.value)
            val_tender = tender.get("value", {})
            presupuesto_ref = float(val_tender.get("amount", 0.0)) if val_tender else 0.0
            moneda = val_tender.get("currency", "PEN") if val_tender else "PEN"

            # Información de Adjudicaciones (awards)
            awards = rel.get("awards", [])
            monto_adjudicado = 0.0
            ganador_nombre = None
            ganador_ruc = None
            fecha_adjudicacion = None

            for aw in awards:
                if aw.get("status") in ["active", "adjudicado", "consentido"]:
                    val_aw = aw.get("value", {})
                    if val_aw:
                        monto_adjudicado += float(val_aw.get("amount", 0.0))
                    fecha_adjudicacion = aw.get("date")
                    suppliers = aw.get("suppliers", [])
                    if suppliers:
                        ganador_nombre = suppliers[0].get("name")
                        ganador_ruc = suppliers[0].get("id")
                    break

            # Si no hay award activo, tomar el primero si existe
            if not ganador_nombre and awards:
                first_aw = awards[0]
                val_aw = first_aw.get("value", {})
                if val_aw:
                    monto_adjudicado = float(val_aw.get("amount", 0.0))
                fecha_adjudicacion = first_aw.get("date")
                supps = first_aw.get("suppliers", [])
                if supps:
                    ganador_nombre = supps[0].get("name")
                    ganador_ruc = supps[0].get("id")

            # Documentos vinculados (Bases, Términos de Referencia)
            documentos_adjuntos: List[DocumentoAdjunto] = []
            for doc in tender.get("documents", []):
                doc_title = doc.get("title", "Documento")
                doc_url = doc.get("url")
                if doc_url:
                    documentos_adjuntos.append(DocumentoAdjunto(
                        tipo=doc_title,
                        ruta_local="",
                        url_origen=doc_url
                    ))

            # Extracción analítica de normas y requisitos en descripción y títulos
            texto_tecnico = f"{titulo} {tender.get('description', '')}"
            normas = EngineeringIntelligenceEngine.extraer_normas(texto_tecnico)
            disciplina = EngineeringIntelligenceEngine.clasificar_disciplina(texto_tecnico)
            reqs = EngineeringIntelligenceEngine.extraer_requisitos_tecnicos(texto_tecnico)

            proyecto = ProyectoIngenieria(
                id_referencia=ocid,
                fuente_origen="OECE_OCDS_STANDARD",
                titulo_proyecto=titulo,
                disciplina=disciplina,
                entidad_o_cliente=entidad_nombre,
                presupuesto_referencial=presupuesto_ref,
                monto_adjudicado=monto_adjudicado or presupuesto_ref,
                postor_ganador=ganador_nombre or "Pendiente de publicación",
                ruc_ganador=ganador_ruc or "",
                moneda=moneda,
                fecha_convocatoria=tender.get("datePublished"),
                fecha_adjudicacion=fecha_adjudicacion,
                normas_identificadas=normas,
                requisitos=reqs,
                documentos=documentos_adjuntos
            )
            proyectos.append(proyecto)

        print(f"[OCDS Kit Bridge] Se mapearon exitosamente {len(proyectos)} proyectos normalizados.")
        return proyectos
