<?php

namespace app\Http\Controllers\api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Fabric;


class FabricController extends Controller
{

    public function store(Request $request)
    {
        $validated = $request->validate([
            'design_id'     => 'required|integer|exists:designs,id',
            'width'         => 'required|integer',
            'height'        => 'required|integer',
            'cut_positions' => 'nullable|json',
        ]);

        if ($request->user()->designs()->where('id', $validated['design_id'])->doesntExist()) {
             return response()->json(['message' => 'Unauthorized.'], 403);
         }

        $fabric = Fabric::create($validated);

        return response()->json([
            'message' => 'Fabric created successfully!',
            'fabric'  => $fabric
        ], 201);
    }


    public function update(Request $request, Fabric $fabric)
    {
        if ($request->user()->id !== $fabric->design->user_id) {
            return response()->json(['message' => 'Unauthorized. You do not have permission to update this fabric.'], 403);
        }

        $validated = $request->validate([
            'width'         => 'nullable|integer',
            'height'        => 'nullable|integer',
            'cut_positions' => 'nullable|json',
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
            return response()->json(['message' => 'Unauthorized. You do not have permission to delete this fabric.'], 403);
        }

        $fabric->delete();

        return response()->json([
            'message' => 'Fabric deleted successfully!'
        ], 200);
    }
}
