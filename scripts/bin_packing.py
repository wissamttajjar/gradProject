import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np

# === Fabric Configuration ===
FABRIC_WIDTH = 300  # in cm
FABRIC_HEIGHT = 600  # in cm
SET_COUNT = 22  # Number of full garments you want to produce

# === Garment Part Definitions ===
garment_parts = [
    {"name": "front", "width": 50.77, "height": 51.28, "quantity": SET_COUNT},
    {"name": "back", "width": 50.77, "height": 51.28, "quantity": SET_COUNT},
    {"name": "sleeve", "width": 23.98, "height": 42.45, "quantity": SET_COUNT * 2}
]


def point_in_polygon(point, polygon):
    """Check if a point is inside a polygon"""
    path = Path(polygon)
    return path.contains_point(point)


def polygons_overlap(poly_a, poly_b):
    """Check if two polygons overlap"""
    path_a = Path(poly_a)
    path_b = Path(poly_b)

    # Check if any vertex of A is inside B
    for point in poly_a:
        if path_b.contains_point(point):
            return True

    # Check if any vertex of B is inside A
    for point in poly_b:
        if path_a.contains_point(point):
            return True

    # Check edge intersections (simplified)
    # for i in range(len(poly_a)):
    #     for j in range(len(poly_b)):
    #         if line_intersect(poly_a[i - 1], poly_a[i], poly_b[j - 1], poly_b[j]):
    #             return True
    return False


def line_intersect(a1, a2, b1, b2):
    """Check if line segments a1-a2 and b1-b2 intersect"""
    # Implementation of line segment intersection test
    # (Can use cross-product method)
    pass


# === Generate All Parts to Place ===
def expand_parts(part_defs):
    expanded = []
    for part in part_defs:
        for i in range(part["quantity"]):
            expanded.append({
                "name": part["name"],
                "width": part["width"],
                "height": part["height"],
                "instance": i + 1  # For labeling
            })
    return expanded


# === Placement Helpers ===
def fits(part, rect):
    return part["width"] <= rect["width"] and part["height"] <= rect["height"]


def split_space(rect, part):
    new_rects = []
    rem_w = rect["width"] - part["width"]
    rem_h = rect["height"] - part["height"]

    if rem_w > 0:
        new_rects.append({
            "x": rect["x"] + part["width"],
            "y": rect["y"],
            "width": rem_w,
            "height": part["height"]
        })

    if rem_h > 0:
        new_rects.append({
            "x": rect["x"],
            "y": rect["y"] + part["height"],
            "width": rect["width"],
            "height": rem_h
        })

    return new_rects


def check_overlap(part, placed_rects):
    for placed in placed_rects:
        if not (
                part["x"] + part["width"] <= placed["x"] or
                part["x"] >= placed["x"] + placed["width"] or
                part["y"] + part["height"] <= placed["y"] or
                part["y"] >= placed["y"] + placed["height"]
        ):
            return True  # Overlaps
    return False


def place_parts_on_fabric(fabric_w, fabric_h, parts):
    placed_parts = []
    free_rects = [{"x": 0, "y": 0, "width": fabric_w, "height": fabric_h}]

    # Sort parts by area in descending order (largest first)
    parts_sorted = sorted(parts, key=lambda p: p["width"] * p["height"], reverse=True)

    for part in parts_sorted:
        # Sort free rectangles by best fit (smallest remaining area after placement)
        free_rects.sort(key=lambda r: (r["width"] - part["width"]) * (r["height"] - part["height"]))

        placed = False
        for i, rect in enumerate(free_rects):
            # Try both orientations (original and rotated)
            for width, height in [(part["width"], part["height"]), (part["height"], part["width"])]:
                if width <= rect["width"] and height <= rect["height"]:
                    candidate = {
                        "name": part["name"],
                        "x": rect["x"],
                        "y": rect["y"],
                        "width": width,
                        "height": height,
                        "instance": part["instance"]
                    }

                    if check_overlap(candidate, placed_parts):
                        continue

                    # Place the part
                    placed_parts.append(candidate)

                    # Split the remaining space (maximize the larger dimension)
                    new_rects = []
                    rem_w = rect["width"] - width
                    rem_h = rect["height"] - height

                    if rem_w >= rem_h:
                        if rem_w > 0:
                            new_rects.append({
                                "x": rect["x"] + width,
                                "y": rect["y"],
                                "width": rem_w,
                                "height": rect["height"]
                            })
                        if rem_h > 0:
                            new_rects.append({
                                "x": rect["x"],
                                "y": rect["y"] + height,
                                "width": width,
                                "height": rem_h
                            })
                    else:
                        if rem_h > 0:
                            new_rects.append({
                                "x": rect["x"],
                                "y": rect["y"] + height,
                                "width": rect["width"],
                                "height": rem_h
                            })
                        if rem_w > 0:
                            new_rects.append({
                                "x": rect["x"] + width,
                                "y": rect["y"],
                                "width": rem_w,
                                "height": height
                            })

                    free_rects.pop(i)
                    free_rects.extend(new_rects)
                    placed = True
                    break
            if placed:
                break

        if not placed:
            return None  # Packing failed

    return placed_parts


# === Visualization ===
def visualize_parts(placed_parts, fabric_w, fabric_h):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, fabric_w)
    ax.set_ylim(0, fabric_h)
    ax.set_title(f"Fabric Layout for {SET_COUNT} Garments")
    ax.set_xlabel("Width (cm)")
    ax.set_ylabel("Height (cm)")

    colors = ['skyblue', 'salmon', 'lightgreen', 'plum', 'orange', 'lightgray']

    for i, part in enumerate(placed_parts):
        color = colors[i % len(colors)]
        ax.add_patch(plt.Rectangle(
            (part["x"], part["y"]),
            part["width"],
            part["height"],
            edgecolor='black',
            facecolor=color,
            alpha=0.8
        ))
        ax.text(
            part["x"] + part["width"] / 2,
            part["y"] + part["height"] / 2,
            f'{part["name"]}\n#{part["instance"]}',
            ha='center',
            va='center',
            fontsize=7
        )

    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# === Run the Packing ===
all_parts = expand_parts(garment_parts)
result = place_parts_on_fabric(FABRIC_WIDTH, FABRIC_HEIGHT, all_parts)

if result:
    print(f"✅ Successfully packed all {SET_COUNT} full garments into the fabric.")
    visualize_parts(result, FABRIC_WIDTH, FABRIC_HEIGHT)
else:
    print(f"❌ Not enough space to pack {SET_COUNT} full garments into the fabric.")
