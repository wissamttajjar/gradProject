<?php

namespace App\Http\Controllers\api;

use App\Http\Controllers\Controller;
use App\Models\Design;
use App\Models\Fabric;
use Illuminate\Http\Request;

class FabricController extends Controller
{
    public function store(Request $request)
    {
        $validated = $request->validate([
            'design_id' => 'required|integer|exists:designs,id',
            'width'     => 'required|integer|min:1',
            'height'    => 'required|integer|min:1',
        ]);

        $design = Design::findOrFail($validated['design_id']);

        if ($request->user()->id !== $design->user_id) {
            return response()->json(['message' => 'Unauthorized.'], 403);
        }

        // Get pattern pieces from the design
        $pieces = $design->getPatternPieces();
        if (!$pieces) {
            return response()->json(['message' => 'Design has no pattern pieces'], 400);
        }

        $fabric = Fabric::create([
            'design_id' => $validated['design_id'],
            'width'     => $validated['width'],
            'height'    => $validated['height'],
            'cut_positions' => null
        ]);

        return response()->json([
            'message' => 'Fabric created successfully!',
            'fabric'  => $fabric,
            'pattern_pieces' => $pieces
        ], 201);
    }

    public function update(Request $request, Fabric $fabric)
    {
        if ($request->user()->id !== $fabric->design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to update this fabric.'
            ], 403);
        }

        $validated = $request->validate([
            'width'  => 'nullable|integer|min:1',
            'height' => 'nullable|integer|min:1',
            'size'   => 'nullable|string|in:38,40,42,44,46,48',
        ]);

        $fabric->update($validated);

        return response()->json([
            'message' => 'Fabric updated successfully!',
            'fabric'  => $fabric
        ], 200);
    }

    public function destroy(Request $request, Fabric $fabric)
    {
        if ($request->user()->id !== $fabric->design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to delete this fabric.'
            ], 403);
        }

        $fabric->delete();

        return response()->json([
            'message' => 'Fabric deleted successfully!'
        ], 200);
    }

    public function show(Request $request, Fabric $fabric)
    {
        if ($request->user()->id !== $fabric->design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to view this fabric.'
            ], 403);
        }

        return response()->json([
            'fabric' => $fabric
        ], 200);
    }

    public function index(Request $request)
    {
        $fabrics = $request->user()->fabrics()->with('design')->get();

        return response()->json([
            'fabrics' => $fabrics
        ], 200);
    }
}
