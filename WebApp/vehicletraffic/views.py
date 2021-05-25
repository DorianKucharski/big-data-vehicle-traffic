"""
    Widoki stron. Metody zwracają odpowiednie do url szablony stron.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
import requests
import datetime
import time


# Create your views here.

def index(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok głównej strony kokpitu aplikacji. Pozyskuje dane poprzez odwołanie do API, na podstawie których
    oblicza statystyki.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    domain = request.build_absolute_uri('/')
    r = requests.get(domain + "api/get_raw").json()["data"]
    timestamp = datetime.datetime.fromtimestamp(int(time.time())).replace(hour=0, minute=0, second=0).timestamp()
    measurements = 0
    today_cars_in = 0
    today_cars_out = 0

    for e in r:
        measurements += e[1] + e[2]
        if e[0] > timestamp:
            today_cars_in += e[1]
            today_cars_out += e[2]

    data = {"measurements": measurements, "entries": len(r), "today_cars_in": today_cars_in,
            "today_cars_out": today_cars_out, "15_minutes_cars_in": r[-1][1], "15_minutes_cars_out": r[-1][2]}

    return render(request, "vehicle_traffic_home.html", data)


def line_chart(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu liniowego.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_line_chart.html", {})


def cars_in(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu blokowego samochodów przyjeżdżających.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_cars_in.html", {})


def cars_out(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu blokowego samochodów wyjeżdżających.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_cars_out.html", {})


def cars_all(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu blokowego wszystkich samochodów.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_cars_all.html", {})


def by_hours(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu ruchu zagregowanego na podstawie dni godzin.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_by_hours.html", {})


def by_days_of_week(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu ruchu zagregowanego na podstawie dni tygodnia.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_by_days_of_week.html", {})


def by_days_of_month(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu ruchu zagregowanego na podstawie dni miesiąca.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_by_days_of_month.html", {})


def by_months(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wykresu ruchu zagregowanego na podstawie miesięcy.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_by_months.html", {})


def real_time(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok podglądu czasu rzeczywistego danych ze skryptu detekcji pojazdów.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_real_time.html", {})


def camera(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok obrazu z kamery.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "vehicle_traffic_camera.html", {})
