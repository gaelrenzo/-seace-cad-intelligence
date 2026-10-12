"""
MÓDULO: seace_cad_intelligence/storage/repository.py
Persistencia polimórfica relacional + JSON para conocimiento de ingeniería.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..core.models import ProyectoIngenieria, RequisitoTecnico, DocumentoAdjunto


class AdaptiveKnowledgeRepository:
    """
    Repositorio SQLite con esquema abierto y campos serializados en JSON.
    Permite almacenar especificaciones de cualquier disciplina sin migraciones de esquema.
    """

    def __init__(self, db_path: str = "data/seace_intelligence.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._inicializar_esquema()

    def _inicializar_esquema(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id_referencia TEXT PRIMARY KEY,
                fuente_origen TEXT NOT NULL,
                titulo_proyecto TEXT NOT NULL,
                disciplina TEXT NOT NULL,
                entidad_o_cliente TEXT NOT NULL,
                presupuesto_referencial REAL,
                monto_adjudicado REAL,
                ratio_adjudicacion REAL,
                postor_ganador TEXT,
                ruc_ganador TEXT,
                moneda TEXT DEFAULT 'PEN',
                fecha_convocatoria TEXT,
                fecha_adjudicacion TEXT,
                normas_json TEXT,         -- Lista de normas (JSON)
                requisitos_json TEXT,     -- Requisitos y dimensiones (JSON)
                documentos_json TEXT,     -- Documentos adjuntos (JSON)
                metadatos_extra_json TEXT,-- Atributos libres (JSON)
                fecha_registro TIMESTAMP
            );
            """)

            # Índices de alto rendimiento para búsqueda rápida
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_disciplina ON proyectos(disciplina);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entidad ON proyectos(entidad_o_cliente);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_postor ON proyectos(postor_ganador);")
            conn.commit()

    def guardar_proyecto(self, p: ProyectoIngenieria) -> bool:
        """Guarda o actualiza un proyecto en la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO proyectos (
                id_referencia, fuente_origen, titulo_proyecto, disciplina,
                entidad_o_cliente, presupuesto_referencial, monto_adjudicado,
                ratio_adjudicacion, postor_ganador, ruc_ganador, moneda,
                fecha_convocatoria, fecha_adjudicacion, normas_json,
                requisitos_json, documentos_json, metadatos_extra_json, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p.id_referencia,
                p.fuente_origen,
                p.titulo_proyecto,
                p.disciplina,
                p.entidad_o_cliente,
                p.presupuesto_referencial,
                p.monto_adjudicado,
                p.ratio_adjudicacion(),
                p.postor_ganador,
                p.ruc_ganador,
                p.moneda,
                p.fecha_convocatoria,
                p.fecha_adjudicacion,
                json.dumps(p.normas_identificadas, ensure_ascii=False),
                json.dumps([r.__dict__ for r in p.requisitos], ensure_ascii=False),
                json.dumps([{
                    "tipo": d.tipo, "ruta_local": d.ruta_local, "url_origen": d.url_origen
                } for d in p.documentos], ensure_ascii=False),
                json.dumps(p.metadatos_extra, ensure_ascii=False),
                p.fecha_registro.isoformat()
            ))
            conn.commit()
            return True

    def buscar_por_criterios(self, disciplina: Optional[str] = None, 
                             norma: Optional[str] = None, 
                             texto: Optional[str] = None,
                             limite: int = 50) -> List[Dict[str, Any]]:
        """Búsqueda flexible en el repositorio."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            filtros = []
            params = []
            
            if disciplina:
                filtros.append("disciplina LIKE ?")
                params.append(f"%{disciplina}%")
            if norma:
                filtros.append("normas_json LIKE ?")
                params.append(f"%{norma}%")
            if texto:
                filtros.append("(titulo_proyecto LIKE ? OR entidad_o_cliente LIKE ? OR postor_ganador LIKE ?)")
                params.extend([f"%{texto}%", f"%{texto}%", f"%{texto}%"])

            where_clause = " WHERE " + " AND ".join(filtros) if filtros else ""
            query = f"SELECT * FROM proyectos {where_clause} ORDER BY fecha_registro DESC LIMIT ?"
            params.append(limite)

            filas = cursor.execute(query, params).fetchall()
            
            resultados = []
            for f in filas:
                d = dict(f)
                d["normas_identificadas"] = json.loads(d["normas_json"] or "[]")
                d["requisitos"] = json.loads(d["requisitos_json"] or "[]")
                resultados.append(d)
            return resultados

    def obtener_por_id(self, id_referencia: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            fila = cursor.execute("SELECT * FROM proyectos WHERE id_referencia = ?", (id_referencia,)).fetchone()
            if fila:
                d = dict(fila)
                d["normas_identificadas"] = json.loads(d["normas_json"] or "[]")
                d["requisitos"] = json.loads(d["requisitos_json"] or "[]")
                return d
            return None

    def obtener_estadisticas(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            total_proyectos = cursor.execute("SELECT COUNT(*) FROM proyectos").fetchone()[0]
            total_monto = cursor.execute("SELECT SUM(monto_adjudicado) FROM proyectos").fetchone()[0] or 0.0
            disciplinas = cursor.execute("SELECT disciplina, COUNT(*) FROM proyectos GROUP BY disciplina").fetchall()
            return {
                "total_proyectos": total_proyectos,
                "total_monto_adjudicado_pen": round(total_monto, 2),
                "distribucion_disciplinas": dict(disciplinas)
            }
