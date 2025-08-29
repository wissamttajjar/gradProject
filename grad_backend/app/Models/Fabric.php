<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Storage;

class Fabric extends Model
{
    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'design_id',
        'width',
        'height',
        'size',
        'num_of_pieces',
        'cut_positions',
        'packing_results',
        'layout_image_path',
        'coordinates_json_path',
        'utilization'
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'cut_positions' => 'array',
        'packing_results' => 'array',
        'utilization' => 'decimal:2'
    ];

    /**
     * Get the design that owns the fabric.
     */
    public function design(): BelongsTo
    {
        return $this->belongsTo(Design::class);
    }

    /**
     * Get the layout image URL for web access.
     */
    public function getLayoutImageUrlAttribute(): ?string
    {
        if (!$this->layout_image_path) {
            return null;
        }

        // If file is in storage directory, generate URL
        if (strpos($this->layout_image_path, storage_path('app')) === 0) {
            $relativePath = str_replace(storage_path('app') . '/', '', $this->layout_image_path);
            return Storage::url($relativePath);
        }

        // If it's an absolute path, return as-is (for local development)
        return $this->layout_image_path;
    }

    /**
     * Get the coordinates JSON URL for web access.
     */
    public function getCoordinatesJsonUrlAttribute(): ?string
    {
        if (!$this->coordinates_json_path) {
            return null;
        }

        if (strpos($this->coordinates_json_path, storage_path('app')) === 0) {
            $relativePath = str_replace(storage_path('app') . '/', '', $this->coordinates_json_path);
            return Storage::url($relativePath);
        }

        return $this->coordinates_json_path;
    }

    /**
     * Check if packing is completed.
     */
    public function getIsPackedAttribute(): bool
    {
        return !empty($this->packing_results) && !empty($this->layout_image_path);
    }

    /**
     * Get the total number of pieces in packing results.
     */
    public function getTotalPiecesAttribute(): int
    {
        return is_array($this->packing_results) ? count($this->packing_results) : 0;
    }

    /**
     * Scope a query to only include packed fabrics.
     */
    public function scopePacked($query)
    {
        return $query->whereNotNull('packing_results')
            ->whereNotNull('layout_image_path');
    }

    /**
     * Scope a query to only include unpacked fabrics.
     */
    public function scopeUnpacked($query)
    {
        return $query->whereNull('packing_results')
            ->orWhereNull('layout_image_path');
    }

    /**
     * Scope a query to only include fabrics with good utilization.
     */
    public function scopeHighUtilization($query, $threshold = 0.7)
    {
        return $query->where('utilization', '>=', $threshold);
    }

    /**
     * Delete associated files when fabric is deleted.
     */
    protected static function booted(): void
    {
        static::deleting(function (Fabric $fabric) {
            // Delete associated files
            if ($fabric->layout_image_path && file_exists($fabric->layout_image_path)) {
                @unlink($fabric->layout_image_path);
            }
            if ($fabric->coordinates_json_path && file_exists($fabric->coordinates_json_path)) {
                @unlink($fabric->coordinates_json_path);
            }
        });
    }
}
