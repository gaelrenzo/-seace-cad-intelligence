"""
MÓDULO: seace_cad_intelligence/cad_bridge/parametric_primary_line.py
Generador paramétrico de componentes y armados normalizados de Líneas Primarias 22.9 kV
conforme a las Normas Técnicas DGE (Bases para el Diseño de Líneas y Redes Primarias para
Electrificación Rural - R.D. 018-2003-EM/DGE, R.M. N° 091-2002-EM/VME), CNE Suministro 2011,
NTP 339.027 (Postes C.A.C.) e IEC 60076 / IEC 61109.

Soporta exportación paramétrica en CadQuery (3D CAD-as-Code) y generación directa en DXF (ezdxf).
"""

from typing import Dict, Any, List, Tuple
import math
import os

try:
    import ezdxf
    from ezdxf import colors
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False


class PrimaryLineParametricGenerator:
    """
    Modelado paramétrico de alta fidelidad para ingeniería de detalle de Líneas Primarias:
    - Postes de Concreto Armado Centrifugado (C.A.C. 12/300, 12/400, 13/400).
    - Armados normalizados DGE: PS-1 (Suspensión), PA-1 (Ángulo), PR-1 (Retención/Derivación/Terminal).
    - Subestación Aérea Biposte SAB-1 (100 kVA, 22.9 / 0.38-0.22 kV).
    - Retenidas mecánicas tipo R-1 (inclinada simple y contraviento).
    """

    # Catálogo normalizado de postes C.A.C. según NTP 339.027
    CATALOGO_POSTES: Dict[str, Dict[str, float]] = {
        "12/300": {
            "altura_m": 12.0, "diam_cima_mm": 150.0, "diam_base_mm": 330.0,
            "empotramiento_m": 1.40, "carga_trabajo_daN": 300.0, "peso_aprox_kg": 920.0
        },
        "12/400": {
            "altura_m": 12.0, "diam_cima_mm": 180.0, "diam_base_mm": 360.0,
            "empotramiento_m": 1.40, "carga_trabajo_daN": 400.0, "peso_aprox_kg": 1150.0
        },
        "13/400": {
            "altura_m": 13.0, "diam_cima_mm": 180.0, "diam_base_mm": 375.0,
            "empotramiento_m": 1.50, "carga_trabajo_daN": 400.0, "peso_aprox_kg": 1320.0
        }
    }

    # -------------------------------------------------------------------------
    # GENERADORES DE CÓDIGO CADQUERY (CAD-AS-CODE 3D)
    # -------------------------------------------------------------------------

    @classmethod
    def generar_script_poste_cac(cls, modelo: str = "12/400") -> str:
        """Genera script CadQuery para un poste tronco-cónico de C.A.C. normalizado."""
        info = cls.CATALOGO_POSTES.get(modelo, cls.CATALOGO_POSTES["12/400"])
        h = info["altura_m"] * 1000.0
        r_cima = info["diam_cima_mm"] / 2.0
        r_base = info["diam_base_mm"] / 2.0
        t_empot = info["empotramiento_m"] * 1000.0

        return f'''"""
Poste C.A.C. Paramétrico {modelo} (NTP 339.027 / DGE)
Altura: {info["altura_m"]} m | Carga de Trabajo: {info["carga_trabajo_daN"]} daN
Empotramiento normalizado: {info["empotramiento_m"]} m
"""
import cadquery as cq

ALTURA = {h}
R_CIMA = {r_cima}
R_BASE = {r_base}
EMPOTRAMIENTO = {t_empot}

# Tronco de cono principal
poste = (
    cq.Workplane("XY")
    .circle(R_BASE)
    .workplane(offset=ALTURA)
    .circle(R_CIMA)
    .loft(combine=True)
)

# Anillo marcador de línea de tierra / empotramiento
marca_tierra = (
    cq.Workplane("XY")
    .workplane(offset=EMPOTRAMIENTO)
    .circle(R_BASE - ((R_BASE - R_CIMA) * (EMPOTRAMIENTO / ALTURA)) + 5.0)
    .rect(50.0, 50.0)
)

# Agujeros pasantes en la cima para fijación de pernos de cruceta (5/8")
poste = (
    poste.faces(">Z").workplane(offset=-250.0)
    .transformed(rotate=(90, 0, 0))
    .circle(18.0 / 2.0)
    .cutThruAll()
)

# Modelo consolidado listo para exportar STEP
# cq.exporters.export(poste, "poste_cac_{modelo.replace('/', '_')}.step")
'''

    @classmethod
    def generar_script_armado_ps1(cls) -> str:
        """Genera script CadQuery para el armado DGE PS-1 (Alineamiento / Suspensión 22.9 kV)."""
        return '''"""
Armado Normalizado DGE PS-1: Estructura de Alineamiento y Suspensión en Media Tensión 22.9 kV
Componentes:
- Poste C.A.C. 12 m
- Cruceta simétrica de acero galvanizado en caliente L 75x75x6.4 mm x 1.50 m
- Aisladores tipo Pin ANSI 56-3 (25 kV) con espiga de F°G° 3/4"
- Conductor AAAC 35 mm² fijado con atadura preformada
"""
import cadquery as cq

# 1. Cruceta angular L 75x75x6.4 mm x 1500 mm
CRUCETA_L = 1500.0
L_ALA = 75.0
E_CHAPA = 6.4

cruceta = (
    cq.Workplane("XY")
    .rect(CRUCETA_L, L_ALA)
    .extrude(E_CHAPA)
)

# 2. Espigas y aisladores tipo Pin (Fase central en cima, laterales en extremos)
def crear_aislador_pin():
    cuerpo = (
        cq.Workplane("XY")
        .circle(120.0)
        .extrude(80.0)
        .faces(">Z").workplane()
        .circle(90.0)
        .extrude(70.0)
        .faces(">Z").workplane()
        .circle(50.0)
        .extrude(60.0)
    )
    return cuerpo

aislador_izq = crear_aislador_pin().translate((-650.0, 0, E_CHAPA))
aislador_der = crear_aislador_pin().translate((650.0, 0, E_CHAPA))
aislador_cen = crear_aislador_pin().translate((0.0, 0, E_CHAPA + 250.0))

armado_ps1 = cruceta.union(aislador_izq).union(aislador_der).union(aislador_cen)
# cq.exporters.export(armado_ps1, "armado_dge_ps1_22_9kv.step")
'''

    @classmethod
    def generar_script_armado_pa1(cls) -> str:
        """Genera script CadQuery para el armado DGE PA-1 (Ángulo 22.9 kV)."""
        return '''"""
Armado Normalizado DGE PA-1: Estructura de Ángulo en Media Tensión 22.9 kV
Componentes:
- Poste C.A.C. 12/400
- Cruceta angular de arriostre y retención L 75x75x6.4 mm
- Cadenas de aisladores poliméricos de suspensión 25 kV (6 aletas HTV, longitud 450 mm)
- Grapas de anclaje de aleación de aluminio tipo pistola
"""
import cadquery as cq

# Cruceta de ángulo reforzada
cruceta = cq.Workplane("XY").box(1800.0, 80.0, 80.0)

# Cadena de aislador polimérico (cilindro de núcleo + 6 aletas)
def crear_aislador_polimerico():
    nucleo = cq.Workplane("XY").circle(15.0).extrude(450.0)
    aletas = cq.Workplane("XY")
    for z in [80.0, 140.0, 200.0, 260.0, 320.0, 380.0]:
        aleta = (
            cq.Workplane("XY")
            .workplane(offset=z)
            .circle(60.0)
            .extrude(12.0)
        )
        nucleo = nucleo.union(aleta)
    return nucleo

aislador_1 = crear_aislador_polimerico().rotate((0, 0, 0), (1, 0, 0), 90).translate((-750.0, 250.0, 0))
aislador_2 = crear_aislador_polimerico().rotate((0, 0, 0), (1, 0, 0), 90).translate((0.0, 250.0, 0))
aislador_3 = crear_aislador_polimerico().rotate((0, 0, 0), (1, 0, 0), 90).translate((750.0, 250.0, 0))

armado_pa1 = cruceta.union(aislador_1).union(aislador_2).union(aislador_3)
# cq.exporters.export(armado_pa1, "armado_dge_pa1_22_9kv.step")
'''

    @classmethod
    def generar_script_armado_pr1(cls) -> str:
        """Genera script CadQuery para el armado DGE PR-1 (Retención / Derivación / Terminal 22.9 kV)."""
        return '''"""
Armado Normalizado DGE PR-1: Estructura de Retención / Derivación / Terminal 22.9 kV
Componentes:
- Doble cruceta de retención F°G° L 75x75x6.4 mm x 2000 mm
- 03 Cortacircuitos fusibles tipo Cut-Out 27 kV / 100 A (BIL 150 kV)
- 03 Pararrayos poliméricos de óxido de zinc (ZnO) 21 kV / 10 kA
- 03 Cadenas de aisladores poliméricos de retención 25 kV
"""
import cadquery as cq

# Doble cruceta de retención separada 200 mm
cruceta_del = cq.Workplane("XY").box(2000.0, 75.0, 75.0).translate((0, 100.0, 0))
cruceta_tras = cq.Workplane("XY").box(2000.0, 75.0, 75.0).translate((0, -100.0, 0))
crucetas = cruceta_del.union(cruceta_tras)

# Soporte de cut-out y pararrayos
soporte_equipos = cq.Workplane("XY").box(1800.0, 50.0, 50.0).translate((0, 0, 600.0))

# Módulo de Cut-Out (Tubo aislante inclinado 20°)
def crear_cutout():
    cuerpo = cq.Workplane("XY").circle(25.0).extrude(400.0)
    aislador = cq.Workplane("XY").box(80.0, 80.0, 150.0).translate((0, 0, 150.0))
    return cuerpo.union(aislador).rotate((0,0,0), (1,0,0), 20)

# Módulo de Pararrayos ZnO
def crear_pararrayos_zno():
    cuerpo = cq.Workplane("XY").circle(35.0).extrude(380.0)
    for z in [60.0, 120.0, 180.0, 240.0, 300.0]:
        aleta = cq.Workplane("XY").workplane(offset=z).circle(55.0).extrude(15.0)
        cuerpo = cuerpo.union(aleta)
    return cuerpo

equipos = cq.Workplane("XY")
for x in [-600.0, 0.0, 600.0]:
    co = crear_cutout().translate((x, 150.0, 650.0))
    pa = crear_pararrayos_zno().translate((x, -150.0, 650.0))
    equipos = equipos.union(co).union(pa)

armado_pr1 = crucetas.union(soporte_equipos).union(equipos)
# cq.exporters.export(armado_pr1, "armado_dge_pr1_22_9kv.step")
'''

    @classmethod
    def generar_script_armado_sab1(cls) -> str:
        """Genera script CadQuery para Subestación Aérea Biposte SAB-1 100 kVA."""
        return '''"""
Armado Normalizado DGE SAB-1: Subestación de Distribución Aérea Biposte 100 kVA
Tensión: 22.9 / 0.38 - 0.22 kV | Grupo: Dyn5 | Régimen: ONAN | Altitud: 3850 msnm
Componentes:
- Biposte C.A.C. 13/400 (interdistancia entre ejes: 2000 mm)
- Plataforma portatransformador metálica con 2 vigas UPN-120 de F°G°
- Transformador de distribución 100 kVA trifásico con aletas radiadoras
- Seccionamiento Cut-Out 27 kV y protección pararrayos ZnO 21 kV en cabecera
- Tablero de distribución general de baja tensión IP65 adosado al poste
"""
import cadquery as cq

INTEREJE = 2000.0

# 1. Postes gemelos CAC 13/400
poste_izq = cq.Workplane("XY").circle(180.0).workplane(offset=13000.0).circle(90.0).loft().translate((-INTEREJE/2, 0, 0))
poste_der = cq.Workplane("XY").circle(180.0).workplane(offset=13000.0).circle(90.0).loft().translate((INTEREJE/2, 0, 0))
postes = poste_izq.union(poste_der)

# 2. Plataforma metálica a cota +6.00 m
viga_1 = cq.Workplane("XY").box(2600.0, 120.0, 60.0).translate((0, 300.0, 6000.0))
viga_2 = cq.Workplane("XY").box(2600.0, 120.0, 60.0).translate((0, -300.0, 6000.0))
plataforma = viga_1.union(viga_2)

# 3. Transformador trifásico 100 kVA (Cuba rectangular con aletas y boquillas MT)
cuba = cq.Workplane("XY").box(950.0, 700.0, 1100.0).translate((0, 0, 6600.0))
# Boquillas MT 22.9 kV (3 unidades)
boquillas_mt = cq.Workplane("XY")
for x in [-250.0, 0.0, 250.0]:
    b = cq.Workplane("XY").circle(35.0).extrude(350.0).translate((x, 150.0, 7150.0))
    boquillas_mt = boquillas_mt.union(b)

# 4. Tablero BT IP65 montado en fuste de poste a +1.80 m
tablero_bt = cq.Workplane("XY").box(600.0, 350.0, 800.0).translate((-INTEREJE/2 + 250.0, 200.0, 1800.0))

armado_sab1 = postes.union(plataforma).union(cuba).union(boquillas_mt).union(tablero_bt)
# cq.exporters.export(armado_sab1, "armado_dge_sab1_100kva.step")
'''

    @classmethod
    def generar_script_retenida_r1(cls) -> str:
        """Genera script CadQuery para Retenida Mecánica R-1 a tierra."""
        return '''"""
Retenida Mecánica Inclinada R-1 para Línea Primaria 22.9 kV
Componentes:
- Perno de ojo de F°G° 5/8" en cabeza de poste
- Cable de acero galvanizado Siemens-Martin 3/8" (Carga rotura 3150 kgf)
- Aislador de tracción tipo nuez ANSI 54-1 (a 3.0 m de altura)
- Varilla de anclaje de F°G° 5/8" x 2.40 m con guardacabo
- Bloque de concreto ciclópeo de anclaje 0.40 x 0.40 x 0.20 m enterrado a 1.80 m
"""
import cadquery as cq
import math

# Bloque de anclaje de concreto
bloque = cq.Workplane("XY").box(400.0, 400.0, 200.0).translate((8000.0, 0, -1800.0))

# Varilla de anclaje a 45°
varilla = (
    cq.Workplane("XY")
    .circle(16.0 / 2.0)
    .extrude(2400.0)
    .rotate((0,0,0), (0,1,0), -45)
    .translate((8000.0, 0, -1800.0))
)

# Cable de retenida
cable = (
    cq.Workplane("XY")
    .circle(9.52 / 2.0)
    .extrude(11500.0)
    .rotate((0,0,0), (0,1,0), -45)
    .translate((0, 0, 10500.0))
)

# Aislador tipo nuez
aislador_nuez = (
    cq.Workplane("XY")
    .box(110.0, 80.0, 140.0)
    .rotate((0,0,0), (0,1,0), -45)
    .translate((5500.0, 0, 3000.0))
)

retenida = bloque.union(varilla).union(cable).union(aislador_nuez)
# cq.exporters.export(retenida, "retenida_mecanica_r1.step")
'''

    # -------------------------------------------------------------------------
    # GENERADORES DIRECTOS DE MODELOS DXF 2D/3D (AUTOCAD COMPATIBLE)
    # -------------------------------------------------------------------------

    @classmethod
    def exportar_dxf_armado(cls, tipo_armado: str, ruta_salida: str, params: Dict[str, Any] = None) -> str:
        """
        Genera directamente un archivo DXF profesional con bloques, capas y cotas normalizadas
        utilizando ezdxf.
        """
        if not EZDXF_AVAILABLE:
            raise ImportError("ezdxf no está instalado en el entorno.")

        os.makedirs(os.path.dirname(ruta_salida) or ".", exist_ok=True)
        doc = ezdxf.new("R2010", setup=True)
        msp = doc.modelspace()

        # Capas normalizadas
        doc.layers.add("ESTRUCTURA_POSTE", color=colors.CYAN)
        doc.layers.add("CRUCETA_Y_FERRETERIA", color=colors.YELLOW)
        doc.layers.add("AISLADORES_POLIMERICOS", color=colors.GREEN)
        doc.layers.add("CONDUCTOR_FASE", color=colors.RED)
        doc.layers.add("EQUIPAMIENTO_MT", color=colors.MAGENTA)
        doc.layers.add("RETENIDA_ACERO", color=colors.BLUE)
        doc.layers.add("COTAS_Y_TEXTOS", color=colors.WHITE)

        tipo = tipo_armado.upper()

        if "PS-1" in tipo or "PS1" in tipo or "SUSPENSION" in tipo:
            cls._dibujar_dxf_ps1(msp)
        elif "PA-1" in tipo or "PA1" in tipo or "ANGULO" in tipo:
            cls._dibujar_dxf_pa1(msp)
        elif "PR-1" in tipo or "PR1" in tipo or "RETENCION" in tipo:
            cls._dibujar_dxf_pr1(msp)
        elif "SAB-1" in tipo or "SAB1" in tipo or "SED" in tipo:
            cls._dibujar_dxf_sab1(msp)
        elif "RETENIDA" in tipo or "R-1" in tipo:
            cls._dibujar_dxf_retenida(msp)
        elif "POSTE" in tipo:
            cls._dibujar_dxf_poste(msp, params.get("modelo", "12/400") if params else "12/400")
        else:
            cls._dibujar_dxf_ps1(msp)

        doc.saveas(ruta_salida)
        return ruta_salida

    @classmethod
    def _dibujar_dxf_poste(cls, msp, modelo: str = "12/400"):
        info = cls.CATALOGO_POSTES.get(modelo, cls.CATALOGO_POSTES["12/400"])
        h = info["altura_m"]
        r_c = info["diam_cima_mm"] / 2000.0
        r_b = info["diam_base_mm"] / 2000.0
        t_emp = info["empotramiento_m"]

        # Fuste del poste
        puntos = [(-r_b, 0.0), (-r_c, h), (r_c, h), (r_b, 0.0), (-r_b, 0.0)]
        msp.add_lwpolyline(puntos, close=True, dxfattribs={"layer": "ESTRUCTURA_POSTE"})

        # Línea de terreno natural
        msp.add_line((-1.5, t_emp), (1.5, t_emp), dxfattribs={"layer": "COTAS_Y_TEXTOS", "linetype": "DASHED"})
        msp.add_text("Nivel de Terreno Natural (N.T.N.)", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.15}).set_placement((1.6, t_emp))
        msp.add_text(f"POSTE C.A.C. {modelo} (H={h}m, Empotramiento={t_emp}m)", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.25}).set_placement((-1.5, h + 0.3))

    @classmethod
    def _dibujar_dxf_ps1(cls, msp):
        """Detalle 2D frontal del Armado DGE PS-1."""
        cls._dibujar_dxf_poste(msp, "12/300")
        h = 12.0
        # Cruceta de alineamiento 1.50 m
        msp.add_lwpolyline([(-0.75, h - 0.25), (0.75, h - 0.25), (0.75, h - 0.18), (-0.75, h - 0.18), (-0.75, h - 0.25)],
                           close=True, dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        # Aislador central en punta
        msp.add_lwpolyline([(-0.10, h), (0.10, h), (0.12, h + 0.25), (-0.12, h + 0.25), (-0.10, h)],
                           close=True, dxfattribs={"layer": "AISLADORES_POLIMERICOS"})
        # Aislador lateral izquierdo
        msp.add_lwpolyline([(-0.65, h - 0.18), (-0.55, h - 0.18), (-0.53, h + 0.10), (-0.67, h + 0.10), (-0.65, h - 0.18)],
                           close=True, dxfattribs={"layer": "AISLADORES_POLIMERICOS"})
        # Aislador lateral derecho
        msp.add_lwpolyline([(0.55, h - 0.18), (0.65, h - 0.18), (0.67, h + 0.10), (0.53, h + 0.10), (0.55, h - 0.18)],
                           close=True, dxfattribs={"layer": "AISLADORES_POLIMERICOS"})
        # Conductores de fase
        msp.add_circle((0.0, h + 0.25), 0.04, dxfattribs={"layer": "CONDUCTOR_FASE"})
        msp.add_circle((-0.60, h + 0.10), 0.04, dxfattribs={"layer": "CONDUCTOR_FASE"})
        msp.add_circle((0.60, h + 0.10), 0.04, dxfattribs={"layer": "CONDUCTOR_FASE"})

        msp.add_text("ARMADO DGE PS-1: ALINEAMIENTO / SUSPENSION 22.9 kV", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.30}).set_placement((-2.5, h + 0.8))

    @classmethod
    def _dibujar_dxf_pa1(cls, msp):
        """Detalle 2D frontal del Armado DGE PA-1."""
        cls._dibujar_dxf_poste(msp, "12/400")
        h = 12.0
        # Cruceta de ángulo 1.80 m
        msp.add_lwpolyline([(-0.90, h - 0.30), (0.90, h - 0.30), (0.90, h - 0.22), (-0.90, h - 0.22), (-0.90, h - 0.30)],
                           close=True, dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        # 3 Cadenas de suspensión polimérica
        for x in [-0.75, 0.0, 0.75]:
            msp.add_line((x, h - 0.22), (x, h + 0.40), dxfattribs={"layer": "AISLADORES_POLIMERICOS"})
            for ya in [h - 0.10, h + 0.05, h + 0.20, h + 0.35]:
                msp.add_ellipse((x, ya), (0.08, 0.0), 0.3, dxfattribs={"layer": "AISLADORES_POLIMERICOS"})
            msp.add_circle((x, h + 0.42), 0.04, dxfattribs={"layer": "CONDUCTOR_FASE"})

        # Retenida biselar en cabeza
        msp.add_line((0.0, h - 0.30), (-4.5, 1.40), dxfattribs={"layer": "RETENIDA_ACERO", "linetype": "DASHDOT"})
        msp.add_text("Retenida Mecanica R-1", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.20}).set_placement((-3.0, 5.0))

        msp.add_text("ARMADO DGE PA-1: ANGULO Y RETENCION CON AISLADOR POLIMERICO 22.9 kV", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.30}).set_placement((-3.5, h + 0.8))

    @classmethod
    def _dibujar_dxf_pr1(cls, msp):
        """Detalle 2D frontal del Armado DGE PR-1 (Retención / Derivación / Terminal)."""
        cls._dibujar_dxf_poste(msp, "12/400")
        h = 12.0
        # Doble cruceta F°G°
        msp.add_lwpolyline([(-1.0, h - 0.40), (1.0, h - 0.40), (1.0, h - 0.32), (-1.0, h - 0.32), (-1.0, h - 0.40)],
                           close=True, dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        # Soporte de Cut-Out y Pararrayos
        msp.add_line((-1.0, h + 0.40), (1.0, h + 0.40), dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        for x in [-0.70, 0.0, 0.70]:
            # Cortacircuito Cut-Out
            msp.add_line((x - 0.15, h + 0.40), (x - 0.25, h + 0.85), dxfattribs={"layer": "EQUIPAMIENTO_MT", "color": colors.MAGENTA})
            msp.add_circle((x - 0.25, h + 0.85), 0.06, dxfattribs={"layer": "EQUIPAMIENTO_MT"})
            # Pararrayos ZnO
            msp.add_lwpolyline([(x + 0.10, h + 0.40), (x + 0.20, h + 0.40), (x + 0.20, h + 0.80), (x + 0.10, h + 0.80), (x + 0.10, h + 0.40)],
                               close=True, dxfattribs={"layer": "EQUIPAMIENTO_MT"})

        # Retenida a tierra
        msp.add_line((0.0, h - 0.40), (-5.0, 1.40), dxfattribs={"layer": "RETENIDA_ACERO", "linetype": "DASHDOT"})

        msp.add_text("ARMADO DGE PR-1: DERIVACION / RETENCION CON CUT-OUT 27 kV Y ZnO 21 kV", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.30}).set_placement((-3.5, h + 1.1))

    @classmethod
    def _dibujar_dxf_sab1(cls, msp):
        """Detalle 2D de la Subestación Aérea Biposte SAB-1 100 kVA."""
        intereje = 2.00
        h = 13.0
        # Postes gemelos 13/400
        for x_p in [-intereje/2, intereje/2]:
            msp.add_lwpolyline([
                (x_p - 0.18, 0.0), (x_p - 0.09, h), (x_p + 0.09, h), (x_p + 0.18, 0.0), (x_p - 0.18, 0.0)
            ], close=True, dxfattribs={"layer": "ESTRUCTURA_POSTE"})

        # Línea de tierra
        msp.add_line((-2.5, 1.50), (2.5, 1.50), dxfattribs={"layer": "COTAS_Y_TEXTOS", "linetype": "DASHED"})

        # Plataforma portatransformador a cota +6.00 m
        msp.add_lwpolyline([(-1.40, 6.00), (1.40, 6.00), (1.40, 6.15), (-1.40, 6.15), (-1.40, 6.00)],
                           close=True, dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        # Diagonales de arriostre
        msp.add_line((-1.0, 5.00), (-1.30, 6.00), dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        msp.add_line((1.0, 5.00), (1.30, 6.00), dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})

        # Transformador trifásico 100 kVA
        msp.add_lwpolyline([(-0.50, 6.15), (0.50, 6.15), (0.50, 7.30), (-0.50, 7.30), (-0.50, 6.15)],
                           close=True, dxfattribs={"layer": "EQUIPAMIENTO_MT"})
        msp.add_text("TRAFO 100 kVA 22.9/0.38-0.22 kV", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.18}).set_placement((-0.45, 6.65))

        # Boquillas MT en tapa
        for xb in [-0.25, 0.0, 0.25]:
            msp.add_line((xb, 7.30), (xb, 7.70), dxfattribs={"layer": "EQUIPAMIENTO_MT"})
            msp.add_circle((xb, 7.70), 0.05, dxfattribs={"layer": "EQUIPAMIENTO_MT"})

        # Equipos superiores (Cut-Out y Pararrayos a cota 12.0 m)
        msp.add_line((-1.20, 12.00), (1.20, 12.00), dxfattribs={"layer": "CRUCETA_Y_FERRETERIA"})
        for xb in [-0.60, 0.0, 0.60]:
            msp.add_line((xb, 12.00), (xb, 12.50), dxfattribs={"layer": "EQUIPAMIENTO_MT"})
            msp.add_circle((xb, 12.50), 0.05, dxfattribs={"layer": "EQUIPAMIENTO_MT"})

        # Tablero de BT a +1.80 m
        msp.add_lwpolyline([(-intereje/2 + 0.25, 1.80), (-intereje/2 + 0.85, 1.80),
                            (-intereje/2 + 0.85, 2.60), (-intereje/2 + 0.25, 2.60),
                            (-intereje/2 + 0.25, 1.80)], close=True, dxfattribs={"layer": "EQUIPAMIENTO_MT"})
        msp.add_text("TABLERO BT IP65", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.14}).set_placement((-intereje/2 + 0.30, 2.20))

        # Doble retenida contraviento
        msp.add_line((-intereje/2, 11.5), (-intereje/2 - 4.5, 1.50), dxfattribs={"layer": "RETENIDA_ACERO", "linetype": "DASHDOT"})
        msp.add_line((intereje/2, 11.5), (intereje/2 + 4.5, 1.50), dxfattribs={"layer": "RETENIDA_ACERO", "linetype": "DASHDOT"})

        msp.add_text("ARMADO DGE SAB-1: SUBESTACION AEREA BIPOSTE 100 kVA (22.9/0.38-0.22 kV)",
                     dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.32}).set_placement((-4.0, h + 0.8))

    @classmethod
    def _dibujar_dxf_retenida(cls, msp):
        """Detalle 2D de la Retenida Mecánica R-1 con bloque de anclaje."""
        # Poste de referencia
        msp.add_line((0.0, 0.0), (0.0, 12.0), dxfattribs={"layer": "ESTRUCTURA_POSTE"})
        msp.add_line((-1.0, 1.40), (7.0, 1.40), dxfattribs={"layer": "COTAS_Y_TEXTOS", "linetype": "DASHED"})
        msp.add_text("Nivel de Terreno Natural", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.15}).set_placement((1.0, 1.50))

        # Cable de retenida
        msp.add_line((0.0, 10.5), (5.5, 1.40), dxfattribs={"layer": "RETENIDA_ACERO"})
        # Aislador tipo nuez a 3.0 m de altura
        msp.add_circle((4.4, 3.0), 0.12, dxfattribs={"layer": "AISLADORES_POLIMERICOS"})
        msp.add_text("Aislador tipo nuez ANSI 54-1", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.15}).set_placement((4.6, 3.2))

        # Varilla de anclaje subterránea
        msp.add_line((5.5, 1.40), (6.8, -0.40), dxfattribs={"layer": "RETENIDA_ACERO"})
        # Bloque de anclaje de concreto
        msp.add_lwpolyline([(6.5, -0.60), (7.1, -0.60), (7.1, -0.20), (6.5, -0.20), (6.5, -0.60)],
                           close=True, dxfattribs={"layer": "ESTRUCTURA_POSTE"})
        msp.add_text("Bloque Concreto 0.40x0.40x0.20m", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.14}).set_placement((6.0, -0.80))
        msp.add_text("RETENIDA MECANICA R-1 A TIERRA (45°)", dxfattribs={"layer": "COTAS_Y_TEXTOS", "height": 0.28}).set_placement((1.0, 11.0))
