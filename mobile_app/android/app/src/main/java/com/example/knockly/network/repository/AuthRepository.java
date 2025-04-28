package com.example.knockly.network.repository;

import com.example.knockly.network.ApiClient;
import com.example.knockly.network.AuthInterceptor;
import com.example.knockly.network.dto.Token;
import com.example.knockly.network.dto.LoginRequest;
import com.example.knockly.network.service.AuthService;

import retrofit2.Call;

public class AuthRepository {

    private final AuthService svc;

    public AuthRepository(AuthService svc) { this.svc = svc; }

    public static AuthRepository create(AuthInterceptor.TokenStore tokenStore) {
        return new AuthRepository(
                ApiClient.get(tokenStore).create(AuthService.class)
        );
    }

    public Call<Token> login(String user, String pass) {
        return svc.login(new LoginRequest(user, pass));
    }

    public Call<Token> register(String user, String pass) {
        return svc.register(new LoginRequest(user, pass));
    }
}
