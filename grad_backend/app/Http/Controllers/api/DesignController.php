<?php

// app/Http/Controllers/DesignCreationController.php
namespace App\Http\Controllers;

use App\Models\Design;
use App\Models\DesignCreationProcess;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\Rule;

class DesignCreationController extends Controller
{
    // Define the steps and their validation rules
    protected $steps = [
        1 => [
            'rules' => [
                'sleeve_type' => ['required', 'string', Rule::in(['short', 'long', 'three-quarter'])],
                'field' => 'sleeve_type'
            ],
            2 => [
                'rules' => [
                    'collar_type' => ['required', 'string', Rule::in(['round', 'v-neck', 'polo'])],
                    'field' => 'collar_type'
                ],
                3 => [
                    'rules' => [
                        'color' => ['required', 'string', 'max:50'],
                    ],
                    'field' => 'color'
                ],
                4 => [
                    'rules' => [
                        'fabric_type' => ['required', 'string', Rule::in(['cotton', 'linen', 'polyester'])],
                        'field' => 'fabric_type'
                    ]
                ];

    public function start(Request $request)
    {
        // Check if user already has an active process
        $existingProcess = DesignCreationProcess::where('user_id', Auth::id())
            ->where('is_completed', false)
            ->first();

        if ($existingProcess) {
            return response()->json([
                'process_id' => $existingProcess->id,
                'current_step' => $existingProcess->current_step,
                'message' => 'Existing design process resumed'
            ]);
        }

        // Create new process
        $process = DesignCreationProcess::create([
            'user_id' => Auth::id(),
            'current_step' => 1,
            'completed_steps' => [],
            'design_data' => [],
            'is_completed' => false
        ]);

        return response()->json([
            'process_id' => $process->id,
            'current_step' => 1,
            'message' => 'Design process started'
        ]);
    }

    public function processStep(Request $request, $step)
    {
        $request->validate([
            'process_id' => 'required|exists:design_creation_processes,id,user_id,'.Auth::id()
        ]);

        $process = DesignCreationProcess::find($request->process_id);

        // Validate step progression
        if ($step != $process->current_step) {
            return response()->json([
                'error' => 'Invalid step sequence. Current step is '.$process->current_step
            ], 400);
        }

        // Validate step-specific data
        $stepData = $request->validate($this->steps[$step]['rules']);

        // Update process data
        $designData = $process->design_data ?? [];
        $designData[$this->steps[$step]['field'] = $stepData[$this->steps[$step]['field']];

        $completedSteps = $process->completed_steps ?? [];
        if (!in_array($step, $completedSteps)) {
            $completedSteps[] = $step;
        }

        $process->update([
            'design_data' => $designData,
            'completed_steps' => $completedSteps,
            'current_step' => $step + 1
        ]);

        return response()->json([
            'process_id' => $process->id,
            'next_step' => $process->current_step <= count($this->steps) ? $process->current_step : null,
            'completed_steps' => $completedSteps,
            'message' => 'Step '.$step.' completed successfully'
        ]);
    }

    public function finish(Request $request)
    {
        $request->validate([
            'process_id' => 'required|exists:design_creation_processes,id,user_id,'.Auth::id()
        ]);

        $process = DesignCreationProcess::find($request->process_id);

        // Verify all steps are completed
        if (count($process->completed_steps ?? []) !== count($this->steps)) {
            return response()->json([
                'error' => 'Please complete all design steps before finishing'
            ], 400);
        }

        // Create the final design
        $design = Design::create([
            'user_id' => Auth::id(),
            'sleeve_type' => $process->design_data['sleeve_type'],
            'collar_type' => $process->design_data['collar_type'],
            'color' => $process->design_data['color'],
            'fabric_type' => $process->design_data['fabric_type']
        ]);

        // Mark process as completed
        $process->update(['is_completed' => true]);

        return response()->json([
            'success' => true,
            'design' => $design,
            'message' => 'Design created successfully'
        ]);
    }

    public function getCurrentProcess(Request $request)
    {
        $process = DesignCreationProcess::where('user_id', Auth::id())
            ->where('is_completed', false)
            ->first();

        if (!$process) {
            return response()->json(['message' => 'No active design process'], 404);
        }

        return response()->json([
            'process_id' => $process->id,
            'current_step' => $process->current_step,
            'completed_steps' => $process->completed_steps,
            'design_data' => $process->design_data
        ]);
    }
}
