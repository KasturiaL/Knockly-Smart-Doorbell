package com.example.knockly.network.repository;

import com.example.knockly.network.ApiClient;
import com.example.knockly.network.AuthInterceptor;
import com.example.knockly.network.dto.Token;
import com.example.knockly.network.dto.LoginRequest;
import com.example.knockly.network.dto.UserInfo;
import com.example.knockly.network.service.AuthService;

import retrofit2.Call;

// Allows call to the API
// Initially created when app opens in KnocklyApp class
// To call in activity use "authRepo = AuthRepository.getInstance(LoginManager.getInstance())"
// Or if existing variable holding Login Manager then use that as argument
// Needs LoginManager to store & get access tokens
public class AuthRepository {

    private static AuthRepository instance;
    private final AuthService svc;

    private AuthRepository(AuthService svc) {
        this.svc = svc;
    }

    public static AuthRepository getInstance(AuthInterceptor.TokenStore tokenStore) {
        if (instance == null){
            return new AuthRepository(
                    ApiClient.get(tokenStore).create(AuthService.class)
            );
        }
        return instance;
    }

    public static void resetInstance(AuthInterceptor.TokenStore tokenStore) {
        instance = new AuthRepository(
                ApiClient.get(tokenStore).create(AuthService.class));
    }

    public Call<Token> login(String user, String pass) {
        return svc.login(new LoginRequest(user, pass));
    }

    public Call<Token> register(String user, String pass) {
        return svc.register(new LoginRequest(user, pass));
    }

    public Call<UserInfo> getCurrentUser() {
        return svc.getCurrentUser();
    }
}
