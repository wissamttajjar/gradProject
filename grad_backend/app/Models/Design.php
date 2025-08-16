<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use App\Models\Fabric;

class Design extends Model
{
    protected $fillable = [
        'user_id', 'sleeve_type', 'collar_type',
        'color', 'fabric_type'
    ];

    public function fabrics(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(Fabric::class);
    }


}
