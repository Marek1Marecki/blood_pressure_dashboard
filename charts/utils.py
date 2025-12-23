"""Moduł zawierający funkcje pomocnicze dla modułów wykresów.

Ten plik gromadzi wspólne narzędzia i funkcje, które są wykorzystywane
przez różne moduły generujące wykresy w aplikacji. Celem jest unikanie
powielania kodu i centralizacja standardowych operacji.
"""

import plotly.graph_objects as go
from config import TEMPLATE_PLOTLY


def utworz_pusty_wykres(tytul="Brak danych do wyświetlenia"):
    """Tworzy pusty obiekt wykresu Plotly z wyśrodkowanym komunikatem.

    Ta funkcja jest używana w całej aplikacji do generowania standardowego,
    pustego wykresu w sytuacjach, gdy brakuje danych do wizualizacji lub
    wystąpił błąd. Zapobiega to awariom aplikacji i informuje użytkownika
    o problemie w spójny sposób.

    Args:
        tytul (str, optional): Tekst, który ma zostać wyświetlony na
            środku pustego wykresu. Domyślnie "Brak danych do wyświetlenia".

    Returns:
        go.Figure: Pusty obiekt `plotly.graph_objects.Figure` z ukrytymi
            osiami i widocznym tytułem.
    """
    return go.Figure().update_layout(
        title=tytul,
        xaxis={'visible': False},
        yaxis={'visible': False},
        template=TEMPLATE_PLOTLY
    )


def validate_dataframe(df, required_columns):
    """Weryfikuje, czy ramka danych zawiera wymagane kolumny.

    Args:
        df (pd.DataFrame): Ramka danych przekazywana do generatora wykresu.
        required_columns (list[str]): Lista kolumn niezbędnych do poprawnej wizualizacji.

    Returns:
        tuple[bool, str]:
            - bool: True, jeśli ramka jest niepusta i zawiera wszystkie wymagane kolumny.
            - str: Komunikat do przekazania na pustym wykresie w razie błędu.
    """
    if df is None or df.empty:
        return False, "Brak danych wejściowych do wizualizacji"

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        pretty = ', '.join(missing)
        return False, f"Brakujące kolumny: {pretty}"

    return True, ""


def export_to_pdf(wykresy, output_path="dashboard.pdf", width=1200, height=800):
    """Zapisuje kolekcję wykresów Plotly do jednego pliku PDF.

    Wymaga zainstalowanych pakietów `kaleido` (rendering PNG) oraz `Pillow`.

    Args:
        wykresy (Mapping[str, go.Figure]): Słownik identyfikatorów -> figur.
        output_path (str): Ścieżka docelowego pliku PDF.
        width (int): Szerokość renderowanej grafiki w pikselach.
        height (int): Wysokość renderowanej grafiki w pikselach.
    """
    if not wykresy:
        return None

    import io
    from PIL import Image

    images = []
    for fig in wykresy.values():
        if fig is None:
            continue
        img_bytes = fig.to_image(format="png", width=width, height=height)
        images.append(Image.open(io.BytesIO(img_bytes)))

    if not images:
        return None

    images[0].save(output_path, save_all=True, append_images=images[1:])
    return output_path