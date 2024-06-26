import numpy as np



def clip_line_to_box(x1, y1, z1, x2, y2, z2, box_min, box_max):
    """Clips a line segment to a box."""
    tmin, tmax = 0.0, 1.0
    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1

    for i in range(3):
        if i == 0:
            p1, p2, p3, p4 = x1, dx, box_min[i], box_max[i]
        elif i == 1:
            p1, p2, p3, p4 = y1, dy, box_min[i], box_max[i]
        else:
            p1, p2, p3, p4 = z1, dz, box_min[i], box_max[i]
        
        if p2 == 0:
            if p1 < p3 or p1 > p4:
                return None
        else:
            t1 = (p3 - p1) / p2
            t2 = (p4 - p1) / p2
            tmin, tmax = max(tmin, min(t1, t2)), min(tmax, max(t1, t2))
            if tmin > tmax:
                return None
    
    return (x1 + tmin * dx, y1 + tmin * dy, z1 + tmin * dz), (x1 + tmax * dx, y1 + tmax * dy, z1 + tmax * dz)

def dda_line_3d(x1, y1, z1, x2, y2, z2, part_size):
    dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    steps = int(max(abs(dx), abs(dy), abs(dz)))

    Xinc, Yinc, Zinc = dx / steps, dy / steps, dz / steps

    x, y, z = x1, y1, z1
    blocks = []

    for _ in range(steps + 1):
        block_x, block_y, block_z = int(x // part_size[0]), int(y // part_size[1]), int(z // part_size[2])
        if (block_x, block_y, block_z) not in blocks:
            blocks.append((block_x, block_y, block_z))
        x += Xinc
        y += Yinc
        z += Zinc

    return blocks

def line_length_in_block(x1, y1, z1, x2, y2, z2, block, part_size):
    part_x, part_y, part_z = block
    part_size_x, part_size_y, part_size_z = part_size
    block_min_x, block_max_x = part_x * part_size_x, (part_x + 1) * part_size_x
    block_min_y, block_max_y = part_y * part_size_y, (part_y + 1) * part_size_y
    block_min_z, block_max_z = part_z * part_size_z, (part_z + 1) * part_size_z

    intersections = []

    def intersect_plane(p1, p2, p3, p4):
        t = (p3 - p1) / (p2 - p1)
        if 0 <= t <= 1:
            return t
        return None

    # Calculate intersections with block boundaries
    if x2 != x1:
        t1, t2 = intersect_plane(x1, x2, block_min_x, block_max_x), intersect_plane(x1, x2, block_max_x, block_min_x)
        if t1 is not None: intersections.append((block_min_x, y1 + t1 * (y2 - y1), z1 + t1 * (z2 - z1)))
        if t2 is not None: intersections.append((block_max_x, y1 + t2 * (y2 - y1), z1 + t2 * (z2 - z1)))
    if y2 != y1:
        t1, t2 = intersect_plane(y1, y2, block_min_y, block_max_y), intersect_plane(y1, y2, block_max_y, block_min_y)
        if t1 is not None: intersections.append((x1 + t1 * (x2 - x1), block_min_y, z1 + t1 * (z2 - z1)))
        if t2 is not None: intersections.append((x1 + t2 * (x2 - x1), block_max_y, z1 + t2 * (z2 - z1)))
    if z2 != z1:
        t1, t2 = intersect_plane(z1, z2, block_min_z, block_max_z), intersect_plane(z1, z2, block_max_z, block_min_z)
        if t1 is not None: intersections.append((x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1), block_min_z))
        if t2 is not None: intersections.append((x1 + t2 * (x2 - x1), y1 + t2 * (y2 - y1), block_max_z))

    intersections = sorted(intersections, key=lambda point: (point[0] - x1)**2 + (point[1] - y1)**2 + (point[2] - z1)**2)

    if len(intersections) >= 2:
        p1, p2 = intersections[:2]
        return np.linalg.norm(np.array(p2) - np.array(p1))
    return 0

# Пример использования:
grid_size_x, grid_size_y, grid_size_z = 1000, 1000, 200
part_size = (10, 10, 10)

station_lat, station_lon, station_height = 0.0, 0.0, 0
satellite_lat, satellite_lon, satellite_height = 75.0, 70.0, 20015780

station_x, station_y, station_z = latlon_to_xyz(station_lat, station_lon, station_height, grid_size_x, grid_size_y, grid_size_z)
satellite_x, satellite_y, satellite_z = latlon_to_xyz(satellite_lat, satellite_lon, satellite_height, grid_size_x, grid_size_y, grid_size_z)

print(f"Station:", station_x, station_y, station_z)
print(f"Sat:", satellite_x, satellite_y, satellite_z)

box_min = (0, 0, 100)
box_max = (grid_size_x, grid_size_y, grid_size_z)

clipped_line = clip_line_to_box(station_x, station_y, station_z, satellite_x, satellite_y, satellite_z, box_min, box_max)

print(clipped_line)

if clipped_line:
    (clipped_x1, clipped_y1, clipped_z1), (clipped_x2, clipped_y2, clipped_z2) = clipped_line

    blocks = dda_line_3d(clipped_x1, clipped_y1, clipped_z1, clipped_x2, clipped_y2, clipped_z2, part_size)
    lengths_in_blocks = [line_length_in_block(clipped_x1, clipped_y1, clipped_z1, clipped_x2, clipped_y2, clipped_z2, block, part_size) for block in blocks]

    print("Blocks:", len(blocks))
    print("Blocks:", blocks)
    print("Lengths in blocks:", len(lengths_in_blocks))
    print("Lengths in blocks:", lengths_in_blocks)
else:
    print("The line does not intersect the array.")





