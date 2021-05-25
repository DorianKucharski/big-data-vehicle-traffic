"""
    Widoki stron. Realizują one zaimplementowane zapytania API, poprzez zwracanie odpowiedzi w postaci Json.
    API nie wykorzystuje modułu REST_FRAMEWORK Django, ponieważ API samo w sobie nie odnosi się do danych aplikacji
    webowej, a do danych pozyskanych z bazy MongoDB Cloud, dlatego też importowanie domyślnej postaci API Django nie
    miałoby tu sensu.
"""

from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest
import pymongo
import time
import datetime
import paho.mqtt.client as mqtt

loop = True
timestamp = 0
direction = ""


def get_mongo_collection() -> pymongo.collection:
    """
        Metoda pomocnicza. Nawiązuje połączenie z bazą danych MongoDB i zwraca obiekt kolekcji w której znajdują się
        dane.

        Returns
        ----------
        pymongo.collection
            Obiekt kolekcji
    """
    mongo_url = "mongodb+srv://bigdata:Bigdata2021@cluster0.bbcfv.mongodb.net/" \
                "myFirstDatabase?retryWrites=true&w=majority"
    mongo_client = pymongo.MongoClient(mongo_url)
    db = mongo_client['BigData']
    return db["VehicleTraffic"]


def get_mongo_data() -> list:
    """
        Metoda pomocnicza. Zwraca dane z kolekcji MongoDB w postaci listy list, gdzie każda zagnieżdżona lista
        reprezentuje dane w postaci [TIMESTAMP, LICZBA_SAMOCHODÓW_WJEŻDŻAJĄCYCH, LICZBA_SAMOCHODÓW_WYJEŻDŻAJĄCYCH].
        Dane przefiltorowane są pod kątem czasu, tak by w wynikowych danych nie znalazły się wpisy odnoszące się
        do przyszłości.

        Returns
        ----------
        list
            Lista zawierająca dane
    """
    timestamp = int(time.time())
    collection = get_mongo_collection()
    cursor = collection.find({}, {'_id': False})
    mongo_data = [list(data.values()) for data in list(cursor)]
    mongo_data = [data for data in mongo_data if data[0] < timestamp]
    return mongo_data


def get_by(by_what: str, names: list) -> dict:
    """
        Metoda pomocnicza. Agreguje dane na podstawie parametru "by_what" powiązując wyniki z przekazanymi przez
        "names" nazwami.

        Parameters
        ----------
        by_what: str
            określa na podstawie czego ma zachodzić agregacja, możliwe opcje to "hour", "day_of_week", "day_of_month"
            oraz "month"

        names: str
            określenia przedziałów czasu, czyli godziny, dni tygodnia, dni miesiąca, lub nazwy miesięcy

        Returns
        ----------
        dict
            słownik w formacie obsługiwanym przez bibliotekę ZoomCharts, zawierający zaagregowaną listę z danymi
            w postaci [NAZWA_PRZEDZIAŁU_CZASOWEGO, SAMOCHODY_WJEŻDŻAJĄCE, SAMOCHODY_WYJEŻDŻAJĄCE]
    """
    data = get_mongo_data()
    values = {}
    for x in data:
        date = datetime.datetime.fromtimestamp(x[0])

        if by_what == "hour":
            value = date.hour
        elif by_what == "day_of_week":
            value = date.weekday()
        elif by_what == "day_of_month":
            value = date.day
        else:
            value = date.month

        if value not in values:
            values[value] = [0, 0]
        values[value][0] += x[1]
        values[value][1] += x[2]

    values = [list(value) for value in values.items()]
    content = {"subvalues": [{"name": h[0], "in": h[1][0], "out": h[1][1]} for h in values]}
    for i in range(len(content['subvalues'])):
        content['subvalues'][i]['name'] = names[i]
    return content


def get_raw(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca wszystkie dane z bazy danych w postaci listy zagnieżdżonej w słowniku pod kluczem "data".

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    return JsonResponse({"data": get_mongo_data()})


def get_all(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca wszystkie dane z bazy w formacie przystosowanym dla biblioteki ZoomCharts.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    mongo_data = get_mongo_data()

    content = {"unit": "m", "dataLimitFrom": mongo_data[0][0], "dataLimitTo": mongo_data[-1][0],
               "from": mongo_data[0][0], "to": mongo_data[-1][0],
               "info": ["Date", "Cars in", "Cars out"],
               "values": mongo_data}

    return JsonResponse(content)


def by_hours(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca dane z bazy zaagregowane na podstawie godzin.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    names = [str(i) + ":00" for i in range(24)]
    content = get_by("hour", names)
    return JsonResponse(content)


def by_days_of_week(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca dane z bazy zaagregowane na podstawie dni tygodnia.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    names = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
    content = get_by("day_of_week", names)
    return JsonResponse(content)


def by_days_of_month(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca dane z bazy zaagregowane na podstawie dni miesiąca.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    names = [str(i) for i in range(1, 32)]
    content = get_by("day_of_month", names)
    return JsonResponse(content)


def by_months(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca dane z bazy zaagregowane na podstawie miesięcy.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    names = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień",
             "Październik", "Listopad", "Grudzień"]
    content = get_by("month", names)
    return JsonResponse(content)


def real_time(request: WSGIRequest) -> JsonResponse:
    """
    Zapytanie API. Zwraca dane w czasie rzeczywistym pozyskane z subscribera mqtt.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    JsonResponse
        Odpowiedź w formacie Json
    """
    global loop
    loop = True
    client = mqtt.Client()

    def on_message(_client, _userdata, msg):
        global loop, timestamp, direction
        timestamp, direction = msg.payload.decode("utf-8").split(" ")
        client.loop_stop()
        loop = False

    client.on_message = on_message
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.username_pw_set("bigdata", "Bigdata2021")
    client.connect("cf3d53718bf9452e937c720384e211ae.s1.eu.hivemq.cloud", 8883)
    client.subscribe("bigdata/real_time")

    client.loop_start()

    while loop:
        time.sleep(0.1)

    content = {"timestamp": timestamp, "direction": direction}
    return JsonResponse(content)
