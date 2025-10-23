# 💓 Dashboard Pomiarów Ciśnienia Krwi

Dashboard do analizy pomiarów ciśnienia krwi zgodny z wytycznymi ESC/ESH (Europejskie Towarzystwo Kardiologiczne).

## 📁 Struktura Projektu (Pełna Modularyzacja)

```
blood_pressure_dashboard/
├── app.py                      # Główny plik uruchamiający (~80 linii!)
├── config.py                   # Konfiguracja i stałe
├── data_processing.py          # Wczytywanie i przetwarzanie danych
├── README.md                   # Ten plik
│
├── charts/                     # 📊 Moduł wykresów
│   ├── __init__.py            # Import wszystkich wykresów
│   ├── utils.py               # Narzędzia wspólne
│   ├── trend.py               # Wykres trendu w czasie
│   ├── circadian.py           # Rytm dobowy
│   ├── correlation.py         # Korelacje SYS-DIA-PUL
│   ├── heatmap.py             # Heatmapa
│   ├── histogram.py           # Histogramy rozkładu
│   ├── classification.py      # Macierz i klasyfikacja ESC
│   ├── comparison.py          # Porównania (box/violin)
│   └── summary.py             # Podsumowanie i KPI
│
├── layouts/                    # 🎨 Moduł layoutów
│   ├── __init__.py
│   └── tabs.py                # Definicje wszystkich zakładek
│
└── callbacks/                  # 🔄 Moduł callbacków
    ├── __init__.py
    └── callbacks.py           # Wszystkie callbacki
```

## 🚀 Uruchomienie

1. **Zainstaluj wymagane biblioteki:**
```bash
pip install dash pandas plotly openpyxl
```

2. **Przygotuj plik Excel:**
   - Nazwa: `Pomiary_SYS_DIA.xlsx`
   - Kolumny wymagane: `Data`, `Godzina`, `SYS`, `DIA`, `PUL`

3. **Uruchom aplikację:**
```bash
python app.py
```

4. **Otwórz przeglądarkę:**
   - Adres: http://127.0.0.1:8050

## ✨ Jak Dodać Nową Zakładkę (Krok po kroku)

### Przykład: Dodanie zakładki "Analiza Tygodniowa"

#### **Krok 1: Utwórz plik z wykresem**

Utwórz `charts/weekly_analysis.py`:

```python
"""
Wykres analizy tygodniowej
"""

import plotly.graph_objects as go
from charts.utils import utworz_pusty_wykres
from config import TEMPLATE_PLOTLY

def generate_weekly_analysis_chart(df):
    """Generuje wykres analizy tygodniowej."""
    if df.empty:
        return utworz_pusty_wykres()
    
    try:
        # Dodaj dzień tygodnia
        df['Dzień Tygodnia'] = df['Datetime'].dt.day_name()
        
        # Grupowanie po dniu tygodnia
        weekly = df.groupby('Dzień Tygodnia').agg({
            'SYS': 'mean',
            'DIA': 'mean'
        }).reset_index()
        
        # Tworzenie wykresu
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekly['Dzień Tygodnia'],
            y=weekly['SYS'],
            name='SYS'
        ))
        fig.add_trace(go.Bar(
            x=weekly['Dzień Tygodnia'],
            y=weekly['DIA'],
            name='DIA'
        ))
        
        fig.update_layout(
            title="Średnie Ciśnienie wg Dnia Tygodnia",
            template=TEMPLATE_PLOTLY,
            barmode='group'
        )
        
        return fig
    
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
```

#### **Krok 2: Dodaj import w `charts/__init__.py`**

```python
from charts.weekly_analysis import generate_weekly_analysis_chart

__all__ = [
    # ... pozostałe importy ...
    'generate_weekly_analysis_chart'  # NOWY
]
```

#### **Krok 3: Wygeneruj wykres początkowy w `app.py`**

```python
# W sekcji "INICJALIZACJA DANYCH I WYKRESÓW POCZĄTKOWYCH"
from charts import (
    # ... pozostałe importy ...
    generate_weekly_analysis_chart  # NOWY
)

# W słowniku initial_figures
initial_figures = {
    # ... pozostałe wykresy ...
    'weekly': generate_weekly_analysis_chart(initial_df)  # NOWY
}
```

#### **Krok 4: Dodaj zakładkę w `layouts/tabs.py`**

Dodaj funkcję:
```python
def create_weekly_tab(initial_fig_weekly):
    """Tworzy zakładkę analizy tygodniowej."""
    return dcc.Tab(label='📅 Analiza Tygodniowa', children=[
        dcc.Graph(id='graph-weekly', figure=initial_fig_weekly)
    ])
```

Dodaj wywołanie w `create_app_layout()`:
```python
dcc.Tabs(id="tabs-container", children=[
    # ... pozostałe zakładki ...
    create_weekly_tab(initial_figures['weekly'])  # NOWY
])
```

#### **Krok 5: Dodaj callback w `callbacks/callbacks.py`**

```python
@callback(Output('graph-weekly', 'figure'), Input('data-store', 'data'))
def update_weekly(stored_data):
    """Aktualizuje wykres analizy tygodniowej."""
    if stored_data is None:
        return {}
    df = pd.read_json(StringIO(stored_data), orient='split')
    return generate_weekly_analysis_chart(df)
```

#### **Krok 6: (Opcjonalnie) Dodaj do eksportu HTML**

W `callbacks/callbacks.py`, w funkcji `export_html`, w słowniku `wykresy`:
```python
wykresy = {
    # ... pozostałe wykresy ...
    'Analiza_Tygodniowa': generate_weekly_analysis_chart(df),  # NOWY
}
```

### ✅ Gotowe!

Teraz masz nową zakładkę "📅 Analiza Tygodniowa" w dashboardzie!

## 📊 Istniejące Zakładki

1. **📊 Podsumowanie** - KPI i wykres kołowy klasyfikacji
2. **🏥 Klasyfikacja ESC** - Kategorie ESC/ESH + wykres słupkowy
3. **🗺️ Macierz** - Macierz klasyfikacji pomiarów
4. **📈 Trend** - Trend ciśnienia w czasie
5. **🕒 Rytm dobowy** - Średnie ciśnienie wg godziny
6. **❤️ Korelacje** - Zależność SYS-DIA-PUL
7. **🌡️ Heatmapa** - Mapa cieplna SYS (dzień x godzina)
8. **⚖️ Porównanie** - Box/violin plot (godziny lub dzień roboczy/weekend)
9. **📊 Rozkład** - Histogramy SYS/DIA/PUL

## 🎨 Kategorie Ciśnienia (Aktualne Wytyczne)

| Kategoria | SYS (mmHg) | DIA (mmHg) | Kolor |
|-----------|------------|------------|-------|
| Optymalne | < 120 | < 70 | 🟢 Zielony |
| Prawidłowe | 120-129 | 70-79 | 🟢 Jasnozielony |
| Podwyższone | 130-139 | 80-89 | 🟡 Złoty |
| Nadciśnienie 1° | 140-159 | 90-99 | 🟠 Pomarańczowy |
| Nadciśnienie 2° | 160-179 | 100-109 | 🔴 Pomidorowy |
| Nadciśnienie 3° | ≥ 180 | ≥ 110 | 🔴 Ciemnoczerwony |
| Izolowane nadciśnienie skurczowe | ≥ 140 | < 90 | 🟣 Fioletowy |

**⚕️ Zasada kliniczna:** Przy niejednoznacznych parach (SYS w jednej kategorii, DIA w innej, zwłaszcza niższej) klasyfikacja następuje do **wyższej kategorii**.

## 🔧 Konfiguracja

Wszystkie ustawienia w pliku `config.py`:

```python
# Nazwa pliku z danymi
NAZWA_PLIKU_EXCEL = "Pomiary_SYS_DIA.xlsx"

# Standardowe godziny pomiarów
STANDARDOWE_GODZINY = [10, 13, 16, 19, 22]

# Progi ESC
PROGI_ESC = {
    'niskie': {'sys': 100, 'dia': 60},
    'optymalne': {'sys': 120, 'dia': 80},
    # ...
}

# Kolory kategorii
KOLORY_ESC = {
    'Optymalne': '#2ca02c',
    # ...
}
```

## 🛠️ Zalety Pełnej Struktury Modularnej

✅ **`app.py` ma tylko ~80 linii** - ultraczytelny!  
✅ **Łatwość dodawania zakładek** - 6 prostych kroków (~5 minut)  
✅ **Separacja odpowiedzialności** - data/charts/layout/callbacks oddzielnie  
✅ **Reużywalność** - funkcje można wykorzystać w innych projektach  
✅ **Czytelność** - łatwo znaleźć i poprawić kod  
✅ **Skalowalność** - możesz dodać 50+ zakładek bez bałaganu  
✅ **Testowanie** - każdy moduł można testować osobno  
✅ **Współpraca** - zespół może pracować równolegle nad różnymi modułami  

## 📝 Najważniejsze Pliki

- **`app.py`** - uruchamiasz ten plik (tylko inicjalizacja!)
- **`config.py`** - tu zmieniasz progi i kolory
- **`charts/*.py`** - tu dodajesz nowe wykresy
- **`layouts/tabs.py`** - tu dodajesz nowe zakładki
- **`callbacks/callbacks.py`** - tu dodajesz callbacki

## 💡 Wskazówki

1. **Nowy wykres?** → Utwórz `charts/nazwa.py`
2. **Zmiana progów?** → Edytuj `config.py`
3. **Nowe dane?** → Zmień `NAZWA_PLIKU_EXCEL` w `config.py`
4. **Problem?** → Każdy moduł ma własną obsługę błędów

## 📄 Licencja

Ten projekt jest dostępny na licencji MIT.

---

**Autor:** System modularny dla łatwego rozwoju  
**Wersja:** 2.0 (Modularna)  
**Data:** 2025