#Author: Andres Ortiz
import Formulas.SpectralTable as ST
import attenuations as AT
import data_requester as DR
import Formulas.basicFormulas as BF
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.basemap import Basemap
from PIL import Image, ImageTk

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Attenuation Application")
        self.geometry("1600x1200")

        #Pick a random place to get weather from. Default Colorado Springs
        self.city_data = {
            "Colorado Springs": {"latitude":38.8339, "longitude":-104.8214},
            "Houston": {"latitude":29.7604, "longitude":-95.3698}
        }
        #TODO: update this with a tool that reads cities in from a file
        #First we want to load the Water and Oxygen data and Coefficients of interest
        self.oxygen_data = ST.loadOxygenData()
        self.water_data = ST.loadWaterData()
        self.coefficients_of_interest = AT.loadCoefficients()
        #Get the API Key
        self.api_key = DR.loadAPIkey()
        self.create_widgets()
        self.initializePlots()

    def create_widgets(self):
        self.lat_entry_label = tk.Label(self, text="City:")
        self.lat_entry_label.grid(row=0, column=0, padx=10, pady=5)
        # Create the dropdown for city selection
        cities_list = list(self.city_data.keys())
        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.dropdown_var, values=cities_list)
        self.dropdown.set(cities_list[0])  # Set the default selected city
        self.dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_city_change)

        # Create entry fields for custom latitude and longitude
        self.lat_entry_label = tk.Label(self, text="Latitude:")
        self.lat_entry_label.grid(row=1, column=0, padx=10, pady=5)
        self.lat_entry = tk.Entry(self)
        self.lat_entry.grid(row=1, column=1, padx=10, pady=5)

        self.lon_entry_label = tk.Label(self, text="Custom Longitude:")
        self.lon_entry_label.grid(row=2, column=0, padx=10, pady=5)
        self.lon_entry = tk.Entry(self)
        self.lon_entry.grid(row=2, column=1, padx=10, pady=5)

        # Create the elevation slider
        self.elevation_slider_label = tk.Label(self, text="Elevation:")
        self.elevation_slider_label.grid(row=3, column=0, padx=10, pady=5)
        self.elevation_slider = tk.Scale(self, from_=2, to=90, orient=tk.HORIZONTAL, command=self.on_elevation_slider_change)
        self.elevation_slider.grid(row=3, column=1, padx=10, pady=5)

        # Create three matplotlib figures for the plots
        self.figure1 = plt.figure()
        self.figure2 = plt.figure()
        self.figure3 = plt.figure()
        self.figure4 = plt.figure()

        # Create the canvas widgets for the plots
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self)
        self.canvas1.get_tk_widget().grid(row=0, column=2, padx=10, pady=10, columnspan=4, rowspan=8)

        self.canvas2 = FigureCanvasTkAgg(self.figure2, master=self)
        self.canvas2.get_tk_widget().grid(row=0, column=6, padx=10, pady=10, columnspan=4, rowspan=8)

        self.canvas3 = FigureCanvasTkAgg(self.figure3, master=self)
        self.canvas3.get_tk_widget().grid(row=8, column=2, padx=10, pady=10, columnspan=4, rowspan=8)

        self.canvas4 = FigureCanvasTkAgg(self.figure4, master=self)
        self.canvas4.get_tk_widget().grid(row=8, column=6, padx=10, pady=10, columnspan=4, rowspan=8)

    def on_elevation_slider_change(self, *args):
        #Callback function to update plots #3 and #4 when elevation is changed.
        self.updateElevationPlots()

    def on_dropdown_city_change(self, *args):
        #Callback function to update all plots when latitude and longitude are selected
        self.updateAllPlots()

    def updateElevationPlots():
        pass

    def updateAllPlots():
        pass

    def initializePlots(self, *args):
        selected_city = self.dropdown_var.get()  # Get the selected city from the dropdown
        city_dict = self.city_data[selected_city]
        lat = float(city_dict['latitude'])  # Get the custom latitude from the entry field
        long = float(city_dict['longitude'])  # Get the custom longitude from the entry field
        elevation = self.elevation_slider.get()  # Get the elevation value from the slider
        self.lat_entry.insert(0,lat)
        self.lon_entry.insert(0,long)

        weather_data = DR.get_weather_data(latitude=lat, longitude=long, api_key=self.api_key)
        pressure, water_vapor_density, temperature = DR.extract_weather_info(weather_data)

        frequency_band_SA = np.linspace(50.474214, 834.145546, 1000)
        OX_basic_coefficients_list_SA = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_SA]
        W_basic_coefficients_list_SA = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_SA]
        spga_list = [AT.specific_gaseous_attenuation(
            frequency=freq, barometric_pressure=pressure, water_vapor_density=water_vapor_density,
            Temperature=temperature, OXD=self.oxygen_data, WD=self.water_data, OBC=OX_basic_coefficients, WBC=W_basic_coefficients) 
            for freq, OX_basic_coefficients, W_basic_coefficients in zip(frequency_band_SA,OX_basic_coefficients_list_SA,W_basic_coefficients_list_SA)]
        
        frequency_band_OX = np.linspace(50.474214, 350, 1000)
        OX_basic_coefficients_list_OX = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_OX]
        instantOxygen_list = [AT.slantPath_instantanueousOxygen_attenuation(frequency=freq, barometric_pressure=pressure, water_vapor_density=water_vapor_density,
            Temperature=temperature, elevation=elevation, OXD=self.oxygen_data, BC=OX_basic_coefficients_OX, coi=self.coefficients_of_interest)
            for freq, OX_basic_coefficients_OX in zip(frequency_band_OX, OX_basic_coefficients_list_OX)]

        frequency_band_W = np.linspace(22.235080, 1780, 1000)
        W_basic_coefficients_list_W = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_W]
        instantWater_list = [AT.slantPath_instantanueousWater_attenuation(frequency=freq, barometric_pressure=pressure, water_vapor_density=water_vapor_density,
            Temperature=temperature, elevation=elevation, WD=self.water_data, BC=W_basic_coefficients_W)
            for freq, W_basic_coefficients_W in zip(frequency_band_W, W_basic_coefficients_list_W)]

        self.plotMercator(lat, long)
        self.plotAttenuationFrequencyBand(frequency_band_SA, spga_list, lat, long)
        self.plotInstantaneousOxygen(frequency_band_OX, instantOxygen_list, lat, long)
        self.plotInstantaneousWater(frequency_band_W, instantWater_list, lat, long)

    def plotMercator(self,lat, long):
        pass


    def mercator_projection(self, lon, lat):
        """
        Convert latitude and longitude to Mercator coordinates.
        """
        r_major = 6378137.0  # Earth's semi-major axis (in meters)
        x = r_major * np.radians(lon)
        y = r_major * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
        return x, y

    #This updates plot #2
    def plotAttenuationFrequencyBand(self,x_data, y_data, lat, long):
        self.figure2.clear()
        ax1 = self.figure2.add_subplot(111)
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Spefic Attenuation [dB/KM]')
        ax1.set_title(f'Specific Attenuation at Latitude {lat}, Longitude {long}')
        ax1.grid(True, which='both')
        canvas = FigureCanvasTkAgg(self.figure2, master=self)
        canvas.draw()

    def plotInstantaneousOxygen(self, x_data, y_data, lat, long):
        self.figure3.clear()
        ax1 = self.figure3.add_subplot(111)
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Attenuation [dB]')
        ax1.set_title(f"Oxygen Attenuation at Latitude {lat}, Longitude {long}")
        ax1.grid(True, which='both')
        canvas = FigureCanvasTkAgg(self.figure3, master=self)
        canvas.draw()
        
    def plotInstantaneousWater(self, x_data, y_data, lat, long):
        self.figure4.clear()
        ax1 = self.figure4.add_subplot(111)
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Attenuation [dB]')
        ax1.set_title(f"Water Attenuation at Latitude {lat}, Longitude {long}")
        ax1.grid(True, which='both')
        canvas = FigureCanvasTkAgg(self.figure3, master=self)
        canvas.draw()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
    print("Cheerio")

    
    


    