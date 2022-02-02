
class Waypoint:
    waypoints = []

    def __init__(self, wp):
        self.name, self.lat, self.lng, self.radius = wp
        Waypoint.waypoints.append(self)