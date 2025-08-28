import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Where to write shape.json so the packing script can read it.
# By default, write next to the packing script (same directory).
SHAPE_JSON_PATH = os.environ.get("SHAPE_JSON_PATH", "./shape.json")

def _to_algo_shape(payload: dict) -> dict:
    """
    Convert Laravel payload to algorithm 'shape.json' schema.

    Laravel payload shape (example):
    {
      "fabric": {"width": 100, "height": 150},
      "pieces": [
        {
          "piece_id": "FRONT",
          "qty": 1,
          "outline": {"format": "polygon", "points": [[26,0],[26,29],...]}
        },
        ...
      ]
    }

    Algorithm expects:
    {
      "fabric_width": 100,
      "fabric_height": 150,
      "num_pieces": 1,
      "pieces": [
        {"name": "FRONT", "x": [...], "y": [...]},
        {"name": "BACK",  "x": [...], "y": [...]}
      ]
    }
    """
    fabric = payload.get("fabric", {})
    try:
        fabric_width = float(fabric["width"])
        fabric_height = float(fabric["height"])
    except Exception:
        raise ValueError("fabric.width and fabric.height are required (numbers).")

    pieces_in = payload.get("pieces", [])
    pieces_out = []

    for piece in pieces_in:
        name = str(piece.get("piece_id", "PIECE"))
        qty = int(piece.get("qty", 1))
        outline = piece.get("outline", {})
        points = outline.get("points", [])

        if not isinstance(points, list) or not points:
            raise ValueError(f"Missing/invalid outline.points for piece '{name}'")

        # Split into separate x[], y[] lists and ensure floats
        x = [float(p[0]) for p in points]
        y = [float(p[1]) for p in points]

        # Duplicate per qty by repeating the piece entry (algo has global num_pieces,
        # we keep it =1 to avoid duplicating every piece globally).
        for idx in range(qty):
            final_name = f"{name}_{idx+1}" if qty > 1 else name
            pieces_out.append({"name": final_name, "x": x, "y": y})

    algo = {
        "fabric_width": fabric_width,
        "fabric_height": fabric_height,
        "num_pieces": 1,       # IMPORTANT: keep 1 because we already expanded by qty
        "pieces": pieces_out
    }
    return algo

@app.post("/convert")
def convert():
    """
    POST JSON from Laravel, convert to algorithm schema, write shape.json,
    and return it for debugging/verification.
    """
    try:
        payload = request.get_json(force=True, silent=False)
        algo_json = _to_algo_shape(payload)

        # Ensure directory exists, then write shape.json
        out_path = os.path.abspath(SHAPE_JSON_PATH)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(algo_json, f, ensure_ascii=False, indent=2)

        return jsonify({
            "ok": True,
            "shape_json_path": out_path,
            "shape": algo_json
        }), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    # Run on 5001 by default (change if you want)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
