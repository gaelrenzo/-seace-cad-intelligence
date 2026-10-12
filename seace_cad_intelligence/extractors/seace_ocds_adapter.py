"""
MÓDULO: seace_cad_intelligence/extractors/seace_ocds_adapter.py
Adaptador para datasets masivos de Adjudicaciones del CONOSCE / OECE (CSV o JSON OCDS).
"""

import os
import pandas as pd
from typing import Any, Dict, List
from ..core.adapters import BaseDataSourceAdapter
from ..core.models import ProyectoIngenieria
from ..core.analyzer import EngineeringIntelligenceEngine


class SEACEOcdsAdapter(BaseDataSourceAdapter):
    """Procesa exportaciones masivas de datos abiertos del OECE (Perú)."""

    def __init__(self):
        self.config: Dict[str, Any] = {}

    def inicializar(self, config: Dict[str, Any]) -> bool:
        self.config = config
        return True

    def extraer_proyectos(self, criterios: Dict[str, Any]) -> List[ProyectoIngenieria]:
        """
        Lee un archivo CSV del OECE (ej. Adjudicaciones_2025.csv) y devuelve
        los proyectos filtrados por palabras clave o montos.
        """
        archivo_fuente = criterios.get("ruta_archivo")
        palabras_clave = criterios.get("palabras_clave", [])
        monto_minimo = criterios.get("monto_minimo", 0.0)

        if not archivo_fuente or not os.path.exists(archivo_fuente):
            print(f"[SEACE OCDS] Archivo no especificado o inexistente: {archivo_fuente}")
            return []

        print(f"[SEACE OCDS] Leyendo dataset masivo: {archivo_fuente}")
        
        # Ensayar separadores usuales en OECE: '|', ';', ','
        df = None
        for sep in ["|", ";", ","]:
            try:
                df = pd.read_csv(archivo_fuente, sep=sep, encoding="latin-1", low_memory=False)
                if len(df.columns) > 3:
                    break
            except Exception:
                continue

        if df is None:
            print("[SEACE OCDS] No se pudo parsear el archivo con las codificaciones esperadas.")
            return []

        # Normalización de encabezados
        df.columns = [c.strip().upper() for c in df.columns]

        # Identificar columnas críticas
        col_desc = next((c for c in df.columns if any(k in c for k in ["DES_OBJETO", "OBJETO", "DESCRIPCION", "TITULO"])), None)
        col_monto = next((c for c in df.columns if any(k in c for k in ["MONTO_ADJUDICADO", "VALOR_ADJUDICADO", "MONTO"])), None)
        col_id = next((c for c in df.columns if any(k in c for k in ["COD_CONVOCATORIA", "ID_PROCESO", "NOMENCLATURA"])), df.columns[0])
        col_entidad = next((c for c in df.columns if "ENTIDAD" in c), "ENTIDAD")
        col_ganador = next((c for c in df.columns if any(k in c for k in ["PROVEEDOR", "GANADOR", "CONTRATISTA"])), "GANADOR")
        col_ruc = next((c for c in df.columns if "RUC" in c), "RUC")

        if not col_desc:
            print("[SEACE OCDS] Error: No se localizó la columna de descripción del objeto.")
            return []

        # Filtrado por expresiones regulares de palabras clave
        if palabras_clave:
            patron = "|".join(palabras_clave)
            df_filtrado = df[df[col_desc].astype(str).str.contains(patron, case=False, na=False)]
        else:
            df_filtrado = df

        proyectos: List[ProyectoIngenieria] = []
        for _, fila in df_filtrado.iterrows():
            descripcion = str(fila.get(col_desc, ""))
            monto_adj = 0.0
            if col_monto and pd.notna(fila.get(col_monto)):
                try:
                    monto_adj = float(str(fila.get(col_monto)).replace(",", "").strip())
                except ValueError:
                    monto_adj = 0.0

            if monto_adj < monto_minimo:
                continue

            # Análisis inteligente de normas y disciplina
            normas = EngineeringIntelligenceEngine.extraer_normas(descripcion)
            disciplina = EngineeringIntelligenceEngine.clasificar_disciplina(descripcion)
            requisitos = EngineeringIntelligenceEngine.extraer_requisitos_tecnicos(descripcion)

            p = ProyectoIngenieria(
                id_referencia=str(fila.get(col_id, "N/A")),
                fuente_origen="SEACE_OCDS",
                titulo_proyecto=descripcion,
                disciplina=disciplina,
                entidad_o_cliente=str(fila.get(col_entidad, "ENTIDAD PUBLICA")),
                presupuesto_referencial=monto_adj,
                monto_adjudicado=monto_adj,
                postor_ganador=str(fila.get(col_ganador, "CONTRATISTA ADJUDICADO")),
                ruc_ganador=str(fila.get(col_ruc, "")),
                normas_identificadas=normas,
                requisitos=requisitos
            )
            proyectos.append(p)

        print(f"[SEACE OCDS] Se extrajeron {len(proyectos)} proyectos técnicos calificados.")
        return proyectos
