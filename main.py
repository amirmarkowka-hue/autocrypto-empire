import random
import time
import os
import pickle
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex

# ============================================================
# НАСТРОЙКИ / КОНСТАНТЫ
# ============================================================

START_RUB = 100_000
START_USD = 1_000
START_BET = 100.0
START_STR = 100.0
PRICE_MULT = 8
STROBE_COST = 15_000
STAGE_COST = {1: 0.05, 2: 0.08, 3: 0.15, 4: 0.30}
STAGE_POWER = {0: 1.0, 1: 1.05, 2: 1.15, 3: 1.35, 4: 1.7}
BASE_CAR_SLOTS = 3
DOLLARS_PER_MINUTE = 1
USD_TO_RUB = 100
ACTION_MINUTES = 15
ADMIN_PASSWORD = "admin2026"

# НОВЫЕ КОНСТАНТЫ
REPAIR_COST_PER_PERCENT = 1500  # 1500 руб за 1% ремонта
JDM_SWAP_COST = 250_000         # Стоимость свапа 2JZ
JDM_BRANDS = ["Toyota", "Nissan", "Mazda", "Subaru", "Mitsubishi", "Honda"]

COLORS = {
    "bg": "#0D1117", "card": "#161B22", "card2": "#1F2430",
    "primary": "#58A6FF", "success": "#3FB950", "warning": "#D29922",
    "danger": "#F85149", "text": "#E6EDF3", "text_dim": "#8B949E",
    "accent": "#A371F7", "gold": "#FFD700",
}

CITIES = {
    "Москва":       {"fuel": 0,     "rarity_min": 4, "rarity_max": 5, "price_mod": 2.0,
                     "cond_min": 88, "cond_max": 100, "desc": "Элитный · премиум"},
    "Лыткарино":    {"fuel": 3_000, "rarity_min": 2, "rarity_max": 4, "price_mod": 1.5,
                     "cond_min": 60, "cond_max": 95, "desc": "Средний"},
    "Люберцы":      {"fuel": 4_500, "rarity_min": 2, "rarity_max": 4, "price_mod": 1.5,
                     "cond_min": 60, "cond_max": 95, "desc": "Средний"},
    "Жуковский":    {"fuel": 4_000, "rarity_min": 2, "rarity_max": 4, "price_mod": 1.5,
                     "cond_min": 60, "cond_max": 95, "desc": "Средний"},
    "Островцы":     {"fuel": 3_500, "rarity_min": 1, "rarity_max": 3, "price_mod": 1.0,
                     "cond_min": 40, "cond_max": 92, "desc": "Эконом"},
    "д. Васильево": {"fuel": 2_500, "rarity_min": 1, "rarity_max": 2, "price_mod": 1.0,
                     "cond_min": 20, "cond_max": 85, "desc": "Деревня"},
}

GARAGE_TEMPLATES = [
    {"name": "Эконом-гараж",   "cls": "Эконом",  "price_rub": 50_000,  "price_usd": 0,   "slots": 3},
    {"name": "Гараж-стандарт", "cls": "Эконом",  "price_rub": 150_000, "price_usd": 0,   "slots": 5},
    {"name": "Средний гараж",  "cls": "Средний", "price_rub": 400_000, "price_usd": 0,   "slots": 10},
    {"name": "Премиум-гараж",  "cls": "Средний", "price_rub": 700_000, "price_usd": 0,   "slots": 15},
    {"name": "Элитный гараж",  "cls": "Элитный", "price_rub": 0,       "price_usd": 800, "slots": 30},
]

MINE_TEMPLATES = [
    {"name": "Базовая ферма", "cls": "Базовая", "price_usd": 100,  "bet_day": 0.5,  "str_day": 1.0},
    {"name": "Средняя ферма", "cls": "Средняя", "price_usd": 500,  "bet_day": 2.0,  "str_day": 4.0},
    {"name": "Элитная ферма", "cls": "Элитная", "price_usd": 2500, "bet_day": 10.0, "str_day": 20.0},
]

CAR_DATABASE = [
    ("Lada", "Granta", 6_500, 87, 1), ("Lada", "Vesta", 11_000, 113, 1),
    ("Renault", "Logan", 9_000, 90, 1), ("Hyundai", "Solaris", 14_000, 123, 1),
    ("Kia", "Rio", 15_000, 123, 1), ("Volkswagen", "Polo", 17_000, 110, 2),
    ("Ford", "Focus", 18_000, 125, 2), ("Toyota", "Corolla", 22_000, 140, 2),
    ("Skoda", "Octavia", 24_000, 150, 2), ("Honda", "Civic", 26_000, 158, 2),
    ("Mazda", "CX-5", 32_000, 165, 3), ("Toyota", "Camry", 35_000, 200, 3),
    ("Nissan", "X-Trail", 33_000, 170, 3), ("Volkswagen", "Passat", 36_000, 180, 3),
    ("Toyota", "Mark II", 20_000, 200, 3), ("Toyota", "Chaser", 22_000, 220, 3),
    ("Toyota", "Chaser Tourer V", 24_000, 280, 4), ("Toyota", "Supra", 55_000, 320, 4),
    ("Nissan", "Silvia S15", 30_000, 250, 3), ("Nissan", "Skyline R34", 75_000, 280, 4),
    ("Nissan", "Skyline GT-R R35", 95_000, 570, 5), ("Mazda", "RX-7 FD", 45_000, 280, 4),
    ("Mazda", "RX-8", 18_000, 231, 3), ("Subaru", "Impreza WRX STI", 35_000, 300, 4),
    ("Mitsubishi", "Lancer Evolution X", 38_000, 291, 4), ("Honda", "NSX", 90_000, 290, 5),
    ("BMW", "3 Series", 48_000, 255, 3), ("Mercedes-Benz", "C-Class", 52_000, 245, 3),
    ("Audi", "A4", 50_000, 240, 3), ("Lexus", "ES", 55_000, 215, 4),
    ("BMW", "5 Series", 62_000, 330, 4), ("Mercedes-Benz", "E-Class", 65_000, 320, 4),
    ("Audi", "Q7", 75_000, 340, 4), ("Porsche", "Macan", 85_000, 360, 4),
    ("Porsche", "911 Carrera", 145_000, 385, 5), ("BMW", "M5", 120_000, 625, 5),
    ("Mercedes-Benz", "AMG GT", 160_000, 585, 5), ("Audi", "R8", 180_000, 610, 5),
    ("Ferrari", "F8 Tributo", 280_000, 720, 5), ("Lamborghini", "Huracán", 260_000, 640, 5),
    ("McLaren", "720S", 300_000, 720, 5), ("Bugatti", "Chiron", 1_500_000, 1500, 5),
]

CONDITIONS = {
    (0, 30): "Ржавая", (30, 45): "Плохая", (45, 60): "Уставшая",
    (60, 75): "Рабочая", (75, 88): "Хорошая", (88, 95): "Отличная", (95, 101): "Идеал",
}

def condition_label(cond):
    for (lo, hi), name in CONDITIONS.items():
        if lo <= cond < hi: return name
    return "?"

def cond_color(cond):
    if cond >= 88: return COLORS["success"]
    if cond >= 60: return COLORS["warning"]
    return COLORS["danger"]

def rub(v): return f"{v:,.0f} ₽".replace(",", " ")
def usd(v): return f"${v:,.0f}".replace(",", " ")

try: _BASE = os.path.dirname(os.path.abspath(__file__))
except NameError: _BASE = os.getcwd()
SAVE_FILE = os.path.join(_BASE, "savegame.pkl")

# ============================================================
# МОДЕЛИ
# ============================================================

class Crypto:
    def __init__(self, name, symbol, price, volatility, start_price):
        self.name = name; self.symbol = symbol; self.price = price
        self.start_price = start_price; self.volatility = volatility
        self.history = [price]; self.trend = 0.0

    def update_price(self):
        if random.random() < 0.12: self.trend = random.uniform(-0.025, 0.025)
        change = random.gauss(self.trend, self.volatility)
        self.price = max(1.0, self.price * (1 + change))
        self.history.append(self.price)
        if len(self.history) > 40: self.history.pop(0)

    def change_percent(self, days=5):
        if len(self.history) < 2: return 0
        old = self.history[-min(days, len(self.history))]
        return (self.price - old) / old * 100

class MiningFarm:
    def __init__(self, template):
        self.name = template["name"]; self.cls = template["cls"]
        self.price_usd = template["price_usd"]
        self.bet_day = template["bet_day"]; self.str_day = template["str_day"]

class Car:
    def __init__(self, brand, model, base_price, base_power, rarity, condition=None):
        self.brand = brand; self.model = model
        self.full_name = f"{brand} {model}"
        self.base_price = base_price * PRICE_MULT
        self.base_power = base_power; self.rarity = rarity
        self.condition = condition if condition is not None else random.randint(60, 100)
        self.stage = 0
        self.has_strobe = False
        self.jdm_swapped = False # НОВОЕ: Сделан ли свап
        self.purchase_price = 0
        self.market_price = self.base_price
        self.update_price()

    def update_price(self):
        cond_f = 0.4 + self.condition / 100 * 0.7
        demand = random.uniform(0.88, 1.12)
        self.market_price = max(500, round(self.base_price * cond_f * demand))

    @property
    def power(self):
        base = self.base_power * STAGE_POWER[self.stage]
        if self.jdm_swapped:
            base *= 1.35 # Свап дает +35% к мощности
        return int(base)

    @property
    def upgrade_invested(self):
        total = sum(int(self.base_price * STAGE_COST[s]) for s in range(1, self.stage + 1))
        if self.has_strobe: total += STROBE_COST
        if self.jdm_swapped: total += JDM_SWAP_COST
        return total

    @property
    def sell_price(self):
        return int((self.market_price + self.upgrade_invested * 0.6) * 0.85)

class Player:
    def __init__(self, name, code):
        self.name = name; self.code = code
        self.money = START_RUB; self.dollars = START_USD
        self.portfolio = {"BET": START_BET, "STR": START_STR}
        self.cars = []; self.owned_garages = []; self.mining_farms = []
        self.stats = {
            "started_at": datetime.now().isoformat(), "total_seconds": 0.0,
            "dollars_paid_minutes": 0, "rub_earned": 0.0, "rub_spent": 0.0,
            "usd_earned_time": 0, "usd_spent": 0, "cars_bought": 0, "cars_sold": 0,
            "car_profit": 0.0, "crypto_buys": 0, "crypto_sells": 0, "crypto_profit": 0.0,
            "garages_bought": 0, "mining_bought": 0, "upgrades_installed": 0,
            "strobes_installed": 0, "jdm_swaps": 0, "haggles_success": 0,
            "cities_visited": 1, "best_car_sale": 0.0, "best_crypto_trade": 0.0,
            "peak_net_worth": START_RUB + START_USD * USD_TO_RUB + START_BET * 500 + START_STR * 250,
            "days_played": 1, "tutorial_done": False,
        }

    def crypto_value(self, bet, star): return self.portfolio["BET"] * bet.price + self.portfolio["STR"] * star.price
    def cars_value(self): return sum(c.market_price + c.upgrade_invested for c in self.cars)
    def total_capacity(self): return BASE_CAR_SLOTS + sum(GARAGE_TEMPLATES[idx]["slots"] for city, idx in self.owned_garages)
    def net_worth(self, bet, star): return self.money + self.dollars * USD_TO_RUB + self.cars_value() + self.crypto_value(bet, star)

# ============================================================
# UI-ХЕЛПЕРЫ
# ============================================================

def make_card(bg=None, radius=dp(16)):
    card = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8), size_hint_y=None)
    card.bind(minimum_height=card.setter('height'))
    with card.canvas.before:
        Color(*get_color_from_hex(bg or COLORS["card"]))
        card._bg = RoundedRectangle(radius=[radius])
    card.bind(pos=lambda w, v: setattr(w._bg, 'pos', v), size=lambda w, v: setattr(w._bg, 'size', v))
    return card

def make_label(text, size=sp(14), color=None, bold=False, halign='left'):
    lbl = Label(text=text, font_size=size, bold=bold, color=get_color_from_hex(color or COLORS["text"]),
                halign=halign, valign='middle', size_hint_y=None)
    lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
    lbl.bind(texture_size=lambda w, v: setattr(w, 'height', v[1]))
    return lbl

def make_button(text, on_press, color=None, size=sp(15), height=dp(48), bg=None):
    btn = Button(text=text, font_size=size, bold=True, background_normal='', background_down='',
                 background_color=get_color_from_hex(bg or COLORS["primary"]), color=get_color_from_hex(color or COLORS["text"]),
                 size_hint_y=None, height=height)
    with btn.canvas.before:
        Color(*get_color_from_hex(bg or COLORS["primary"]))
        btn._bg = RoundedRectangle(radius=[dp(10)])
    btn.bind(pos=lambda w, v: setattr(w._bg, 'pos', v), size=lambda w, v: setattr(w._bg, 'size', v))
    btn.bind(on_press=on_press)
    return btn

def show_popup(title, message, on_ok=None):
    popup = Popup(title=title, title_size=sp(16),
                  content=Label(text=message, font_size=sp(14), color=get_color_from_hex(COLORS["text"]), halign='center', valign='middle'),
                  size_hint=(0.85, 0.4), background_color=get_color_from_hex(COLORS["card"]),
                  title_color=get_color_from_hex(COLORS["text"]))
    popup.content.bind(size=lambda w, v: setattr(w, 'text_size', v))
    if on_ok: popup.bind(on_dismiss=lambda *_: on_ok())
    popup.open()

def input_popup(title, hint, on_confirm, initial=""):
    content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    lbl = make_label(hint, size=sp(13), color=COLORS["text_dim"], halign='center')
    lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
    content.add_widget(lbl)
    ti = TextInput(text=initial, multiline=False, font_size=sp(16), background_color=get_color_from_hex(COLORS["card2"]),
                   foreground_color=get_color_from_hex(COLORS["text"]), cursor_color=get_color_from_hex(COLORS["primary"]), padding=[dp(10), dp(10)])
    content.add_widget(ti)
    btn_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
    cancel = Button(text="Отмена", background_color=get_color_from_hex(COLORS["card2"]), background_normal='')
    ok = Button(text="ОК", background_color=get_color_from_hex(COLORS["primary"]), background_normal='')
    btn_box.add_widget(cancel); btn_box.add_widget(ok)
    content.add_widget(btn_box)

    popup = Popup(title=title, title_size=sp(16), content=content, size_hint=(0.9, 0.35),
                  background_color=get_color_from_hex(COLORS["card"]), title_color=get_color_from_hex(COLORS["text"]))

    def _confirm(*_): popup.dismiss(); on_confirm(ti.text.strip())
    def _cancel(*_): popup.dismiss()
    ok.bind(on_press=_confirm); cancel.bind(on_press=_cancel)
    popup.open()

def confirm_popup(title, message, on_yes, on_no=None):
    content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    lbl = make_label(message, size=sp(14), halign='center')
    lbl.bind(size=lambda w, v: setattr(w, 'text_size', v))
    content.add_widget(lbl)
    btn_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
    no = Button(text="Нет", background_color=get_color_from_hex(COLORS["card2"]), background_normal='')
    yes = Button(text="Да", background_color=get_color_from_hex(COLORS["success"]), background_normal='')
    btn_box.add_widget(no); btn_box.add_widget(yes)
    content.add_widget(btn_box)

    popup = Popup(title=title, title_size=sp(16), content=content, size_hint=(0.85, 0.4),
                  background_color=get_color_from_hex(COLORS["card"]), title_color=get_color_from_hex(COLORS["text"]))

    def _yes(*_): popup.dismiss(); on_yes()
    def _no(*_): popup.dismiss(); on_no() if on_no else None
    yes.bind(on_press=_yes); no.bind(on_press=_no)
    popup.open()

# ============================================================
# ЭКРАНЫ
# ============================================================

class BaseScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))
        with self.root.canvas.before:
            Color(*get_color_from_hex(COLORS["bg"]))
            self._bg = Rectangle()
        self.root.bind(pos=lambda w, v: setattr(self._bg, 'pos', v), size=lambda w, v: setattr(self._bg, 'size', v))
        self.add_widget(self.root)

    def build_header(self, title):
        bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        back = Button(text="←", size_hint_x=None, width=dp(50), font_size=sp(22), background_normal='',
                      background_color=get_color_from_hex(COLORS["card2"]), color=get_color_from_hex(COLORS["text"]))
        back.bind(on_press=lambda *_: self.app.goto('menu'))
        bar.add_widget(back)
        bar.add_widget(Label(text=title, font_size=sp(18), bold=True, color=get_color_from_hex(COLORS["text"])))
        bar.add_widget(Widget(size_hint_x=None, width=dp(50)))
        self.root.add_widget(bar)

class MenuScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'menu'; self.build()

    def build(self):
        self.root.clear_widgets()
        p = self.app.game.player; g = self.app.game; bet = g.betkoin; star = g.starkoin

        top = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        info = BoxLayout(orientation='vertical')
        info.add_widget(make_label(f"👤 {p.name}", size=sp(15), bold=True))
        info.add_widget(make_label(f"📍 {g.city}  ·  День {g.day}, {g.hour:02d}:{g.minute:02d}", size=sp(11), color=COLORS["text_dim"]))
        top.add_widget(info)
        self.root.add_widget(top)

        bal_card = make_card(COLORS["card2"]); bal_card.size_hint_y = None; bal_card.height = dp(90)
        bal = BoxLayout(spacing=dp(6))
        for title, val, color in [("₽", rub(p.money), COLORS["success"]), ("$", usd(p.dollars), COLORS["primary"]),
                                  ("🪙 BET", f"{p.portfolio['BET']:.1f}", COLORS["gold"]), ("⭐ STR", f"{p.portfolio['STR']:.1f}", COLORS["gold"])]:
            b = BoxLayout(orientation='vertical')
            b.add_widget(make_label(title, size=sp(11), color=COLORS["text_dim"]))
            b.add_widget(make_label(val, size=sp(16), bold=True, color=color))
            bal.add_widget(b)
        bal_card.add_widget(bal)
        self.root.add_widget(bal_card)

        nw = p.net_worth(bet, star)
        start_nw = START_RUB + START_USD * USD_TO_RUB + START_BET * 500 + START_STR * 250
        profit = nw - start_nw
        pc = COLORS["success"] if profit >= 0 else COLORS["danger"]; arrow = "▲" if profit >= 0 else "▼"
        cap_card = make_card(COLORS["card"]); cap_card.size_hint_y = None; cap_card.height = dp(58)
        cap_row = BoxLayout()
        cap_row.add_widget(make_label("🏦 Капитал", size=sp(13), color=COLORS["text_dim"]))
        cap_row.add_widget(make_label(rub(nw), size=sp(16), bold=True, color=COLORS["gold"], halign='right'))
        cap_card.add_widget(cap_row)
        cap_card.add_widget(make_label(f"{arrow} {profit:+,.0f} ₽", size=sp(11), color=pc, halign='right'))
        self.root.add_widget(cap_card)

        scroll = ScrollView(); grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        grid.bind(minimum_height=grid.setter('height'))

        items = [
            ("🚗 Автосалон", lambda *_: self.app.goto('shop')),
            ("🏠 Мой гараж", lambda *_: self.app.goto('garage')),
            ("💱 Крипта", lambda *_: self.app.goto('crypto')),
            ("🏢 Недвижимость", lambda *_: self.app.goto('realestate')),
            ("📈 Статистика", lambda *_: self.app.goto('stats')),
            ("🛏️ Спать", lambda *_: self.app.doSleep()),
            ("🚙 Город", lambda *_: self.app.goto('travel')),
            ("💾 Сохранить", lambda *_: self.app.doSave()),
        ]
        for label, cb in items:
            grid.add_widget(make_button(label, cb, height=dp(58)))
        scroll.add_widget(grid); self.root.add_widget(scroll)

    def on_pre_enter(self, *args): self.build()

class ShopScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'shop'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("🚗 Автосалон")
        p = self.app.game.player; g = self.app.game

        if not g.available_cars:
            self.root.add_widget(make_label("Все машины распроданы. Идите спать.", size=sp(14), color=COLORS["warning"], halign='center'))
            return

        self.root.add_widget(make_label(f"Слотов: {len(p.cars)}/{p.total_capacity()}   ₽ {rub(p.money)}", size=sp(12), color=COLORS["text_dim"], halign='center'))
        scroll = ScrollView(); box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=[0, dp(6)])
        box.bind(minimum_height=box.setter('height'))

        for i, car in enumerate(g.available_cars, 1):
            card = make_card(); card.size_hint_y = None; card.height = dp(130)
            top = BoxLayout(size_hint_y=None, height=dp(24))
            top.add_widget(make_label(f"#{i}  {car.full_name}", size=sp(15), bold=True))
            top.add_widget(make_label("★"*car.rarity + "☆"*(5-car.rarity), size=sp(12), color=COLORS["accent"], halign='right'))
            card.add_widget(top)
            card.add_widget(make_label(f"{car.power} л.с.  ·  {car.condition}% ({condition_label(car.condition)})", size=sp(12), color=cond_color(car.condition)))
            
            bottom = BoxLayout(size_hint_y=None, height=dp(44))
            afford = p.money >= car.market_price
            bottom.add_widget(make_label(rub(car.market_price), size=sp(16), bold=True, color=COLORS["success"] if afford else COLORS["danger"]))
            buy = Button(text="Купить", font_size=sp(13), bold=True, background_normal='', size_hint_x=None, width=dp(100),
                         background_color=get_color_from_hex(COLORS["primary"] if afford else COLORS["text_dim"]), color=get_color_from_hex(COLORS["text"]))
            buy.bind(on_press=lambda *_, c=car: self.buy(c))
            bottom.add_widget(buy); card.add_widget(bottom); box.add_widget(card)

        scroll.add_widget(box); self.root.add_widget(scroll)

    def buy(self, car):
        app = self.app; game = app.game; p = game.player
        if len(p.cars) >= p.total_capacity(): return show_popup("Лимит", f"Нет слотов! ({p.total_capacity()}). Купите гараж.")
        if p.money < car.market_price: return show_popup("Ошибка", "Недостаточно денег.")

        def do_buy():
            price = car.market_price
            p.money -= price; p.stats["rub_spent"] += price; p.stats["cars_bought"] += 1
            car.purchase_price = price; p.cars.append(car); game.available_cars.remove(car)
            game.advance_time(); game.save_game()
            show_popup("✅ Куплено", f"{car.full_name}\nза {rub(price)}"); self.build()

        def haggled(price): car.market_price = price; ask_code(p, do_buy)
        confirm_popup("Торг", "Поторговаться с продавцом?", on_yes=lambda: self._haggle_roll(car.market_price, haggled), on_no=lambda: do_buy())

    def _haggle_roll(self, price, on_done):
        if random.random() < 0.4:
            new_price = int(price * (1 - random.uniform(0.05, 0.65)))
            show_popup("✅ Успех!", f"Новая цена: {rub(new_price)}", on_ok=lambda: on_done(new_price))
            self.app.game.player.stats["haggles_success"] += 1
        else:
            show_popup("❌ Отказ", "Продавец не уступил.", on_ok=lambda: on_done(price))

def ask_code(player, on_success):
    input_popup("🔐 Код-подпись", "Введите ваш код:", lambda t: on_success() if t == player.code else show_popup("Ошибка", "Неверный код!"))

class GarageScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'garage'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("🏠 Мой гараж")
        p = self.app.game.player
        if not p.cars: return self.root.add_widget(make_label("У вас пока нет машин.", size=sp(14), color=COLORS["text_dim"], halign='center'))

        scroll = ScrollView(); box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        for i, car in enumerate(p.cars, 1):
            card = make_card(); card.size_hint_y = None; card.height = dp(115)
            top = BoxLayout(size_hint_y=None, height=dp(24))
            top.add_widget(make_label(f"#{i}  {car.full_name}", size=sp(15), bold=True))
            badges = f" S{car.stage}" if car.stage > 0 else ""
            if car.has_strobe: badges += " ✨"
            if car.jdm_swapped: badges += " 🔥JDM"
            if badges: top.add_widget(make_label(badges, size=sp(12), color=COLORS["accent"], halign='right'))
            card.add_widget(top)

            card.add_widget(make_label(f"{car.power} л.с.  ·  {car.condition}% ({condition_label(car.condition)})", size=sp(12), color=cond_color(car.condition)))
            card.add_widget(make_label(f"Куплено за: {rub(car.purchase_price)}", size=sp(11), color=COLORS["text_dim"]))
            card.add_widget(make_button("Управлять", lambda *_, c=car: self.open_car(c), height=dp(40), size=sp(13)))
            box.add_widget(card)

        scroll.add_widget(box); self.root.add_widget(scroll)

    def open_car(self, car): self.app.current_car = car; self.app.goto('cardetail')

class CarDetailScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'cardetail'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("🔧 Автомобиль")
        car = self.app.current_car
        if not car: return
        p = self.app.game.player

        # Оборачиваем в ScrollView, так как кнопок стало больше
        scroll = ScrollView()
        main_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=dp(8))
        main_box.bind(minimum_height=main_box.setter('height'))

        info = make_card(); info.size_hint_y = None; info.height = dp(190)
        info.add_widget(make_label(f"{car.full_name}", size=sp(18), bold=True))
        info.add_widget(make_label(f"Мощность: {car.power} л.с. (база {car.base_power})", size=sp(13)))
        info.add_widget(make_label(f"Stage: {car.stage}/4   Страбы: {'✅' if car.has_strobe else '❌'}", size=sp(13)))
        info.add_widget(make_label(f"Состояние: {car.condition}% ({condition_label(car.condition)})", size=sp(13), color=cond_color(car.condition)))
        info.add_widget(make_label(f"Куплено: {rub(car.purchase_price)}", size=sp(13), color=COLORS["text_dim"]))
        info.add_widget(make_label(f"Рынок: {rub(car.sell_price)}", size=sp(14), bold=True, color=COLORS["success"]))
        if car.jdm_swapped:
            info.add_widget(make_label("🔥 Установлен свап 2JZ", size=sp(14), bold=True, color=COLORS["danger"]))
        main_box.add_widget(info)

        max_sell = int(car.purchase_price * 1.4)
        main_box.add_widget(make_label(f"Макс. цена продажи: {rub(max_sell)} (+40%)", size=sp(12), color=COLORS["gold"], halign='center'))

        main_box.add_widget(make_button("💸 Продать (своя цена)", lambda *_: self.sell(car)))
        
        # НОВОЕ: Кнопка ремонта (Шпаклёвка)
        if car.condition < 100:
            repair_cost = (100 - car.condition) * REPAIR_COST_PER_PERCENT
            main_box.add_widget(make_button(f"🔧 Ремонт до 100% · {rub(repair_cost)}", lambda *_: self.repair(car), bg=COLORS["warning"]))
        
        if car.stage < 4:
            cost = int(car.base_price * STAGE_COST[car.stage + 1])
            gain = int((STAGE_POWER[car.stage + 1] / STAGE_POWER[car.stage] - 1) * 100)
            main_box.add_widget(make_button(f"⚙️ Stage {car.stage+1} (+{gain}%) · {rub(cost)}", lambda *_: self.upgrade(car)))
        
        if not car.has_strobe:
            main_box.add_widget(make_button(f"✨ Страбоскопы · {rub(STROBE_COST)}", lambda *_: self.add_strobe(car), bg=COLORS["accent"]))

        # НОВОЕ: JDM Свап
        if car.brand in JDM_BRANDS and not car.jdm_swapped:
            main_box.add_widget(make_button(f"🔥 Свап 2JZ (+35% мощн.) · {rub(JDM_SWAP_COST)}", lambda *_: self.jdm_swap(car), bg=COLORS["danger"]))

        scroll.add_widget(main_box)
        self.root.add_widget(scroll)

    def sell(self, car):
        p = self.app.game.player; max_sell = int(car.purchase_price * 1.4)
        def do_sell(text):
            try: ask = int(text.replace(" ", "")) if text else car.sell_price
            except ValueError: return
            if ask < 1 or ask > max_sell: return show_popup("Ошибка", f"Цена от 1 до {rub(max_sell)}")
            profit = ask - car.purchase_price
            p.money += ask; p.stats["rub_earned"] += ask; p.stats["cars_sold"] += 1
            p.stats["car_profit"] += profit; p.stats["best_car_sale"] = max(p.stats["best_car_sale"], ask)
            p.cars.remove(car); self.app.game.advance_time(); self.app.game.save_game()
            show_popup("✅ Продано", f"{car.full_name} за {rub(ask)}\nПрибыль: {profit:+,.0f} ₽", on_ok=lambda: self.app.goto('garage'))
        input_popup("💰 Продажа", f"Ваша цена (до {rub(max_sell)}):", do_sell, initial=str(car.sell_price))

    def repair(self, car):
        p = self.app.game.player
        cost = (100 - car.condition) * REPAIR_COST_PER_PERCENT
        if p.money < cost: return show_popup("Ошибка", f"Нужно {rub(cost)}")
        def do():
            p.money -= cost; p.stats["rub_spent"] += cost
            car.condition = 100; car.update_price()
            self.app.game.advance_time(30); self.app.game.save_game()
            show_popup("✅ Готово", "Машина отремонтирована (100%)!"); self.build()
        confirm_popup("🔧 Ремонт", f"Восстановить состояние за {rub(cost)}?", on_yes=do)

    def upgrade(self, car):
        p = self.app.game.player; cost = int(car.base_price * STAGE_COST[car.stage + 1])
        if p.money < cost: return show_popup("Ошибка", f"Нужно {rub(cost)}")
        def do():
            p.money -= cost; p.stats["rub_spent"] += cost; p.stats["upgrades_installed"] += 1
            car.stage += 1; car.market_price = int(car.market_price * 1.05)
            self.app.game.advance_time(); self.app.game.save_game()
            show_popup("✅ Stage", f"Stage {car.stage} установлен!\nМощность: {car.power} л.с."); self.build()
        confirm_popup("Тюнинг", f"Установить Stage {car.stage+1} за {rub(cost)}?", on_yes=do)

    def add_strobe(self, car):
        p = self.app.game.player
        if p.money < STROBE_COST: return show_popup("Ошибка", f"Нужно {rub(STROBE_COST)}")
        def do():
            p.money -= STROBE_COST; p.stats["rub_spent"] += STROBE_COST; p.stats["strobes_installed"] += 1
            car.has_strobe = True; self.app.game.advance_time(); self.app.game.save_game()
            show_popup("✨ Готово", "Страбоскопы установлены!"); self.build()
        confirm_popup("Страбы", f"Установить страбоскопы за {rub(STROBE_COST)}?", on_yes=do)

    def jdm_swap(self, car):
        p = self.app.game.player
        if p.money < JDM_SWAP_COST: return show_popup("Ошибка", f"Нужно {rub(JDM_SWAP_COST)}")
        def do():
            p.money -= JDM_SWAP_COST; p.stats["rub_spent"] += JDM_SWAP_COST; p.stats["jdm_swaps"] += 1
            car.jdm_swapped = True; car.market_price = int(car.market_price * 1.5)
            self.app.game.advance_time(120); self.app.game.save_game()
            show_popup("🔥 JDM", f"Свап 2JZ установлен!\nНовая мощность: {car.power} л.с."); self.build()
        confirm_popup("🔥 JDM Свап", f"Поставить легендарный 2JZ за {rub(JDM_SWAP_COST)}?", on_yes=do)

class CryptoScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'crypto'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("💱 Крипто-биржа")
        g = self.app.game; p = g.player
        for crypto, icon in [(g.betkoin, "🪙"), (g.starkoin, "⭐")]:
            card = make_card(); card.size_hint_y = None; card.height = dp(160)
            chg = crypto.change_percent(); arrow = "▲" if chg >= 0 else "▼"; chg_color = COLORS["success"] if chg >= 0 else COLORS["danger"]
            card.add_widget(make_label(f"{icon} {crypto.name} ({crypto.symbol})", size=sp(16), bold=True))
            card.add_widget(make_label(f"{rub(crypto.price)}   {arrow} {chg:+.2f}%", size=sp(14), color=chg_color))
            held = p.portfolio[crypto.symbol]
            card.add_widget(make_label(f"У вас: {held:.4f} ≈ {rub(held * crypto.price)}", size=sp(12), color=COLORS["text_dim"]))
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
            row.add_widget(make_button("Купить", lambda *_, c=crypto: self.trade(c, "BUY"), height=dp(40), size=sp(13)))
            row.add_widget(make_button("Продать", lambda *_, c=crypto: self.trade(c, "SELL"), bg=COLORS["danger"], height=dp(40), size=sp(13)))
            card.add_widget(row); self.root.add_widget(card)

    def trade(self, crypto, action):
        p = self.app.game.player; sym = crypto.symbol
        hint = f"Сколько {sym} {'купить' if action=='BUY' else 'продать'}? (макс {p.money/crypto.price:.2f})" if action=='BUY' else f"Сколько {sym} продать? (есть {p.portfolio[sym]:.4f})"
        def do(text):
            try: amount = float(text)
            except ValueError: return
            if amount <= 0: return
            if action == "BUY":
                cost = amount * crypto.price
                if cost > p.money: return show_popup("Ошибка", "Недостаточно денег!")
                p.money -= cost; p.stats["rub_spent"] += cost; p.portfolio[sym] += amount; p.stats["crypto_buys"] += 1
                self.app.game.advance_time(5); self.app.game.save_game()
                show_popup("✅ Куплено", f"{amount:.4f} {sym} за {rub(cost)}")
            else:
                if amount > p.portfolio[sym]: return show_popup("Ошибка", "Недостаточно монет!")
                rev = amount * crypto.price
                p.money += rev; p.stats["rub_earned"] += rev; p.portfolio[sym] -= amount; p.stats["crypto_sells"] += 1; p.stats["crypto_profit"] += rev
                self.app.game.advance_time(5); self.app.game.save_game()
                show_popup("✅ Продано", f"{amount:.4f} {sym} за {rub(rev)}")
            self.build()
        input_popup(f"{'Купить' if action=='BUY' else 'Продать'} {sym}", hint, do)

class RealEstateScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'realestate'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("🏢 Недвижимость")
        g = self.app.game; p = g.player
        self.root.add_widget(make_label(f"₽ {rub(p.money)}   $ {usd(p.dollars)}   Слотов: {p.total_capacity()}", size=sp(12), color=COLORS["text_dim"], halign='center'))
        scroll = ScrollView(); box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        box.add_widget(make_label("🏠 Гаражи", size=sp(15), bold=True, color=COLORS["primary"]))
        for i, t in enumerate(GARAGE_TEMPLATES, 1):
            owned = (g.city, i - 1) in p.owned_garages
            card = make_card(COLORS["card2"] if owned else COLORS["card"]); card.size_hint_y = None; card.height = dp(90)
            card.add_widget(make_label(f"{t['name']} ({t['cls']})", size=sp(14), bold=True))
            card.add_widget(make_label(f"+{t['slots']} слотов", size=sp(12), color=COLORS["text_dim"]))
            if owned: card.add_widget(make_label("✅ Куплен", size=sp(13), color=COLORS["success"]))
            else:
                price = rub(t["price_rub"]) if t["price_rub"] > 0 else usd(t["price_usd"])
                card.add_widget(make_button(f"Купить · {price}", lambda *_, idx=i-1: self.buy_garage(idx), height=dp(36), size=sp(13)))
            box.add_widget(card)

        box.add_widget(make_label("⛏️ Майнинг-фермы", size=sp(15), bold=True, color=COLORS["primary"]))
        for i, t in enumerate(MINE_TEMPLATES, 1):
            card = make_card(); card.size_hint_y = None; card.height = dp(90)
            card.add_widget(make_label(f"{t['name']} ({t['cls']})", size=sp(14), bold=True))
            card.add_widget(make_label(f"+{t['bet_day']:.2f} BET, +{t['str_day']:.2f} STR/день", size=sp(12), color=COLORS["success"]))
            card.add_widget(make_button(f"Купить · {usd(t['price_usd'])}", lambda *_, idx=i-1: self.buy_mining(idx), height=dp(36), size=sp(13)))
            box.add_widget(card)

        scroll.add_widget(box); self.root.add_widget(scroll)

    def buy_garage(self, idx):
        g = self.app.game; p = g.player; t = GARAGE_TEMPLATES[idx]
        if (g.city, idx) in p.owned_garages: return
        if t["price_rub"] > 0:
            if p.money < t["price_rub"]: return show_popup("Ошибка", f"Нужно {rub(t['price_rub'])}")
            p.money -= t["price_rub"]; p.stats["rub_spent"] += t["price_rub"]
        else:
            if p.dollars < t["price_usd"]: return show_popup("Ошибка", f"Нужно {usd(t['price_usd'])}")
            p.dollars -= t["price_usd"]; p.stats["usd_spent"] += t["price_usd"]
        p.owned_garages.append((g.city, idx)); p.stats["garages_bought"] += 1; g.save_game()
        show_popup("✅ Готово", f"{t['name']} куплен!"); self.build()

    def buy_mining(self, idx):
        g = self.app.game; p = g.player; t = MINE_TEMPLATES[idx]
        if p.dollars < t["price_usd"]: return show_popup("Ошибка", f"Нужно {usd(t['price_usd'])}")
        p.dollars -= t["price_usd"]; p.stats["usd_spent"] += t["price_usd"]; p.mining_farms.append(MiningFarm(t)); p.stats["mining_bought"] += 1
        g.save_game(); show_popup("✅ Готово", f"{t['name']} куплена!"); self.build()

class StatsScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'stats'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("📈 Статистика")
        g = self.app.game; p = g.player; bet = g.betkoin; star = g.starkoin
        nw = p.net_worth(bet, star); start_nw = START_RUB + START_USD * USD_TO_RUB + START_BET * 500 + START_STR * 250
        profit = nw - start_nw
        scroll = ScrollView(); box = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, padding=dp(4))
        box.bind(minimum_height=box.setter('height'))
        def row(label, value, color=None):
            r = BoxLayout(size_hint_y=None, height=dp(30))
            r.add_widget(make_label(label, size=sp(13), color=COLORS["text_dim"]))
            r.add_widget(make_label(value, size=sp(13), bold=True, color=color or COLORS["text"], halign='right'))
            box.add_widget(r)
        box.add_widget(make_label(f"👤 {p.name}", size=sp(15), bold=True))
        box.add_widget(make_label(f"📍 {g.city}  ·  День {g.day}", size=sp(12), color=COLORS["text_dim"]))
        box.add_widget(Widget(size_hint_y=None, height=dp(8)))
        row("₽ Рубли", rub(p.money), COLORS["success"]); row("$ Доллары", usd(p.dollars), COLORS["primary"])
        row("🪙 BET", f"{p.portfolio['BET']:.4f}", COLORS["gold"]); row("⭐ STR", f"{p.portfolio['STR']:.4f}", COLORS["gold"])
        row("🚗 Авто", rub(p.cars_value())); row("🏦 Капитал", rub(nw), COLORS["gold"])
        pc = COLORS["success"] if profit >= 0 else COLORS["danger"]
        row("📊 Прибыль", f"{profit:+,.0f} ₽", pc); row("🏆 Пик", rub(p.stats["peak_net_worth"]), COLORS["gold"])
        box.add_widget(Widget(size_hint_y=None, height=dp(8)))
        row("💸 Заработано", rub(p.stats["rub_earned"]), COLORS["success"]); row("💳 Потрачено", rub(p.stats["rub_spent"]), COLORS["danger"])
        row("🚗 Куплено/Продано", f"{p.stats['cars_bought']} / {p.stats['cars_sold']}")
        row("🔧 Тюнинг", str(p.stats["upgrades_installed"])); row("🔥 JDM Свапы", str(p.stats["jdm_swaps"]))
        row("🤝 Торг", str(p.stats["haggles_success"])); row("🏠 Гаражей", str(p.stats["garages_bought"]))
        scroll.add_widget(box); self.root.add_widget(scroll)

class TravelScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw); self.name = 'travel'; self.build()

    def build(self):
        self.root.clear_widgets(); self.build_header("🚙 Сменить город")
        g = self.app.game; p = g.player
        self.root.add_widget(make_label(f"₽ {rub(p.money)}", size=sp(14), bold=True, color=COLORS["success"], halign='center'))
        scroll = ScrollView(); box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        for name, info in CITIES.items():
            here = name == g.city
            card = make_card(COLORS["card2"] if here else COLORS["card"]); card.size_hint_y = None; card.height = dp(100)
            t = BoxLayout(size_hint_y=None, height=dp(24))
            t.add_widget(make_label(f"{name}", size=sp(15), bold=True))
            if here: t.add_widget(make_label("← здесь", size=sp(11), color=COLORS["success"], halign='right'))
            card.add_widget(t); card.add_widget(make_label(info["desc"], size=sp(11), color=COLORS["text_dim"]))
            fuel = "бесплатно" if info["fuel"] == 0 else rub(info["fuel"])
            card.add_widget(make_label(f"Бензин: {fuel}  ·  Цены ×{info['price_mod']:.1f}", size=sp(11), color=COLORS["text_dim"]))
            if not here: card.add_widget(make_button(f"Ехать ({fuel})", lambda *_, d=name: self.travel(d), height=dp(36), size=sp(13)))
            box.add_widget(card)

        scroll.add_widget(box); self.root.add_widget(scroll)

    def travel(self, dest):
        g = self.app.game; p = g.player; fuel = CITIES[dest]["fuel"]
        if p.money < fuel: return show_popup("Ошибка", f"Нужно {rub(fuel)}")
        def do():
            p.money -= fuel; p.stats["rub_spent"] += fuel
            if p.stats["cities_visited"] < len(CITIES): p.stats["cities_visited"] += 1
            g.city = dest; g.advance_time(90); g.generate_market(); g.save_game()
            show_popup("✅ Прибыли", f"Вы в {dest}!", on_ok=lambda: self.app.goto('menu'))
        confirm_popup("Переезд", f"Переехать в {dest} за {rub(fuel)}?", on_yes=do)

# ============================================================
# APP
# ============================================================

class Game:
    def __init__(self):
        self.betkoin = Crypto("Беткоин", "BET", 500.0, 0.055, 500.0)
        self.starkoin = Crypto("Старкоин", "STR", 250.0, 0.085, 250.0)
        self.player = None; self.available_cars = []; self.day = 1; self.hour = 9; self.minute = 0; self.city = "Москва"
        self.session_start = time.time(); self.session_start_seconds = 0.0

    def advance_time(self, minutes=ACTION_MINUTES):
        total = self.hour * 60 + self.minute + minutes
        days_added = total // (24 * 60); total %= 24 * 60
        self.hour = total // 60; self.minute = total % 60; self.day += days_added

    def generate_market(self):
        city = CITIES[self.city]; self.available_cars = []; pool = []
        for brand, model, price, power, rarity in CAR_DATABASE:
            if city["rarity_min"] <= rarity <= city["rarity_max"]: pool.append((brand, model, price, power, rarity))
        random.shuffle(pool)
        for brand, model, price, power, rarity in pool[:random.randint(8, 12)]:
            self.available_cars.append(Car(brand, model, int(price * city["price_mod"]), power, rarity, random.randint(city["cond_min"], city["cond_max"])))

    def save_game(self):
        try:
            self.update_time()
            with open(SAVE_FILE, "wb") as f:
                pickle.dump({"day": self.day, "hour": self.hour, "minute": self.minute, "city": self.city,
                             "player": self.player, "betkoin": self.betkoin, "starkoin": self.starkoin,
                             "available_cars": self.available_cars, "session_start_seconds": self.player.stats["total_seconds"]}, f)
            return True
        except Exception: return False

    def load_game(self):
        try:
            with open(SAVE_FILE, "rb") as f: data = pickle.load(f)
            self.day = data.get("day", 1); self.hour = data.get("hour", 9); self.minute = data.get("minute", 0); self.city = data.get("city", "Москва")
            self.player = data["player"]; self.betkoin = data["betkoin"]; self.starkoin = data["starkoin"]; self.available_cars = data["available_cars"]
            self.session_start_seconds = data.get("session_start_seconds", 0.0); self.session_start = time.time()
            return True
        except Exception: return False

    def has_save(self): return os.path.exists(SAVE_FILE)
    def update_time(self):
        if self.session_start and self.player:
            elapsed = time.time() - self.session_start; total = self.session_start_seconds + elapsed
            self.player.stats["total_seconds"] = total; total_min = int(total / 60)
            if total_min > self.player.stats["dollars_paid_minutes"]:
                delta = total_min - self.player.stats["dollars_paid_minutes"]
                self.player.dollars += delta * DOLLARS_PER_MINUTE; self.player.stats["usd_earned_time"] += delta * DOLLARS_PER_MINUTE
                self.player.stats["dollars_paid_minutes"] = total_min

class AutoCryptoApp(App):
    current_car = None

    def build(self):
        Window.clearcolor = get_color_from_hex(COLORS["bg"])
        self.title = "AUTO-CRYPTO EMPIRE"
        self.game = Game()
        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))

        if self.game.has_save(): self._ask_load()

        self.sm.add_widget(MenuScreen(self)); self.sm.add_widget(ShopScreen(self)); self.sm.add_widget(GarageScreen(self))
        self.sm.add_widget(CarDetailScreen(self)); self.sm.add_widget(CryptoScreen(self)); self.sm.add_widget(RealEstateScreen(self))
        self.sm.add_widget(StatsScreen(self)); self.sm.add_widget(TravelScreen(self))
        
        Clock.schedule_once(lambda dt: self._start_flow(), 0.1)
        return self.sm

    def _ask_load(self):
        confirm_popup("💾 Сохранение", "Найдено сохранение. Загрузить?", on_yes=lambda: self._do_load(), on_no=lambda: self._do_new())
        self._loaded_choice = None
        while self._loaded_choice is None: pass

    def _do_load(self): self.game.load_game(); self._loaded_choice = True
    def _do_new(self): self._loaded_choice = False; self._start_flow()

    def _start_flow(self):
        if not self.game.player: self._new_game()

    def _new_game(self):
        def get_name(text):
            name = text or "Трейдер"
            def get_code(text2):
                code = text2
                if len(code) < 4: return show_popup("Ошибка", "Код минимум 4 символа") or self._new_game()
                self.game.player = Player(name, code); self.game.session_start = time.time(); self.game.session_start_seconds = 0.0
                self.game.hour = 9; self.game.minute = 0; self.game.generate_market(); self.game.save_game(); self.sm.current = 'menu'
            input_popup("🔐 Код-подпись", "Минимум 4 символа:", get_code)
        input_popup("👤 Имя", "Как тебя зовут, трейдер?", get_name)

    def goto(self, screen_name):
        self.sm.transition = SlideTransition(direction="left"); self.sm.current = screen_name

    def doSave(self):
        if self.game.save_game(): show_popup("✅ Сохранено", "Прогресс сохранён!")
        else: show_popup("Ошибка", "Не удалось сохранить.")

    def doSleep(self):
        g = self.game
        if g.hour < 20: return show_popup("Слишком рано", f"Сейчас {g.hour:02d}:{g.minute:02d}\nСпи после 20:00.")
        def do():
            g.day += 1; g.hour = 9; g.minute = 0; g.player.stats["days_played"] = g.day
            g.betkoin.update_price(); g.starkoin.update_price()
            for car in g.player.cars: car.update_price()
            mined_bet = sum(f.bet_day for f in g.player.mining_farms); mined_str = sum(f.str_day for f in g.player.mining_farms)
            g.player.portfolio["BET"] += mined_bet; g.player.portfolio["STR"] += mined_str
            g.generate_market(); g.save_game()
            msg = f"День {g.day}. Доброе утро!"
            if mined_bet > 0 or mined_str > 0: msg += f"\n\n⛏️ +{mined_bet:.2f} BET, +{mined_str:.2f} STR"
            show_popup("🌅 Новый день", msg, on_ok=lambda: self.goto('menu'))
        confirm_popup("🛏️ Сон", f"Сейчас {g.hour:02d}:{g.minute:02d}. Лечь спать?", on_yes=do)

if __name__ == "__main__":
    AutoCryptoApp().run()