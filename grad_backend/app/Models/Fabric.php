<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Fabric extends Model
{
    use HasFactory;

    protected $fillable = [
        'design_id',
        'width',
        'height',
        'cut_positions',
    ];

    protected $casts = [
        'cut_positions' => 'array',
    ];

    public function design()
    {
        return $this->belongsTo(Design::class);
    }
}
