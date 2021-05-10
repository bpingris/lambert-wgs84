import pymongo
import migrate
import geometry
import time


def main():
    client = pymongo.MongoClient(
        host="localhost", port=27017, username="lycos", password="lycos"
    )

    s1 = time.perf_counter()

    p = geometry.Polygon.from_angular(
        [
            (2.9498291015625, 46.68901548485151),
            (3.00201416015625, 46.62869257083747),
            (3.11187744140625, 46.6701718034738),
            (2.9498291015625, 46.68901548485151),
        ]
    )

    point = geometry.Point.from_angular((3.03148090839386, 46.63538575294019))

    poin2 = geometry.Point.from_angular((3.032446503639221, 46.635864594998814))
    points = p.nearest_points(point) 
    geometry.geojson(*points)

    s2 = time.perf_counter()
    print(s2 - s1)

    # migrate.migrate(client)


if __name__ == "__main__":
    main()
