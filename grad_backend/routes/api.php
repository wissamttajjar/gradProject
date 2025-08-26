<?php

use App\Http\Controllers\api\AuthController;
use App\Http\Controllers\api\DesignController;
use App\Http\Controllers\api\FabricController;
use App\Http\Controllers\api\PatternController;
use Illuminate\Support\Facades\Route;

//unauthenticated api functions

//unauthenticated user api functions
Route::post("register" , [AuthController::class , "register"]);
Route::post("login" , [AuthController::class , "login"]);

Route::post('/pattern/import', [PatternController::class, 'importRules']);
Route::get('/pattern', [PatternController::class, "getPattern"]);

//authenticated api functions
Route::group(["middleware" => ["auth:api"]] , function (){

    //authenticated user api functions
    Route::get("show-profile" , [AuthController::class , "showProfile"]);
    Route::post("logout" , [AuthController::class , "logout"]);

    //authenticated user design api functions
    Route::post('/create_designs', [DesignController::class, 'store']);
    Route::patch('/update_design/{design}', [DesignController::class, 'update']);
    Route::delete('/delete_design/{design}', [DesignController::class, 'destroy']);

    Route::post('/create_fabric', [FabricController::class, 'store']);
    Route::patch('/update_fabric/{fabric}', [FabricController::class, 'update']);
    Route::delete('/delete_fabric/{fabric}', [FabricController::class, 'destroy']);





});
