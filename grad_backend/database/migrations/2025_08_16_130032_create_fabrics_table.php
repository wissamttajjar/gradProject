<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('fabrics', function (Blueprint $table) {
            $table->id();
            $table->foreignId('design_id')->constrained()->onDelete('cascade');
            $table->integer('width');
            $table->integer('height');
            $table->integer('num_of_pieces');
            $table->json('cut_positions')->nullable();
            $table->json('packing_results')->nullable();
            $table->string('layout_image_path')->nullable();
            $table->string('coordinates_json_path')->nullable();
            $table->decimal('utilization', 5, 2)->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('fabrics');
    }
};
