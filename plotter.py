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

        self.getCityData()
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

        #Create Pressure, Water Vapor Denisty, Temperature
        self.pressure_label = tk.Label(self, text="Pressure:")
        self.pressure_label.grid(row = 4, column=0, padx=10, pady=5)
        self.wvd_label = tk.Label(self, text="Water Vapor Density")
        self.wvd_label.grid(row = 5, column=0, padx=10, pady=5)
        self.temperature_label = tk.Label(self, text="Temperature")
        self.temperature_label.grid(row = 6, column=0, padx=10, pady=5)

        self.pressure_value_label = tk.Label(self, text="0 hPA")
        self.pressure_value_label.grid(row = 4, column=1, padx=10, pady=5)
        self.wvd_value_label = tk.Label(self, text="0 g/m^3")
        self.wvd_value_label.grid(row = 5, column=1, padx=10, pady=5)
        self.temperature_value_label = tk.Label(self, text="0 C")
        self.temperature_value_label.grid(row = 6, column=1, padx=10, pady=5)


        # Create matplotlib figures for the plots
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
        self.elevation_slider.config(state=tk.DISABLED)
        #Callback function to update plots #3 and #4 when elevation is changed.
        self.updateElevationPlots()
        self.elevation_slider.config(state=tk.NORMAL)

    def on_dropdown_city_change(self, *args):
        self.dropdown.config(state=tk.DISABLED)
        new_city = self.dropdown.get()
        latitude = self.city_data[new_city]["latitude"]
        longitude = self.city_data[new_city]["longitude"]

        self.lat_entry.delete(0, tk.END)
        self.lat_entry.insert(0, latitude)
        self.lon_entry.delete(0, tk.END)
        self.lon_entry.insert(0, longitude)
        #Callback function to update all plots when latitude and longitude are selected
        self.updateAllPlots(latitude, longitude)
        self.dropdown.config(state=tk.NORMAL)

    def getCityData(self):
        #Pick a random place to get weather from. Default Colorado Springs
        self.city_data = {
            "Colorado Springs": {"latitude":38.8339, "longitude":-104.8214},
            "Houston": {"latitude":29.7604, "longitude":-95.3698}
        }
        filepath = "./cities.txt"
        with open(filepath, "r") as file:
            line = file.readline()
            while line:
                entry_array = line.split(" ")
                city = entry_array[0]
                latitude = entry_array[1]
                longitude = entry_array[2]
                self.city_data[city] = {"latitude": float(latitude), "longitude": float(longitude)}
                line = file.readline()

    def updateElevationPlots(self):
        elevation = self.elevation_slider.get()
        lat = self.lat_entry.get()
        long = self.lon_entry.get()
        frequency_band_SA = np.linspace(50.474214, 834.145546, 1000)
        
        frequency_band_OX = np.linspace(50.474214, 350, 1000)
        OX_basic_coefficients_list_OX = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_OX]
        instantOxygen_list = [AT.slantPath_instantanueousOxygen_attenuation(frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, elevation=elevation, OXD=self.oxygen_data, BC=OX_basic_coefficients_OX, coi=self.coefficients_of_interest)
            for freq, OX_basic_coefficients_OX in zip(frequency_band_OX, OX_basic_coefficients_list_OX)]

        frequency_band_W = np.linspace(22.235080, 1000, 1000)
        W_basic_coefficients_list_W = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_W]
        instantWater_list = [AT.slantPath_instantanueousWater_attenuation(frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, elevation=elevation, WD=self.water_data, BC=W_basic_coefficients_W)
            for freq, W_basic_coefficients_W in zip(frequency_band_W, W_basic_coefficients_list_W)]
        
        self.replotInstantaneousOxygen(frequency_band_OX, instantOxygen_list, lat, long)
        self.replotInstantaneousWater(frequency_band_W, instantWater_list, lat, long)

    def updateAllPlots(self, lat, long):
        weather_data = DR.get_weather_data(latitude=lat, longitude=long, api_key=self.api_key)
        self.pressure, self.water_vapor_density, self.temperature = DR.extract_weather_info(weather_data)

        self.pressure_value_label.config(text=str(self.pressure)+" hPA")
        self.wvd_value_label.config(text="{:.2f}".format(self.water_vapor_density)+" g/m^3")
        self.temperature_value_label.config(text="{:.2f}".format(((self.temperature-273.15)*9/5)+32)+" °F")

        elevation = self.elevation_slider.get()
        frequency_band_SA = np.linspace(50.474214, 834.145546, 1000)
        OX_basic_coefficients_list_SA = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_SA]
        W_basic_coefficients_list_SA = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_SA]
        spga_list = [AT.specific_gaseous_attenuation(
            frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, OXD=self.oxygen_data, WD=self.water_data, OBC=OX_basic_coefficients, WBC=W_basic_coefficients) 
            for freq, OX_basic_coefficients, W_basic_coefficients in zip(frequency_band_SA,OX_basic_coefficients_list_SA,W_basic_coefficients_list_SA)]
        
        frequency_band_OX = np.linspace(50.474214, 350, 1000)
        OX_basic_coefficients_list_OX = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_OX]
        instantOxygen_list = [AT.slantPath_instantanueousOxygen_attenuation(frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, elevation=elevation, OXD=self.oxygen_data, BC=OX_basic_coefficients_OX, coi=self.coefficients_of_interest)
            for freq, OX_basic_coefficients_OX in zip(frequency_band_OX, OX_basic_coefficients_list_OX)]

        frequency_band_W = np.linspace(22.235080, 1000, 1000)
        W_basic_coefficients_list_W = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_W]
        instantWater_list = [AT.slantPath_instantanueousWater_attenuation(frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, elevation=elevation, WD=self.water_data, BC=W_basic_coefficients_W)
            for freq, W_basic_coefficients_W in zip(frequency_band_W, W_basic_coefficients_list_W)]
        
        self.replotAttenuationFrequencyBand(frequency_band_SA, spga_list, lat, long)
        self.replotInstantaneousOxygen(frequency_band_OX, instantOxygen_list, lat, long)
        self.replotInstantaneousWater(frequency_band_W, instantWater_list, lat, long)

    def initializePlots(self, *args):
        selected_city = self.dropdown_var.get()  # Get the selected city from the dropdown
        city_dict = self.city_data[selected_city]
        lat = float(city_dict['latitude'])  # Get the custom latitude from the entry field
        long = float(city_dict['longitude'])  # Get the custom longitude from the entry field
        elevation = self.elevation_slider.get()  # Get the elevation value from the slider
        self.lat_entry.insert(0,lat)
        self.lon_entry.insert(0,long)

        weather_data = DR.get_weather_data(latitude=lat, longitude=long, api_key=self.api_key)
        self.pressure, self.water_vapor_density, self.temperature = DR.extract_weather_info(weather_data)

        self.pressure_value_label.config(text=str(self.pressure)+" hPA")
        self.wvd_value_label.config(text="{:.2f}".format(self.water_vapor_density)+" g/m^3")
        self.temperature_value_label.config(text="{:.2f}".format(((self.temperature-273.15)*9/5)+32)+" °F")

        frequency_band_SA = np.linspace(50.474214, 834.145546, 1000)
        OX_basic_coefficients_list_SA = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_SA]
        W_basic_coefficients_list_SA = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_SA]
        spga_list = [AT.specific_gaseous_attenuation(
            frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, OXD=self.oxygen_data, WD=self.water_data, OBC=OX_basic_coefficients, WBC=W_basic_coefficients) 
            for freq, OX_basic_coefficients, W_basic_coefficients in zip(frequency_band_SA,OX_basic_coefficients_list_SA,W_basic_coefficients_list_SA)]
        
        frequency_band_OX = np.linspace(50.474214, 350, 1000)
        OX_basic_coefficients_list_OX = [BF.getBasicCoefficients(frequency=freq,data=self.oxygen_data) for freq in frequency_band_OX]
        instantOxygen_list = [AT.slantPath_instantanueousOxygen_attenuation(frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, elevation=elevation, OXD=self.oxygen_data, BC=OX_basic_coefficients_OX, coi=self.coefficients_of_interest)
            for freq, OX_basic_coefficients_OX in zip(frequency_band_OX, OX_basic_coefficients_list_OX)]

        frequency_band_W = np.linspace(22.235080, 1000, 1000)
        W_basic_coefficients_list_W = [BF.getBasicCoefficients(frequency=freq, data=self.water_data) for freq in frequency_band_W]
        instantWater_list = [AT.slantPath_instantanueousWater_attenuation(frequency=freq, barometric_pressure=self.pressure, water_vapor_density=self.water_vapor_density,
            Temperature=self.temperature, elevation=elevation, WD=self.water_data, BC=W_basic_coefficients_W)
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
        city = self.dropdown.get()
        ax1 = self.figure2.add_subplot(111)
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Spefic Attenuation [dB/KM]')
        ax1.set_title(f'Specific Attenuation in {city} \nat Latitude {lat}, Longitude {long}')
        ax1.grid(True, which='both')
        canvas = FigureCanvasTkAgg(self.figure2, master=self)
        canvas.draw()
    def replotAttenuationFrequencyBand(self,x_data, y_data, lat, long):
        ax1 = self.figure2.gca()
        city = self.dropdown.get()
        ax1.clear()
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Spefic Attenuation [dB/KM]')
        ax1.set_title(f'Specific Attenuation in {city} \nat Latitude {lat}, Longitude {long}')
        ax1.grid(True, which='both')
        self.canvas2.draw()
    #This updates plot #3
    def plotInstantaneousOxygen(self, x_data, y_data, lat, long):
        self.figure3.clear()
        city = self.dropdown.get()
        ax1 = self.figure3.add_subplot(111)
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Attenuation [dB]')
        ax1.set_title(f"Oxygen Attenuation in {city} \nat Latitude {lat}, Longitude {long}")
        ax1.grid(True, which='both')
        canvas = FigureCanvasTkAgg(self.figure3, master=self)
        canvas.draw()
    def replotInstantaneousOxygen(self, x_data, y_data, lat, long):
        ax1 = self.figure3.gca()
        city = self.dropdown.get()
        ax1.clear()
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Attenuation [dB]')
        ax1.set_title(f"Oxygen Attenuation in {city} \nat Latitude {lat}, Longitude {long}")
        ax1.grid(True, which='both')
        self.canvas3.draw()
    #This updates plot #4
    def plotInstantaneousWater(self, x_data, y_data, lat, long):
        self.figure4.clear()
        city = self.dropdown.get()
        ax1 = self.figure4.add_subplot(111)
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Attenuation [dB]')
        ax1.set_title(f"Water Attenuation in {city} \nat Latitude {lat}, Longitude {long}")
        ax1.grid(True, which='both')
        canvas = FigureCanvasTkAgg(self.figure4, master=self)
        canvas.draw()
    def replotInstantaneousWater(self, x_data, y_data, lat, long):
        ax1 = self.figure4.gca()
        city = self.dropdown.get()
        ax1.clear()
        ax1.semilogy(x_data, y_data)
        ax1.set_xlabel('Frequency [GHz]')
        ax1.set_ylabel('Attenuation [dB]')
        ax1.set_title(f"Water Attenuation in {city} \nat Latitude {lat}, Longitude {long}")
        ax1.grid(True, which='both')
        self.canvas4.draw()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
    print("Cheerio")

    
    


    