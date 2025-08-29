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
    public function preparePackingPayload(int $fabricId)
    {

        $fabric = Fabric::find($fabricId);

        if (!$fabric) {
            return response()->json(['error' => 'Fabric not found.'], 404);
        }

        try {
            $design = Design::with('patternRule')->findOrFail($fabric->design_id);
            $pieces = $design->patternRule->pieces;
            $size = $design->size;
            $selectedPieces = $pieces[$size] ?? [];

            $formattedPieces = [$size => $selectedPieces];
            $totalPiecesCount = $fabric -> num_of_pieces;

        } catch (ModelNotFoundException $e) {
            return response()->json(['error' => 'Design not found.'], 404);
        }

        $payload = [
            'fabric_width' => $fabric->width,
            'fabric_height' => $fabric->height,
            'num_pieces' => $totalPiecesCount,
            'pieces' => $formattedPieces,
        ];

        $jsonPayload = json_encode($payload);

        $descriptorspec = array(
            0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
            1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
            2 => array("pipe", "w")   // stderr is a pipe that the child will write to
        );

        $process = proc_open('python "C:/Users/wissam_T/Desktop/5th/graduation project/gradProject/grad_backend/storage/app/packing-algo/genetic_packing.py"', $descriptorspec, $pipes);

        if (is_resource($process)) {
            // Write the JSON payload to the Python script's standard input
            fwrite($pipes[0], $jsonPayload);
            fclose($pipes[0]);

            // Read the output from the Python script
            $pythonOutput = stream_get_contents($pipes[1]);
            fclose($pipes[1]);

            // Read any error messages from the Python script
            $pythonErrors = stream_get_contents($pipes[2]);
            fclose($pipes[2]);

            // Close the process
            $returnCode = proc_close($process);

            // You can now process the output and errors
            // For example, return them as a JSON response
            return response()->json([
                'status' => 'success',
                'python_output' => $pythonOutput,
                'python_errors' => $pythonErrors,
                'return_code' => $returnCode
            ]);
        } else {
            return response()->json(['error' => 'Failed to start the Python process.'], 500);
        }

    }

}
