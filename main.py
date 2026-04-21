"""Main."""
import datetime
import os

import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

from requester import request_weather, WeatherData

from utils import WeatherAPICodes

COUNTRY_CODE = 'UK'
POST_CODE = 'L21'

def lookup_icon(weatherdata: WeatherData) -> str:
    """Receives weather_id from API response and builds filepath to use."""
    folder = 'day' if weatherdata.is_day else 'night'

    weather_icon = None
    if weatherdata.weather_id in WeatherAPICodes.THUNDERSTORM:
        weather_icon = 'lighting-storm.png'
    elif weatherdata.weather_id in WeatherAPICodes.THUNDER_WITH_RAIN:
        weather_icon = 'thunderstorm.png'
    elif weatherdata.weather_id in WeatherAPICodes.HAIL:
        weather_icon = 'hail.png'
    elif weatherdata.weather_id in WeatherAPICodes.DRIZZLE:
        weather_icon = 'drizzle.png'
    elif weatherdata.weather_id in WeatherAPICodes.LIGHT_RAIN:
        weather_icon = 'drizzle.png'
    elif weatherdata.weather_id in WeatherAPICodes.MEDIUM_RAIN:
        weather_icon = 'rain.png'
    elif weatherdata.weather_id in WeatherAPICodes.HEAVY_RAIN:
        folder = 'cloud'
        weather_icon = 'downpour.png'
    elif weatherdata.weather_id in WeatherAPICodes.SNOW:
        folder = 'cloud'
        weather_icon = 'snow.png'
    elif weatherdata.weather_id in WeatherAPICodes.SLEET:
        folder = 'cloud'
        weather_icon = 'sleet.png'
    elif weatherdata.weather_id in WeatherAPICodes.HAIL:
        weather_icon = 'hail.png'
    elif weatherdata.weather_id in WeatherAPICodes.VISIBILITY:
        weather_icon = 'hazy.png'
    elif weatherdata.weather_id in WeatherAPICodes.CLEAR:
        weather_icon = 'clear.png'
    elif weatherdata.weather_id in WeatherAPICodes.LIGHT_CLOUDS:
        weather_icon = 'slightly-cloudy.png' if folder == 'day' else 'clear.png'
    elif weatherdata.weather_id in WeatherAPICodes.MEDIUM_CLOUDS:
        weather_icon = 'cloudy.png'
    elif weatherdata.weather_id in WeatherAPICodes.HEAVY_CLOUDS:
        folder = 'cloud'
        weather_icon = 'overcast.png'
    filepath = f'icons/{folder}/{weather_icon}'
    return filepath

class WeatherApp:
    """Bundles data from Weather API response."""
    def __init__(self, root):
        self.locations = [('GB', 'L21'),
                          ('GB', 'LA9'),
                          ('GB', 'WC1')]
        self.location_idx = 0
        self.weatherdata = request_weather(country_code=self.locations[self.location_idx][0],
                                           zipcode=self.locations[self.location_idx][1])
        self.root = root
        self.root.title("Pi Weather Kiosk")
        self.root.geometry("720x1280") # Portrait for Pi Touch Display 2
        self.root.configure(bg='#1a1a1a')

        # 1. Setup Fonts
        self.temp_font = font.Font(family="Helvetica", size=90, weight="bold")
        self.city_font = font.Font(family="Helvetica", size=32)
        self.info_font = font.Font(family="Helvetica", size=18)

        # 2. Create UI Containers (Frames)
        self.main_frame = tk.Frame(self.root, bg='#1a1a1a')
        self.main_frame.place(relx=0.5, rely=0.4, anchor="center")
        self.diagnotics_frame = tk.Frame(self.root, bg='#1a1a1a')
        self.diagnotics_frame.place(relx=0.5, rely=1, anchor="s")

    def _clear(self):
        # Remove pre-existing widgets.
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        for widget in self.diagnotics_frame.winfo_children():
            widget.destroy()

    def _icons_weather_lookup(self):
        """Update general data for the report."""
        self.icon_label = tk.Label(self.main_frame, bg='#1a1a1a')
        self.icon_label.pack(pady=20)

        filepath = lookup_icon(weatherdata=self.weatherdata)
        self.set_weather_icon(filepath)

        self.temp_label = tk.Label(self.main_frame,
                                   text=f"{self.weatherdata.temp}°C",
                                   fg="#00d4ff",
                                   bg="#1a1a1a",
                                   font=self.temp_font)
        self.temp_label.pack()

        self.city_label = tk.Label(self.main_frame,
                                   text=self.weatherdata.name,
                                   fg="white",
                                   bg="#1a1a1a",
                                   font=self.city_font)
        self.city_label.pack(pady=5)

        self.desc_label = tk.Label(self.main_frame,
                                   text=self.weatherdata.weather_type,
                                   fg="#888888",
                                   bg="#1a1a1a",
                                   font=self.info_font)

        self.desc_label = tk.Label(self.main_frame,
                                   text=self.weatherdata.weather_desc,
                                   fg="#888888",
                                   bg="#1a1a1a",
                                   font=self.info_font)
        self.desc_label.pack()

    def _icons_metrics_lookup(self):
        """Update metrics data for the report."""
        # Metrics
        self.grid_container = tk.Frame(self.main_frame, bg='#1a1a1a')
        self.grid_container.pack(pady=20)

        # Humidity
        humidity_img = Image.open('icons/metric/humidity.png').resize((60, 60),
                                                                      Image.Resampling.LANCZOS)
        self.humidity_icon = ImageTk.PhotoImage(humidity_img)
        self.humidity_icon_label = tk.Label(self.grid_container,
                                            bg='#1a1a1a',
                                            image=self.humidity_icon)
        self.humidity_icon_label.grid(row=0, column=1, padx=20, pady=20)

        self.humidity_label = tk.Label(self.grid_container,
                                       text=str(self.weatherdata.humidity) + '%',
                                       fg='#888888',
                                       bg='#1a1a1a',
                                       font=self.info_font)
        self.humidity_label.grid(row=1, column=1)

        # Windspeed
        wind_img = Image.open('icons/metric/wind-direction.png').resize((60, 60), Image.Resampling.LANCZOS)
        self.wind_icon = ImageTk.PhotoImage(wind_img)
        self.wind_icon_label = tk.Label(self.grid_container,
                                        bg='#1a1a1a',
                                        image=self.wind_icon)
        self.wind_icon_label.grid(row=0, column=2, pady=20, padx=20)

        self.windspeed_label = tk.Label(self.grid_container,
                                        text=str(self.weatherdata.wind_speed) + str(self.weatherdata.wind_direction),
                                        fg='#888888',
                                        bg='#1a1a1a',
                                        font=self.info_font)
        self.windspeed_label.grid(row=1, column=2)

        # Sunrise
        sunrise_img = Image.open('icons/metric/sunrise.png').resize((60, 60),
                                                                    Image.Resampling.LANCZOS)
        self.sunrise_icon = ImageTk.PhotoImage(sunrise_img)
        self.sunrise_icon_label = tk.Label(self.grid_container,
                                           bg='#1a1a1a',
                                           image=self.sunrise_icon)
        self.sunrise_icon_label.grid(row=0, column=3, pady=20, padx=20)
        self.sunrise_label = tk.Label(self.grid_container,
                                      text=str(self.weatherdata.sunrise),
                                      fg='#888888',
                                      bg='#1a1a1a',
                                      font=self.info_font)
        self.sunrise_label.grid(row=1, column=3)

        # Sunset
        sunset_img = Image.open('icons/metric/sunset.png').resize((60, 60), Image.Resampling.LANCZOS)
        self.sunset_icon = ImageTk.PhotoImage(sunset_img)
        self.sunset_icon_label = tk.Label(self.grid_container, bg='#1a1a1a', image=self.sunset_icon)
        self.sunset_icon_label.grid(row=0, column=4, pady=20, padx=20)
        self.sunset_label = tk.Label(self.grid_container,
                                     text=str(self.weatherdata.sunset),
                                     fg='#888888',
                                     bg='#1a1a1a',
                                     font=self.info_font)
        self.sunset_label.grid(row=1, column=4)

    def _metrics_lookup(self):
        """Update metrics data for the report."""
        current_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.timestamp_label = tk.Label(self.diagnotics_frame, text=f'Last updated at {current_ts}',)
        self.timestamp_label.pack(pady=5)

    def refresh(self):
        """Serves icons reflecting the data provided by Weather API."""

        self._clear()

        # Find latest weather.
        self.weatherdata = request_weather(zipcode=self.locations[self.location_idx][1],
                                           country_code=self.locations[self.location_idx][0])
        self._icons_weather_lookup()
        self._icons_metrics_lookup()

        # Diagnostics
        self._metrics_lookup()

        # Adds 1, and if the idx reaches the same num as the length of locations, returns to 0.
        self.location_idx = (self.location_idx + 1) % len(self.locations)
        self.root.after(10000, self.refresh)

    def set_weather_icon(self, icon_name):
        """Uses Pillow to load, resize, and display a transparent PNG icon."""
        try:
            # Load the image
            full_path = os.path.join(os.path.dirname(__file__), icon_name)
            pil_img = Image.open(full_path).convert("RGBA")

            # Resize smoothly to 250x250 pixels
            pil_img = pil_img.resize((250, 250), Image.Resampling.LANCZOS)

            # Convert to Tkinter-compatible format
            self.tk_icon = ImageTk.PhotoImage(pil_img)
            self.icon_label.config(image=self.tk_icon)

        except Exception as e:
            print(f"Error loading icon: {e}")
            self.icon_label.config(text="[Icon Missing]", fg="white")


if __name__ == "__main__":
    root = tk.Tk()
    # root.attributes('-fullscreen', True) # Uncomment for the Pi
    app = WeatherApp(root)
    app.refresh() # Provides initial info at startup.
    root.mainloop()
