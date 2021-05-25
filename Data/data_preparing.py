"""
    Przygotowanie danych pobranych z Kaggle
"""

import random
import pandas


def generate_year(df_tmp: pandas.DataFrame, year: int) -> pandas.DataFrame:
    """
        Generuje dane na zadany rok, posługując się przekazanymi danymi w obiekcie DataFrame. Generowanie obdywa się poprzez
        kopiowanie wpisów z równoległych dat i nakładanie na nich niewielkiego szumu, bazując na odchyleniu standardowym.

        Parameters
        ----------
        df_tmp: pandas.DataFrame
            Dane z wybranego roku

        year: int
            Rok który ma być wygenerowany

        Returns
        ----------
        pandas.DataFrame
            Wygenerowane dane
    """
    new_df = df_tmp.copy()
    new_df = new_df[new_df["Year"] == 2020]
    new_df["Year"].replace([2020], year, inplace=True)
    sd = int(new_df["Volume"].std())
    new_df["Volume"] = new_df["Volume"].apply(lambda x: x + int((random.randint(0, sd) * random.randint(0, 100)) / 100))
    return new_df


if __name__ == '__main__':
    # Wczytywanie danych z pliku csv do obiektu DataFrame
    df = pandas.read_csv("Radar_Traffic_Counts.csv")

    # Filtrowanie danych na podstawie lokalizacji w kolumnie location_name
    df = df[df['location_name'] == " CAPITAL OF TEXAS HWY / WALSH TARLTON LN"]

    # Usuwanie zbednych kolumn
    df.drop('location_name', axis=1, inplace=True)
    df.drop('location_latitude', axis=1, inplace=True)
    df.drop('location_longitude', axis=1, inplace=True)
    df.drop('Day of Week', axis=1, inplace=True)
    df.drop('Time Bin', axis=1, inplace=True)

    # Filtrowanie danych starszych niz te z 2018. Starsze dane byly niekompletne.
    df = df[df["Year"] >= 2018]

    # Usuwanie duplikatow bazujac na kolumnach okreslajacych czas
    df = df.drop_duplicates(subset=['Year', 'Month', 'Day', 'Hour', 'Minute', 'Direction'], keep='first')

    # Zmiana wartosci w kolumnie direction
    df["Direction"].replace({"NB": "IN", "SB": "OUT"}, inplace=True)

    # Zmiana lat na bardziej terazniejsze
    df["Year"].replace([2019], 2021, inplace=True)
    df["Year"].replace([2018], 2020, inplace=True)

    # Generowanie i laczenie danych
    df2 = generate_year(df, 2019)
    df = pandas.concat([df, df2])

    # Utworzenie kolumny datatime na podstawie innych kolumn okreslajacych czas
    df['Datetime'] = pandas.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])

    # Usuwanie niepotrzebnych kolumn
    df = df[['Datetime', 'Direction', 'Volume']]

    # Sortowanie
    df = df.sort_values(by=['Datetime'])

    # Konwersja danych w kolumnie Datetime na timestamp
    df['Datetime'] = df['Datetime'].astype('int64') // 10 ** 9

    # Zapis danych do pliku
    df.to_csv("prepared_data.csv", index=False)
