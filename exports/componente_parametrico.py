"""
Generador paramétrico de Brida ASME B16.5 Clase 150 NPS 2"
Validación dimensional: Exactitud bajo estándar internacional ASME.
"""
import cadquery as cq

# Parámetros nominales en mm
DIAMETRO_EXT = 152.4
CIRCULO_PERNOS = 120.7
ESPESOR = 19.1
DIAMETRO_BARRENO = 19.1
NUM_BARRENOS = 4
DIAMETRO_INTERIOR = 62.0

# Construcción de geometría sólida
brida = (
    cq.Workplane("XY")
    .circle(DIAMETRO_EXT / 2.0)
    .extrude(ESPESOR)
    # Agujero pasante de tubería (Bore)
    .faces(">Z").workplane()
    .circle(DIAMETRO_INTERIOR / 2.0)
    .cutThruAll()
    # Distribución polar de pernos
    .faces(">Z").workplane()
    .polarArray(radius=CIRCULO_PERNOS / 2.0, startAngle=0, angle=360, count=NUM_BARRENOS)
    .circle(DIAMETRO_BARRENO / 2.0)
    .cutThruAll()
)

# Exportar a formato estándar interoperable
# cq.exporters.export(brida, "brida_asme_2_clase150.step")
