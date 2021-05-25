"""
    Publisher MQTT
"""

import paho.mqtt.client as mqtt
import time
from Publisher.VehicleCounter import VehicleCounter

client = mqtt.Client()


def on_connect(_client, _userdata, _flags, rc):
    """
        Callback MQTT wywolywany po ustanowieniu polaczenia z brokerem.
    """
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))


def on_detect(direction):
    """
        Callback obiektu detekcji pojazdow, wykonywany po wykryciu przejeżdżającego samochodu.
        Publikuje na dwóch kanałach MQTT informacje o timestampie i kierunku pojazdu.
        Jeden kanał obsługiwany jest przez subskrybenta MQTT zliczającego zdarzenia i wysyłającego dane do MongoDB,
        drugi do wyświetlania danych w czasie rzeczywistym w aplikacji mobilnej.
    """
    timestamp = int(time.time())
    client.publish("bigdata/vehicle_traffic", direction)
    client.publish("bigdata/real_time", str(timestamp) + " " + direction, retain=True)
    print(timestamp, direction)


if __name__ == '__main__':
    # Ustawienie callbacku nawiązania połączenia
    client.on_connect = on_connect

    # Łączenie z brokerem MQTT
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.username_pw_set("bigdata", "Bigdata2021")
    client.connect("cf3d53718bf9452e937c720384e211ae.s1.eu.hivemq.cloud", 8883)

    # Utworzenie obiektu detekcji pojazdów
    v = VehicleCounter(preview=False)

    # Ustawienie callbacka wykonywanego po detekcji pojazdu
    v.on_detect = on_detect

    # Uruchomienie detekcji
    v.start()
