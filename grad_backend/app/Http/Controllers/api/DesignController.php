<?php

namespace app\Http\Controllers\api;

use App\Http\Controllers\Controller;
use App\Models\Design;
use Illuminate\Http\Request;

class DesignController extends Controller
{
    public function store(Request $request): \Illuminate\Http\JsonResponse
    {
        $validated = $request->validate([
            'sleeve_type' => 'required|string|max:255',
            'collar_type' => 'required|string|max:255',
            'color'       => 'required|string|max:255',
            'fabric_type' => 'required|string|max:255',
        ]);

        $validated['user_id'] = auth()->user()->id;

        $design = Design::create($validated);

        return response()->json([
            'message' => 'Design created successfully!',
            'design'  => $design
        ], 201);
    }

    public function update(Request $request, Design $design): \Illuminate\Http\JsonResponse
    {
        if ($request->user()->id !== $design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to update this design.'
            ], 403);
        }

        $validated = $request->validate([
            'sleeve_type' => 'nullable|string|max:255',
            'collar_type' => 'nullable|string|max:255',
            'color'       => 'nullable|string|max:255',
            'fabric_type' => 'nullable|string|max:255',
        ]);

        $design->update($validated);

        return response()->json([
            'message' => 'Design updated successfully!',
            'design'  => $design
        ], 200);
    }

    public function destroy(Request $request, Design $design): \Illuminate\Http\JsonResponse
    {
        // 1. Check if the authenticated user owns this design
        if ($request->user()->id !== $design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to delete this design.'
            ], 403);
        }

        // 2. Delete the design
        $design->delete();

        return response()->json([
            'message' => 'Design deleted successfully!'
        ], 200);
    }
}

