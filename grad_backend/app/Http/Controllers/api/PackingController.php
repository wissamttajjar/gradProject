<?php

namespace App\Http\Controllers\api;

use App\Http\Controllers\Controller;
use App\Models\Design;
use App\Models\Fabric;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Symfony\Component\Process\Process;

class PackingController extends Controller
{
    public function pack(Request $request)
    {
        $validated = $request->validate([
            'fabric_id' => 'required|exists:fabrics,id',
        ]);

        $fabric = Fabric::with('design.patternRule')->findOrFail($validated['fabric_id']);

        $design = $fabric->design;

        // pieces are stored per size inside pattern_rules.pieces (JSON keyed by size)
        $allPiecesBySize = $design->patternRule->pieces;
        $selectedPieces = $allPiecesBySize[$design->size] ?? [];
        if (!is_array($selectedPieces) || empty($selectedPieces)) {
            return response()->json(['ok' => false, 'error' => 'No pieces for design size'], 422);
        }

        // 2) Build payload for Flask converter
        $payload = [
            "fabric" => [
                "width" => $fabric->width,
                "height" => $fabric->height,
            ],
            "pieces" => $selectedPieces
        ];

        // 3) Call Flask service to write shape.json in the packing directory
        // ENV 'FLASK_BASE' e.g. http://localhost:5001
        $flaskBase = config('services.packing.flask_base', env('PACKING_FLASK_BASE', 'http://127.0.0.1:5001'));
        $resp = Http::timeout(20)->post($flaskBase.'/convert', $payload);

        if (!$resp->ok() || !$resp->json('ok')) {
            return response()->json(['ok' => false, 'error' => 'Flask conversion failed', 'details' => $resp->json()], 500);
        }

        // 4) Run the packing script (must be run in its directory so it sees shape.json)
        // CONFIG:
        //   PACKING_SCRIPT_PATH: absolute path to your packing script (e.g., /var/app/packing/packing_main.py)
        //   PACKING_WORKDIR:     the directory where shape.json lives (same dir as script, usually)
        //   SHAPE_JSON_PATH:     must match what Flask wrote, passed to the script via env
        $script = realpath(storage_path('app/packing-algo/genetic_packing.py'));
        $workdir = realpath(storage_path('app/packing-algo'));
        $shapePath = $resp->json('shape_json_path')
            ?? realpath(storage_path('app/packing-algo/shape.json'));

        $process = new Process(['python', $script], $workdir, [
            'SHAPE_JSON_PATH' => $shapePath,
        ]);

        $process->setTimeout(120);
        $process->run();

        if (!$process->isSuccessful()) {
            return response()->json([
                'ok' => false,
                'error' => 'Packing script failed',
                'stderr' => $process->getErrorOutput(),
                'stdout' => $process->getOutput(),
            ], 500);
        }

        // NOTE: If your packing script prints JSON placements, decode and return them.
        // If it prints logs, return them for now (or adjust the script to print JSON).
        $stdout = trim($process->getOutput());
        $maybeJson = json_decode($stdout, true);

        if (json_last_error() === JSON_ERROR_NONE && is_array($maybeJson)) {
            return response()->json(['ok' => true, 'result' => $maybeJson]);
        }

        // Fallback: return raw output (until you wire JSON from the script)
        return response()->json(['ok' => true, 'stdout' => $stdout]);
    }
}
