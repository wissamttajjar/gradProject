<?php

namespace App\Console\Commands;

use App\Services\PatternRuleService;
use Illuminate\Console\Command;

class ImportPatternRules extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'patterns:import {file}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Import pattern rules from JSON file';

    /**
     * Execute the console command.
     */
    public function handle(PatternRuleService $service): void
    {
        $service->importFromJson($this->argument('file'));
        $this->info('Pattern rules imported successfully!');
    }
}
