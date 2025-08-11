import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity
from shapely.strtree import STRtree
from shapely.prepared import prep
import time

# === Configuration ===
FABRIC_WIDTH = 300
FABRIC_HEIGHT = 600
SET_COUNT = 40

# === Complex Shape Definitions ===
garment_parts = [
    {
        "name": "front",
        "outline": [(0, 0), (50, 0), (45, 20), (40, 50), (0, 50)],
        "quantity": SET_COUNT,
        "allow_rotation": True
    },
    {
        "name": "sleeve",
        "outline": [(0, 0), (25, 0), (20, 40), (5, 40)],
        "quantity": SET_COUNT * 2,
        "allow_rotation": True
    },
    {
        "name": "collar",
        "outline": [(0, 0), (30, 0), (25, 15), (5, 15)],
        "quantity": SET_COUNT,
        "allow_rotation": True
    }
]


# === Optimized Nesting Engine ===
class OptimizedNester:
    def __init__(self, width, height):
        self.fabric = Polygon([(0, 0), (width, 0), (width, height), (0, height)])
        self.free_space = [self.fabric]
        self.placed_parts = []
        self.spatial_index = STRtree([])  # Initialize empty STRtree
        self.prepared_fabric = prep(self.fabric)
        self.part_sequence = []

    def place_all_parts(self, parts):
        """Main method to place all parts with optimization"""
        self.prepare_part_sequence(parts)

        for part in self.part_sequence:
            if not self.place_part(part):
                print(f"Failed to place {part['name']}-{part['instance']}")
                return False
        return True

    def prepare_part_sequence(self, parts):
        """Sort parts by area descending (largest first)"""
        expanded = []
        for part in parts:
            for i in range(part["quantity"]):
                poly = Polygon(part["outline"])
                expanded.append({
                    "name": part["name"],
                    "polygon": poly,
                    "outline": part["outline"],
                    "area": poly.area,
                    "allow_rotation": part["allow_rotation"],
                    "instance": i + 1
                })

        self.part_sequence = sorted(expanded, key=lambda x: -x["area"])

    def place_part(self, part):
        original_poly = part["polygon"]
        best_placement = None
        best_score = -np.inf

        orientations = self.generate_orientations(original_poly, part["allow_rotation"])
        candidate_positions = self.generate_candidate_positions(orientations[0])

        for rotated_poly in orientations:
            for position in candidate_positions:
                translated = affinity.translate(rotated_poly, *position)

                if not self.is_valid_placement(translated):
                    continue

                score = self.calculate_placement_score(translated)
                if score > best_score:
                    best_score = score
                    best_placement = translated

        if best_placement:
            self.commit_placement(best_placement)
            return True

        # Fallback: brute-force try all positions
        return self.brute_force_placement(original_poly, part)

    @staticmethod
    def generate_orientations(poly, allow_rotation):
        """Generate rotated versions with caching"""
        if not allow_rotation:
            return [poly]

        return [
            poly,
            affinity.rotate(poly, 90, origin='centroid'),
            affinity.rotate(poly, 180, origin='centroid'),
            affinity.rotate(poly, 270, origin='centroid')
        ]

    def generate_candidate_positions(self, poly):
        """Generate positions using bottom-left and NFP heuristics"""
        positions = set()

        # 1. Basic grid positions
        min_x, min_y = 0, 0
        max_x = FABRIC_WIDTH - (poly.bounds[2] - poly.bounds[0])
        max_y = FABRIC_HEIGHT - (poly.bounds[3] - poly.bounds[1])

        grid_step = max((poly.bounds[2] - poly.bounds[0]) / 2,
                        (poly.bounds[3] - poly.bounds[1]) / 2)

        for x in np.arange(min_x, max_x, grid_step):
            for y in np.arange(min_y, max_y, grid_step):
                positions.add((x, y))

        # 2. Edge positions from placed parts
        if self.placed_parts:
            for placed in self.placed_parts:
                for x, y in placed.exterior.coords:
                    positions.add((x, y))
                    positions.add((x, y + (poly.bounds[3] - poly.bounds[1])))
                    positions.add((x + (poly.bounds[2] - poly.bounds[0]), y))

        return positions

    def is_valid_placement(self, poly):
        """Check if placement is valid"""
        # Check fabric bounds
        if not self.prepared_fabric.contains(poly):
            return False

        # Check collisions using spatial index
        for idx in self.spatial_index.query(poly):
            if poly.intersects(self.placed_parts[idx]):
                return False
        return True

    def calculate_placement_score(self, poly):
        """Score based on utilization and compactness"""
        score = 0

        # 1. Distance to edges (prefer edges)
        min_dist = min(
            poly.distance(Point(0, 0)),
            poly.distance(Point(FABRIC_WIDTH, 0)),
            poly.distance(Point(FABRIC_WIDTH, FABRIC_HEIGHT)),
            poly.distance(Point(0, FABRIC_HEIGHT))
        )
        score += 100 / (1 + min_dist)

        # 2. Compactness (prefer arrangements that minimize bounding box)
        if self.placed_parts:
            combined = unary_union(self.placed_parts + [poly])
            score -= combined.envelope.area * 0.01

        return score

    def commit_placement(self, poly):
        """Finalize the placement"""
        self.placed_parts.append(poly)
        # Rebuild spatial index with all placed parts
        self.spatial_index = STRtree(self.placed_parts)

        # Update free space (simplified)
        new_free = []
        for space in self.free_space:
            difference = space.difference(poly)
            if not difference.is_empty:
                if hasattr(difference, 'geoms'):  # MultiPolygon
                    new_free.extend(difference.geoms)
                else:  # Polygon
                    new_free.append(difference)
        self.free_space = new_free

    def brute_force_placement(self, poly, part):
        """Fallback placement method"""
        orientations = self.generate_orientations(poly, part["allow_rotation"])

        for rotated_poly in orientations:
            width = rotated_poly.bounds[2] - rotated_poly.bounds[0]
            height = rotated_poly.bounds[3] - rotated_poly.bounds[1]

            for x in np.arange(0, FABRIC_WIDTH - width, 5):
                for y in np.arange(0, FABRIC_HEIGHT - height, 5):
                    translated = affinity.translate(rotated_poly, x, y)
                    if self.is_valid_placement(translated):
                        self.commit_placement(translated)
                        return True
        return False


# === Visualization ===
def visualize(nester):
    fig, ax = plt.subplots(figsize=(14, 8))

    # Draw fabric
    fabric_x, fabric_y = nester.fabric.exterior.xy
    ax.fill(fabric_x, fabric_y, 'lightgray', alpha=0.2, zorder=1)

    # Draw placed parts
    colors = plt.cm.tab20.colors
    for i, part in enumerate(nester.placed_parts):
        x, y = part.exterior.xy
        ax.fill(x, y, fc=colors[i % len(colors)], ec='black', alpha=0.7, zorder=2)

        # Add label
        centroid = part.centroid
        ax.text(centroid.x, centroid.y, f"{i + 1}", ha='center', va='center', fontsize=8)

    # Calculate metrics
    total_area = nester.fabric.area
    used_area = sum(p.area for p in nester.placed_parts)
    utilization = used_area / total_area

    # Add info box
    metrics = f"""
    Fabric: {FABRIC_WIDTH}x{FABRIC_HEIGHT} cm
    Utilization: {utilization:.1%}
    Parts Placed: {len(nester.placed_parts)}
    """
    ax.text(-0.6, 1, metrics, transform=ax.transAxes,
            va='top', bbox=dict(facecolor='white', alpha=0.8))

    ax.set_xlim(0, FABRIC_WIDTH)
    ax.set_ylim(0, FABRIC_HEIGHT)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.title("Optimized Fabric Nesting")
    plt.show()


# === Main Execution ===
def run_optimized_nesting():
    start_time = time.time()

    nester = OptimizedNester(FABRIC_WIDTH, FABRIC_HEIGHT)
    success = nester.place_all_parts(garment_parts)

    if success:
        print(f"✅ Successfully placed all parts in {time.time() - start_time:.2f} seconds")
        visualize(nester)
    else:
        print("❌ Failed to place all parts")
        visualize(nester)  # Show partial results


if __name__ == "__main__":
    run_optimized_nesting()