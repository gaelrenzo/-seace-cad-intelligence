# SEACE Engineering & CAD Intelligence Framework 🇵🇪⚙️

> **Sistema modular y adaptativo de inteligencia de ingeniería:** minería de proyectos adjudicados (ganadores) en el SEACE / OECE y generador paramétrico CAD bajo normas internacionales (ISO, ASME, IEC, AWS).

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/architecture-modular%20%26%20clean-brightgreen.svg)]()
[![Standards](https://img.shields.io/badge/standards-ISO%20%7C%20ASME%20%7C%20IEC%20%7C%20AISC-orange.svg)]()

---

## 🎯 ¿Qué hace este proyecto?

1. **Minería de Licitaciones Ganadoras:** Ingiere datos masivos del OECE (CONOSCE / OCDS) o directamente mediante web crawling automatizado del portal SEACE 3.0.
2. **Extracción y Validación de Normas:** Detecta automáticamente normas técnicas internacionales (`ISO 1101`, `ASME B16.5`, `ASME B31.3`, `AWS D1.1`, `IEC 61439`, etc.) y magnitudes físicas (presión, caudal, potencia, dimensiones).
3. **Repositorio Adaptativo Híbrido:** Almacena el conocimiento técnico en una base de datos relacional + JSON estructurado en SQLite, capaz de catalogar cualquier disciplina sin alterar tablas.
4. **CAD Paramétrico como Código (CAD-as-Code):** Transforma los requisitos extraídos en scripts paramétricos para **CadQuery** / **FreeCAD Python**, garantizando exactitud geométrica dimensional y tolerancias GD&T.
5. **Generador de Nuevos Expedientes y TDRs:** Permite redactar términos de referencia y memorias descriptivas de **autoría propia**, respaldados en precedentes exitosos y precios de mercado verificados.

---

## 📐 Estructura Modular del Proyecto

```text
seace-cad-intelligence/
├── config.yaml                     # Parámetros, disciplinas y normas por defecto
├── requirements.txt                # Dependencias del ecosistema
├── seace_cad_intelligence/
│   ├── core/                       # Núcleo de dominio (SOLID)
│   │   ├── models.py               # Entidades universales de ingeniería
│   │   ├── adapters.py             # Clase base abstracta de ingestión (Patrón Estrategia)
│   │   └── analyzer.py             # Motor léxico/semántico de normas y dimensiones
│   ├── integrations/               # Integración con repositorios especializados
│   │   ├── ocdskit_bridge.py       # Ingestión de paquetes OCDS (open-contracting/ocdskit)
│   │   ├── docling_bridge.py       # Minería de tablas y materiales (IBM Docling / pdfplumber)
│   │   └── seace_scraper_engine.py # Scraping batch con parameters.csv (Ed1123/seace-scraper)
│   ├── extractors/                 # Conectores adaptativos de datos
│   │   ├── seace_ocds_adapter.py   # Ingestor masivo de datasets OECE/CONOSCE
│   │   ├── seace_web_crawler.py    # Crawler interactivo con Playwright para SEACE 3.0
│   │   └── pdf_spec_parser.py      # Parser de PDFs (Bases Integradas / TDRs)
│   ├── storage/                    # Persistencia de conocimiento
│   │   └── repository.py           # Repositorio híbrido SQLite + JSON
│   ├── cad_bridge/                 # Generación CAD Paramétrica (CadQuery & build123d)
│   │   ├── parametric_flange.py    # Bridas ASME B16.5 Clase 150
│   │   ├── parametric_shaft.py     # Ejes escalonados ISO 2768-mK / DIN 6885
│   │   ├── parametric_chassis.py   # Skids y bastidores estructurales AISC 360
│   │   ├── parametric_enclosure.py # Gabinetes eléctricos IEC 61439 (build123d / CadQuery)
│   │   └── export_manager.py       # Coordinador y exportador de código CAD
│   ├── templates/                  # Documentación de autoría
│   │   └── tdr_generator.py        # Generador de TDRs y expedientes técnicos
│   └── cli.py                      # Interfaz de línea de comandos (CLI)
└── tests/
    ├── test_pipeline.py            # Pruebas unitarias de pipeline
    └── test_integrations.py        # Pruebas de integraciones (OCDS, Docling, CAD)
```

---

## 🚀 Inicio Rápido

### 1. Instalación de dependencias
```bash
pip install -r requirements.txt
```

*(Opcional: Si deseas utilizar el crawler web interactivo de SEACE con Playwright)*:
```bash
playwright install chromium
```

---

### 2. Uso mediante Línea de Comandos (CLI)

#### Cargar proyectos de demostración (Perú)
```bash
python -m seace_cad_intelligence.cli demo
```

#### Ver estadísticas de la base de datos
```bash
python -m seace_cad_intelligence.cli stats
```

#### Buscar proyectos ganadores por Norma o Especialidad
```bash
python -m seace_cad_intelligence.cli search --norma "ASME"
python -m seace_cad_intelligence.cli search --disciplina "Mecanica"
```

#### Generar Código CAD Paramétrico
```bash
# Brida bajo ASME B16.5 de 2 pulgadas
python -m seace_cad_intelligence.cli generate-cad --tipo brida --nps 2 --output exports/brida_2in.py

# Eje escalonado bajo ISO 2768
python -m seace_cad_intelligence.cli generate-cad --tipo eje --output exports/eje_transmision.py

# Bastidor estructural bajo AISC 360
python -m seace_cad_intelligence.cli generate-cad --tipo skid --output exports/skid_motobomba.py
```

#### Generar un nuevo Expediente Técnico / TDR de Autoría Propia
Toma un proyecto ganador como benchmark técnico-económico y genera el documento formal de ingeniería:
```bash
python -m seace_cad_intelligence.cli generate-tdr \
  --ref "AS-SM-12-2024-SEDAPAL" \
  --titulo "SISTEMA DE BOMBEO Y DISTRIBUCION DE AGUA POTABLE SECTOR NORTE" \
  --autor "Ing. Renzo Mamani" \
  --output "exports/TDR_Sistema_Bombeo.md"
```

---

## 🧩 ¿Cómo agregar nuevas funcionalidades en el futuro?

El framework está diseñado bajo el principio **Open/Closed** (abierto a la extensión, cerrado a la modificación):

1. **Para agregar una nueva fuente de datos (ej. licitaciones privadas o mineras):**
   - Crea un nuevo archivo en `seace_cad_intelligence/extractors/mi_fuente_adapter.py`.
   - Hereda de `BaseDataSourceAdapter` e implementa `extraer_proyectos()`.
2. **Para agregar un nuevo componente CAD:**
   - Añade una nueva clase generadora en `seace_cad_intelligence/cad_bridge/`.
   - Regístrala en `export_manager.py`.
3. **Para cambiar la base de datos:**
   - La capa `AdaptiveKnowledgeRepository` está desacoplada del resto del sistema.

---

## 📜 Licencia y Autoría
Desarrollado con rigor de Ingeniería Senior en CAD y Automatización para formulación de proyectos técnicos de alto estándar.
