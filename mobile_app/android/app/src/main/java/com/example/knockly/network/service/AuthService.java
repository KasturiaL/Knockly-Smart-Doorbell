package com.example.knockly.network.service;

import com.example.knockly.network.dto.LoginRequest;
import com.example.knockly.network.dto.Token;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface AuthService {
    @POST("auth/login")
    Call<Token> login(@Body LoginRequest body);

    @POST("auth/register")
    Call<Token> register(@Body LoginRequest body);
}
