#Author: Andres Ortiz
import Formulas.SpectralTable as ST
import attenuations as AT
import data_requester as DR
import Formulas.basicFormulas as BF
import time

if __name__ == "__main__":
    #First we want to load the Water and Oxygen data and Coefficients of interest
    oxygen_data = ST.loadOxygenData()
    water_data = ST.loadWaterData()
    coefficients_of_interest = AT.loadCoefficients()
    #Get the API Key
    api_key = DR.loadAPIkey()
    #Pick a random place to get weather from. Default Colorado Springs
    lat = 38.8339 #N
    long = -104.8214 #W
    weather_data = DR.get_weather_data(latitude=lat, longitude=long, api_key=api_key)
    pressure, water_vapor_density, temperature = DR.extract_weather_info(weather_data)
    frequency = 70 #GHz
    OX_basic_coefficients = BF.getBasicCoefficients(frequency=frequency,data=oxygen_data)
    W_basic_coefficients = BF.getBasicCoefficients(frequency=frequency, data=water_data)
    start_time = time.time()
    spga = AT.specific_gaseous_attenuation(frequency=frequency, barometric_pressure=pressure, water_vapor_density=water_vapor_density,
                                           Temperature=temperature, OXD=oxygen_data, WD=water_data, OBC=OX_basic_coefficients, WBC=W_basic_coefficients)

    end_time = time.time()
    elapsed_time = end_time-start_time
    print(f"Specific Attenuation value: {spga:.10f}. Elapsed calculation time: {elapsed_time:.4f} seconds")


    