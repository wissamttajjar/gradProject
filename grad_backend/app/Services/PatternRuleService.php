<?php


// app/Services/PatternRuleService.php
namespace App\Services;

use App\Models\PatternRule;
use Illuminate\Support\Facades\Storage;

class PatternRuleService
{
public function importFromJson($jsonPath)
{
$rules = json_decode(file_get_contents($jsonPath), true);

foreach ($rules as $ruleData) {
    $this->fixAssetPaths($ruleData['assets'], $ruleData['sleeves'], $ruleData['neckline']);

PatternRule::updateOrCreate(
['rule_id' => $ruleData['id']],
[
'sleeves' => $ruleData['sleeves'],
'neckline' => $ruleData['neckline'],
'prompt_template' => $ruleData['prompt_template'],
'assets' => $ruleData['assets'],
'pieces' => $ruleData['pieces']
]
);
}
}

protected function fixAssetPaths(&$assets, $sleeves, $neckline)
{
foreach ($assets['pattern_images'] as $size => &$images) {
foreach ($images as $type => &$path) {
// Extract filename and create new path
$filename = basename($path);
$newPath = "storage/pattern-images/{$sleeves}/{$neckline}/{$type}/{$filename}";

// You can add logic here to move/copy files if needed
$path = $newPath;
}
}
}

public function findRule($sleeves, $neckline)
{
return PatternRule::where('sleeves', $sleeves)
->where('neckline', $neckline)
->first();
}
}
