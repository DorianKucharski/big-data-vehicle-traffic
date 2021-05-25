"""
    Upload danych z pliku do bazy danych
"""

import pandas
import pymongo


if __name__ == '__main__':
    # Wczytywanie danych z pliku
    df = pandas.read_csv("prepared_data.csv")

    # Konwersja obiektu DataFrame do listy
    data = df.to_dict("records")

    # Sumowanie liczby przejeżdżających samochodów w danym czasie
    try:
        for i in range(0, len(data), 1):
            if data[i]["Direction"] == "OUT":
                data[i]["Out"] = data[i]["Volume"]
                data[i]["In"] = data[i + 1]["Volume"]
            else:
                data[i]["In"] = data[i]["Volume"]
                data[i]["Out"] = data[i + 1]["Volume"]

            del data[i]["Direction"]
            del data[i]["Volume"]
            del data[i + 1]

    except IndexError:
        pass

    # Adres URL bazy danych MongoDB
    mongo_url = "mongodb+srv://bigdata:Bigdata2021@cluster0.bbcfv.mongodb.net/" \
                "myFirstDatabase?retryWrites=true&w=majority"


    # Ustanowienie połączenia, wybranie bazy danych i kolekcji
    mongo_client = pymongo.MongoClient(mongo_url)
    db = mongo_client['BigData']
    collection = db["VehicleTraffic"]

    # Wczytywanie danych do bazy danych
    collection.insert_many(data)
