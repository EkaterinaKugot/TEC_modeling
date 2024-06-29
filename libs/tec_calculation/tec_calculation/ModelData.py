import numpy as np
from numpy.typing import NDArray
from datetime import datetime

from simurg_core.models.simple_tec import get_ne


KM_PER_DEGREE = 111


class ModelData:
    def __init__(
        self,
        part_size: tuple[int],
        start_h_from_ground: int,
        end_h_from_ground: int,
    ):
        self.part_size = part_size
        self.global_size = (
            180 * KM_PER_DEGREE,
            360 * KM_PER_DEGREE,
            end_h_from_ground,
        )
        self.number_part = (
            self.global_size[0] // self.part_size[0],
            self.global_size[1] // self.part_size[1],
            self.global_size[2] // self.part_size[2]
            - start_h_from_ground // self.part_size[2],
        )
        self.start_h_from_ground = start_h_from_ground

        self.ne_0 = 2e12
        self.hmax = 300
        self.half_thickness = 100

        self.diagonal = np.sqrt(
            self.part_size[0] ** 2
            + self.part_size[1] ** 2
            + self.part_size[2] ** 2
        )

        self.neighbours = []

    def calculate_intersection_coords(
        self,
        line_start: NDArray,
        line_end: NDArray,
        box_min: NDArray,
        box_max: NDArray,
    ) -> list[bool | NDArray]:
        direction = line_end - line_start

        tmin = np.where(
            direction != 0, (box_min - line_start) / direction, -np.inf
        )
        tmax = np.where(
            direction != 0, (box_max - line_start) / direction, np.inf
        )

        t_enter = np.max(np.minimum(tmin, tmax))
        t_exit = np.min(np.maximum(tmin, tmax))

        if np.any(direction == 0):
            for i in range(3):
                if direction[i] == 0:
                    if (
                        line_start[i] < box_min[i]
                        or line_start[i] > box_max[i]
                    ):

                        return False, None, None
        if t_enter <= t_exit and t_exit >= 0:
            intersection_start = line_start + t_enter * direction
            intersection_end = line_start + t_exit * direction
            return True, intersection_start, intersection_end
        return False, None, None

    def calculate_neighbours(
        self, idx_x: int, idx_y: int, idx_z: int
    ) -> list[list[int]]:
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = idx_x + dx
                if x < 0:
                    x = self.number_part[0] - 1
                elif x >= self.number_part[0]:
                    x = 0
                y = idx_y + dy
                if y < 0:
                    y = self.number_part[1] - 1
                elif y >= self.number_part[1]:
                    y = 0
                neighbors.append([x, y, idx_z])
        return neighbors

    def calculate_intersecs(
        self,
        line: NDArray,
        part_width: int,
        part_height: int,
        part_depth: int,
        xyz: list[int],
    ) -> list[
        list[int] | list[list[int]] | tuple[tuple[NDArray]] | float | NDArray
    ]:
        x, y, z = xyz

        box_min = np.array([x, y, z])
        box_max = np.array([x + part_width, y + part_height, z + part_depth])

        center = (box_min + box_max) / 2

        intersects, intersection_start, intersection_end = (
            self.calculate_intersection_coords(
                line[0], line[1], box_min, box_max
            )
        )
        if intersects:
            idx_x = int(x // part_width)
            idx_y = int(y // part_height)
            idx_z = int(z // part_depth)
            length = np.linalg.norm(intersection_end - intersection_start)
            neighbours = self.calculate_neighbours(idx_x, idx_y, idx_z)
            return (
                [idx_x, idx_y, idx_z],
                center,
                neighbours,
                (tuple(intersection_start), tuple(intersection_end)),
                length,
            )
        return None, None, None, None, None

    def calculate_lens(
        self, line: NDArray
    ) -> list[list[tuple[tuple[float]]] | list[float]]:
        coords_intersects = []
        lengths = []
        global_idx = []
        center_idx = []
        global_width, global_height, global_depth = self.global_size
        part_width, part_height, part_depth = self.part_size

        if len(self.neighbours) == 0:
            for x in range(0, global_width, part_width):
                for y in range(0, global_height, part_height):
                    for z in range(
                        self.start_h_from_ground, global_depth, part_depth
                    ):
                        xyz = [x, y, z]
                        g_idx, center, neighbours, intersection, length = (
                            self.calculate_intersecs(
                                line, part_width, part_height, part_depth, xyz
                            )
                        )
                        if g_idx is not None:
                            global_idx.append(g_idx)
                            center_idx.append(center)
                            self.neighbours.append(neighbours)
                            coords_intersects.append(intersection)
                            lengths.append(length)
                            if (
                                g_idx[2]
                                == self.global_size[2] // self.part_size[2] - 1
                                and line[0][0] == line[1][0]
                                and line[0][1] == line[1][1]
                            ):
                                return (
                                    coords_intersects,
                                    global_idx,
                                    center_idx,
                                    lengths,
                                )
        else:
            tmp_neighbours = []
            for i in self.neighbours:
                for indices in i:
                    xyz = [
                        indices[0] * part_width,
                        indices[1] * part_height,
                        indices[2] * part_depth,
                    ]
                    g_idx, center, neighbours, intersection, length = (
                        self.calculate_intersecs(
                            line, part_width, part_height, part_depth, xyz
                        )
                    )
                    if g_idx is not None and not g_idx in global_idx:
                        global_idx.append(g_idx)
                        center_idx.append(center)
                        tmp_neighbours.append(neighbours)
                        coords_intersects.append(intersection)
                        lengths.append(length)
                        if (
                            g_idx[2]
                            == self.global_size[2] // self.part_size[2] - 1
                            and line[0][0] == line[1][0]
                            and line[0][1] == line[1][1]
                        ):
                            self.neighbours = tmp_neighbours
                            return (
                                coords_intersects,
                                global_idx,
                                center_idx,
                                lengths,
                            )
            self.neighbours = tmp_neighbours
            if len(global_idx) < self.number_part[2]:
                self.neighbours = []
                return self.calculate_lens(line)
        return coords_intersects, global_idx, center_idx, lengths

    def calculate_TEC(
        self,
        start_line: list[float],
        end_line: list[float],
        date: datetime,
        show: bool = False,
    ):
        yday = date.timetuple().tm_yday
        UT = date.hour + date.minute / 60.0 + date.second / 3600.0

        start_xyz = self.latlon_to_xyz(
            start_line[0], start_line[1], start_line[2]
        )  # in x, y, z
        end_xyz = self.latlon_to_xyz(
            end_line[0], end_line[1], end_line[2]
        )  # in x, y, z

        line = np.array([start_xyz, end_xyz])
        coords_intersects, global_idx, center_idx, lengths = (
            self.calculate_lens(line)
        )

        if show:
            self.show_intersection_data(coords_intersects, global_idx, lengths)
        coeff = [l / self.diagonal for l in lengths]
        tec = 0
        center_llh = np.array(
            [self.xyz_to_latlon(c[0], c[1], c[2]) for c in center_idx]
        )
        for n, (lat, lon, h) in enumerate(center_llh):
            ne = get_ne(
                yday,
                UT,
                lat,
                lon,
                h,
                ne_0=self.ne_0,
                hmax=self.hmax,
                half_thickness=self.half_thickness,
            )
            tec += lengths[n] * ne * 1000
        return tec / 1e16

    def latlon_to_xyz(self, lat, lon, height):
        degrees_lat = np.degrees(lat)
        degrees_lon = np.degrees(lon)
        x = (degrees_lat + 90) / 180 * self.global_size[0]  # широта -90 90
        y = (degrees_lon + 180) / 360 * self.global_size[1]  # долгота -180 180
        z = height / 1000  # km
        return x, y, z

    def xyz_to_latlon(self, x, y, z):
        degrees_lat = (x / self.global_size[0]) * 180 - 90
        degrees_lon = (y / self.global_size[1]) * 360 - 180
        lon = np.radians(degrees_lon)
        lat = np.radians(degrees_lat)
        height = z
        return lat, lon, height

    @classmethod
    def show_intersection_data(
        cls,
        coords_intersects: list[tuple[tuple[float]]],
        global_idx: list[list[list[int]]],
        lengths: list[float],
    ):
        for idx, ((x, y, z), (start, end), length) in enumerate(
            zip(global_idx, coords_intersects, lengths)
        ):
            print(f"Part {idx} ({x}, {y}, {z}):")
            print(f"  Start: {start}")
            print(f"  End: {end}")
            print(f"  Length: {length}")

    @classmethod
    def convert_degrees_to_kms(cls, deg):
        return int(deg * KM_PER_DEGREE)

    @classmethod
    def convert_kms_to_degrees(cls, km):
        degree = int(km / KM_PER_DEGREE)
        return degree
