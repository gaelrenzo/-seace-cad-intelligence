"""
MÓDULO: seace_cad_intelligence/cli.py
Interfaz de línea de comandos (CLI) principal del framework.
"""

import argparse
import sys
import os
from .storage.repository import AdaptiveKnowledgeRepository
from .core.models import ProyectoIngenieria, RequisitoTecnico
from .cad_bridge.export_manager import CADCodeExporter
from .templates.tdr_generator import EngineeringTDRGenerator


def poblar_demo(repo: AdaptiveKnowledgeRepository):
    """Inserta proyectos de prueba reales del contexto peruano para validar el pipeline."""
    proyectos_demo = [
        ProyectoIngenieria(
            id_referencia="AS-SM-12-2024-SEDAPAL",
            fuente_origen="SEACE_OCDS",
            titulo_proyecto="MEJORAMIENTO DEL SISTEMA DE BOMBEO ELECTROMECANICO Y LINEA DE IMPULSION",
            disciplina="Mecanica",
            entidad_o_cliente="SEDAPAL",
            presupuesto_referencial=1850000.0,
            monto_adjudicado=1795000.0,
            postor_ganador="CONSORCIO HIDRAULICO DEL SUR",
            ruc_ganador="20548963211",
            normas_identificadas=["ASME B16.5", "ASME B31.3", "ISO 9906", "AWS D1.1"],
            requisitos=[
                RequisitoTecnico("Presión de diseño", 150.0, "psi", norma_asociada="ASME B16.5"),
                RequisitoTecnico("Diámetro de tubería", 100.0, "mm", norma_asociada="ISO 7005"),
                RequisitoTecnico("Potencia de electrobomba", 75.0, "hp"),
                RequisitoTecnico("Caudal nominal", 45.0, "lps")
            ]
        ),
        ProyectoIngenieria(
            id_referencia="LP-SM-04-2025-ELECTROPERU",
            fuente_origen="SEACE_OCDS",
            titulo_proyecto="FABRICACION Y MONTAJE DE ESTRUCTURA METALICA Y PUENTE GRUA 20 TN",
            disciplina="Mecanica",
            entidad_o_cliente="ELECTROPERU S.A.",
            presupuesto_referencial=3200000.0,
            monto_adjudicado=3150000.0,
            postor_ganador="METALMECANICA INDUSTRIAL S.A.C.",
            ruc_ganador="20104587963",
            normas_identificadas=["AISC 360", "ISO 1101", "ISO 2768-M", "CMAA 70"],
            requisitos=[
                RequisitoTecnico("Capacidad de carga", 20.0, "tn"),
                RequisitoTecnico("Luz del puente", 18.5, "m"),
                RequisitoTecnico("Tolerancia de mecanizado", 0.05, "mm", norma_asociada="ISO 2768-mK")
            ]
        ),
        ProyectoIngenieria(
            id_referencia="CP-SM-08-2024-MINEM",
            fuente_origen="SEACE_OCDS",
            titulo_proyecto="SUMINISTRO E INSTALACION DE TABLEROS ELECTRICOS Y CELDAS DE MEDIA TENSION 22.9 KV",
            disciplina="Electrica",
            entidad_o_cliente="MINISTERIO DE ENERGIA Y MINAS",
            presupuesto_referencial=2450000.0,
            monto_adjudicado=2380000.0,
            postor_ganador="INGENIERIA Y POTENCIA ELECTRICA E.I.R.L.",
            ruc_ganador="20601245899",
            normas_identificadas=["IEC 61439", "IEC 62271-200", "IEEE C37.20.2", "CNE"],
            requisitos=[
                RequisitoTecnico("Tensión nominal", 22.9, "kv", norma_asociada="IEC 62271"),
                RequisitoTecnico("Frecuencia", 60.0, "hz"),
                RequisitoTecnico("Corriente de cortocircuito", 25.0, "ka")
            ]
        ),
        ProyectoIngenieria(
            id_referencia="LP-SM-15-2024-ELECTROPUNO",
            fuente_origen="SEACE_OCDS",
            titulo_proyecto="CREACION Y MEJORAMIENTO DE REDES Y LINEA PRIMARIA 22.9 KV Y SUBESTACIONES EN ZONAS RURALES - PUNO",
            disciplina="Electrica",
            entidad_o_cliente="ELECTRO PUNO S.A.A.",
            presupuesto_referencial=4850000.0,
            monto_adjudicado=4680000.0,
            postor_ganador="CONSORCIO ELECTROMECANICO ALTIPLANO",
            ruc_ganador="20448192033",
            normas_identificadas=["CNE SUMINISTRO 2011", "R.D. 018-2003-EM/DGE", "NTP 370.258", "NTP 339.027", "IEC 60076", "IEC 61089", "IEC 60071-2", "ASTM B399", "ASTM A153"],
            requisitos=[
                RequisitoTecnico("Tensión nominal MT", 22.9, "kv", norma_asociada="CNE Suministro"),
                RequisitoTecnico("Sección conductor AAAC", 35.0, "mm2", norma_asociada="NTP 370.258"),
                RequisitoTecnico("Potencia transformador SED", 100.0, "kva", norma_asociada="IEC 60076"),
                RequisitoTecnico("Altura poste C.A.C.", 12.0, "m", norma_asociada="NTP 339.027"),
                RequisitoTecnico("Nivel básico de aislamiento BIL", 150.0, "kv", norma_asociada="IEC 60071-2"),
                RequisitoTecnico("Tensión asignada Cut-Out", 27.0, "kv", norma_asociada="ANSI C37.42"),
                RequisitoTecnico("Tensión nominal Pararrayos ZnO", 21.0, "kv", norma_asociada="IEC 60099-4")
            ]
        )
    ]
    for p in proyectos_demo:
        repo.guardar_proyecto(p)
    print(f"[OK] Se cargaron {len(proyectos_demo)} proyectos precedentes de demostración en la base de datos.")


def main():
    parser = argparse.ArgumentParser(description="SEACE CAD Intelligence CLI")
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponibles")

    # Comando: demo
    subparsers.add_parser("demo", help="Poblar base de datos con proyectos reales de ejemplo")

    # Comando: stats
    subparsers.add_parser("stats", help="Mostrar estadísticas de la base de datos de conocimiento")

    # Comando: search
    p_search = subparsers.add_parser("search", help="Buscar proyectos por criterios")
    p_search.add_argument("--disciplina", type=str, help="Filtrar por disciplina (Mecanica, Electrica, etc.)")
    p_search.add_argument("--norma", type=str, help="Filtrar por norma (ej. ASME, ISO, IEC, CNE, NTP)")
    p_search.add_argument("--texto", type=str, help="Texto libre en título o postor")

    # Comando: generate-cad
    p_cad = subparsers.add_parser("generate-cad", help="Generar script CAD paramétrico o archivo DXF")
    p_cad.add_argument("--tipo", type=str, required=True,
                       choices=["brida", "eje", "skid", "tablero", "poste", "ps1", "pa1", "pr1", "sab1", "retenida"],
                       help="Tipo de componente electromecánico o estructural")
    p_cad.add_argument("--motor", type=str, default="cadquery", choices=["cadquery", "build123d"], help="Motor CAD")
    p_cad.add_argument("--formato", type=str, default="python", choices=["python", "dxf"], help="Formato de salida (script python o plano DXF)")
    p_cad.add_argument("--output", type=str, default="exports/componente_parametrico.py", help="Ruta del archivo generado")
    p_cad.add_argument("--modelo", type=str, default="12/400", choices=["12/300", "12/400", "13/400"], help="Modelo de poste C.A.C.")
    p_cad.add_argument("--nps", type=str, default="2", help="Tamaño nominal de tubería (para brida)")
    p_cad.add_argument("--alto", type=float, default=1200.0, help="Altura en mm (para tablero o skid)")
    p_cad.add_argument("--ancho", type=float, default=800.0, help="Ancho en mm (para tablero o skid)")
    p_cad.add_argument("--prof", type=float, default=400.0, help="Profundidad en mm (para tablero)")

    # Comando: generate-tdr
    p_tdr = subparsers.add_parser("generate-tdr", help="Generar TDR de nuevo proyecto basado en precedentes")
    p_tdr.add_argument("--ref", type=str, required=True, help="ID de referencia del proyecto precedente")
    p_tdr.add_argument("--titulo", type=str, required=True, help="Título del nuevo proyecto de tu autoría")
    p_tdr.add_argument("--autor", type=str, default="Ing. Renzo Mamani", help="Nombre del proyectista")
    p_tdr.add_argument("--output", type=str, default="exports/TDR_Nuevo_Proyecto.md", help="Ruta del archivo Markdown")

    # Comando: ocds-unpack (Integración ocdskit)
    p_ocds = subparsers.add_parser("ocds-unpack", help="Importar paquete de entregas OCDS (JSON) al repositorio")
    p_ocds.add_argument("--archivo", type=str, required=True, help="Ruta al archivo JSON OCDS del OECE")

    # Comando: batch-template (Integración seace-scraper)
    p_batch = subparsers.add_parser("batch-template", help="Generar plantilla parameters.csv para scraping batch")
    p_batch.add_argument("--output", type=str, default="parameters_template.csv", help="Ruta del archivo CSV")

    # Comando: parse-docling (Integración Docling/pdfplumber)
    p_doc = subparsers.add_parser("parse-docling", help="Minería profunda de metrados y materiales en PDF")
    p_doc.add_argument("--pdf", type=str, required=True, help="Ruta al expediente técnico en PDF")

    args = parser.parse_args()

    repo = AdaptiveKnowledgeRepository()

    if args.comando == "demo":
        poblar_demo(repo)

    elif args.comando == "stats":
        stats = repo.obtener_estadisticas()
        print("\n=== ESTADÍSTICAS DEL REPOSITORIO DE INGENIERÍA ===")
        print(f"Total de proyectos catalogados: {stats['total_proyectos']}")
        print(f"Monto total adjudicado registrado: S/. {stats['total_monto_adjudicado_pen']:,.2f}")
        print("Distribución por disciplinas:")
        for disc, cant in stats["distribucion_disciplinas"].items():
            print(f"  - {disc}: {cant} proyectos")
        print("="*50 + "\n")

    elif args.comando == "search":
        res = repo.buscar_por_criterios(disciplina=args.disciplina, norma=args.norma, texto=args.texto)
        print(f"\n[+] Se encontraron {len(res)} proyectos coincidentes:\n")
        for r in res:
            print(f"• [{r['id_referencia']}] {r['titulo_proyecto'][:60]}...")
            print(f"  Entidad: {r['entidad_o_cliente']} | Ganador: {r['postor_ganador']}")
            print(f"  Monto Adjudicado: S/. {r['monto_adjudicado']:,.2f} | Disciplina: {r['disciplina']}")
            print(f"  Normas detectadas: {', '.join(r['normas_identificadas'])}\n")

    elif args.comando == "generate-cad":
        params = {
            "nps": args.nps,
            "alto": args.alto,
            "ancho": args.ancho,
            "profundidad": args.prof,
            "largo": args.alto,
            "modelo": args.modelo
        }
        if args.formato == "dxf":
            salida = CADCodeExporter.exportar_dxf(args.tipo, args.output, params)
            print(f"[OK] Archivo DXF generado con exito en: {salida}")
        else:
            codigo = CADCodeExporter.generar_codigo(args.tipo, params, motor=args.motor)
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(codigo)
            print(f"[OK] Script CAD parametrico ({args.motor}) generado con exito en: {args.output}")

    elif args.comando == "generate-tdr":
        precedente = repo.obtener_por_id(args.ref)
        if not precedente:
            print(f"[-] Error: Proyecto precedente '{args.ref}' no encontrado en la base de datos.")
            sys.exit(1)

        doc = EngineeringTDRGenerator.generar_documento_tdr(
            titulo_nuevo_proyecto=args.titulo,
            autor=args.autor,
            disciplina=precedente.get("disciplina", "Multidisciplinario"),
            normas_aplicables=precedente.get("normas_identificadas", []),
            requisitos_dimensionales=precedente.get("requisitos", []),
            proyecto_precedente=precedente
        )

        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(doc)
        print(f"[OK] Expediente tecnico y TDR generado con exito en: {args.output}")

    elif args.comando == "ocds-unpack":
        from .integrations.ocdskit_bridge import OCDSPackageBridge
        proyectos = OCDSPackageBridge.procesar_archivo_ocds(args.archivo)
        for p in proyectos:
            repo.guardar_proyecto(p)
        print(f"[OK] Se importaron {len(proyectos)} proyectos OCDS al repositorio.")

    elif args.comando == "batch-template":
        from .integrations.seace_scraper_engine import BatchSEACEScraperEngine
        ruta = BatchSEACEScraperEngine.generar_plantilla_parametros(args.output)
        print(f"[OK] Plantilla generada en: {ruta}")

    elif args.comando == "parse-docling":
        from .integrations.docling_bridge import AdvancedDocumentMiner
        partidas = AdvancedDocumentMiner.extraer_tablas_metrados(args.pdf)
        print(f"\n[+] Se identificaron {len(partidas)} partidas de metrado en el documento.")
        for p in partidas[:10]:
            print(f"  - Ítem {p['item']}: {p['descripcion'][:45]} ({p['metrado']} {p['unidad']})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
