from __future__ import annotations

from typing import Any

from numpy.typing import NDArray
import tcod
import tcod.noise

from game_map import tile_types
from game_map.game_map import GameMap


def generate_heightmap(width: int, height: int, scale: float, octaves: int, lacunarity: float) -> NDArray[Any]:
    shape = (width, height)

    noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.NOISE_SIMPLEX,
        implementation=0,
        octaves=octaves,
        lacunarity=lacunarity,
        seed=42,
    )
    samples = noise[tcod.noise.grid(shape, scale, origin=(0, 0))]

    return (samples + 1) / 2


def generate_island(
    map_width: int,
    map_height: int,
):
    """Generate a new island map."""

    height_map = generate_heightmap(
        width=map_width,
        height=map_height,
        scale=0.09,
        octaves=6,
        lacunarity=2.0,
    )

    x_center = map_width // 2
    y_center = map_height // 2

    island = GameMap(map_width, map_height)
    for x in range(map_width):
        for y in range(map_height):
            len_from_center_x = abs(x_center - x) / x_center
            len_from_center_y = abs(y_center - y) / y_center

            h = height_map[y][x] * (1 - max(len_from_center_x, len_from_center_y))

            if x == 0 or y == 0 or x == map_width - 1 or y == map_height - 1:
                island.tiles[x, y] = tile_types.water
            elif h < 0.15:
                island.tiles[x, y] = tile_types.water
            elif h < 0.2:
                island.tiles[x, y] = tile_types.sand
            elif h > 0.7:
                island.tiles[x, y] = tile_types.mountain
            elif 0.4 < h < 0.7:
                island.tiles[x, y] = tile_types.forrest
            else:
                island.tiles[x, y] = tile_types.grass

    return island
