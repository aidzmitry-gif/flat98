"""Daylight render of B01. Coordinates come from the approved O1 plan export.

Run render_b01_o1_two_sashes.cjs first. Mitsuba 3.9.1 is installed locally in
tmp/b01-mitsuba-runtime. The room-facing camera uses a section at the media wall.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tmp/b01-mitsuba-runtime'))
import mitsuba as mi

mi.set_variant('scalar_rgb')
T = mi.ScalarTransform4f


def linear(rgb):
    rgb = np.asarray(rgb, dtype=np.float32)
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)


def pigment(hex_color):
    return {'type': 'rgb', 'value': linear(np.array(ImageColor.getrgb(hex_color)) / 255).tolist()}


def texture(values):
    return {'type': 'bitmap', 'bitmap': mi.Bitmap(linear(np.clip(values / 255, 0, 1))),
            'filter_type': 'bilinear', 'wrap_mode': 'repeat', 'raw': True}


def matte(color, roughness=.35):
    diffuse = pigment(color) if isinstance(color, str) else color
    return mi.load_dict({'type': 'roughplastic', 'distribution': 'ggx', 'alpha': roughness,
                         'diffuse_reflectance': diffuse, 'int_ior': 1.44})


def grain_texture(color, kind, size=512):
    x, y = np.meshgrid(np.linspace(0, 1, size), np.linspace(0, 1, size))
    random = np.random.default_rng(24).normal(0, .006, x.shape)
    if kind == 'oak':
        flow = y + .015 * np.sin(x * 8 + y * 4) + .008 * np.sin(x * 21 + y * 9)
        gain = 1 + .038 * np.sin(flow * 108) + .019 * np.sin(flow * 304) + .025 * np.sin(flow * 31) + random
    elif kind == 'stone':
        flow = 8.5 * y + 6 * x + np.sin(x * 7 + y * 3) + .45 * np.cos(y * 19 - x * 14)
        gain = 1 + .009 * np.cos(y * 52 + x * 11) - .075 * np.maximum(np.sin(flow), 0) ** 19 + random * .4
    else:
        weave = np.sin(x * 1380) * np.sin(y * 1420)
        gain = 1 + .016 * weave + .018 * np.sin(x * 35 + y * 42) * np.sin(x * 49 - y * 56) + random
    return texture(gain[..., None] * ImageColor.getrgb(color))


def oak_floor(width, depth):
    x, y = np.meshgrid(np.linspace(0, width, 2304), np.linspace(0, depth, 1412))
    plank = .105 * math.sqrt(2)
    u, v = (x + y) / plank, (y - x) / plank
    i, j = np.floor(u), np.floor(v)
    band = (i - j) % 8
    horizontal = band < 4
    row = np.where(horizontal, i - band, i)
    col = np.where(horizontal, j, j - (7 - band))
    board = (np.sin(12.9898 * row + 78.233 * col) * 43758.5453) % 1
    length = np.where(horizontal, u - row, v - col)
    cross = np.where(horizontal, v - col, u - row)
    drift = cross + .016 * np.sin(length * 1.8 + board * 9) + .008 * np.cos(length * 4 + cross * 10)
    knot = np.hypot((length - (.5 + board * 2.7)) * .29, cross - (.30 + board * .43))
    rings = .035 * (board > .82) * np.exp(-knot * 13) * (1 + np.cos(knot * 130))
    seam = np.minimum.reduce((cross, 1 - cross, length, 4 - length))
    value = 1 + .16 * (board - .5) + .022 * np.sin(drift * 91) + .018 * np.sin(drift * 193)
    value -= rings + .12 * np.exp(-(seam / .007) ** 2)
    return texture(value[..., None] * np.array([187, 155, 116]))


def landscape_texture(artwork=False):
    x, y = np.meshgrid(np.linspace(0, 1, 920), np.linspace(0, 1, 485))
    clouds = np.sin(19 * x + 2 * y) * np.sin(7 * x - 18 * y) + .5 * np.sin(74 * x + 51 * y)
    sky = np.stack((185 + 44 * y, 161 + 45 * y, 126 + 52 * y), axis=-1)
    colors = ((188, 154, 112), (172, 128, 89), (118, 121, 91), (72, 94, 73)) if artwork else (
        (159, 170, 146), (132, 151, 128), (104, 137, 112), (73, 111, 93))
    for i, color in enumerate(colors):
        ridge = .66 - .126 * i + .077 * np.sin(x * (4.5 + i) + 1.75 * i) + .022 * np.sin(x * 24 + i)
        opacity = np.clip((ridge - y + .010 * clouds) * (42 if artwork else 150), 0, 1)[..., None]
        pigment = np.asarray(color) + 3.8 * clouds[..., None]
        sky = sky * (1 - opacity) + opacity * pigment
    return texture(sky + (2.7 if artwork else .9) * clouds[..., None])


def mesh(name, points, faces, normals=None, uv=None):
    result = mi.Mesh(name, len(points), len(faces), has_vertex_normals=normals is not None,
                     has_vertex_texcoords=uv is not None)
    params = mi.traverse(result)
    params['vertex_positions'] = np.asarray(points, dtype=np.float32).ravel()
    params['faces'] = np.asarray(faces, dtype=np.uint32).ravel()
    if normals is not None:
        params['vertex_normals'] = np.asarray(normals, dtype=np.float32).ravel()
    if uv is not None:
        params['vertex_texcoords'] = np.asarray(uv, dtype=np.float32).ravel()
    params.update()
    return result


def rounded_box(name, lo, hi, bevel, rotation=None):
    lo, hi = np.array(lo), np.array(hi)
    radius = min(bevel, min(hi - lo) * .46)
    points, normals, faces, uv = [], [], [], []

    def divisions(axis):
        if radius == 0:
            return np.array([lo[axis], hi[axis]])
        edge = radius * np.array([0, .25, .52, .77, 1])
        return np.r_[lo[axis] + edge, hi[axis] - edge[::-1]]

    for axis in range(3):
        a, b = (axis + 1) % 3, (axis + 2) % 3
        for sign in (-1, 1):
            start = len(points)
            aa, bb = divisions(a), divisions(b)
            for va in aa:
                for vb in bb:
                    p = lo.copy()
                    p[a], p[b], p[axis] = va, vb, (hi if sign > 0 else lo)[axis]
                    n = np.eye(3)[axis] * sign
                    if radius:
                        center = np.clip(p, lo + radius, hi - radius)
                        n = p - center
                        n /= np.linalg.norm(n)
                        p = center + radius * n
                    if rotation is not None:
                        matrix, center = rotation
                        p, n = center + matrix @ (p - center), matrix @ n
                    points.append(p)
                    normals.append(n)
                    uv.append(((va - lo[a]) / (hi[a] - lo[a]), (vb - lo[b]) / (hi[b] - lo[b])))
            for ia in range(len(aa) - 1):
                for ib in range(len(bb) - 1):
                    i = start + ia * len(bb) + ib
                    j = i + len(bb)
                    faces.extend(((i, j, j + 1), (i, j + 1, i + 1)) if sign > 0
                                 else ((i, j + 1, j), (i, i + 1, j + 1)))
    return mesh(name, points, faces, normals, uv)


class RoomRender:
    def __init__(self, data, overview):
        self.data = data
        self.overview = overview
        self.width = data['room']['width'] / 1000
        self.depth = data['room']['depth'] / 1000
        self.height = data['room']['assumedHeight'] / 1000
        self.rect = {item['id']: np.array(item['rect']) / 1000 for item in data['furniture']}
        self.parts = {}
        self.ivory = matte('#e5d9c9', .29)
        self.wall = matte('#e1d5c7', .55)
        self.ceiling = matte('#efe7dc', .62)
        self.kick = matte('#a09381', .35)
        self.wood = matte(grain_texture('#ad855e', 'oak'), .29)
        self.stone = matte(grain_texture('#e4d8c2', 'stone'), .27)
        self.backsplash = matte(grain_texture('#e9ddcb', 'stone'), .3)
        self.olive = matte(grain_texture('#878867', 'fabric'), .58)
        self.olive_dark = matte(grain_texture('#6e7252', 'fabric'), .57)
        self.linen = matte(grain_texture('#d7c7ad', 'fabric'), .59)
        self.terracotta = matte(grain_texture('#a86f50', 'fabric'), .51)
        self.black = matte('#242728', .36)
        self.appliance = matte('#111417', .11)
        self.nickel = mi.load_dict({'type': 'roughconductor', 'material': 'Al', 'alpha': .27})
        self.brass = mi.load_dict({'type': 'roughconductor', 'material': 'Au', 'alpha': .24})
        self.glass = mi.load_dict({'type': 'thindielectric', 'int_ior': 1.47})

    def add(self, name, shape):
        self.parts[f'{name}_{len(self.parts):04d}'] = shape

    def box(self, name, lo, hi, bsdf, bevel=0, rotation=None):
        lo, hi = np.array(lo, dtype=float), np.array(hi, dtype=float)
        assert np.all(hi > lo), (name, lo, hi)
        if bevel or rotation is not None:
            shape = rounded_box(name, lo, hi, bevel, rotation)
            shape.set_bsdf(bsdf)
        else:
            shape = {'type': 'cube', 'to_world': T().translate((hi + lo) / 2).scale((hi - lo) / 2),
                     'bsdf': bsdf}
        self.add(name, shape)

    def quad(self, name, corners, bsdf):
        shape = mesh(name, corners, [(0, 1, 2), (0, 2, 3)], uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        shape.set_bsdf(bsdf)
        self.add(name, shape)

    def tube(self, name, p0, p1, radius, bsdf):
        self.add(name, {'type': 'cylinder', 'p0': p0, 'p1': p1, 'radius': radius, 'bsdf': bsdf})

    def sphere(self, name, center, radius, bsdf, stretch=(1, 1, 1)):
        if stretch == (1, 1, 1):
            self.add(name, {'type': 'sphere', 'center': center, 'radius': radius, 'bsdf': bsdf})
            return
        vertices, normals, faces = [], [], []
        count = 24
        scale = radius * np.array(stretch)
        for theta in np.linspace(.0001, math.pi - .0001, 13):
            for phi in np.linspace(0, 2 * math.pi, count, endpoint=False):
                unit = np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])
                normal = unit / scale
                vertices.append(np.array(center) + unit * scale)
                normals.append(normal / np.linalg.norm(normal))
        for row in range(12):
            for i in range(count):
                a, b = row * count + i, row * count + (i + 1) % count
                faces.extend(((a, b + count, b), (a, a + count, b + count)))
        shape = mesh(name, vertices, faces, normals)
        shape.set_bsdf(bsdf)
        self.add(name, shape)

    def area(self, name, center, half_width, half_height, angle, radiance):
        self.add(name, {'type': 'rectangle', 'to_world': T().translate(center).rotate([1, 0, 0], angle)
                         .scale([half_width, half_height, 1]),
                         'emitter': {'type': 'area', 'radiance': {'type': 'rgb', 'value': radiance}}})

    def shell(self):
        w, d, h = self.width, self.depth, self.height
        self.box('slab', (0, 0, -.11), (w, d, -.001), self.kick)
        self.quad('herringbone_LVT', [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0)], matte(oak_floor(w, d), .31))
        d2 = self.data['entrance']
        a, b, top = [d2[key] / 1000 for key in ('start', 'end', 'height')]
        entry_thickness = .160  # B01 partition 3/1, APT-001 revision 9.
        self.box('entry_jamb_media', (-entry_thickness, 0, 0), (0, a, h), self.wall)
        self.box('entry_jamb_kitchen', (-entry_thickness, b, 0), (0, d, h), self.wall)
        self.box('entry_lintel', (-entry_thickness, a, top), (0, b, h), self.wall)
        self.box('entry_frame_media', (-.060, a, 0), (-.003, a + .007, top), self.kick)
        self.box('entry_frame_kitchen', (-.060, b - .007, 0), (-.003, b, top), self.kick)
        self.box('entry_frame_top', (-.060, a + .007, top - .007), (-.003, b - .007, top), self.kick)
        self.entry_leaf(a, b, top)
        if self.overview:
            self.box('cut_sofa_wall', (0, d, -.11), (w + .145, d + .12, .12), self.wall)
            self.box('media_wall', (0, -.12, -.11), (w, 0, h), self.wall)
        else:
            self.box('sofa_wall', (0, d, 0), (w + .145, d + .13, h), self.wall)
            self.box('ceiling', (-entry_thickness, 0, h), (w + .145, d + .13, h + .075), self.ceiling)
            for x, y in ((1.03, 1.5), (2.85, 1.22), (4.58, 1.48), (1.03, 2.55), (4.58, 2.58)):
                self.box('downlight_trim', (x - .044, y - .044, h - .010), (x + .044, y + .044, h), self.ceiling, .012)
                self.area('recessed_lamp', (x, y, h - .0105), .031, .031, 180, [8, 6.0, 4.4])

    def entry_leaf(self, a, b, top):
        self.box('D2_flush_leaf', (-.035, a + .007, .009), (-.003, b - .007, top - .007), self.ivory, .003)
        # Variant B: hinges at the media-side jamb (a), latch at the fridge-side jamb (b).
        handle_y = b - .093
        self.tube('D2_handle_stem', (-.001, handle_y, 1.03), (.039, handle_y, 1.03), .010, self.brass)
        self.tube('D2_handle', (.039, handle_y, 1.03), (.039, handle_y - .110, 1.03), .009, self.brass)

    def terrace(self):
        o1 = self.data['terrace']
        a, mid, b, z0, z1 = [o1[key] / 1000 for key in ('start', 'split', 'end', 'sketchSill', 'assumedTop')]
        w, d, h = self.width, self.depth, self.height
        left_width = b - mid
        hinge = np.array([w, b])
        # For the observer facing +X from the room, +Y is left. Rotate the closed
        # vector (0, -width) 90 degrees inward about this left end jamb.
        tip = hinge + np.array([-left_width, 0])
        assert np.allclose(hinge, [5.710, 2.200]) and np.allclose(tip, [4.910, 2.200])
        wall_height = .25 if self.overview else h
        self.box('O1_pier_media_side', (w, 0, -.11), (w + .145, a, wall_height), self.wall)
        self.box('O1_pier_desk_side', (w, b, -.11), (w + .145, d, wall_height), self.wall)
        if not self.overview:
            self.box('O1_lintel', (w, a, z1), (w + .145, b, h), self.wall)
        self.box('O1_threshold', (w - .008, a, -.03), (w + .145, b, z0), self.stone)
        for y0, y1 in ((a, a + .036), (b - .036, b)):
            self.box('O1_outer_jamb', (w, y0, z0), (w + .069, y1, z1), self.black, .004)
        for low, high in ((z0, z0 + .031), (z1 - .036, z1)):
            self.box('O1_outer_crossrail', (w, a, low), (w + .069, b, high), self.black, .004)

        # Right leaf in its closed plane. The central profile belongs to this leaf.
        zlo, zhi = z0 + .032, z1 - .039
        r0, r1 = a + .037, mid
        for y0, y1 in ((r0, r0 + .039), (r1 - .044, r1)):
            self.box('O1_right_stile', (w + .008, y0, zlo), (w + .053, y1, zhi), self.black, .004)
        for zz in (zlo, zhi - .046):
            self.box('O1_right_rail', (w + .008, r0, zz), (w + .053, r1, zz + .046), self.black, .004)
        self.quad('O1_right_glazing', [(w + .030, r0 + .039, zlo + .046), (w + .030, r1 - .044, zlo + .046),
                                       (w + .030, r1 - .044, zhi - .046), (w + .030, r0 + .039, zhi - .046)], self.glass)

        # Left leaf on a single hinge axis at Y=2200, open toward decreasing X.
        x0, x1 = tip[0], hinge[0]
        ylo, yhi = b - .027, b + .014
        for xx0, xx1 in ((x0, x0 + .049), (x1 - .047, x1)):
            self.box('O1_left_open_stile', (xx0, ylo, zlo), (xx1, yhi, zhi), self.black, .004)
        for zz in (zlo, zhi - .046):
            self.box('O1_left_open_rail', (x0, ylo, zz), (x1, yhi, zz + .046), self.black, .004)
        self.quad('O1_left_open_glazing', [(x0 + .049, b, zlo + .046), (x1 - .047, b, zlo + .046),
                                           (x1 - .047, b, zhi - .046), (x0 + .049, b, zhi - .046)], self.glass)
        for z in (.36, 1.35, 2.11):
            self.tube('O1_left_hinge', (w - .012, b - .013, z), (w - .012, b - .013, z + .054), .009, self.black)
        self.tube('O1_handle_axle', (x0 + .025, ylo - .033, 1.10), (x0 + .025, yhi + .026, 1.10), .009, self.black)
        self.tube('O1_open_handle', (x0 + .025, ylo - .034, 1.01), (x0 + .025, ylo - .034, 1.105), .009, self.black)
        if not self.overview:
            for index in range(4):
                z = z1 + .018 + index * .043
                self.box('linen_roman_fold', (w - .080 - index * .004, a - .017, z),
                         (w - .009, b + .017, z + .056), self.linen, .021)

        if not self.overview:
            self.exterior(a, b)

    def exterior(self, a, b):
        w = self.width
        stone = matte('#c0b7a4', .5)
        self.box('terrace_visible_floor', (w + .145, a - .27, -.08), (w + 1.9, b + .48, .015), stone)
        for z in (.12, 1.02):
            self.tube('terrace_rail', (w + 1.84, a - .26, z), (w + 1.84, b + .45, z), .016, self.black)
        for y in np.linspace(a - .25, b + .45, 15):
            self.tube('terrace_baluster', (w + 1.84, y, .016), (w + 1.84, y, 1.02), .009, self.black)
        rng = np.random.default_rng(46)
        greens = [matte(color, .65) for color in ('#708854', '#83936b', '#a1ae78', '#909f63', '#6d7e55')]
        for cx, cy, cz in ((8.0, 5.7, 1.65), (8.8, 6.1, 2.54), (9.0, 7.25, 1.45), (10, 7.9, 3.1), (10.6, 8.6, 2.3)):
            for _ in range(78):
                dx, dy, dz = rng.normal(0, .48, 3)
                self.sphere('distant_foliage', (cx + dx, cy + dy, cz + dz), rng.uniform(.065, .18),
                            greens[rng.integers(len(greens))])

    def kitchen(self):
        front_depth = .021
        self.box('entry_run_continuous_plinth', (.038, 1.730, 0), (.558, 3.483, .074), self.kick)
        self.box('sofa_run_continuous_plinth', (.558, 2.942, 0), (1.800, 3.483, .074), self.kick)
        for name in ('corner', 'prep', 'hob', 'pullout', 'sink', 'dishwasher'):
            x0, y0, x1, y1 = self.rect[name]
            along_entry = name in ('sink', 'dishwasher')
            self.box('cabinet_shell', (x0 + .001, y0 + (.020 if not along_entry else .001), .074),
                     (x1 - (front_depth if along_entry else .001), y1 - .001, .832), self.ivory)
            if along_entry:
                self.box(name + '_facade', (x1 - front_depth, y0 + .002, .076), (x1, y1 - .002, .817), self.ivory, .0025)
                self.box('recessed_groove', (x1 - .016, y0 + .009, .819), (x1 - .003, y1 - .009, .831), self.kick)
            elif name != 'corner':
                levels = [.077, .822] if name == 'pullout' else [.077, .357, .611, .822]
                for za, zb in zip(levels, levels[1:]):
                    self.box(name + '_drawer', (x0 + .002, y0, za + .0025), (x1 - .002, y0 + front_depth, zb - .0025), self.ivory, .0025)
            if name != 'sink':
                self.box('stone_counter', (x0, y0, .833), (x1, y1, .860), self.stone, .002)
        self.sink()
        self.hob()

        self.fridge()
        x0, y0, x1, y1 = self.rect['oven']
        self.box('600_oven_tower', (x0, y0 + .028, .068), (x1, y1, 2.400), self.ivory)
        self.box('tower_plinth', (x0 + .004, y0 + .045, 0), (x1 - .004, y1, .070), self.kick)
        for za, zb in ((.072, .661), (1.701, 2.400)):
            self.box('tower_drawer_or_door', (x0 + .002, y0, za), (x1 - .002, y0 + .029, zb), self.ivory, .003)
        for za, zb in ((.665, 1.255), (1.260, 1.697)):
            self.box('oven_microwave_black_glass', (x0 + .003, y0 + .002, za),
                     (x1 - .003, y0 + .028, zb), self.appliance, .005)
            self.box('appliance_door_inset', (x0 + .052, y0 + .001, za + .071),
                     (x1 - .051, y0 + .004, zb - .093), matte('#222a2d', .18), .003)
            self.tube('oven_handle', (x0 + .075, y0 + .008, zb - .079), (x1 - .075, y0 + .008, zb - .079), .0075, self.nickel)
            self.box('oven_control_display', (x0 + .239, y0 + .001, zb - .038),
                     (x0 + .365, y0 + .003, zb - .019), matte('#4b5149', .28), .001)

        self.box('entry_stone_splashback', (.002, 1.731, .861), (.023, 3.500, 1.466), self.backsplash, .001)
        self.box('sofa_wall_stone_splashback', (.020, 3.478, .861), (1.799, 3.500, 1.466), self.backsplash, .001)
        for y0, y1 in ((1.73, 2.33), (2.33, 2.90), (2.90, 3.17)):
            self.box('entry_wall_upper_door', (0, y0 + .002, 1.468), (.325, y1 - .002, 2.40), self.ivory, .003)
        if not self.overview:
            for x0, x1 in ((0, .600), (.600, 1.10), (1.10, 1.60), (1.60, 1.80)):
                self.box('sofa_wall_upper_door', (x0 + .002, 3.169, 1.468), (x1 - .002, 3.499, 2.40), self.ivory, .003)
            self.area('backsplash_warm_strip', (.95, 3.25, 1.466), .83, .010, 180, [18, 12.2, 7.5])
        for y in (2.04, 2.58, 2.96):
            self.area('sink_strip_glow', (.28, y, 1.467), .010, .15, 180, [14, 9.7, 6.3])

    def fridge(self):
        x0, y0, x1, y1 = self.rect['fridge']
        self.box('600x600_fridge_case', (x0, y0, .068), (x1 - .020, y1, 2.400), self.ivory)
        self.box('fridge_plinth', (x0, y0 + .004, 0), (x1 - .041, y1 - .004, .069), self.kick)
        for za, zb in ((.070, .722), (.727, 1.934), (1.939, 2.400)):
            self.box('integrated_fridge_panel', (x1 - .020, y0 + .002, za), (x1, y1 - .002, zb), self.ivory, .003)

    def sink(self):
        x0, y0, x1, y1 = self.rect['sink']
        sx0, sy0, sx1, sy1 = .123, y0 + .079, .503, y1 - .082
        for a, b, c, d in ((x0, y0, sx0, y1), (sx1, y0, x1, y1), (sx0, y0, sx1, sy0), (sx0, sy1, sx1, y1)):
            self.box('cut_counter_around_sink', (a, b, .833), (c, d, .860), self.stone, .0015)
        basin = matte('#6c6358', .25)
        self.box('sink_basin_inset', (sx0, sy0, .824), (sx1, sy1, .833), basin, .007)
        cy = (sy0 + sy1) / 2
        self.tube('faucet_base', (.075, cy, .860), (.075, cy, 1.098), .014, self.brass)
        points = [(.158 - .083 * math.cos(t), cy, 1.098 + .083 * math.sin(t)) for t in np.linspace(0, math.pi, 15)]
        for a, b in zip(points, points[1:]):
            self.tube('faucet_arc', a, b, .011, self.brass)
            self.sphere('faucet_arc_join', b, .011, self.brass)
        self.tube('faucet_spout', points[-1], (.241, cy, 1.063), .010, self.brass)

    def hob(self):
        x0, y0, x1, y1 = self.rect['hob']
        self.box('hob', (x0 + .015, y0 + .059, .860), (x1 - .015, y1 - .053, .867), self.appliance, .003)
        ring = matte('#5a6060', .5)
        for cx in (x0 + .143, x1 - .143):
            for cy in (y0 + .179, y1 - .162):
                points = [(cx + .072 * math.cos(t), cy + .072 * math.sin(t), .8676) for t in np.linspace(0, 2 * math.pi, 25)]
                for a, b in zip(points, points[1:]):
                    self.tube('hob_indicator_ring', a, b, .00075, ring)

    def sofa(self):
        x0, y0, x1, y1 = self.rect['sofa']
        self.box('sofa_recessed_base', (x0 + .045, y0 + .044, .018), (x1 - .045, y1 - .025, .112), self.kick, .024)
        self.box('Domo_seat_base', (x0, y0, .103), (x1, y1, .377), self.olive, .043)
        self.box('Domo_back', (x0, y1 - .239, .355), (x1, y1, .940), self.olive, .054)
        for x in (x0, x1 - .155):
            self.box('Domo_narrow_arm', (x, y0 + .025, .363), (x + .155, y1 - .184, .684), self.olive, .050)
        mid = (x0 + x1) / 2
        for a, b in ((x0 + .155, mid - .006), (mid + .006, x1 - .155)):
            self.box('Domo_seat_cushion', (a, y0 + .010, .355), (b, y1 - .194, .476), self.olive, .043)
            self.box('Domo_back_cushion', (a + .013, y1 - .371, .438), (b - .013, y1 - .202, .917), self.olive, .062)
        for cx, cz, color, angle in ((x0 + .425, .700, self.olive_dark, -.19), (x1 - .445, .663, self.linen, .17)):
            c = np.array([cx, y1 - .470, cz])
            cosine, sine = math.cos(angle), math.sin(angle)
            rotate = np.array([[cosine, 0, sine], [0, 1, 0], [-sine, 0, cosine]])
            self.box('sofa_throw_pillow', c - [.207, .084, .174], c + [.207, .084, .174], color, .079, (rotate, c))
        if not self.overview:
            self.sofa_art()

    def sofa_art(self):
        self.box('slim_oak_art_frame', (2.754, 3.466, 1.384), (4.186, 3.5, 2.102), self.wood, .004)
        self.quad('wall_art_canvas', [(2.774, 3.464, 1.403), (4.166, 3.464, 1.403),
                                      (4.166, 3.464, 2.083), (2.774, 3.464, 2.083)],
                  matte(landscape_texture(artwork=True), .60))

    def table_and_desk(self):
        self.dining()
        self.desk()

    def dining(self):
        self.dining_table(self.rect['table'])
        for name in ('chair-1', 'chair-2'):
            self.dining_chair(self.rect[name])

    def dining_table(self, rect, turned=False):
        x0, y0, x1, y1 = rect
        self.box('1400x800_stone_tabletop', (x0, y0, .710), (x1, y1, .750), self.stone, .015)
        along, across = (.075, .127), (.055, .107)
        x_offsets, y_offsets = (across, along) if turned else (along, across)
        for x in (x0 + x_offsets[0], x1 - x_offsets[1]):
            for y in (y0 + y_offsets[0], y1 - y_offsets[1]):
                self.box('table_oak_leg', (x, y, 0), (x + .052, y + .052, .716), self.wood, .008)
        self.vase(((x0 + x1) / 2, (y0 + y1) / 2, .75))

    def dining_chair(self, rect, facing_x=False):
        x0, y0, x1, y1 = rect

        def point(x, y, z):
            # Parked chairs are square and bilaterally symmetric.
            return (x0 + y - y0, y0 + x - x0, z) if facing_x else (x, y, z)

        for x in (x0 + .058, x1 - .058):
            for y in (y0 + .059, y1 - .059):
                self.tube('chair_oak_leg', point(x, y, .007),
                          point(x, (y + (y0 + y1) / 2) / 2, .444), .015, self.wood)
        self.box('chair_seat', point(x0, y0 + .025, .416), point(x1, y1, .481), self.terracotta, .029)
        for x in (x0 + .059, x1 - .059):
            self.tube('chair_back_support', point(x, y0 + .066, .440),
                      point(x, y0 + .035, .750), .015, self.wood)
        self.box('chair_curved_back_pad', point(x0, y0, .629), point(x1, y0 + .083, .850), self.terracotta, .039)

    def desk(self):
        x0, y0, x1, y1 = self.rect['desk']
        self.box('1200x600_desk_surface', (x0, y0, .716), (x1, y1, .750), self.wood, .007)
        for x in (x0 + .008, x1 - .031):
            self.box('desk_panel_leg', (x, y0 + .042, 0), (x + .023, y1, .716), self.ivory, .003)
        self.desk_accessories()
        if not self.overview:
            self.box('desk_overhead_oak_back', (x0, 3.475, 1.478), (x1, 3.5, 2.40), self.wood)
            for x in (x0, (x0 + x1) / 2 - .010, x1 - .020):
                self.box('desk_open_niche_side', (x, 3.171, 1.478), (x + .020, 3.475, 2.40), self.wood, .002)
            for z in (1.478, 1.755, 2.016):
                self.box('desk_open_shelf', (x0, 3.171, z), (x1, 3.476, z + .020), self.wood, .002)
            for a, b in ((x0 + .002, 5.098), (5.102, x1 - .002)):
                self.box('desk_cream_upper_door', (a, 3.155, 2.038), (b, 3.5, 2.400), self.ivory, .003)
            for i, color in enumerate(('#c2ac92', '#d4c6ae', '#999987', '#e0d4bd', '#ae8f73')):
                x = 5.245 + i * .052
                self.box('work_shelf_book', (x, 3.252, 1.775), (x + .034, 3.442, 1.944 + .013 * (i % 3)), matte(color, .53), .002)
            self.area('desk_warm_strip', (5.10, 3.273, 1.477), .535, .008, 180, [12.5, 8.7, 5.4])

    def desk_accessories(self, laptop_x=5.055, lamp_x=4.657):
        self.box('laptop_base', (laptop_x - .154, 3.079, .750), (laptop_x + .153, 3.304, .763),
                 self.appliance, .006)
        c = np.array([laptop_x, 3.293, .858])
        angle = -.15
        matrix = np.array([[1, 0, 0], [0, math.cos(angle), -math.sin(angle)], [0, math.sin(angle), math.cos(angle)]])
        self.box('laptop_display', c - [.153, .006, .098], c + [.153, .006, .098],
                 self.appliance, .005, (matrix, c))
        self.tube('desk_lamp_base', (lamp_x, 3.278, .750), (lamp_x, 3.278, .771), .075, self.brass)
        self.tube('desk_lamp_stem', (lamp_x, 3.278, .770), (lamp_x, 3.278, 1.07), .009, self.brass)
        self.sphere('desk_lamp_shade', (lamp_x, 3.278, 1.077), .111, self.brass, (1, 1, .42))

    def vase(self, center):
        x, y, z = center
        glaze = matte('#a29c82', .23)
        profile = [(0, .047), (.018, .061), (.063, .075), (.110, .067), (.153, .039), (.194, .026), (.201, .031)]
        points, faces = [], []
        count = 28
        for height, radius in profile:
            points.extend((x + radius * math.cos(t), y + radius * math.sin(t), z + height)
                          for t in np.linspace(0, 2 * math.pi, count, endpoint=False))
        for row in range(len(profile) - 1):
            for i in range(count):
                a, b = row * count + i, row * count + (i + 1) % count
                faces.extend(((a, b, b + count), (a, b + count, a + count)))
        shape = mesh('ceramic_vase', points, faces)
        shape.set_bsdf(glaze)
        self.add('ceramic_vase', shape)
        self.tube('vase_opening', (x, y, z + .17), (x, y, z + .194), .024, self.kick)
        stem = matte('#5d6049', .55)
        leaves = matte('#929371', .48)
        for dx, dy, dz in ((-.125, .04, .39), (.046, -.051, .49), (.156, .041, .43)):
            self.tube('branch', (x, y, z + .188), (x + dx, y + dy, z + dz), .0023, stem)
            for i in range(4):
                ratio = .41 + i * .16
                self.sphere('small_leaf', (x + dx * ratio + (-1) ** i * .014, y + dy * ratio, z + .188 + (dz - .188) * ratio),
                            .021, leaves, (1.4, .55, .38))

    def media(self):
        x0, y0, x1, y1 = self.rect['media']
        self.box('media_recessed_plinth', (x0 + .045, y0 + .02, .01), (x1 - .045, y1 - .046, .091), self.kick)
        for i in range(5):
            a = x0 + i * (x1 - x0) / 5
            self.box('media_front', (a + .002, y0, .091), (a + .558, y1, .517), self.ivory, .003)
        self.box('media_oak_top', (x0, y0, .517), (x1, y1, .540), self.wood, .004)
        self.box('ALR_screen', (2.351, .009, .851), (4.589, .035, 2.120), self.black, .004)
        self.quad('landscape_on_screen', [(4.577, .037, .863), (2.363, .037, .863), (2.363, .037, 2.108),
                                          (4.577, .037, 2.108)], matte(landscape_texture(), .26))
        self.box('UST_projector', (3.222, .128, .540), (3.718, .428, .646), self.appliance, .015)
        x0, y0, x1, y1 = self.rect['books']
        self.box('bookcase_back', (x0, y0, 0), (x1, y0 + .023, 2.4), self.wood)
        for x in (x0, x1 - .025):
            self.box('bookcase_upright', (x, y0, 0), (x + .025, y1, 2.4), self.wood, .003)
        colors = [matte(c, .55) for c in ('#d7c7a9', '#a79e83', '#686a59', '#c2ac91')]
        for level, z in enumerate((.470, .855, 1.240, 1.620, 2.001, 2.376)):
            self.box('bookcase_shelf', (x0, y0, z), (x1, y1, z + .024), self.wood, .003)
            if level == 5:
                continue
            for i in range(5):
                xx = x0 + .061 + i * .053 + (level % 2) * .144
                self.box('shelf_book', (xx, .056, z + .024), (xx + .038, .222, z + .195 + i % 3 * .032), colors[i % len(colors)], .003)
        self.box('bookcase_lower_door', (x0 + .027, .027, .065), (x1 - .027, y1, .467), self.ivory, .004)

    def scene(self, width, height, camera=None):
        self.shell()
        self.terrace()
        self.kitchen()
        self.sofa()
        self.table_and_desk()
        if self.overview:
            self.media()
        else:
            self.area('broad_fill', (2.85, -5.2, 1.69), 3.3, 1.45, -90, [7.0, 6.65, 6.13])
        self.add('sunlight', {'type': 'directional', 'direction': [-.80, .28, -.52],
                               'irradiance': {'type': 'rgb', 'value': [2.05, 1.84, 1.56]}})
        self.add('daylight_sky', {'type': 'constant', 'radiance': {'type': 'rgb', 'value': [.64, .68, .72]}})
        if camera is not None:
            origin, target, fov = camera
        elif self.overview:
            origin, target, fov = [9.9, 7.35, 7.75], [2.83, 1.78, .64], 54
        else:
            origin, target, fov = [2.855, -4.50, 1.78], [2.855, 2.00, 1.20], 63
        return mi.load_dict({
            'type': 'scene',
            'integrator': {'type': 'path', 'max_depth': 8, 'rr_depth': 4},
            'sensor': {'type': 'perspective', 'fov': fov, 'fov_axis': 'x',
                       'to_world': T().look_at(origin=origin, target=target, up=[0, 0, 1]),
                       'film': {'type': 'hdrfilm', 'width': width, 'height': height, 'rfilter': {'type': 'gaussian'}}},
            **self.parts,
        })


def audit(data):
    objects = {item['id']: item['rect'] for item in data['furniture']}
    assert (data['room']['width'], data['room']['depth']) == (5710, 3500)
    assert objects['fridge'] == [0, 1130, 600, 1730]
    assert objects['dishwasher'] == [0, 1730, 600, 2330]
    assert objects['oven'] == [1800, 2900, 2400, 3500]
    assert objects['sofa'] == [2485, 2300, 4455, 3500]
    assert objects['table'] == [2770, 1500, 4170, 2300]
    o1 = data['terrace']
    assert o1['end'] - o1['start'] == 1600 and o1['end'] - o1['split'] == 800
    assert data['room']['width'] - 800 > objects['sofa'][2]


def write_pfm(path, image):
    height, width, _ = image.shape
    with path.open('wb') as stream:
        stream.write(f'PF\n{width} {height}\n-1.0\n'.encode('ascii'))
        np.asarray(image[::-1], dtype='<f4').tofile(stream)


def read_pfm(path):
    with path.open('rb') as stream:
        assert stream.readline().strip() == b'PF'
        width, height = map(int, stream.readline().split())
        scale = float(stream.readline())
        data = np.fromfile(stream, dtype='<f4' if scale < 0 else '>f4')
    return data.reshape(height, width, 3)[::-1] * abs(scale)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--preview', action='store_true')
    cli.add_argument('--overview', action='store_true')
    cli.add_argument('--samples', type=int)
    cli.add_argument('--exposure', type=float, default=1.0)
    cli.add_argument('--hdr-input', type=Path, help='Develop a saved linear render without tracing again')
    options = cli.parse_args()
    data = json.loads((ROOT / 'tmp/b01-o1-two-sashes.json').read_text(encoding='utf-8'))
    audit(data)
    if options.hdr_input:
        radiance = read_pfm(options.hdr_input)
    else:
        builder = RoomRender(data, options.overview)
        if options.overview:
            dimensions = (960, 600) if options.preview else (1920, 1200)
        else:
            dimensions = (960, 450) if options.preview else (1920, 900)
        scene = builder.scene(*dimensions)
        glazing = [name for name in builder.parts if 'glazing' in name]
        assert len(glazing) == 2 and any('left_open' in name for name in glazing)
        samples = options.samples or (16 if options.preview else 144)
        print(f'Rendering {dimensions[0]} x {dimensions[1]}, {samples} spp, {len(builder.parts)} objects', flush=True)
        radiance = np.asarray(mi.render(scene, spp=samples, seed=19))
        if not options.preview:
            write_pfm(ROOT / ('tmp/b01-overview-audited.pfm' if options.overview else 'tmp/b01-room-audited.pfm'), radiance)
    x = np.maximum(radiance, 0) * options.exposure
    # Filmic display mapping preserves light marble detail near the window.
    display = np.clip(x * (2.51 * x + .03) / (x * (2.43 * x + .59) + .14), 0, 1)
    display = np.where(display <= .0031308, display * 12.92, 1.055 * display ** (1 / 2.4) - .055)
    if options.preview:
        output = ROOT / ('tmp/b01-preview-overview.png' if options.overview else 'tmp/b01-preview-room.png')
    else:
        name = 'B01_объём_с_открытой_створкой_v3.png' if options.overview else 'B01_рендер_открытая_левая_створка_v2.png'
        output = ROOT / 'output/visualizations' / name
    Image.fromarray(np.round(display * 255).astype(np.uint8)).save(output)
    print(f'PASS: {output.name}', flush=True)


if __name__ == '__main__':
    main()
