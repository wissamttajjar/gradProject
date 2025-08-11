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
        Schema::create('designs', function (Blueprint $table) {
            $table->id();
            $table->unsignedInteger("user_id");
            $table->string('sleeve_type');
            $table->string('collar_type');
            $table->string('color');
            $table->string('fabric_type');
//            $table->string('image_1');
//            $table->string('image_2');
//            $table->string('image_3');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('designs');
    }
};
