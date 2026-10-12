"""
MÓDULO: seace_cad_intelligence/templates/tdr_generator.py
Generador automático de Términos de Referencia (TDR) y Especificaciones Técnicas
para nuevos proyectos de autoría, basados en precedentes ganadores.
"""

from typing import Dict, Any, List
from datetime import datetime


class EngineeringTDRGenerator:
    """Sintetiza especificaciones técnicas bajo estándares peruanos e internacionales."""

    @classmethod
    def generar_documento_tdr(cls, 
                              titulo_nuevo_proyecto: str,
                              autor: str,
                              disciplina: str,
                              normas_aplicables: List[str],
                              requisitos_dimensionales: List[Dict[str, Any]],
                              proyecto_precedente: Dict[str, Any] = None) -> str:
        """
        Genera el documento técnico base en formato Markdown para el nuevo proyecto.
        """
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        precedente_info = ""
        if proyecto_precedente:
            precedente_info = f"""
> [!NOTE]
> **Precedente de Referencia Técnico-Económico:**
> - Proceso Adjudicado: {proyecto_precedente.get('id_referencia', 'N/A')}
> - Entidad Original: {proyecto_precedente.get('entidad_o_cliente', 'N/A')}
> - Monto Adjudicado Referencial: S/. {proyecto_precedente.get('monto_adjudicado', 0.0):,.2f}
"""

        normas_txt = "\n".join([f"- **{n}**: Cumplimiento obligatorio en diseño, fabricación y ensayos." for n in normas_aplicables]) or "- Normas técnicas generales ISO / ASME aplicables."
        
        reqs_tabla = ""
        if requisitos_dimensionales:
            lineas = [
                "| Parámetro Técnico | Valor Nominal | Unidad | Tolerancia / Norma |",
                "| :--- | :--- | :--- | :--- |"
            ]
            for r in requisitos_dimensionales:
                lineas.append(f"| {r.get('parametro', 'Dimensión')} | {r.get('valor_nominal', '-')} | {r.get('unidad', '-')} | {r.get('norma_asociada', 'ISO 2768-mK')} |")
            reqs_tabla = "\n".join(lineas)
        else:
            reqs_tabla = "_Parámetros a definir según memoria de cálculo paramétrica._"

        documento = f"""# EXPEDIENTE TÉCNICO Y TÉRMINOS DE REFERENCIA
## PROYECTO: {titulo_nuevo_proyecto.upper()}

**Autor / Proyectista:** {autor}  
**Especialidad:** {disciplina}  
**Fecha:** {fecha_actual}  
**Estado:** Documento de Ingeniería de Detalle  

---
{precedente_info}

### 1. OBJETIVO DEL PROYECTO
Establecer las condiciones técnicas mínimas, parámetros dimensionales, normas de diseño y criterios de control de calidad para la fabricación, montaje y puesta en servicio de los componentes electromecánicos y estructurales.

### 2. MARCO NORMATIVO INTERNACIONAL Y TÉCNICO APLICABLE
Todas las dimensiones, tolerancias y materiales se regirán estrictamente por los siguientes estándares:
{normas_txt}

### 3. REQUERIMIENTOS TÉCNICOS MÍNIMOS (RTM) Y ESPECIFICACIONES DIMENSIONALES
Los componentes deberán ser modelados y fabricados de acuerdo con la siguiente matriz paramétrica:

{reqs_tabla}

### 4. GARANTÍA DE EXACTITUD GEOMÉTRICA (CAD & GD&T)
1. **Modelado 3D Paramétrico:** Todos los elementos han sido generados mediante scripts paramétricos con tolerancias según norma ISO 2768 (clase media / fina).
2. **Intercambiabilidad:** Las uniones embridadas cumplirán rigurosamente con ASME B16.5 para garantizar acoplamiento hermético.
3. **Control de Calidad:** Pruebas hidrostáticas a 1.5 veces la presión de diseño y tintes penetrantes en cordones de soldadura según AWS D1.1.

### 5. METRADO Y PRESUPUESTO ESTIMADO
La estructura de partidas presupuestales toma como benchmark los rendimientos de mercado verificados en contrataciones públicas previas.

---
*Documento generado automáticamente por el Framework SEACE CAD Intelligence.*
"""
        return documento
