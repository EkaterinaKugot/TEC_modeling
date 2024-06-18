import numpy as np
from numpy.typing import NDArray

class ModelData:
    def __init__(self, part_size: tuple[int]):
        self.global_size = (10, 10, 10)
        np.random.seed(29)
        self.global_arr = np.random.randint(0, 101, size=self.global_size)
        self.part_size = part_size
        
        self.overall_size = (self.global_size[0]*part_size[0], self.global_size[1]*part_size[1], self.global_size[2]*part_size[2])
        self.diagonal = np.sqrt(self.part_size[0]**2 + self.part_size[1]**2 + self.part_size[2]**2)

        self.global_idx = []
        self.neighbours = []

    
    def calculate_intersection_coords(
            self, 
            line_start: NDArray, 
            line_end: NDArray, 
            box_min: NDArray, 
            box_max: NDArray
        ) -> list[bool | NDArray]:
        direction = line_end - line_start
        
        tmin = np.where(direction != 0, (box_min - line_start) / direction, -np.inf)
        tmax = np.where(direction != 0, (box_max - line_start) / direction, np.inf)
        
        t_enter = np.max(np.minimum(tmin, tmax))
        t_exit = np.min(np.maximum(tmin, tmax))

        if np.any(direction == 0):
            for i in range(3):
                if direction[i] == 0:
                    if line_start[i] < box_min[i] or line_start[i] > box_max[i]:
                        return False, None, None
        
        if t_enter <= t_exit and t_exit >= 0:
            intersection_start = line_start + t_enter * direction
            intersection_end = line_start + t_exit * direction
            return True, intersection_start, intersection_end
        
        return False, None, None
    
    
    def calculate_neighbours(self, idx_x: int, idx_y: int, idx_z: int) -> list[list[int]]:
        neighbors = []
        for dy in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                y = idx_y + dy 
                if y < 0:
                    y = self.global_size[1] - 1
                elif y >= self.global_size[1]:
                    y = 0

                z = idx_z + dz
                if z < 0:
                    z = self.global_size[2] - 1
                elif z >= self.global_size[2]:
                    z = 0
                neighbors.append([idx_x, y, z])

        return neighbors
    
    
    def calculate_intersecs(
            self, 
            line: NDArray, 
            part_width: int, 
            part_height: int, 
            part_depth: int, 
            xyz: list[int]
        ) -> list[list[int] | list[list[int]] | tuple[tuple[NDArray]] | float]:
        x, y, z = xyz
        
        box_min = np.array([x, y, z])
        box_max = np.array([x + part_width, y + part_height, z + part_depth])
                        
        intersects, intersection_start, intersection_end = self.calculate_intersection_coords(
                            line[0], line[1], box_min, box_max
                        )
        if intersects:
            idx_x = int(x // part_width)
            idx_y = int(y // part_height)
            idx_z = int(z // part_depth)
            length = np.linalg.norm(intersection_end - intersection_start)
            neighbours = self.calculate_neighbours(idx_x, idx_y, idx_z)
            return [idx_x, idx_y, idx_z], neighbours, (tuple(intersection_start), tuple(intersection_end)), length
        return None, None, None, None
        

    def calculate_lens(self, line: NDArray) -> list[list[tuple[tuple[float]]] | list[float]]:
        coords_intersects = []
        lengths = []
        overall_width, overall_height, overall_depth = self.overall_size
        part_width, part_height, part_depth = self.part_size

        if len(self.neighbours) == 0:
            for x in range(0, overall_width, part_width):
                for y in range(0, overall_height, part_height):
                    for z in range(0, overall_depth, part_depth):
                        xyz = [x, y, z]
                        global_idx, neighbours, intersection, length = self.calculate_intersecs(line, part_width, part_height, part_depth, xyz)
                        if global_idx is not None:
                            self.global_idx.append(global_idx)
                            self.neighbours.append(neighbours)
                            coords_intersects.append(intersection)
                            lengths.append(length)
        else:
            tmp_neighbours = []
            self.global_idx = []
            for i in self.neighbours:
                for indices in i:
                    xyz = [indices[0] * part_width, indices[1] * part_height, indices[2] * part_depth]
                    global_idx, neighbours, intersection, length = self.calculate_intersecs(
                        line, 
                        part_width, 
                        part_height, 
                        part_depth, 
                        xyz
                    )
                    if global_idx is not None and not global_idx in self.global_idx:
                        self.global_idx.append(global_idx)
                        tmp_neighbours.append(neighbours)
                        coords_intersects.append(intersection)
                        lengths.append(length)

            self.neighbours = tmp_neighbours
        
        return coords_intersects, lengths
    

    def calculate_TEC(self, line: NDArray, show: bool = False):
        coords_intersects, lengths = self.calculate_lens(line)
        if show:
            self.show_intersection_data(coords_intersects, self.global_idx, lengths)
        coeff = [l/self.diagonal for l in lengths]
        tec = 0
        for n, (x, y, z) in enumerate(self.global_idx):
            tec += coeff[n] * self.global_arr[x][y][z]
        return tec


    @classmethod
    def show_intersection_data(
        self, 
        coords_intersects: list[tuple[tuple[float]]], 
        global_idx: list[list[list[int]]], 
        lengths: list[float]
    ):
        for idx, ((x, y, z), (start, end), length) in enumerate(zip(global_idx, coords_intersects, lengths)):
            print(f"Part {idx} ({x}, {y}, {z}):")
            print(f"  Start: {start}")
            print(f"  End: {end}")
            print(f"  Length: {length}")



