import matplotlib.pyplot as plt
import numpy as np
from simurg_core.models.simple_tec import get_tec
from tec_calculation.ModelData import ModelData
from datetime import datetime
import logging
import time

logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

start_time = time.time()
z_step = 10
part_size = (550, 550, z_step)

tecs = []
tecs2 = []

start_h_from_ground = 100
end_h_from_ground = 1000
kargs = {"z_start": start_h_from_ground, "z_end": end_h_from_ground, "l_step": z_step,
                 "ne_0": 2e12, "hmax": 300, "half_thickness": 100}

date = datetime(2024, 1, 1, 18, 0, 0)
yday = date.timetuple().tm_yday       
UT = date.hour + date.minute / 60. + date.second / 3600.

lat_step = 1
lon_step = 1
lat_range = list(range(-90, 90, lat_step))
lon_range = list(range(-180, 180, lon_step))

my_tecs = []
model_tecs = []

h_site = 0
h_sat = 20015780.84050447

for lat in lat_range:
    tmp_my_tecs = []
    tmp_model_tecs = []
    m = ModelData(part_size, start_h_from_ground, end_h_from_ground)
    for lon in lon_range:
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        tec = m.calculate_TEC([lat_rad, lon_rad, h_site], [lat_rad, lon_rad, h_sat], date)
        d = get_tec(yday=yday, UT=UT, az=0, el=np.pi / 2.,
                    lat_0=lat_rad, lon_0=lon_rad,
                    **kargs)
        tmp_my_tecs.append(tec)
        tmp_model_tecs.append(d)

    my_tecs.append(tmp_my_tecs)
    model_tecs.append(tmp_model_tecs)

execution_time = (time.time() - start_time) / 60.0
print("Время выполнения: ", execution_time)
#Время выполнения:  3.9555572986602785

fig, ax = plt.subplots(2, 1, figsize=(10, 8))

tec1 = ax[0].imshow(my_tecs)
ax[0].set_title('My')
fig.colorbar(tec1, ax=ax[0], orientation='vertical')

tec2 = ax[1].imshow(model_tecs)
ax[1].set_title('get_tec()')
fig.colorbar(tec2, ax=ax[1], orientation='vertical')

plt.show()