<?php

use App\Http\Controllers\api\AuthController;
use Illuminate\Support\Facades\Route;

//unauthenticated api functions

//unauthenticated user api functions
Route::post("register" , [AuthController::class , "register"]);
Route::post("login" , [AuthController::class , "login"]);

//authenticated api functions
Route::group(["middleware" => ["auth:api"]] , function (){

    //authenticated user api functions
    Route::get("show-profile" , [AuthController::class , "showProfile"]);
    Route::post("logout" , [AuthController::class , "logout"]);


});
