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
        Schema::create('pattern_rules', function (Blueprint $table) {
            $table->id();
            $table->string('rule_id')->unique();
            $table->string('sleeves');
            $table->string('neckline');
            $table->text('prompt_template');
            $table->json('assets');
            $table->json('pieces');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('pattern_rules');
    }
};
