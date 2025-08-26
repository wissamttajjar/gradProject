<?php

// app/Models/PatternRule.php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Casts\Attribute;

class PatternRule extends Model
{
    protected $casts = [
        'assets' => 'array',
        'pieces' => 'array',
    ];

    protected $fillable = [
        'rule_id', 'sleeves', 'neckline', 'prompt_template', 'assets', 'pieces'
    ];

    // Helper method to get asset path
    public function getAssetPath($size, $type)
    {
        return storage_path('app/' . $this->assets['pattern_images'][$size][$type]);
    }
}
