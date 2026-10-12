"""
MÓDULO: seace_cad_intelligence/extractors/seace_web_crawler.py
Crawler para el Buscador Público de SEACE 3.0 (JSF / PrimeFaces).
"""

from typing import Any, Dict, List
from ..core.adapters import BaseDataSourceAdapter
from ..core.models import ProyectoIngenieria
from ..core.analyzer import EngineeringIntelligenceEngine


class SEACEWebCrawler(BaseDataSourceAdapter):
    """Interacción automatizada con el portal web de SEACE usando Playwright."""

    URL_BUSCADOR = "https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"

    def __init__(self):
        self.headless: bool = False
        self.timeout_ms: int = 40000

    def inicializar(self, config: Dict[str, Any]) -> bool:
        self.headless = config.get("headless", False)
        self.timeout_ms = config.get("timeout_ms", 40000)
        return True

    def extraer_proyectos(self, criterios: Dict[str, Any]) -> List[ProyectoIngenieria]:
        """
        Navega al buscador público, llena los filtros de búsqueda y extrae resultados.
        Requiere tener instalado Playwright (`playwright install chromium`).
        """
        proyectos: List[ProyectoIngenieria] = []
        anio = str(criterios.get("anio", "2025"))
        palabra_clave = criterios.get("palabra_clave", "ELECTROMECANICO")
        objeto = criterios.get("objeto", "Obra")

        print(f"[SEACE Crawler] Iniciando navegador (Headless: {self.headless})...")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("[SEACE Crawler] Playwright no está instalado. Ejecute: pip install playwright && playwright install")
            return []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1366, "height": 768})
            page = context.new_page()

            try:
                page.goto(self.URL_BUSCADOR, timeout=self.timeout_ms)
                page.wait_for_load_state("networkidle")

                # Pestaña 1: Procedimientos de Selección
                tab1 = page.locator("a[href*='tbBuscador:tab1']")
                if tab1.is_visible():
                    tab1.click()
                    page.wait_for_timeout(1000)

                # Año de convocatoria
                sel_anio = page.locator("select[id*='cboAnio']")
                if sel_anio.is_visible():
                    sel_anio.select_option(anio)

                # Objeto de contratación
                sel_obj = page.locator("select[id*='cboObjetoContratacion']")
                if sel_obj.is_visible():
                    sel_obj.select_option(label=objeto)

                # Descripción del objeto
                txt_obj = page.locator("input[id*='txtObjeto']")
                if txt_obj.is_visible():
                    txt_obj.fill(palabra_clave)

                print("\n" + "="*60)
                print("[SEACE Crawler] Resuelva el CAPTCHA gráfico en la ventana del navegador.")
                print("[SEACE Crawler] Haga clic en 'Buscar' cuando esté listo.")
                print("="*60 + "\n")

                # Esperar hasta 90 segundos a que la tabla cargue filas
                page.wait_for_selector("div[id*='tblResultados'] tbody tr", timeout=90000)
                page.wait_for_timeout(2000)

                filas = page.locator("div[id*='tblResultados'] tbody tr").all()
                for f in filas:
                    celdas = f.locator("td").all_text_contents()
                    if len(celdas) >= 5:
                        entidad = celdas[1].strip()
                        nomenclatura = celdas[2].strip()
                        descripcion = celdas[4].strip()
                        monto_txt = celdas[5].strip() if len(celdas) > 5 else "0"
                        
                        try:
                            monto = float(monto_txt.replace(",", "").replace("S/.", "").strip())
                        except ValueError:
                            monto = 0.0

                        normas = EngineeringIntelligenceEngine.extraer_normas(descripcion)
                        disciplina = EngineeringIntelligenceEngine.clasificar_disciplina(descripcion)
                        reqs = EngineeringIntelligenceEngine.extraer_requisitos_tecnicos(descripcion)

                        proyectos.append(ProyectoIngenieria(
                            id_referencia=nomenclatura,
                            fuente_origen="SEACE_WEB_BUSCADOR",
                            titulo_proyecto=descripcion,
                            disciplina=disciplina,
                            entidad_o_cliente=entidad,
                            presupuesto_referencial=monto,
                            monto_adjudicado=monto,
                            normas_identificadas=normas,
                            requisitos=reqs
                        ))

                print(f"[SEACE Crawler] Se capturaron {len(proyectos)} procesos en pantalla.")

            except Exception as e:
                print(f"[SEACE Crawler] Error durante la navegación: {e}")
            finally:
                browser.close()

        return proyectos
