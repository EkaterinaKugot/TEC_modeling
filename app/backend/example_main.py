from tec import get_sat_coords
from simurg_core.models.simple_tec import get_tec
from simurg_core.geometry.coord import cart_to_lle, xyz_to_el_az
from tec_calculation.ModelData import ModelData
from coordinates.sat import satellite_xyz

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import logging
import time
import numpy as np


"""poetry run python example_main.py"""

logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

start_time = time.time()
z_step = 10
part_size = (555, 555, z_step)
start_h_from_ground = 100
end_h_from_ground = 1000
start_date = datetime(2024, 1, 1)
end_date = start_date + timedelta(days=1)

input_file = "2024-01-01.rnx"

my_tecs = []
model_tec = []
times = []

kargs = {"z_start": start_h_from_ground, "z_end": end_h_from_ground, "l_step": z_step,
        "ne_0": 2e12, "hmax": 300, "half_thickness": 100}

site_x, site_y, site_z = -3176802.2528, 3303784.1477, 4421038.0496
start_lat, start_lon, start_h = cart_to_lle(site_x, site_y, site_z)
start_line = [start_lat, start_lon, start_h]


lat_sat = []
lon_sat = []

az_sat = []
el_sat = []


if __name__ == "__main__":
    m = ModelData(part_size, start_h_from_ground, end_h_from_ground)

    while start_date < end_date:
        yday = start_date.timetuple().tm_yday       
        UT = start_date.hour + start_date.minute / 60. + start_date.second / 3600.
        sat_x, sat_y, sat_z = satellite_xyz(input_file, "G", 5, start_date)    
        
        el, az = xyz_to_el_az([site_x, site_y, site_z], [sat_x, sat_y, sat_z])

        if np.radians(el) < 0:
            start_date += timedelta(seconds=30)
            continue

        az_sat.append(az)
        el_sat.append(el)
    
        end_lat, end_lon, end_h = cart_to_lle(sat_x, sat_y, sat_z)
        end_line = [end_lat, end_lon, end_h]

        lat_sat.append(end_lat)
        lon_sat.append(end_lon)
        
        tec = m.calculate_TEC(start_line, end_line, start_date)
        times.append(start_date)
        my_tecs.append(tec)

        m_tec = get_tec(yday=yday, UT=UT, az=np.radians(az), el=np.radians(el),
                    lat_0=start_lat, lon_0=start_lon,
                    **kargs)
        model_tec.append(m_tec)
        start_date += timedelta(seconds=30)

    execution_time = (time.time() - start_time) / 60.0
    print("Время выполнения: ", execution_time)
    # Время выполнения:  1.0521740198135376

    print("\nMy TECS:", my_tecs[:10])
    print()
    print("Model TECS:", model_tec[:10])

    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(times, my_tecs, label='My TECs')
    plt.plot(times, model_tec, label='get_tec()')

    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('TEC')

    plt.subplot(3, 1, 2)
    plt.scatter(lon_sat, lat_sat)

    plt.subplot(3, 1, 3)
    plt.scatter(times, el_sat)
  
    plt.show()

        
    
