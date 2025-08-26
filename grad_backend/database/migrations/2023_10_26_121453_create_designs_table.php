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
            $table->unsignedBigInteger('user_id');
            $table->string('sleeve_type');
            $table->string('collar_type');
            $table->string('color');
            $table->string('fabric_type');
            $table->string('size');
            $table->text('generation_prompt');
            $table->foreignId('pattern_rule_id')->nullable()->constrained('pattern_rules');
            $table->timestamps();

            // Add foreign key for user_id
            $table->foreign('user_id')->references('id')->on('users');
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
