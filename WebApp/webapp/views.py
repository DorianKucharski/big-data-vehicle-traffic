"""
    Widoki stron. Metody zwracają odpowiednie do url szablony stron.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest


def index(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok głównej strony aplikacji.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "home.html", {})

def docs_home(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok strony głównej dokumentacji.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    return render(request, "docs.html", {})


def docs(request: WSGIRequest) -> HttpResponse:
    """
    Zwraca widok wybranej strony dokumentacji.

    Parameters
    ----------
    request: WSGIRequest
        Zapytanie

    Returns
    ----------
    HttpResponse
        Odpowiedź
    """
    template = request.path[1:]
    return render(request, template, {})



