import string
from typing import Tuple


def convert_xy_to_grid(
    coords: tuple, map_size: float, catch_out_of_bounds: bool = True
) -> Tuple[int, int]:
    grid_size = 146.3
    grids = list(string.ascii_uppercase) + [
        f"A{letter}" for letter in list(string.ascii_uppercase)
    ]

    if coords[0] > map_size or coords[0] < 0 or coords[1] > map_size or coords[1] < 0:
        if catch_out_of_bounds:
            raise ValueError("Out of bounds")

    return grids[int(coords[0] // grid_size)], int((map_size - coords[1]) // grid_size)
