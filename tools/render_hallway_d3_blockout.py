"""Deterministic D3-to-D1 perspective blockout from APT-001 B01 coordinates.

This is deliberately a geometry check, not a finish/rendering tool.  Coordinates are
millimetres in a local plan system whose origin is the centre of D3; +Z follows the
camera direction (north on the source plan) and +X points east.
"""

from __future__ import annotations

from math import atan2, cos, radians, sin, tan
from pathlib import Path

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parents[1] / "tmp" / "hallway-d3-geometry-blockout.png"
W, H = 1600, 1200
CEILING = 2750.0
CAMERA = (0.0, -100.0, 1600.0)  # centre of D3, just on the bathroom side
TARGET = (-1680.0, 2915.0, 1500.0)  # centre of D1 on the source plan
FOV_DEG = 68.0


def normalize(x: float, z: float) -> tuple[float, float]:
    length = (x * x + z * z) ** 0.5
    return x / length, z / length


fx, fz = normalize(TARGET[0] - CAMERA[0], TARGET[1] - CAMERA[1])
# Screen-right when looking from D3 toward D1.
rx, rz = fz, -fx
FOCAL = (W / 2) / tan(radians(FOV_DEG) / 2)


def camera_space(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, z, y = point
    dx, dz, dy = x - CAMERA[0], z - CAMERA[1], y - CAMERA[2]
    return dx * rx + dz * rz, dy, dx * fx + dz * fz


def project(point: tuple[float, float, float]) -> tuple[float, float] | None:
    sx, sy, depth = camera_space(point)
    if depth <= 30:
        return None
    return W / 2 + FOCAL * sx / depth, H / 2 - FOCAL * sy / depth


def floor_poly(points: list[tuple[float, float]], color: str) -> tuple[float, list[tuple[float, float]], str] | None:
    pts3 = [(x, z, 0.0) for x, z in points]
    projected = [project(p) for p in pts3]
    if any(p is None for p in projected):
        return None
    depth = sum(camera_space(p)[2] for p in pts3) / len(pts3)
    return depth, [p for p in projected if p], color


def wall_poly(
    p1: tuple[float, float], p2: tuple[float, float], color: str, height: float = CEILING
) -> tuple[float, list[tuple[float, float]], str] | None:
    pts3 = [(p1[0], p1[1], 0.0), (p2[0], p2[1], 0.0), (p2[0], p2[1], height), (p1[0], p1[1], height)]
    projected = [project(p) for p in pts3]
    if any(p is None for p in projected):
        return None
    depth = sum(camera_space(p)[2] for p in pts3) / len(pts3)
    return depth, [p for p in projected if p], color


def vertical_panel(
    p1: tuple[float, float], p2: tuple[float, float], bottom: float, top: float, color: str
) -> tuple[float, list[tuple[float, float]], str] | None:
    pts3 = [(p1[0], p1[1], bottom), (p2[0], p2[1], bottom), (p2[0], p2[1], top), (p1[0], p1[1], top)]
    projected = [project(p) for p in pts3]
    if any(p is None for p in projected):
        return None
    depth = sum(camera_space(p)[2] for p in pts3) / len(pts3)
    return depth, [p for p in projected if p], color


def add_grid(
    out: list[tuple[float, list[tuple[float, float]], str]],
    x0: float,
    x1: float,
    z0: float,
    z1: float,
    step: float = 600,
) -> None:
    for x in range(int(x0), int(x1) + 1, int(step)):
        p1, p2 = project((x, z0, 2.0)), project((x, z1, 2.0))
        if p1 and p2:
            depth = (camera_space((x, z0, 2.0))[2] + camera_space((x, z1, 2.0))[2]) / 2
            out.append((depth, [p1, p2], "#b3aaa0"))
    for z in range(int(z0), int(z1) + 1, int(step)):
        p1, p2 = project((x0, z, 2.0)), project((x1, z, 2.0))
        if p1 and p2:
            depth = (camera_space((x0, z, 2.0))[2] + camera_space((x1, z, 2.0))[2]) / 2
            out.append((depth, [p1, p2], "#b3aaa0"))


def main() -> None:
    image = Image.new("RGB", (W, H), "#ded7cf")
    draw = ImageDraw.Draw(image)
    shapes: list[tuple[float, list[tuple[float, float]], str]] = []

    # Real plan floor zones.  The corridor is only 1040 mm deep here.
    for rect, color in (
        ([(-4825, 0), (1315, 0), (1315, 1040), (-4825, 1040)], "#d8d1c8"),
        ([(-2795, 1040), (-705, 1040), (-705, 2915), (-2795, 2915)], "#d9d2c8"),
        ([(-545, 1240), (5165, 1240), (5165, 4740), (-545, 4740)], "#d7d0c7"),
        ([(1315, 1040), (5165, 1040), (5165, -1770), (1315, -1770)], "#dad4cb"),
    ):
        poly = floor_poly(rect, color)
        if poly:
            shapes.append(poly)

    grid: list[tuple[float, list[tuple[float, float]], str]] = []
    add_grid(grid, -4825, 1315, 0, 1040)
    add_grid(grid, -2795, -705, 1040, 2915)
    add_grid(grid, -545, 5165, 1240, 4740)

    # Walls from the B01 plan.  Openings are deliberately omitted rather than
    # guessed; this makes D1, D2, D3 and P2 actual holes in the geometry.
    walls = [
        ((-2795, 1040), (-2795, 2915), "#bdb3a7"),  # entry left wall
        ((-2795, 2915), (-2185, 2915), "#c5bcb2"),  # 610 pier left of D1
        ((-1175, 2915), (-705, 2915), "#c5bcb2"),  # 470 pier right of D1
        ((-705, 1240), (-705, 1440), "#bfb5aa"),  # below D2
        ((-705, 2350), (-705, 2915), "#bfb5aa"),  # above D2
        ((-545, 1240), (5165, 1240), "#c6bcb1"),  # kitchen south wall
        ((-545, 0), (-405, 0), "#c1b7ab"),  # D3 left jamb
        ((405, 0), (1185, 0), "#c1b7ab"),  # D3 right jamb
        ((1315, -1770), (1315, 130), "#bdb3a8"),  # P2 wall below opening
        ((1315, 1040), (1315, 130), "#bdb3a8"),  # P2 small wall above opening
    ]
    for p1, p2, color in walls:
        poly = wall_poly(p1, p2, color)
        if poly:
            shapes.append(poly)

    # D1: black metal door exactly within the 1010 B01 position.  The U01 clear
    # width conflict is intentionally not stretched into the positional chain.
    door = vertical_panel((-2185, 2902), (-1175, 2902), 0, 2150, "#171819")
    if door:
        shapes.append(door)

    # 610-pier treatment: a slim vertical oak/mirror panel only; it cannot grow
    # into a deep corridor cabinet.
    pier = vertical_panel((-2780, 2890), (-2195, 2890), 0, CEILING, "#77533e")
    if pier:
        shapes.append(pier)
    mirror = vertical_panel((-2620, 2878), (-2325, 2878), 330, 2250, "#44484b")
    if mirror:
        shapes.append(mirror)

    # Electrical panel remains on the entry's left inside wall; this is only a
    # flush surface marker, never a storage carcass.
    panel = vertical_panel((-2778, 1740), (-2778, 2050), 850, 1650, "#e1ddd7")
    if panel:
        shapes.append(panel)

    # Floor tiles must sit behind walls but their lines remain useful as a scale check.
    shapes.sort(key=lambda item: item[0], reverse=True)
    for _, polygon, color in shapes:
        draw.polygon(polygon, fill=color)
        draw.line(polygon + [polygon[0]], fill="#83796f", width=2)

    # Thin floor grid after surfaces, before near frames.
    for _, line, color in sorted(grid, key=lambda item: item[0], reverse=True):
        if len(line) == 2:
            draw.line(line, fill=color, width=1)

    # Emphasise exact opening edges.
    for p1, p2 in (
        ((-2185, 2910, 0), (-2185, 2910, 2150)),
        ((-1175, 2910, 0), (-1175, 2910, 2150)),
        ((-705, 1440, 0), (-705, 1440, 2150)),
        ((-705, 2350, 0), (-705, 2350, 2150)),
        ((-405, 0, 0), (-405, 0, 2150)),
        ((405, 0, 0), (405, 0, 2150)),
    ):
        a, b = project(p1), project(p2)
        if a and b:
            draw.line([a, b], fill="#24201d", width=4)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
