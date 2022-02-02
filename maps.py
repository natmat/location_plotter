# https://stackoverflow.com/questions/68614721/how-add-circle-markers-to-a-rendered-folium-map-embedded-in-a-qwebengineview

import io
import os
import random
import sqlite3
import sys
import folium

from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
from jinja2 import Template

from waypoint import Waypoint


from mqtt import My_Mqtt


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
    coordinate_changed = pyqtSignal(str, float, float, float, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._timer_gps = QTimer(interval=1000)
        # self._timer_gps.timeout.connect(self.generate_coordinate)

        self._timer_waypoints = QTimer()

    def start(self):
        # Plot waypoints first
        self._timer_waypoints.singleShot(100, self.plot_waypoints)
        self._timer_gps.start()

    def stop(self):
        self._timer_gps.stop()

    def plot_waypoint(self, wp):
        print("PlotWP:", wp.lat, wp.lng)
        self.coordinate_changed.emit(wp.name, wp.lat, wp.lng, wp.radius, 'blue', True)

    def plot_gps(self, lat, lng):
        self.coordinate_changed.emit(None, lat, lng, 5, 'red', 0)

    def plot_waypoints(self):
        for wp in Waypoint.waypoints:
            self.plot_waypoint(wp)

    # def generate_coordinate(self):
    #     center_lat, center_lng = 51, -2.5
    #     x, y = (random.uniform(-0.5, 0.5) for _ in range(2))
    #     lat = center_lat + x
    #     lng = center_lng + y
    #     self.coordinate_changed.emit(lat, lng, 2000, 'orange')


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        coordinate = (51, -2.5)
        self.map = folium.Map(
            prefer_canvas=True,
            zoom_start=10, location=coordinate, control_scale=True, tiles=None
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

    def add_marker(self, name, latitude, longitude, in_radius=2.0, in_color='blue', marker=False):
        marker = 'true' if marker else 'false'
        js = Template(
            """
        if ({{marker}}) 
            L.marker([{{latitude}}, {{longitude}}]).addTo({{map}}).bindPopup('{{name}}').openPopup();
        L.circle(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": '{{color}}',
                "dashArray": null,
                "dashOffset": null,
                "fill": true,
                "fillColor": 'blue',
                "fillOpacity": 0.1,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": {{radius}},
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.map.get_name(), name=name, latitude=latitude, longitude=longitude, radius=in_radius, color=in_color, marker=marker)
        self.map_view.page().runJavaScript(js)


def main():
    app = QApplication(sys.argv)

    window = Window()
    window.showMaximized()

    provider = CoordinateProvider()
    provider.coordinate_changed.connect(window.add_marker)
    provider.start()

    db = Asdo('asdo_config.db')

    mqtt = My_Mqtt()
    mqtt.run(provider.plot_gps)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
