# ⚡ Szybki Start - Dodawanie Zakładek (Pełna Modularyzacja)

## 🌐 Źródło danych: Google Sheets (skrót)

1. **Arkusz** – przygotuj Google Sheet z kolumnami `Data`, `Godzina`, `SYS`, `DIA`, `PUL`.
2. **Konto serwisowe** – w Google Cloud Console utwórz Service Account, nadaj mu rolę „Editor” i wygeneruj klucz JSON (`google_credentials.json`).
3. **Udostępnienie** – przekaż arkuszowi uprawnienia edycji dla adresu e-mail konta serwisowego.
4. **Konfiguracja** – ustaw `GOOGLE_SHEET_URL`, `WORKSHEET_NAME`, `DATA_CACHE_FILE`, `DATA_CACHE_TTL_MINUTES` w `config.py`.
5. **Odświeżanie** – korzystaj z przycisków „🔄 Odśwież dane” (z cache) oraz „⏭️ Odśwież bez cache” (wymusza pobranie i ignoruje TTL).

> 💡 Limit API Google Sheets to ~60 zapytań/min. Cache + przycisk „⏭️” pomagają kontrolować ruch.

## 📋 Checklista (6 kroków)

### ☑️ 1. Utwórz plik wykresu
```
charts/nazwa_wykresu.py
```

### ☑️ 2. Napisz funkcję generującą wykres
```python
def generate_nazwa_wykresu_chart(df):
    if df.empty:
        return utworz_pusty_wykres()
    # ... logika wykresu ...
    return fig
```

### ☑️ 3. Dodaj import w `charts/__init__.py`
```python
from charts.nazwa_wykresu import generate_nazwa_wykresu_chart

__all__ = [
    # ...
    'generate_nazwa_wykresu_chart'
]
```

### ☑️ 4. Wygeneruj wykres początkowy w `app.py`
```python
from charts import (..., generate_nazwa_wykresu_chart)

initial_figures = {
    # ...
    'nazwa': generate_nazwa_wykresu_chart(initial_df)
}
```

### ☑️ 5. Dodaj zakładkę w `layouts/tabs.py`

Utwórz funkcję:
```python
def create_nazwa_tab(initial_fig):
    return dcc.Tab(label=' Nazwa', children=[
        dcc.Graph(id='graph-nazwa', figure=initial_fig)
    ])
```

Dodaj w `create_app_layout()`:
```python
dcc.Tabs(children=[
    # ...
    create_nazwa_tab(initial_figures['nazwa'])
])
```

### ☑️ 6. Dodaj callback w `callbacks/callbacks.py`

Wewnątrz funkcji `register_callbacks()`:
```python
@callback(Output('graph-nazwa', 'figure'), Input('data-store', 'data'))
def update_nazwa(stored_data):
    if stored_data is None: return {}
    df = pd.read_json(StringIO(stored_data), orient='split')
    return generate_nazwa_wykresu_chart(df)
```

---

## 🎯 Szablon Funkcji Wykresu

```python
"""
Opis wykresu
"""

import plotly.graph_objects as go  # lub plotly.express as px
from charts.utils import utworz_pusty_wykres
from config import TEMPLATE_PLOTLY, WYSOKOSC_WYKRESU_STANDARD


def generate_twoj_wykres(df, parametr=None):
    """
    Krótki opis funkcji.
    
    Args:
        df: DataFrame z pomiarami
        parametr: Opcjonalny parametr
    
    Returns:
        go.Figure: Wykres Plotly
    """
    if df.empty:
        return utworz_pusty_wykres()
    
    try:
        # TU TWOJA LOGIKA
        fig = go.Figure()
        
        # Dodaj dane do wykresu
        fig.add_trace(...)
        
        # Konfiguracja layoutu
        fig.update_layout(
            title="Tytuł Wykresu",
            xaxis_title="Oś X",
            yaxis_title="Oś Y",
            template=TEMPLATE_PLOTLY,
            height=WYSOKOSC_WYKRESU_STANDARD
        )
        
        return fig
    
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
```

---

## 🔍 Najczęstsze Operacje na DataFrame

```python
# Średnia dla każdej godziny
hourly = df.groupby('Hour')['SYS'].mean()

# Grupowanie po dniu tygodnia
weekly = df.groupby(df['Datetime'].dt.day_name())

# Filtrowanie
df_filtered = df[df['SYS'] > 140]

# Dodanie nowej kolumny
df['Nowa'] = df['SYS'] - df['DIA']

# Pivoting dla heatmapy
pivot = df.pivot_table(index='Dzień', columns='Hour', values='SYS')
```

---

## 🎨 Dostępne Stałe z `config.py`

```python
# Kolory
KOLORY_ESC['Optymalne']          # '#2ca02c'
KOLORY_PARAMETROW['SYS']         # 'red'

# Progi
PROGI_ESC['optymalne']['sys']    # 120
PROGI_ESC['wysokie_prawidlowe']['dia']  # 90

# Ustawienia wykresów
TEMPLATE_PLOTLY                   # "plotly_white"
WYSOKOSC_WYKRESU_STANDARD        # 600
WYSOKOSC_WYKRESU_DUZY            # 700
```

---

## 📊 Przykłady Typów Wykresów

### Wykres liniowy
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Datetime'], y=df['SYS'], mode='lines'))
```

### Wykres słupkowy
```python
fig = px.bar(df, x='Kategoria', y='Liczba')
```

### Boxplot
```python
fig = px.box(df, x='Godzina Pomiaru', y='SYS')
```

### Heatmapa
```python
fig = px.imshow(pivot_table, color_continuous_scale='RdYlBu_r')
```

### Wykres kołowy
```python
fig = px.pie(df, names='Kategoria', values='Liczba')
```

---

## ⚠️ Częste Błędy

### 🚨 Typowe problemy przy integracji z Google Sheets

| Komunikat | Przyczyna | Jak naprawić |
| --- | --- | --- |
| ❌ Błąd: Nie znaleziono arkusza Google | Zły URL lub konto serwisowe nie ma dostępu | Zweryfikuj `GOOGLE_SHEET_URL`, udostępnij arkusz kontu serwisowemu |
| ❌ Brakujące kolumny: ... | Arkusz nie zawiera jednej z wymaganych kolumn | Uzupełnij nagłówki `Data`, `Godzina`, `SYS`, `DIA`, `PUL` |
| ⚠️ ... Pokazuję dane z cache sprzed ... | Zapytanie do API nie powiodło się, ale istnieje cache | Sprawdź logi (quota, sieć), ewentualnie wymuś odświeżenie („⏭️”) |
| json.decoder.JSONDecodeError | Uszkodzony plik `google_credentials.json` | Wygeneruj klucz ponownie i skopiuj cały plik |

### ❌ **Zapomnienie o imporcie w `__init__.py`**
```python
# Pamiętaj dodać do charts/__init__.py!
```

❌ **Brak obsługi pustego DataFrame**
```python
if df.empty:
    return utworz_pusty_wykres()  # ← ZAWSZE!
```

❌ **Zapomnienie o try-except**
```python
try:
    # logika
except Exception as e:
    return utworz_pusty_wykres(f"Błąd: {e}")  # ← ZAWSZE!
```

❌ **Niepoprawny ID w callback**
```python
# ID musi się zgadzać z layoutem!
Output('graph-nazwa', 'figure')  # ← Musi być 'graph-nazwa' w dcc.Graph
```

❌ **Brak początkowego wykresu**
```python
# Musisz wygenerować initial_fig_nazwa PRZED layoutem!
```

---

## 🚀 Mini-Przykład (Kompletny)

**1. Utwórz `charts/simple.py`:**
```python
from charts.utils import utworz_pusty_wykres
import plotly.graph_objects as go

def generate_simple_chart(df):
    if df.empty:
        return utworz_pusty_wykres()
    try:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['SYS', 'DIA'], y=[df['SYS'].mean(), df['DIA'].mean()]))
        fig.update_layout(title="Średnie")
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
```

**2. W `charts/__init__.py`:**
```python
from charts.simple import generate_simple_chart
__all__ = [..., 'generate_simple_chart']
```

**3. W `app.py` - import:**
```python
from charts import (..., generate_simple_chart)
```

**4. W `app.py` - początkowy wykres:**
```python
initial_fig_simple = generate_simple_chart(initial_df)
```

**5. W `app.py` - zakładka:**
```python
dcc.Tab(label='Test', children=[
    dcc.Graph(id='graph-simple', figure=initial_fig_simple)
])
```

**6. W `app.py` - callback:**
```python
@callback(Output('graph-simple', 'figure'), Input('data-store', 'data'))
def update_simple(stored_data):
    if stored_data is None: return {}
    df = pd.read_json(StringIO(stored_data), orient='split')
    return generate_simple_chart(df)
```

**✅ Gotowe w 6 krokach!**

---

## 📚 Pomocne Linki

- **Plotly Docs**: https://plotly.com/python/
- **Dash Docs**: https://dash.plotly.com/
- **Pandas Docs**: https://pandas.pydata.org/docs/

---

## 💡 Pro Tips

1. **Testuj z małym DataFrame** - łatwiej debugować
2. **Używaj `print(df.head())`** podczas developmentu
3. **Kopiuj istniejącą funkcję** jako szablon
4. **Sprawdź `charts/trend.py`** jako referencję
5. **Używaj autocomplete** - importuj wszystko na początku

---

## 🎓 Ćwiczenie

**Spróbuj dodać zakładkę "Średnie Dzienne":**

```python
# charts/daily_avg.py
def generate_daily_avg_chart(df):
    if df.empty:
        return utworz_pusty_wykres()
    try:
        daily = df.groupby('Dzień').agg({'SYS': 'mean', 'DIA': 'mean'})
        fig = px.line(daily, y=['SYS', 'DIA'])
        fig.update_layout(title="Średnie dzienne")
        return fig
    except Exception as e:
        return utworz_pusty_wykres(f"Błąd: {e}")
```

**Następnie przejdź przez 7 kroków z checklisty!**

---

## ⏱️ Czas: ~5 minut na zakładkę

Po przećwiczeniu kilku razy, dodawanie nowej zakładki zajmie tylko **5 minut**!

---

**Powodzenia! 🚀**