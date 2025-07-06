import numpy as np
import matplotlib.pyplot as plt
from shapely import affinity
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from descartes import PolygonPatch

# === Fabric Configuration ===
FABRIC_WIDTH = 300  # in cm
FABRIC_HEIGHT = 600  # in cm
SET_COUNT = 15  # Number of full garments you want to produce

# === Garment Part Definitions ===
garment_parts = [
    {
        "name": "front",
        "outline": [(0, 0), (50, 0), (45, 20), (40, 50), (0, 50)],
        "quantity": SET_COUNT,
        "allow_rotation": True
    },
    {
        "name": "back",
        "outline": [(0, 0), (50, 0), (45, 20), (40, 50), (0, 50)],
        "quantity": SET_COUNT,
        "allow_rotation": True
    },
    {
        "name": "sleeve",
        "outline": [(0, 0), (25, 0), (20, 40), (5, 40)],
        "quantity": SET_COUNT * 2,
        "allow_rotation": True
    }
]


# === Core Placement Engine ===
class FabricNester:
    def __init__(self, width, height):
        self.fabric = Polygon([(0, 0), (width, 0), (width, height), (0, height)])
        self.free_space = [self.fabric]
        self.placed_parts = []

    @staticmethod
    def translate_polygon(poly, translation):
        """Proper translation for Shapely polygons"""
        dx, dy = translation
        return affinity.translate(poly, xoff=dx, yoff=dy)

    def place_part(self, part):
        original_poly = Polygon(part["outline"])
        best_score = -np.inf
        best_placement = None

        rotations = self.generate_rotations(original_poly, part["allow_rotation"])

        for rotated_poly in rotations:
            for position in self.generate_positions(rotated_poly):
                # Corrected translation call
                translated_poly = self.translate_polygon(rotated_poly, position)

                if not self.check_fit(translated_poly):
                    continue

                score = self.score_placement(translated_poly)

                if score > best_score:
                    best_score = score
                    best_placement = translated_poly

        if best_placement:
            self.commit_placement(best_placement, part)
            return True
        return False

    def generate_rotations(self, poly, allow_rotation):
        rotations = [poly]
        if allow_rotation:
            for angle in [90, 180, 270]:
                rotated = self.rotate_polygon(poly, angle)
                rotations.append(rotated)
        return rotations

    def rotate_polygon(self, poly, angle):
        """Rotate polygon around its centroid"""
        centroid = np.array(poly.centroid.coords[0])
        points = np.array(poly.exterior.coords)

        # Rotation matrix
        theta = np.radians(angle)
        rot_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])

        # Apply rotation
        rotated = (points - centroid) @ rot_matrix + centroid
        return Polygon(rotated)

    def generate_positions(self, poly):
        """Generate candidate positions using NFP (No-Fit Polygon) approach"""
        # Simplified version - actual NFP would be more complex
        min_x, min_y, max_x, max_y = self.fabric.bounds
        part_width = poly.bounds[2] - poly.bounds[0]
        part_height = poly.bounds[3] - poly.bounds[1]

        step = max(part_width, part_height) / 2
        for x in np.arange(min_x, max_x - part_width, step):
            for y in np.arange(min_y, max_y - part_height, step):
                yield (x, y)

        # Add edge snapping positions
        if self.placed_parts:
            for placed in self.placed_parts:
                for point in placed.exterior.coords:
                    yield (point[0], point[1])

    def check_fit(self, poly):
        """Check if polygon fits in free space and doesn't collide"""
        # Check fabric bounds
        if not self.fabric.contains(poly):
            return False

        # Check collision with placed parts
        for placed in self.placed_parts:
            if poly.intersects(placed):
                return False

        return True

    def score_placement(self, poly):
        """Evaluate placement quality"""
        score = 0

        # 1. Prefer placements that maximize remaining contiguous space
        remaining = self.fabric.difference(poly)
        if isinstance(remaining, MultiPolygon):
            largest_remaining = max(remaining.geoms, key=lambda p: p.area)
        else:
            largest_remaining = remaining

        score += largest_remaining.area * 0.1

        # 2. Prefer alignments with fabric edges
        min_dist_to_edge = min(
            self.fabric.exterior.distance(poly),
            poly.distance(self.fabric)
        )
        score += 100 / (1 + min_dist_to_edge)

        # 3. Prefer compact arrangements (minimize bounding box)
        all_parts = self.placed_parts + [poly]
        combined = unary_union(all_parts)
        score -= combined.envelope.area * 0.01

        return score

    def commit_placement(self, poly, part_data):
        """Finalize the placement"""
        self.placed_parts.append(poly)

        # Update free space
        new_free = []
        for space in self.free_space:
            difference = space.difference(poly)
            if difference.is_empty:
                continue
            if isinstance(difference, MultiPolygon):
                new_free.extend(difference.geoms)
            else:
                new_free.append(difference)
        self.free_space = new_free


def calculate_utilization(nester):
    total_area = nester.fabric.area
    used_area = sum(p.area for p in nester.placed_parts)
    return used_area / total_area


# === Execution ===
def run_nesting():
    nester = FabricNester(FABRIC_WIDTH, FABRIC_HEIGHT)

    # Prepare all parts to place
    all_parts = []
    for part in garment_parts:
        for i in range(part["quantity"]):
            all_parts.append({
                "name": part["name"],
                "outline": part["outline"],
                "allow_rotation": part.get("allow_rotation", False),
                "instance": i + 1
            })

    # Try to place each part
    for part in all_parts:
        success = nester.place_part(part)
        if not success:
            print(f"Failed to place {part['name']}-{part['instance']}")

    visualize(nester)


# === Visualization ===
def visualize(nester):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Draw fabric
    fabric_x, fabric_y = nester.fabric.exterior.xy
    ax.fill(fabric_x, fabric_y, 'lightgray', alpha=0.2, zorder=1)

    # Draw placed parts
    colors = plt.cm.tab20.colors
    for i, part in enumerate(nester.placed_parts):
        # Handle both Polygon and MultiPolygon cases
        if part.geom_type == 'Polygon':
            x, y = part.exterior.xy
            ax.fill(x, y, fc=colors[i % len(colors)], ec='black', alpha=0.7, zorder=2)
        elif part.geom_type == 'MultiPolygon':
            for poly in part.geoms:
                x, y = poly.exterior.xy
                ax.fill(x, y, fc=colors[i % len(colors)], ec='black', alpha=0.7, zorder=2)

        # Add label at centroid
        centroid = part.centroid
        ax.text(centroid.x, centroid.y, f"Part {i + 1}",
                ha='center', va='center', fontsize=8)

    ax.set_xlim(0, FABRIC_WIDTH)
    ax.set_ylim(0, FABRIC_HEIGHT)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()  # Textile convention
    plt.title(f"Fabric Layout (Utilization: {calculate_utilization(nester):.1%})")
    plt.show()


run_nesting()
