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

    @classmethod
    def generar_tdr_linea_primaria(cls,
                                   titulo_nuevo_proyecto: str,
                                   autor: str,
                                   codigo_estudiante: str,
                                   tension_kv: float = 22.9,
                                   longitud_km: float = 0.817,
                                   conductor: str = "AAAC 35 mm²",
                                   altitud_msnm: float = 3850.0,
                                   num_estructuras: int = 9,
                                   proyecto_precedente: Dict[str, Any] = None) -> str:
        """
        Genera un pliego exhaustivo de Términos de Referencia y Especificaciones Técnicas Oficiales
        para una Línea Primaria en Media Tensión conforme a estándares SEACE / DGE / CNE.
        """
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        prec_txt = ""
        if proyecto_precedente:
            prec_txt = (
                "> [!NOTE]\n"
                "> **Precedente Técnico-Económico de Adjudicación SEACE:**\n"
                f"> - Convocatoria Homóloga: `{proyecto_precedente.get('id_referencia', 'LP-SM-15-2024-ELECTROPUNO')}`\n"
                f"> - Entidad Contratante: **{proyecto_precedente.get('entidad_o_cliente', 'ELECTRO PUNO S.A.A.')}**\n"
                f"> - Contratista Adjudicado: **{proyecto_precedente.get('postor_ganador', 'CONSORCIO ELECTROMECANICO ALTIPLANO')}**\n"
                f"> - Presupuesto Referencial de Mercado: **S/. {proyecto_precedente.get('monto_adjudicado', 4680000.0):,.2f}**\n"
            )

        plantilla = """# TÉRMINOS DE REFERENCIA Y ESPECIFICACIONES TÉCNICAS OFICIALES (SEACE)
## LÍNEA PRIMARIA EN MEDIA TENSIÓN {TENSION_KV} kV
### PROYECTO: {TITULO_PROYECTO}

**Proyectista / Autor:** {AUTOR} (Cód. {CODIGO_ESTUDIANTE})  
**Especialidad:** Ingeniería Mecánica Eléctrica — Alta y Media Tensión  
**Nivel de Tensión:** {TENSION_KV} kV (Trifásico 3 hilos, 60 Hz)  
**Altitud Media de Diseño:** {ALTITUD_MSNM:,.0f} msnm (Zona Altiplano Puno)  
**Longitud de Eje:** {LONGITUD_KM:.3f} km | Total Estructuras MT: {NUM_ESTRUCTURAS} unidades  
**Fecha:** {FECHA_ACTUAL}  

---
{PREC_TXT}

## 1. ALCANCE GENERAL Y OBJETO DE LA CONTRATACIÓN
El presente documento fija las condiciones contractuales, técnicas, dimensionales y de control de calidad bajo las cuales el Contratista ejecutará el suministro de bienes, transporte, obras civiles, montaje electromecánico y pruebas de puesta en servicio de la **Línea Primaria en Media Tensión {TENSION_KV} kV** y su correspondiente **Subestación de Distribución Aérea Biposte (SAB-1)**.

## 2. MARCO LEGAL Y NORMATIVA DE OBLIGATORIO CUMPLIMIENTO
1. **Código Nacional de Electricidad (CNE Suministro 2011):** Regla 232 (Gálibos y distancias de seguridad), Regla 250 (Hipótesis climáticas de sobrecarga en Zona 2/3), Regla 252 (Factores de seguridad de estructuras y conductores) y Regla 362 (Puestas a tierra).
2. **Norma DGE - "Bases para el Diseño de Líneas y Redes Primarias para Electrificación Rural" (R.D. N° 018-2003-EM/DGE):** Criterios mecánicos, vanos admisibles, tablas de armados normalizados (PR-1, PS-1, PA-1, SAB-1).
3. **NTP 370.258 / IEC 61089 / ASTM B399:** Conductores de aleación de aluminio homogéneo (AAAC).
4. **NTP 339.027:** Postes de concreto armado centrifugado (C.A.C.) para líneas aéreas.
5. **IEC 60071-1 / IEC 60071-2:** Coordinación de aislamiento y factor de corrección por altitud (>1000 msnm).
6. **IEC 60076:** Transformadores de potencia y distribución sumergidos en aceite mineral.
7. **IEC 61109 / ANSI C29.13:** Aisladores poliméricos tipo suspensión de hule de silicona.
8. **ANSI C37.41 / ANSI C37.42:** Cortacircuitos fusibles de expulsión tipo Cut-Out (27 kV, 100 A, BIL 150 kV).
9. **IEC 60099-4 / IEEE C62.11:** Descargadores de sobretensión de óxido de zinc (ZnO) sin explosores.
10. **ASTM A123 / ASTM A153:** Galvanizado por inmersión en caliente de perfiles y ferretería de acero.

---

## 3. ESPECIFICACIONES TÉCNICAS DE SUMINISTRO DE MATERIALES Y EQUIPOS

### 3.1 Conductor Aéreo de Media Tensión ({CONDUCTOR})
* **Material:** Aleación de aluminio Al-Mg-Si tratado térmicamente (6201-T81).
* **Construcción:** 7 hilos cableados concéntricamente de 2.50 mm de diámetro.
* **Carga de rotura nominal (TR):** Mínimo 1,040.0 kgf (10.20 kN).
* **Peso unitario en aire:** 0.0945 kg/m.
* **Módulo de elasticidad inicial / final:** E = 6,000 kg/mm² (58,860 MPa).
* **Coeficiente de dilatación térmica:** α = 23.0 x 10⁻⁶ 1/°C.
* **Resistencia eléctrica en C.C. a 20°C:** ≤ 0.963 Ω/km (≤ 0.986 Ω/km a 50°C).
* **Límite de tiro en condición de templado (EDS a +15°C):** Máximo 18.0% TR (187.20 kgf).
* **Límite de tiro máximo bajo hipótesis CNE más severa:** Máximo 40.0% TR (416.00 kgf).

### 3.2 Postes de Concreto Armado Centrifugado (C.A.C.)
* **Resistencia a la compresión del concreto:** f'c ≥ 350 kg/cm² a los 28 días.
* **Conicidad:** 15 mm/m uniforme desde la cima hasta la base.
* **Acabado:** Exterior liso, centrifugado, totalmente exento de cangrejeras, fisuras o desprendimientos.
* **Profundidad de empotramiento normalizada:**
  * Postes de 12 m: t = 1.40 m.
  * Postes de 13 m: t = 1.50 m.
* **Capacidad de carga en la cima:**
  * C.A.C. 12 m / 300 daN (Alineamiento y suspensión: E-02, E-03, E-07).
  * C.A.C. 12 m / 400 daN (Ángulos, derivación y terminal: E-01, E-05, E-06, E-08, E-09).
  * C.A.C. 13 m / 400 daN (Subestación biposte SAB-1: E-04 gemelo).
* **Factor de seguridad estructural mínimo:** FS ≥ 2.0 respecto a la rotura nominal.

### 3.3 Aislamiento Polimérico y Coordinación de Sobretensiones a {ALTITUD_MSNM:.0f} msnm
* **Aisladores Poliméricos de Suspensión (25 kV):**
  * Núcleo resistente de fibra de vidrio con resina epoxi de alta resistencia mecánica a la tracción (≥ 70 kN).
  * Cubierta exterior y aletas hidrofóbicas de goma de silicona vulcanizada en caliente (HTV).
  * Nivel Básico de Aislamiento al Impulso (BIL): Sobredimensionado a 150 kV para compensar la menor rigidez dieléctrica del aire a gran altitud (ka = 1.25).
  * Línea de fuga específica mínima: ≥ 31 mm/kV de tensión máxima del sistema (750 mm de fuga neta), apto para ambiente lacustre.
* **Aisladores Tipo Pin ANSI 56-3:**
  * Espiga de acero forjado galvanizado en caliente de 3/4" x 240 mm con rosca de plomo.

### 3.4 Equipamiento de Maniobra y Protección en Media Tensión
* **Cortacircuitos Fusibles Cut-Out:**
  * Tensión nominal: 27 kV, Nivel de Aislamiento BIL: 150 kV.
  * Corriente continua nominal: 100 A, Capacidad interruptiva simétrica: 10 kA.
  * Portafusible de fibra de vidrio recubierta con resina epoxi y tubo de extinción interior de cuerno desionizante.
  * Elemento fusible tipo chicote de expulsión rápida, curva K, calibre 4 A.
* **Descargadores de Sobretensión de Óxido de Zinc (ZnO):**
  * Tipo polimérico sin explosores (gapless) de servicio pesado para distribución (Heavy Duty).
  * Tensión asignada (Ur): 21 kV eficaz.
  * Tensión de operación continua máxima (MCOV): 17.5 kV eficaz.
  * Corriente nominal de descarga: 10 kA (onda 8/20 μs).

### 3.5 Transformador de Distribución de Subestación SAB-1 (Estructura E-04)
* **Potencia Nominal:** 100 kVA.
* **Relación de Transformación:** 22.9 kV / 0.38 - 0.22 kV con regulación en alta tensión en ± 2x2.5%.
* **Grupo de Conexión:** Dyn5 (neutro de baja tensión accesible y aterrado).
* **Frecuencia:** 60 Hz.
* **Régimen de Refrigeración:** ONAN (aceite mineral dieléctrico según ASTM D3487).
* **Sobreelevación de temperatura corregida para altitud:** Diseñado para límite térmico de devanados ≤ 55°C a 3,850 msnm.

### 3.6 Retenidas Mecánicas de Alta Resistencia (Tipo R-1)
* Cable de acero grado Siemens-Martin de 3/8" (9.52 mm, carga de rotura 3,150 kgf).
* Aislador de tracción tipo nuez ANSI 54-1 a cota mínima +3.00 m sobre el terreno.
* Varilla de anclaje de F°G° de 5/8" x 2.40 m con ojal guardacabo y tuerca de apriete.
* Bloque de concreto ciclópeo de anclaje de 0.40 x 0.40 x 0.20 m enterrado a profundidad mínima de 1.80 m.

---

## 4. ESPECIFICACIONES TÉCNICAS DE MONTAJE Y PRUEBAS EN OBRA
1. **Replanteo y Excavación:** Tolerancia en eje de línea ≤ ±20 mm. Fondo de excavación nivelado y apisonado.
2. **Cimentación:** Vaciado con concreto ciclópeo f'c = 140 kg/cm² + 30% piedra mediana de 4". Curado mínimo de 7 días antes del tendido.
3. **Flechado y Tensado de Conductores:**
   * Se realizará mediante teodolito/estación total y dinamómetro contrastado.
   * La tabla de templado y flechas por vano se regirá estrictamente por la Memoria de Cálculo Mecánico.
   * Queda terminantemente prohibido sobrepasar el 18.0% de la carga de rotura (187.20 kgf) en la temperatura de templado.
4. **Pruebas de Aceptación en Sitio (SAT):**
   * Medición de resistencia de puesta a tierra con telurómetro de 4 picas (R ≤ 10.0 Ω en SAB-1).
   * Ensayo de aislamiento fase-tierra y entre fases con Megóhmetro a 5,000 V DC (≥ 1,000 MΩ).
   * Verificación de gálibos verticales libres mediante distanciómetro láser conforme a la Regla 232 del CNE.

---
*Pliego Técnico de Especificaciones emitido bajo los estándares de ingeniería y minería de licitaciones del SEACE CAD Intelligence Framework.*
"""
        return plantilla.format(
            TENSION_KV=tension_kv,
            TITULO_PROYECTO=titulo_nuevo_proyecto.upper(),
            AUTOR=autor,
            CODIGO_ESTUDIANTE=codigo_estudiante,
            ALTITUD_MSNM=altitud_msnm,
            LONGITUD_KM=longitud_km,
            NUM_ESTRUCTURAS=num_estructuras,
            FECHA_ACTUAL=fecha_actual,
            PREC_TXT=prec_txt,
            CONDUCTOR=conductor
        )


