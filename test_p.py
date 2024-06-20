from simurg_core.models.simple_tec import get_ne
import matplotlib.pyplot as plt
import numpy as np
# import seaborn as sns
from simurg_core.models.simple_tec import get_tec
from simurg_core.geometry.coord import cart_to_lle
from tec_modeling import ModelData
from datetime import datetime
import logging
import time


logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)


# def xyz_to_latlon(x, y, z):
#     degrees_lon = (x / global_size[0]) * 360 - 180
#     degrees_lat = (y / global_size[1]) * 180 - 90
#     lon = np.radians(degrees_lon)
#     lat = np.radians(degrees_lat)
#     height = z 
#     return lat, lon, height


# def latlon_to_xyz(self, lat, lon, height):
#     degrees_lat = np.degrees(lat)
#     degrees_lon = np.degrees(lon)
#     x = (degrees_lat + 90) / 180 * self.global_size[0] # широта -90 90
#     y = (degrees_lon + 180) / 360 * self.global_size[1] # долгота -180 180
#     z = height / 1000 #km
#     return x, y, z


# diagonal = np.sqrt(part_size[0]**2 + part_size[1]**2 + part_size[2]**2)

# global_size = (500, 1000, 200)

start_time = time.time()
z_step = 10
part_size = (500, 500, z_step)

tecs = []
tecs2 = []

start_h_from_ground = 100
end_h_from_ground = 1000
kargs = {"z_start": start_h_from_ground, "z_end": end_h_from_ground, "l_step": z_step,
                 "ne_0": 2e12, "hmax": 300, "half_thickness": 100}

date = datetime(2024, 1, 1, 18, 0, 0)
yday = date.timetuple().tm_yday       
UT = date.hour + date.minute / 60. + date.second / 3600.
# m = ModelData(part_size, start_h_from_ground, end_h_from_ground)

lat_range = list(range(-90, 91))
lon_range = list(range(-180, 181))

my_tecs = []
model_tecs = []


for lat in lat_range:
    tmp_my_tecs = []
    tmp_model_tecs = []
    m = ModelData(part_size, start_h_from_ground, end_h_from_ground)
    for lon in lon_range:
        h_site = 0
        h_sat = 20015780.84050447

        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        tec = m.calculate_TEC([lat_rad, lon_rad, h_site], [lat_rad, lon_rad, h_sat], date)
        d = get_tec(yday=yday, UT=UT, az=0, el=np.pi / 2.,
                    lat_0=lat_rad, lon_0=lon_rad,
                    **kargs)
        # print(tec)
        tmp_my_tecs.append(tec)
        tmp_model_tecs.append(d)

    my_tecs.append(tmp_my_tecs)
    model_tecs.append(tmp_model_tecs)
print(len(my_tecs) * len(my_tecs[0]))

execution_time = (time.time() - start_time) / 60.0
print("Время выполнения: ", execution_time)

fig, ax = plt.subplots(2, 1, figsize=(10, 8))

tec1 = ax[0].imshow(my_tecs)
ax[0].set_title('My')
fig.colorbar(tec1, ax=ax[0], orientation='vertical')

tec2 = ax[1].imshow(model_tecs)
ax[1].set_title('get_tec()')
fig.colorbar(tec2, ax=ax[1], orientation='vertical')

plt.show()

# for x in range(0, global_size[0], part_size[0]):
#     nes_tmp = []
#     nes_tmp2 = []
#     for y in range(0, global_size[1], part_size[1]):
#         tec = 0
#         x0, y0, z0 = xyz_to_latlon(x, y, 0)
#         z0 = 0
#         x1, y1, z1 = xyz_to_latlon(x, y, 0)
#         z1 = 20015780.84050447
#         tec = m.calculate_TEC([x0, y0, z0], [x1, y1, z1], date)
#         # for z in range(h_from_ground, global_size[2], part_size[2]):
#         #     center_idx = [x+(part_size[0]/2), y+(part_size[1]/2), z+(part_size[2]/2)]
#         #     center_llh = xyz_to_latlon(center_idx[0], center_idx[1], center_idx[2])
#         #     # print(center_llh)
#         #     ne = get_ne(
#         #         yday=yday,
#         #         UT=UT, 
#         #         lat=center_llh[0], 
#         #         lon=center_llh[1], 
#         #         z=center_llh[2], 
#         #         **kargs
#         #     )
#         #     tec += 10.0 * 1000 * ne 
#         nes_tmp.append(tec)

#         d = get_tec(yday=yday, UT=UT, az=0, el=np.pi / 2.,
#                     lat_0=x0, lon_0=y0,
#                     **kargs)
#         nes_tmp2.append(d)
#     tecs.append(nes_tmp)
#     tecs2.append(nes_tmp2)

# print(len(tecs))   

# fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# tec1 = ax[0].imshow(tecs)
# ax[0].set_title('My')
# fig.colorbar(tec1, ax=ax[0], orientation='vertical')

# tec2 = ax[1].imshow(tecs2)
# ax[1].set_title('get_tec()')
# fig.colorbar(tec2, ax=ax[1], orientation='vertical')

# plt.show()
