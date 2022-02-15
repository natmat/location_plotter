
class Waypoint:
    waypoints = []

    def __init__(self, wp):
        self.name, self.lat, self.lng, self.radius = wp
        Waypoint.waypoints.append(self)

    @classmethod
    def get_bounds(cls):
        lat_min = min(cls.waypoints, key=lambda t: t.lat).lat
        lat_max = max(cls.waypoints, key=lambda t: t.lat).lat
        lng_min = min(cls.waypoints, key=lambda t: t.lng).lng
        lng_max = max(cls.waypoints, key=lambda t: t.lng).lng
        return [(lat_min, lng_min), (lat_max, lng_max)]

    @classmethod
    def get_centre(cls):
        (lat_min,lng_min), (lat_max,lng_max) = cls.get_bounds()
        return ((lat_min+lat_max)/2, (lng_min+lng_max)/2)

    @classmethod
    def print_waypoints(cls):
        for wp in cls.waypoints:
            print(wp.lat)


def main():
    for i in range(0,10,1):
        wp = ("WP" + str(i), 100+i, 200+i, 300+i)
        Waypoint(wp)

    # Waypoint.print_waypoints()
    print(Waypoint.get_bounds())
    print(Waypoint.get_centre())

if __name__ == '__main__':
    main()