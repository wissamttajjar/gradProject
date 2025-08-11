<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Design extends Model
{
    protected $fillable = [
        'user_id', 'sleeve_type', 'collar_type',
        'color', 'fabric_type'
    ];


}

//    public function images(): \Illuminate\Database\Eloquent\Relations\HasMany
//    {
//        return $this->hasMany(Image::class);
//    }
