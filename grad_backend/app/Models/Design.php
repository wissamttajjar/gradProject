<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use App\Models\Fabric;

class Design extends Model
{
    protected $fillable = [
        'user_id', 'sleeve_type', 'collar_type',
        'color', 'fabric_type', 'size',
        'generation_prompt', 'pattern_rule_id'
    ];

    public function fabrics()
    {
        return $this->hasMany(Fabric::class);
    }

    public function patternRule()
    {
        return $this->belongsTo(PatternRule::class);
    }

    // Helper method to get pattern pieces
    public function getPatternPieces()
    {
        if ($this->patternRule && $this->size) {
            return $this->patternRule->pieces[$this->size] ?? null;
        }
        return null;
    }
}
