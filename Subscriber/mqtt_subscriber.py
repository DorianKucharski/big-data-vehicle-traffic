"""
    Zbieranie informacji o przejeżdżających pojazdach, sumowanie ich i wysyłanie do bazy danych.
"""

import paho.mqtt.client as mqtt
import sched
import time
import datetime
import threading
import pymongo


def calculate_first_delay():
    """
        Oblicza czas w sekundach pozostały do kolejnego kwadransu.
    """
    timestamp = int(time.time())
    d = datetime.datetime.fromtimestamp(timestamp)
    how_many_quarters = d.minute // 15 + 1
    delay_minutes = (how_many_quarters * 15) - d.minute
    d = datetime.datetime.fromtimestamp(timestamp + delay_minutes * 60).replace(second=0)
    return int(d.timestamp() - timestamp)


def on_connect(_client, _userdata, _flags, rc):
    """
        Callback ustanowienia połączenia z brokerem MQTT
    """
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))


def on_message(_client, _userdata, msg):
    """
        Callback otrzymania wiadomości od brokera MQTT. Zlicza samochody poruszające się w danym kierunku.
    """
    global cars_in
    global cars_out

    print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))

    if msg.payload.decode("utf-8") == "in":
        cars_in += 1
    else:
        cars_out += 1


if __name__ == '__main__':
    # URL bazy danych MongoDB
    mongo_url = "mongodb+srv://bigdata:Bigdata2021@cluster0.bbcfv.mongodb.net/" \
                "myFirstDatabase?retryWrites=true&w=majority"

    # Utworzenie obiektu klienta MQTT i jego callbacków
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Zerowanie liczby pojazdów
    cars_in = 0
    cars_out = 0

    # Ustanowienie połączenia z brokerem MQTT
    mqtt_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    mqtt_client.username_pw_set("bigdata", "Bigdata2021")
    mqtt_client.connect("cf3d53718bf9452e937c720384e211ae.s1.eu.hivemq.cloud", 8883)
    mqtt_client.subscribe("bigdata/vehicle_traffic")


    def update_thread():
        """
            Funkcja wątku aktualizacji bazy danych
        """

        # Utworzenie obiektu schedulera z modułu sched
        scheduler = sched.scheduler(time.time, time.sleep)

        def update():
            """
                Funkcja wysyłająca dane do bazy danych. Za pomocą obiektu scheduler uruchammiana zostaje co piętnaście
                minut począwszy od pierwszego pełnego kwadransu. Z każdym takim okresem wysyła aktualnie zebrane dane,
                następnie je zerując.
            """
            global cars_in
            global cars_out

            # Timestamp kwadransu
            t = datetime.datetime.fromtimestamp(time.time()).replace(second=0, minute=0, microsecond=0).timestamp()

            # Połączenie z bazą danych
            mongo_client = pymongo.MongoClient(mongo_url)
            db = mongo_client['BigData']
            collection = db["VehicleTraffic"]

            # Utworzenie obiektu danych
            data = [{"timestamp": t, "direction": "in", "volume": cars_in},
                    {"timestamp": t, "direction": "out", "volume": cars_out}]

            print(t, cars_in, cars_out)

            # Wysłanie danych do bazy
            collection.insert_many(data)

            # Zerowanie ilości pojazdów i zlecenie wykonania funkcji
            cars_in = 0
            cars_out = 0
            scheduler.enter(15 * 60, 1, update)

        # Pierwsze wywołanie funkcji aktualizacji
        scheduler.enter(calculate_first_delay(), 1, update)
        scheduler.run()

    # Uruchomienie wątku aktualizacji
    thread = threading.Thread(target=update_thread)
    thread.start()

    # Pętla klienta MQTT
    mqtt_client.loop_forever()
