<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class DesignCreationProcess extends Model
{
    protected $fillable = [
        'user_id',
        'current_step',
        'completed_steps',
        'design_data',
        'is_completed'
    ];

    protected $casts = [
        'completed_steps' => 'array',
        'design_data' => 'array'
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
