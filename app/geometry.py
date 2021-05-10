from typing import Any, Union, cast
from shapely.coords import CoordinateSequence
from shapely.ops import nearest_points
import shapely.geometry as geom
import geopandas
from pyproj import Transformer

LAMBERT = "epsg:2154"
WGS84 = "epsg:4326"

LAMBERT_TO_WGS84 = Transformer.from_crs(LAMBERT, WGS84)
WGS84_TO_LAMBERT = Transformer.from_crs(WGS84, LAMBERT)


def geojson(*forms: Union["Polygon", "Point", "LineString"]):
    """
    Pretty print geometry classes to a geojson compatible format
    """
    print(geopandas.GeoSeries([form.ftype(form.lonlat) for form in forms]).to_json())


def xy_to_lonlat(x: float, y: float) -> tuple[float, float]:
    """
    Transform Lambert93 coordinates to WGS84 (lon, lat) coordinates
    """
    return LAMBERT_TO_WGS84.transform(x, y)[::-1]


def lonlat_to_xy(lon: float, lat: float) -> tuple[float, float]:
    """
    Transform WGS84 (lon, lat) coordinates to Lambert93 coordinates
    """
    return WGS84_TO_LAMBERT.transform(lat, lon)


class Geometry:
    """
    Hold information about coordinates to easily convert them back and forth to Lambert or WGS84
    """
    def __init__(self, coords: CoordinateSequence, ftype: Any):
        self._coords = coords
        self.ftype = ftype

    @property
    def lonlat(self):
        return [xy_to_lonlat(c[0], c[1]) for c in self._coords]

    @property
    def lambert(self):
        return [c for c in self._coords]

    def nearest_points(self, other: Union["Polygon", "LineString", "Point"]):
        points = nearest_points(self, other)
        return [
            Point(cast(tuple[float, float], tuple(*point.coords))) for point in points
        ]


class Polygon(Geometry, geom.Polygon):
    def __init__(self, coords: list[tuple[float, float]]) -> None:
        geom.Polygon.__init__(self, coords)
        Geometry.__init__(self, self.exterior.coords, geom.Polygon)

    @staticmethod
    def from_angular(coords: list[tuple[float, float]]) -> "Polygon":
        coords = [lonlat_to_xy(c[0], c[1]) for c in coords]
        return Polygon(coords)

    @staticmethod
    def from_lambert(coords: list[tuple[float, float]]) -> "Polygon":
        return Polygon(coords)


class LineString(Geometry, geom.LineString):
    def __init__(self, coords: list[tuple[float, float]]) -> None:
        geom.LineString.__init__(self, coords)
        Geometry.__init__(self, self.coords, geom.LineString)

    @staticmethod
    def from_angular(coords: list[tuple[float, float]]) -> "LineString":
        coords = [lonlat_to_xy(c[0], c[1]) for c in coords]
        return LineString(coords)

    @staticmethod
    def from_lambert(coords: list[tuple[float, float]]) -> "LineString":
        return LineString(coords)


class Point(Geometry, geom.Point):
    def __init__(self, coords: tuple[float, float]) -> None:
        geom.Point.__init__(self, coords)
        Geometry.__init__(self, self.coords, geom.Point)

    @staticmethod
    def from_angular(coords: tuple[float, float]) -> "Point":
        coords = lonlat_to_xy(coords[0], coords[1])
        return Point(coords)

    @staticmethod
    def from_lambert(coords: tuple[float, float]) -> "Point":
        return Point(coords)
