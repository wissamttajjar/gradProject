<?php

namespace App\Http\Controllers\api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    //register method -> post ->no middleware
    public function register(Request $request): JsonResponse
    {
        // validate the data is there ??
        $request->validate([
            "name" => "required",
            "email" => "required|email|unique:users",
            "password" => "required|confirmed"
        ]);

        //send data to the database
        $user = new User();
        $user->name = $request->name;
        $user->email = $request->email;
        $user->password = $request->password;

        //save data
        $user->save();

        // validate the data is there ??
        $login_data = $request->validate([

            "email" => "required",
            "password" => "required"

        ]);

        //check user
        if(!auth()->attempt($login_data)){

            return response()->json([

                "status"=> false ,
                "msg" => "invalid email or password ."

            ]);
        }

        //create token
        $token =auth()->user()->createToken("auth_token")->accessToken;

        //return response
        return response()->json([
            "status"=>true ,
            "msg"=>"Owner created !!" ,
            "msg"=>"User data" ,
            "data"=> $login_data ,
            "access_token"=>$token

        ]);
    }

    //login method -> post ->no middleware
    public function login(Request $request): JsonResponse
    {
        // validate the data is there ??
        $login_data = $request->validate([

            "email" => "required",
            "password" => "required"

        ]);

        //check owner
        if(!auth()->attempt($login_data)){

            return response()->json([

                "status"=> false ,
                "msg" => "invalid email or password ."

            ]);
        }

        //create token
        $token =auth()->user()->createToken("auth_token")->accessToken;

        //return response
        return response()->json([
            "status"=>true ,
            "msg"=>"logged in !!" ,
            "data"=> $login_data ,
            "access_token"=>$token

        ]);
    }

    //showProfile method -> get ->in middleware
    public function showProfile(): JsonResponse
    {

        //get user date
        $user_data = auth()->user();

        //return response
        return response()->json([
            "status"=>true ,
            "msg"=>"User data" ,
            "data"=> $user_data
        ]);
    }

    //logout method -> post ->in middleware
    public function logout(Request $request): JsonResponse
    {
        //get user token
        $token = $request->user()->token();

        //revoke token
        $token->revoke();

        //return response
        return response()->json([
            "status"=>true,
            "msg"=>"logged out !"
        ]);
    }
}
