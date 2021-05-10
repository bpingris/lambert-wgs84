import os
import pymongo
import requests
import tempfile
import gzip
import json


def dl_cadastre(client: pymongo.MongoClient):
    print("dropping collection")
    client.lycos.cadastre.drop()
    res = requests.get(
        "https://cadastre.data.gouv.fr/data/etalab-cadastre/2021-02-01/geojson/communes/05/05046/cadastre-05046-parcelles.json.gz"
    )
    if res.status_code != 200:
        return None

    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(res.content)
        with gzip.open(path) as fd:
            data = json.load(fd)
            print("inserting data")
            client.lycos.cadastre.insert_many(
                [
                    {
                        "location": {
                            "type": "Polygon",
                            "coordinates": c["geometry"]["coordinates"],
                        }
                    }
                    for c in data["features"]
                ]
            )
            print("creating index")
            client.lycos.cadastre.create_index([("location", pymongo.GEOSPHERE)])
    finally:
        os.remove(path)


def migrate(client: pymongo.MongoClient):
    dl_cadastre(client)
