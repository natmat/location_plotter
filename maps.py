# https://stackoverflow.com/questions/68614721/how-add-circle-markers-to-a-rendered-folium-map-embedded-in-a-qwebengineview

import io
import os
import sqlite3
import sys

import folium
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
from jinja2 import Template


class Waypoint:
    waypoints = []

    def __init__(self, wp):
        self.name, self.lat, self.lng, self.r = wp
        Waypoint.waypoints.append(self)

    @classmethod
    def plot_waypoints(cls, provider, window):
        for wp in Waypoint.waypoints:
            # print("wp:", wp.lat, wp.lng)
            provider.coordinate_changed.connect(window.add_marker)#(wp.lat, wp.lng, 10, 'red'))


class Asdo:
    def __init__(self, config):
        try:
            self.db = sqlite3.connect(config)
            self.load_wapoints()
        except Exception as e:
            print("Error: sqlite3 connect failed: " + repr(e))
            print("You need a valid asdo_config.db in pwd: " + os.getcwd())
            sys.exit(1)

    def load_wapoints(self):
        try:
            # Load db and select all wp
            c = self.db.cursor()
            for wp in c.execute(
                    "select waypoint_name, waypoint_lat, waypoint_long, waypoint_radius from waypoint order by waypoint_name asc"):
                Waypoint(wp)
        except Exception as e:
            print("Error: sqlite3 connect failed: " + repr(e))
            print("You need a valid asdo_config.db in pwd: " + os.getcwd())
            raise


class CoordinateProvider(QObject):
    coordinate_changed = pyqtSignal(float, float, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(interval=500)
        self._timer.timeout.connect(self.generate_coordinate)

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def generate_coordinate(self):
        import random

        center_lat, center_lng = 52, 1
        x, y = (random.uniform(-0.1, 0.1) for _ in range(2))
        latitude = center_lat + x
        longitude = center_lng + y
        self.coordinate_changed.emit(latitude, longitude, 10, 'red')


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        coordinate = (52, 1)
        self.map = folium.Map(
            prefer_canvas=True,
            zoom_start=12, location=coordinate, control_scale=True, tiles=None
        )
        folium.TileLayer('openstreetmap').add_to(self.map)
        folium.LayerControl().add_to(self.map)

        # Draw point for test
        # folium.Marker(coordinate).add_to(self.map)

        data = io.BytesIO()
        self.map.save(data, close_file=False)

        self.map_view = QWebEngineView()
        self.map_view.setHtml(data.getvalue().decode())

        self.setCentralWidget(self.map_view)

    def add_marker(self, latitude, longitude, radius=2, color='blue'):
        print("maker:", latitude, longitude, radius, color)
        # "color": "#3388ff",
        js = Template(
            """
        L.marker([{{latitude}}, {{longitude}}] )
            .addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'red',
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2.0,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.map.get_name(), latitude=latitude, longitude=longitude)
        self.map_view.page().runJavaScript(js)



def main():
    app = QApplication(sys.argv)

    window = Window()
    window.showMaximized()

    provider = CoordinateProvider()

    db = Asdo('asdo_config.db')
    # Waypoint.plot_waypoints(provider, window)

    provider.coordinate_changed.connect(window.add_marker)

    provider.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
