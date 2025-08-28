#%%
import random
import os
import numpy as np

if "MPLCONFIGDIR" not in os.environ:
    os.environ["MPLCONFIGDIR"] = os.path.join(os.getcwd(), "mplconfig")
    os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely import affinity
from shapely.affinity import translate
from shapely.strtree import STRtree
from IPython.display import display, clear_output
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#%%
def crescent_outline():
    theta = np.linspace(0, 2 * np.pi, 50)
    outer = [(30 + 20 * np.cos(t), 30 + 20 * np.sin(t)) for t in theta]
    inner = [(30 + 12 * np.cos(t), 30 + 12 * np.sin(t)) for t in reversed(theta)]
    return outer + inner


#%%
import json
from shapely.geometry import Polygon

shape_path = os.environ.get(
    "C:/Users/wissam_T/Desktop/5th/graduation project/gradProject/grad_backend/storage/app/pattern-rules/rule_base_system.json",
    "./shape.json")
with open(shape_path, "r", encoding="utf-8") as f:
    config = json.load(f)

FABRIC_WIDTH = config["fabric_width"]
FABRIC_HEIGHT = config["fabric_height"]
NUM_PIECES = config["num_pieces"]

piece_shapes = []
for piece in config["pieces"]:
    x_coords = piece["x"]
    y_coords = piece["y"]
    if len(x_coords) != len(y_coords):
        raise ValueError(f"X/Y length mismatch in piece {piece['name']}")
    outline = list(zip(x_coords, y_coords))
    piece_shapes.append({"name": piece["name"], "outline": outline, "allow_rotation": True})

# --- توسيع القطع حسب التكرار (num_pieces) ---
expanded_pieces = []
for piece in piece_shapes:
    for i in range(NUM_PIECES):
        new_piece = piece.copy()
        new_piece["name"] = f"{piece['name']}_copy{i + 1}"
        expanded_pieces.append(new_piece)

piece_shapes = expanded_pieces

print("إجمالي عدد القطع بعد التوسيع:", len(piece_shapes))
for i, piece in enumerate(piece_shapes, 1):
    print(f"{i}: {piece['name']}")

# --- القماش ---
fabric_polygon = Polygon([
    (0, 0),
    (FABRIC_WIDTH, 0),
    (FABRIC_WIDTH, FABRIC_HEIGHT),
    (0, FABRIC_HEIGHT)
])

#%%

#%%
print(piece_shapes[0])


#%%
def pack_all_vertical(pieces, fabric_width, fabric_height, MARGIN=10.0):
    individual = []
    rotated_infos = []
    for piece in pieces:
        r = 90 if piece.get("allow_rotation", True) else 0
        poly = Polygon(piece["outline"])
        rot = affinity.rotate(poly, r, origin='centroid')
        minx, miny, maxx, maxy = rot.bounds
        w = maxx - minx
        h = maxy - miny
        rotated_infos.append((rot, r, w, h, minx, miny))

    order = sorted(range(len(rotated_infos)), key=lambda i: rotated_infos[i][3], reverse=True)

    x_cursor = 0.0
    y_cursor = 0.0
    col_width = 0.0

    placements = [None] * len(pieces)

    for idx in order:
        rot, r, w, h, minx, miny = rotated_infos[idx]

        if y_cursor + h > fabric_height + 1e-9:
            x_cursor += col_width + MARGIN
            y_cursor = 0.0
            col_width = 0.0

        if x_cursor + w > fabric_width + 1e-9:
            return []

        x_place = x_cursor - minx
        y_place = y_cursor - miny
        placements[idx] = (x_place, y_place, r)

        y_cursor += h + MARGIN
        col_width = max(col_width, w)

    for i in range(len(pieces)):
        individual.append(placements[i])

    return individual


#%%
from shapely.geometry import Polygon
from shapely import affinity


def pack_all_horizontal(pieces, fabric_width, fabric_height, MARGIN=10.0):
    individual = []
    rotated_infos = []
    for piece in pieces:
        r = 0 if piece.get("allow_rotation", True) else 0
        poly = Polygon(piece["outline"])
        rot = affinity.rotate(poly, r, origin='centroid')
        minx, miny, maxx, maxy = rot.bounds
        w = maxx - minx
        h = maxy - miny
        rotated_infos.append((rot, r, w, h, minx, miny))

    order = sorted(range(len(rotated_infos)), key=lambda i: rotated_infos[i][2], reverse=True)

    x_cursor = 0.0
    y_cursor = 0.0
    row_height = 0.0

    placements = [None] * len(pieces)

    for idx in order:
        rot, r, w, h, minx, miny = rotated_infos[idx]

        if x_cursor + w > fabric_width + 1e-9:
            y_cursor += row_height + MARGIN
            x_cursor = 0.0
            row_height = 0.0

        if y_cursor + h > fabric_height + 1e-9:
            return []

        x_place = x_cursor - minx
        y_place = y_cursor - miny
        placements[idx] = (x_place, y_place, r)

        x_cursor += w + MARGIN
        row_height = max(row_height, h)

    for i in range(len(pieces)):
        individual.append(placements[i])

    return individual


#%%
def used_area_of(individual, pieces):
    if not individual:
        return 0.0
    polys = []
    for (x, y, r), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        poly = affinity.rotate(poly, r, origin='centroid')
        poly = affinity.translate(poly, xoff=x, yoff=y)
        polys.append(poly)
    u = polys[0]
    for p in polys[1:]:
        u = u.union(p)
    return u.area


def best_axis_pack(pieces):
    fabric_width = FABRIC_WIDTH
    fabric_height = FABRIC_HEIGHT
    v = pack_all_vertical(pieces, fabric_width, fabric_height)
    h = pack_all_horizontal(pieces, fabric_width, fabric_height)

    area_v = used_area_of(v, pieces) if v else -1
    area_h = used_area_of(h, pieces) if h else -1

    if area_v >= area_h:
        return v
    else:
        return h


#%%
from shapely.geometry import Polygon
from shapely import affinity


def fitness_strict(individual, pieces, fabric_width=FABRIC_WIDTH, fabric_height=FABRIC_HEIGHT, margin=1):
    polys = []
    penalty = 0.0

    for (x, y, r), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        poly = affinity.rotate(poly, r, origin='centroid')
        poly = affinity.translate(poly, xoff=x, yoff=y)
        polys.append(poly)

        if not (0 <= poly.bounds[0] and poly.bounds[2] <= fabric_width and
                0 <= poly.bounds[1] and poly.bounds[3] <= fabric_height):
            penalty += 1e5

    for i, poly in enumerate(polys):
        for j, other in enumerate(polys):
            if i >= j:
                continue
            if poly.intersection(other).area > 0:
                penalty += 1e9

    total_area = sum(p.area for p in polys)
    return total_area - penalty


def repair_individual(individual, pieces, fabric_width=FABRIC_WIDTH, fabric_height=FABRIC_HEIGHT, margin=1):
    repaired = []
    polys = []

    for (x, y, r), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        poly = affinity.rotate(poly, r, origin='centroid')
        poly = affinity.translate(poly, xoff=x, yoff=y)

        if poly.bounds[0] < 0 or poly.bounds[2] > fabric_width or poly.bounds[1] < 0 or poly.bounds[3] > fabric_height:
            x = min(max(0, x), fabric_width - (poly.bounds[2] - poly.bounds[0]))
            y = min(max(0, y), fabric_height - (poly.bounds[3] - poly.bounds[1]))
            poly = affinity.translate(Polygon(piece["outline"]), xoff=x, yoff=y)

        valid = True
        for p in polys:
            if poly.intersection(p).area > 0:
                valid = False

                break

        if valid:
            polys.append(poly)
            repaired.append((x, y, r))

    return repaired


#%%
def tournament_selection(pop, pieces, k=3):
    selected = random.sample(pop, k)
    selected.sort(key=lambda ind: fitness_strict(ind, pieces, FABRIC_WIDTH, FABRIC_HEIGHT), reverse=True)
    return selected[0]


def uniform_crossover(p1, p2):
    return [g1 if random.random() < 0.5 else g2 for g1, g2 in zip(p1, p2)]


#%% md
#
#%%
def visualize_individual_with_title(individual, pieces, title):
    fig, ax = plt.subplots(figsize=(12, 8))
    x, y = fabric_polygon.exterior.xy
    ax.fill(x, y, 'lightgray', alpha=0.3)

    colors = plt.cm.Set3.colors
    for i, ((px, py, rot), piece) in enumerate(zip(individual, pieces)):
        poly = Polygon(piece["outline"])
        rotated = affinity.rotate(poly, rot, origin='centroid')
        translated = affinity.translate(rotated, xoff=px, yoff=py)
        x, y = translated.exterior.xy
        ax.fill(x, y, color=colors[i % len(colors)], alpha=0.8)
        cx, cy = translated.centroid.x, translated.centroid.y
        # ax.text(cx, cy, piece["name"], ha='center', va='center', fontsize=10, weight='bold')

    ax.set_xlim(0, FABRIC_WIDTH)
    ax.set_ylim(0, FABRIC_HEIGHT)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.title(title)
    plt.grid(True)
    plt.show()


#%%

def mutate(ind, mutation_rate=0.1):
    mutated = []
    for x, y, r in ind:
        if random.random() < mutation_rate:
            x += random.uniform(-20, 20)
        if random.random() < mutation_rate:
            y += random.uniform(-20, 20)
        if random.random() < mutation_rate:
            r = random.choice([0, 90])
        mutated.append((x, y, r))
    return mutated


def evolve(pop_size, generations, pieces):
    population = [best_axis_pack(pieces) for _ in range(pop_size)]
    best_ind = None
    best_score = float('-inf')
    fitness_history = []
    generation_layouts = []

    for gen in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1 = tournament_selection(population, pieces)
            p2 = tournament_selection(population, pieces)
            child = uniform_crossover(p1, p2)
            child = mutate(child)
            child = repair_individual(child, pieces, FABRIC_WIDTH, FABRIC_HEIGHT)
            if child:
                new_pop.append(child)

        if not new_pop:
            new_pop = population

        population = new_pop
        current_best = max(population, key=lambda ind: fitness_strict(ind, pieces, FABRIC_WIDTH, FABRIC_HEIGHT))
        current_score = fitness_strict(current_best, pieces, FABRIC_WIDTH, FABRIC_HEIGHT)

        if current_score > best_score:
            best_score = current_score
            best_ind = current_best

        fitness_history.append(current_score)
        generation_layouts.append((current_best, current_score))
        print(f"Generation {gen + 1}: Best Fitness = {current_score:.2f}")

    return best_ind, fitness_history, generation_layouts


#%%
pop_size = 50
generations = 70
best_individual, history, layouts = evolve(pop_size, generations, piece_shapes)


# plot_all_generations_in_grid(layouts, piece_shapes, cols=5)

#%%

def plot_best_individual_raw(individual, pieces, fabric_width, fabric_height):
    fig, ax = plt.subplots(figsize=(12, 8))

    fabric_polygon = Polygon([
        (0, 0), (fabric_width, 0),
        (fabric_width, fabric_height), (0, fabric_height)
    ])
    fx, fy = fabric_polygon.exterior.xy
    ax.fill(fx, fy, 'lightgray', alpha=0.3)

    colors = plt.cm.Set2.colors
    for (px, py, rot), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        rotated = affinity.rotate(poly, rot, origin='centroid')
        translated = affinity.translate(rotated, xoff=px, yoff=py)

        x, y = translated.exterior.xy
        ax.fill(x, y, color=colors[hash(piece["name"]) % len(colors)], alpha=0.85)
        cx, cy = translated.centroid.x, translated.centroid.y
        #ax.text(cx, cy, piece["name"], ha='center', va='center', fontsize=8, color='black')

    ax.set_xlim(0, fabric_width)
    ax.set_ylim(0, fabric_height)
    ax.set_aspect('equal')
    # plt.gca().invert_yaxis()
    ax.set_title("Placement from GA (Raw)", fontsize=14, weight='bold')
    ax.grid(True)
    plt.tight_layout()
    plt.show()


#%%
plot_best_individual_raw(best_individual, piece_shapes, FABRIC_WIDTH, FABRIC_HEIGHT)


#%%

#%%
def _has_overlap_with_margin(g, others, margin=2.0):
    for o in others:
        if g.buffer(margin / 2).intersects(o.buffer(margin / 2)):
            return True
    return False


def compact_to_corner_margin(polygons, fabric_width, fabric_height, step=1.0, margin=3.0, passes=50):
    for _ in range(passes):
        new_polys = []
        for i, p in enumerate(polygons):
            moved = True
            while moved:
                moved = False

                cand = translate(p, xoff=-step, yoff=0)
                if cand.bounds[0] >= 0 and not _has_overlap_with_margin(cand, polygons[:i] + polygons[i + 1:], margin):
                    p = cand
                    moved = True

                cand = translate(p, xoff=0, yoff=-step)
                if cand.bounds[1] >= 0 and not _has_overlap_with_margin(cand, polygons[:i] + polygons[i + 1:], margin):
                    p = cand
                    moved = True
            new_polys.append(p)
        polygons = new_polys
    return polygons


#%%
def plot_best_individual(individual, pieces, compact=False):
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon
    from shapely import affinity

    fabric_width = FABRIC_WIDTH
    fabric_height = FABRIC_HEIGHT

    fig, ax = plt.subplots(figsize=(12, 8))
    fabric_polygon = Polygon([(0, 0), (fabric_width, 0), (fabric_width, fabric_height), (0, fabric_height)])
    fx, fy = fabric_polygon.exterior.xy
    ax.fill(fx, fy, 'lightgray', alpha=0.3)

    polys = []
    for (px, py, rot), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        rotated = affinity.rotate(poly, rot, origin='centroid')
        translated = affinity.translate(rotated, xoff=px, yoff=py)
        polys.append(translated)

    if compact:
        polys = compact_to_corner_margin(polys, fabric_width, fabric_height, step=1.0, margin=3.0)

    colors = plt.cm.Set2.colors
    for i, p in enumerate(polys):
        x, y = p.exterior.xy
        ax.fill(x, y, color=colors[i % len(colors)], alpha=0.85)

    ax.set_xlim(0, fabric_width)
    ax.set_ylim(0, fabric_height)
    ax.set_aspect('equal')
    ax.set_title("Final Placement" + (" (compacted)" if compact else " (raw)"))
    ax.grid(True)
    plt.tight_layout()
    plt.show()


#%%
plot_best_individual(best_individual, piece_shapes, compact=False)

#%%
from shapely.geometry import Polygon
from shapely import affinity
import numpy as np


def build_polys(individual, pieces):
    polys = []
    for (px, py, rot), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        rotated = affinity.rotate(poly, rot, origin='centroid')
        translated = affinity.translate(rotated, xoff=px, yoff=py)
        polys.append(translated)
    return polys


def bbox_area(polys):
    minx, miny, maxx, maxy = polys[0].bounds
    for p in polys[1:]:
        x1, y1, x2, y2 = p.bounds
        minx, miny, maxx, maxy = min(minx, x1), min(miny, y1), max(maxx, x2), max(maxy, y2)
    return (maxx - minx) * (maxy - miny)


from shapely import affinity


def pack_scanline_safe(polys, W, H, margin=3, direction="horizontal"):
    packed = []
    x, y = margin, margin
    line_max = 0

    for p in polys:
        minx, miny, maxx, maxy = p.bounds
        w, h = maxx - minx, maxy - miny

        if direction == "horizontal":

            if x + w + margin > W:
                x = margin
                y += line_max + margin
                line_max = 0
            if y + h + margin > H:
                break
            q = affinity.translate(p, x - minx, y - miny)
            packed.append(q)
            x += w + margin
            line_max = max(line_max, h)

        elif direction == "vertical":
            if y + h + margin > H:
                y = margin
                x += line_max + margin
                line_max = 0
            if x + w + margin > W:
                break
            q = affinity.translate(p, x - minx, y - miny)
            packed.append(q)
            y += h + margin
            line_max = max(line_max, w)

    return packed


def multi_strategy_compact(polys, W, H, margin):
    def bbox_area(polys):
        if not polys:
            return float("inf")
        minx = min(p.bounds[0] for p in polys)
        miny = min(p.bounds[1] for p in polys)
        maxx = max(p.bounds[2] for p in polys)
        maxy = max(p.bounds[3] for p in polys)
        return (maxx - minx) * (maxy - miny)

    orderings = {
        "original": polys,
        "area_desc": sorted(polys, key=lambda p: p.area, reverse=True),
        "width_desc": sorted(polys, key=lambda p: p.bounds[2] - p.bounds[0], reverse=True),
        "height_desc": sorted(polys, key=lambda p: p.bounds[3] - p.bounds[1], reverse=True),
    }

    candidates = []
    for name, ordered in orderings.items():
        for direction in ["horizontal", "vertical"]:
            packed = pack_scanline_safe(ordered, W, H, margin=margin, direction=direction)
            bbox = bbox_area(packed)
            candidates.append((bbox, packed, f"{name}-{direction}"))

    best = min(candidates, key=lambda x: x[0])
    return best[1], best[2]


def individual_to_polys(individual, pieces):
    from shapely.geometry import Polygon
    from shapely import affinity

    polys = []
    for (px, py, rot), piece in zip(individual, pieces):
        poly = Polygon(piece["outline"])
        rotated = affinity.rotate(poly, rot, origin='centroid')
        translated = affinity.translate(rotated, xoff=px, yoff=py)
        polys.append(translated)
    return polys


#%%
def plot_polys(polys, W, H, title="Compacted Layout", save_path=None):
    fig, ax = plt.subplots(figsize=(12, 8))
    fabric_polygon = Polygon([(0, 0), (W, 0), (W, H), (0, H)])
    fx, fy = fabric_polygon.exterior.xy
    ax.fill(fx, fy, 'lightgray', alpha=0.3)

    colors = plt.cm.Set2.colors
    for i, p in enumerate(polys):
        x, y = p.exterior.xy
        ax.fill(x, y, color=colors[i % len(colors)], alpha=0.85)

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.grid(True)
    plt.tight_layout()

    if save_path:  # حفظ الصورة
        plt.savefig(save_path, dpi=300)
        print(f"✅ تم حفظ الصورة في {save_path}")

    plt.show()


#%%
polys = individual_to_polys(best_individual, piece_shapes)

compacted, strategy = multi_strategy_compact(polys, FABRIC_WIDTH, FABRIC_HEIGHT, margin=7)

plot_polys(compacted, FABRIC_WIDTH, FABRIC_HEIGHT,
           f"بعد الرص الذكي - {strategy}",
           save_path="layout.png")


#%%
def export_pieces(polygons, fabric_width, fabric_height,
                  csv_file="piece_coordinates.csv",
                  json_file="piece_coordinates.json", tol=1e-6):
    pieces_data = []
    with open(csv_file, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["piece_id", "x", "y"])

        for i, poly in enumerate(polygons):
            coords = list(poly.exterior.coords)
            centroid = poly.centroid.coords[0]

            for x, y in coords:
                writer.writerow([i, x, y])

            pieces_data.append({
                "piece_id": i,
                "coordinates": [{"x": float(x), "y": float(y)} for x, y in coords],
                "centroid": {"x": float(centroid[0]), "y": float(centroid[1])}
            })

    with open(json_file, "w", encoding="utf-8") as f_json:
        json.dump(pieces_data, f_json, ensure_ascii=False, indent=4)

    print(f"✅ الملفات تم حفظها: {csv_file}, {json_file}")

    # --- التحقق العددي ---
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, poly in enumerate(polygons):
        coords = [(p["x"], p["y"]) for p in data[i]["coordinates"]]
        poly_from_json = Polygon(coords)

        area_diff = abs(poly.area - poly_from_json.area)
        centroid_diff = poly.centroid.distance(poly_from_json.centroid)

        if area_diff > tol or centroid_diff > tol:
            raise ValueError(f"❌ خطأ بالتحقق في القطعة {i}: area_diff={area_diff}, centroid_diff={centroid_diff}")

    print("✅ التحقق العددي ناجح (المساحة والمركز متطابقين)")


#%%
export_pieces(compacted, FABRIC_WIDTH, FABRIC_HEIGHT)
