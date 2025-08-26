<?php

namespace App\Http\Controllers\api;

use App\Http\Controllers\Controller;
use App\Models\Design;
use App\Models\PatternRule;
use App\Services\PatternRuleService;
use Illuminate\Http\Request;

class DesignController extends Controller
{
    protected PatternRuleService $patternService;

    public function __construct(PatternRuleService $patternService)
    {
        $this->patternService = $patternService;
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'sleeve_type' => 'required|string|max:255',
            'collar_type' => 'required|string|max:255',
            'color'       => 'required|string|max:255',
            'fabric_type' => 'required|string|max:255',
            'size'        => 'required|string|in:38,40,42,44,46,48', // NEW
        ]);

        $validated['user_id'] = auth()->id();

        $rule = PatternRule::where('sleeves', $validated['sleeve_type'])
            ->where('neckline', $validated['collar_type'])
            ->firstOrFail();

        // Generate AI prompt
        $validated['generation_prompt'] = str_replace(
            ['[COLOR]', '[FABRIC]'],
            [$validated['color'], $validated['fabric_type']],
            $rule->prompt_template
        );

        $validated['pattern_rule_id'] = $rule->id;

        $design = Design::create($validated);

        return response()->json([
            'message' => 'Design created successfully!',
            'design'  => $design,
            
        ], 201);
    }

    public function update(Request $request, Design $design)
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
            'size'        => 'nullable|string|in:38,40,42,44,46,48', // NEW
        ]);

        // If any design attribute changes, update the prompt
        if ($request->hasAny(['sleeve_type', 'collar_type', 'color', 'fabric_type', 'size'])) {
            $rule = $design->patternRule;
            if (!$rule && $request->hasAny(['sleeve_type', 'collar_type'])) {
                $rule = PatternRule::where('sleeves', $validated['sleeve_type'] ?? $design->sleeve_type)
                    ->where('neckline', $validated['collar_type'] ?? $design->collar_type)
                    ->first();
            }

            if ($rule) {
                $validated['generation_prompt'] = str_replace(
                    ['[COLOR]', '[FABRIC]'],
                    [$validated['color'] ?? $design->color, $validated['fabric_type'] ?? $design->fabric_type],
                    $rule->prompt_template
                );
                $validated['pattern_rule_id'] = $rule->id;
            }
        }

        $design->update($validated);

        return response()->json([
            'message' => 'Design updated successfully!',
            'design'  => $design
        ], 200);
    }

    public function destroy(Request $request, Design $design)
    {
        if ($request->user()->id !== $design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to delete this design.'
            ], 403);
        }

        $design->delete();

        return response()->json([
            'message' => 'Design deleted successfully!'
        ], 200);
    }

    // NEW: Get pattern pieces for a design
    public function getPattern(Request $request, Design $design)
    {
        if ($request->user()->id !== $design->user_id) {
            return response()->json([
                'message' => 'Unauthorized. You do not have permission to view this design.'
            ], 403);
        }

        $pieces = $design->getPatternPieces();

        if (!$pieces) {
            return response()->json([
                'message' => 'No pattern pieces found for this design and size.'
            ], 404);
        }

        return response()->json([
            'pattern_pieces' => $pieces
        ], 200);
    }
}
