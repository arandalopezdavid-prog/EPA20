"""
EPA20 — Buscador de Streaming para España
App Android con Kivy + KivyMD
"""

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
import urllib.request
import threading

BG       = "#0d0f14"
BG2      = "#161820"
BG3      = "#1e2130"
ACCENT   = "#e5a00d"
TEXT     = "#f0f0f0"
TEXT_DIM = "#7a8099"
GREEN    = "#4caf7d"
RED      = "#e05c5c"
ORANGE   = "#ff6b35"

PLATFORM_EMOJI = {
    "netflix": "N", "amazon": "P", "prime": "P",
    "disney": "D+", "hbo": "M", "max": "M",
    "apple": "A", "movistar": "M+", "filmin": "F",
    "rakuten": "R", "skyshowtime": "S", "paramount": "P+",
}

MONETIZACION = {
    "flatrate": ("Suscripcion", GREEN),
    "rent":     ("Alquiler",    ORANGE),
    "buy":      ("Compra",      ORANGE),
    "free":     ("GRATIS",      GREEN),
    "ads":      ("Gratis+Ads",  TEXT_DIM),
    "cinema":   ("En cines",    "#9b59b6"),
}

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex
<RootLayout>:
    orientation: 'vertical'
    md_bg_color: get_color_from_hex("#0d0f14")
    MDBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(100)
        md_bg_color: get_color_from_hex("#161820")
        padding: dp(16)
        spacing: dp(4)
        MDLabel:
            text: "EPA20"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#e5a00d")
            halign: "center"
        MDLabel:
            text: "Buscador de Streaming - Espana"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#7a8099")
            halign: "center"
    MDBoxLayout:
        size_hint_y: None
        height: dp(2)
        md_bg_color: get_color_from_hex("#e5a00d")
    MDBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(90)
        padding: dp(12)
        spacing: dp(8)
        md_bg_color: get_color_from_hex("#0d0f14")
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(8)
            MDTextField:
                id: search_input
                hint_text: "Pelicula o serie..."
                mode: "rectangle"
                line_color_focus: get_color_from_hex("#e5a00d")
                fill_color_normal: get_color_from_hex("#1e2130")
                fill_color_focus: get_color_from_hex("#1e2130")
                on_text_validate: app.buscar()
            MDRaisedButton:
                text: "BUSCAR"
                md_bg_color: get_color_from_hex("#e5a00d")
                text_color: get_color_from_hex("#0d0f14")
                bold: True
                on_release: app.buscar()
    MDLabel:
        id: lbl_estado
        text: ""
        size_hint_y: None
        height: dp(24)
        font_style: "Caption"
        halign: "center"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#7a8099")
    MDScrollView:
        MDBoxLayout:
            id: results_box
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height
    MDLabel:
        text: "Datos de JustWatch.com"
        size_hint_y: None
        height: dp(28)
        font_style: "Caption"
        halign: "center"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#7a8099")
        md_bg_color: get_color_from_hex("#161820")
'''

def nombre_plataforma(package):
    for attr in ["clear_name", "name", "technical_name", "short_name"]:
        val = getattr(package, attr, None)
        if val: return str(val)
    return "Desconocida"

def icono_plataforma(nombre):
    n = nombre.lower()
    for key, ico in PLATFORM_EMOJI.items():
        if key in n: return ico
    return "TV"

class RootLayout(MDBoxLayout):
    pass

class EPA20App(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        Window.clearcolor = get_color_from_hex(BG)
        return Builder.load_string(KV)

    def buscar(self):
        titulo = self.root.ids.search_input.text.strip()
        if not titulo:
            self.set_estado("Escribe un titulo primero", RED)
            return
        self.set_estado("Buscando...", ACCENT)
        self.root.ids.results_box.clear_widgets()
        threading.Thread(target=self._buscar_thread, args=(titulo,), daemon=True).start()

    def _buscar_thread(self, titulo):
        try:
            from simplejustwatchapi.justwatch import search
            resultados = search(titulo, "ES", "es", 8, best_only=True)
            Clock.schedule_once(lambda dt: self._mostrar(titulo, resultados))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_estado("Error: " + str(e), RED))

    def _mostrar(self, titulo, resultados):
        from kivy.metrics import dp
        if not resultados:
            self.set_estado("Sin resultados para " + titulo, RED)
            return
        self.set_estado(str(len(resultados)) + " resultado(s)", GREEN)
        for entry in resultados:
            tipo = "Pelicula" if entry.object_type == "MOVIE" else "Serie"
            anio = entry.release_year or "?"
            card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(8),
                size_hint_y=None, height=dp(150),
                md_bg_color=get_color_from_hex(BG2), radius=[12], elevation=4)
            card.add_widget(MDLabel(text=entry.title, font_style="H6", bold=True,
                theme_text_color="Custom", text_color=get_color_from_hex(TEXT),
                size_hint_y=None, height=dp(32)))
            card.add_widget(MDLabel(text=tipo + " - " + str(anio), font_style="Caption",
                theme_text_color="Custom", text_color=get_color_from_hex(TEXT_DIM),
                size_hint_y=None, height=dp(20)))
            if not entry.offers:
                card.add_widget(MDLabel(text="No disponible en Espana",
                    font_style="Body2", theme_text_color="Custom",
                    text_color=get_color_from_hex(TEXT_DIM), size_hint_y=None, height=dp(28)))
            else:
                plataformas = {}
                for offer in entry.offers:
                    nombre = nombre_plataforma(offer.package)
                    tipo_mon, color = MONETIZACION.get(offer.monetization_type, (offer.monetization_type, TEXT_DIM))
                    plataformas.setdefault(nombre, (tipo_mon, color))
                grid = MDGridLayout(cols=2, spacing=dp(6), size_hint_y=None,
                    height=dp((len(plataformas)//2+1)*52))
                for nombre, (tipo_mon, color) in sorted(plataformas.items()):
                    ico = icono_plataforma(nombre)
                    chip = MDCard(orientation="vertical", padding=dp(8), spacing=dp(2),
                        md_bg_color=get_color_from_hex(BG3), radius=[8],
                        size_hint_y=None, height=dp(48))
                    chip.add_widget(MDLabel(text=ico + "  " + nombre, font_style="Body2",
                        bold=True, theme_text_color="Custom", text_color=get_color_from_hex(TEXT),
                        size_hint_y=None, height=dp(22)))
                    chip.add_widget(MDLabel(text=tipo_mon, font_style="Caption",
                        theme_text_color="Custom", text_color=get_color_from_hex(color),
                        size_hint_y=None, height=dp(18)))
                    grid.add_widget(chip)
                card.add_widget(grid)
                card.height = dp(100 + (len(plataformas)//2+1)*52)
            self.root.ids.results_box.add_widget(card)

    def set_estado(self, msg, color):
        self.root.ids.lbl_estado.text = msg
        self.root.ids.lbl_estado.text_color = get_color_from_hex(color)

if __name__ == "__main__":
    EPA20App().run()
