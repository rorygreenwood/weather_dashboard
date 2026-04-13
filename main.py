import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import os

from requester import request_weather, WeatherData

THUNDERSTORM = [200, 201, 202, 210, 211, 212, 221]
THUNDER_WITH_RAIN = [230, 231, 232]
DRIZZLE = [300, 301, 302, 310, 311, 312, 313, 314, 321]
LIGHT_RAIN = [500, 520]
MEDIUM_RAIN = [501, 502, 521, 531]
HEAVY_RAIN = [503, 504, 522]
SLEET = [611, 612, 613, 615]
SNOW = [600, 601]
HAIL = [511, 616, 620, 621, 622]
VISIBILITY = [701, 711, 721, 731, 741, 751, 761, 762, 771, 781]
CLEAR = [800]
LIGHT_CLOUDS = [801, 802]
MEDIUM_CLOUDS = [803]
HEAVY_CLOUDS = [804]

def lookup_icon(weatherdata: WeatherData) -> str:
    """Receives weather_id from API response and builds filepath to use."""
    folder = 'day' if weatherdata.is_day else 'night'
    
    weather_icon = None
    if weatherdata.weather_id in THUNDERSTORM:
        weather_icon = 'lighting-storm.png'
    elif weatherdata.weather_id in THUNDER_WITH_RAIN:
        weather_icon = 'thunderstorm.png'
    elif weatherdata.weather_id in HAIL:
        weather_icon = 'hail.png'
    elif weatherdata.weather_id in DRIZZLE:
        weather_icon = 'drizzle.png'
    elif weatherdata.weather_id in LIGHT_RAIN:
        weather_icon = 'drizzle.png'
    elif weatherdata.weather_id in MEDIUM_RAIN:
        weather_icon = 'rain.png'
    elif weatherdata.weather_id in HEAVY_RAIN:
        folder = 'cloud'
        weather_icon = 'downpour.png'
    elif weatherdata.weather_id in SNOW:
        folder = 'cloud'
        weather_icon = 'snow.png'
    elif weatherdata.weather_id in SLEET:
        folder = 'cloud'
        weather_icon = 'sleet.png'
    elif weatherdata.weather_id in HAIL:
        weather_icon = 'hail.png'
    elif weatherdata.weather_id in VISIBILITY:
        weather_icon = 'hazy.png'
    elif weatherdata.weather_id in CLEAR:
        weather_icon = 'clear.png'
    elif weatherdata.weather_id in LIGHT_CLOUDS:
        weather_icon = 'slightly-cloudy.png' if folder == 'day' else 'clear.png'
    elif weatherdata.weather_id in MEDIUM_CLOUDS:
        weather_icon = 'cloudy.png'
    elif weatherdata.weather_id in HEAVY_CLOUDS:
        folder = 'cloud'
        weather_icon = 'overcast.png'
    filepath = f'light_icons/{folder}/{weather_icon}'
    return filepath

class WeatherApp:
    def __init__(self, root, weatherdata: WeatherData):
        
        self.weatherdata = weatherdata
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
        self.refresh()

    def refresh(self):
        # 3. Weather Icon (The Pillow Part)
        self.icon_label = tk.Label(self.main_frame, bg='#1a1a1a')
        self.icon_label.pack(pady=20)
        
        filepath = lookup_icon(weatherdata=self.weatherdata)
        self.set_weather_icon(filepath)

        # 4. Text Labels
        self.temp_label = tk.Label(self.main_frame, text=f"{self.weatherdata.temp}°C", fg="#00d4ff", 
                                   bg="#1a1a1a", font=self.temp_font)
        self.temp_label.pack()

        self.city_label = tk.Label(self.main_frame, text=self.weatherdata.name, fg="white", 
                                   bg="#1a1a1a", font=self.city_font)
        self.city_label.pack(pady=5)

        self.desc_label = tk.Label(self.main_frame, text=self.weatherdata.weather_type, fg="#888888", 
                                   bg="#1a1a1a", font=self.info_font)

        self.desc_label = tk.Label(self.main_frame, text=self.weatherdata.weather_desc, fg="#888888", 
                                   bg="#1a1a1a", font=self.info_font)
        self.desc_label.pack()

        # Metrics
        self.grid_container = tk.Frame(self.main_frame, bg='#1a1a1a')
        self.grid_container.pack(pady=20)

        # Humidity
        humidity_img = Image.open('light_icons/metric/humidity.png').resize((60, 60), Image.Resampling.LANCZOS)
        self.humidity_icon = ImageTk.PhotoImage(humidity_img)
        self.humidity_icon_label = tk.Label(self.grid_container, bg='#1a1a1a', image=self.humidity_icon)
        self.humidity_icon_label.grid(row=0, column=1, padx=20, pady=20)

        self.humidity_label = tk.Label(self.grid_container, text=str(self.weatherdata.humidity) + '%', fg='#888888',bg='#1a1a1a', font=self.info_font)
        self.humidity_label.grid(row=1, column=1)

        # todo - Ditto for below items as well


        # Windspeed
        wind_img = Image.open('light_icons/metric/wind-direction.png').resize((60, 60), Image.Resampling.LANCZOS)
        self.wind_icon = ImageTk.PhotoImage(wind_img)
        self.wind_icon_label = tk.Label(self.grid_container, bg='#1a1a1a', image=self.wind_icon)
        self.wind_icon_label.grid(row=0, column=2, pady=20, padx=20)

        self.windspeed_label = tk.Label(self.grid_container, text=str(self.weatherdata.wind_speed) + str(self.weatherdata.wind_direction), fg='#888888',bg='#1a1a1a', font=self.info_font)
        self.windspeed_label.grid(row=1, column=2)

        # Sunrise
        sunrise_img = Image.open('light_icons/metric/sunrise.png').resize((60, 60), Image.Resampling.LANCZOS)
        self.sunrise_icon = ImageTk.PhotoImage(sunrise_img)
        self.sunrise_icon_label = tk.Label(self.grid_container, bg='#1a1a1a', image=self.sunrise_icon)
        self.sunrise_icon_label.grid(row=0, column=3, pady=20, padx=20)

        # Sunset
        sunset_img = Image.open('light_icons/metric/sunset.png').resize((60, 60), Image.Resampling.LANCZOS)
        self.sunset_icon = ImageTk.PhotoImage(sunset_img)
        self.sunset_icon_label = tk.Label(self.grid_container, bg='#1a1a1a', image=self.sunset_icon)
        self.sunset_icon_label.grid(row=0, column=4, pady=20, padx=20)


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
    weatherdata = request_weather()
    root = tk.Tk()
    # root.attributes('-fullscreen', True) # Uncomment for the Pi
    app = WeatherApp(root, weatherdata=weatherdata)
    root.mainloop()