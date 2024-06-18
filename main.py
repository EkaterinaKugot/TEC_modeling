from ModelData import ModelData
import numpy as np

"""poetry run python main.py"""

part_size = (10, 10, 10)

start_line1 = [0, 25, 11]

end_line1 = [99, 54, 29]
end_line2 = [99, 54, 30]
end_line3 = [99, 54, 31]

lines = np.array([[start_line1, end_line1], [start_line1, end_line2], [start_line1, end_line3]])

if __name__ == "__main__":
    m = ModelData(part_size)
    for line in lines:
        tec = m.calculate_TEC(line, show=False)
        print(f"\nTEC = {tec}")
