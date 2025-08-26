<?php

namespace app\Http\Controllers\api;

use App\Models\PatternRule;
use App\Http\Controllers\Controller;
use App\Services\PatternRuleService;
use Illuminate\Http\Request;

class PatternController extends Controller
{
    protected $patternService;

    public function __construct(PatternRuleService $patternService)
    {
        $this->patternService = $patternService;
    }

    public function getPattern(Request $request)
    {
        $request->validate([
            'sleeves' => 'required|string',
            'neckline' => 'required|string',
            'size' => 'required|string|in:38,40,42,44,46,48'
        ]);

        $rule = $this->patternService->findRule(
            $request->sleeves,
            $request->neckline
        );

        $size = $request->size;

        if (!isset($rule->pieces[$size]) || !isset($rule->assets['pattern_images'][$size])) {
            return response()->json(['error' => "Pattern data not found for size {$size}"], 404);
        }

        if (!$rule) {
            return response()->json(['error' => 'Pattern rule not found'], 404);
        }

        return response()->json([
            'pattern' => $rule->pieces[$size],
            'assets' => $rule->assets['pattern_images'][$size],
            'prompt' => str_replace(
                ['[COLOR]', '[FABRIC]'],
                [$request->color ?? 'red', $request->fabric ?? 'cotton'],
                $rule->prompt_template
            )
        ]);
    }

    public function importRules(Request $request)
    {
        $request->validate([
            'json_file' => 'required|file|mimes:json'
        ]);

        $this->patternService->importFromJson(
            $request->file('json_file')->getRealPath()
        );

        return response()->json(['message' => 'Rules imported successfully']);
    }
}
