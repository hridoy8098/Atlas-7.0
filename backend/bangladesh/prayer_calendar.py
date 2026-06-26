import math
import calendar
from datetime import datetime, date


class PrayerCalendar:
    """Calculate Islamic prayer times for Bangladeshi cities."""

    CITIES = {
        "dhaka": {"lat": 23.8103, "lon": 90.4125, "tz": 6},
        "chittagong": {"lat": 22.3569, "lon": 91.7832, "tz": 6},
        "khulna": {"lat": 22.8456, "lon": 89.5403, "tz": 6},
        "rajshahi": {"lat": 24.3636, "lon": 88.6241, "tz": 6},
        "sylhet": {"lat": 24.8949, "lon": 91.8687, "tz": 6},
        "barisal": {"lat": 22.7010, "lon": 90.3535, "tz": 6},
        "rangpur": {"lat": 25.7468, "lon": 89.2504, "tz": 6},
        "mymensingh": {"lat": 24.7471, "lon": 90.4203, "tz": 6},
        "comilla": {"lat": 23.4607, "lon": 91.1809, "tz": 6},
        "bogra": {"lat": 24.8510, "lon": 89.3720, "tz": 6},
    }

    def __init__(self, fajr_angle=18, isha_angle=18):
        self.fajr_angle = fajr_angle
        self.isha_angle = isha_angle

    def list_cities(self):
        return list(self.CITIES.keys())

    def _dtr(self, deg):
        return deg * math.pi / 180.0

    def _rtd(self, rad):
        return rad * 180.0 / math.pi

    def _sun_declination(self, dt):
        n = (dt - datetime(dt.year, 1, 1)).days
        g = self._dtr(357.529 + 0.98560028 * n)
        l = self._dtr(280.459 + 0.98564736 * n)
        ecliptic = 23.439 - 0.00000036 * n
        l_app = l + self._dtr(1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
        decl = self._rtd(math.asin(math.sin(self._dtr(ecliptic)) * math.sin(l_app)))
        eq_time = (self._rtd(l_app) - self._rtd(l_app) % 360) / 15
        return decl, eq_time

    def get_prayer_times(self, city, date_obj=None):
        city = city.lower().strip()
        if city not in self.CITIES:
            raise ValueError(f"City '{city}' not found. Available: {self.list_cities()}")
        if date_obj is None:
            date_obj = date.today()
        lat = self.CITIES[city]["lat"]
        lon = self.CITIES[city]["lon"]
        tz = self.CITIES[city]["tz"]
        dt = datetime(date_obj.year, date_obj.month, date_obj.day)
        decl, _ = self._sun_declination(dt)
        d_rad = self._dtr(decl)
        lat_rad = self._dtr(lat)
        midday = 12.0 - lon / 15.0 + tz
        sha = self._rtd(
            math.acos(
                (math.sin(self._dtr(-0.833)) - math.sin(lat_rad) * math.sin(d_rad))
                / (math.cos(lat_rad) * math.cos(d_rad))
            )
        ) / 15.0
        fajr_sha = self._rtd(
            math.acos(
                (math.sin(self._dtr(-self.fajr_angle)) - math.sin(lat_rad) * math.sin(d_rad))
                / (math.cos(lat_rad) * math.cos(d_rad))
            )
        ) / 15.0
        isha_sha = self._rtd(
            math.acos(
                (math.sin(self._dtr(-self.isha_angle)) - math.sin(lat_rad) * math.sin(d_rad))
                / (math.cos(lat_rad) * math.cos(d_rad))
            )
        ) / 15.0
        asr_alt = self._rtd(
            math.atan(1.0 / (math.tan(lat_rad) + math.tan(d_rad)))
        )
        asr_sha = self._rtd(
            math.acos(
                (math.sin(self._dtr(asr_alt)) - math.sin(lat_rad) * math.sin(d_rad))
                / (math.cos(lat_rad) * math.cos(d_rad))
            )
        ) / 15.0
        return {
            "date": date_obj.isoformat(),
            "city": city,
            "fajr": self._fmt(midday - fajr_sha),
            "sunrise": self._fmt(midday - sha),
            "dhuhr": self._fmt(midday),
            "asr": self._fmt(midday + asr_sha),
            "maghrib": self._fmt(midday + sha),
            "isha": self._fmt(midday + isha_sha),
        }

    def _fmt(self, hours):
        hours = hours % 24
        h = int(hours)
        m = int(round((hours - h) * 60))
        if m == 60:
            h += 1
            m = 0
        h = h % 24
        return f"{h:02d}:{m:02d}"

    def get_monthly_schedule(self, city, year, month):
        city = city.lower().strip()
        if city not in self.CITIES:
            raise ValueError(f"City '{city}' not found. Available: {self.list_cities()}")
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        num_days = calendar.monthrange(year, month)[1]
        schedule = []
        for day in range(1, num_days + 1):
            schedule.append(self.get_prayer_times(city, date(year, month, day)))
        return schedule
