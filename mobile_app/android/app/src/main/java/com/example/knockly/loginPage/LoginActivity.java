package com.example.knockly.loginPage;

import android.content.Intent;

import androidx.annotation.NonNull;
import androidx.biometric.BiometricManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.biometric.BiometricPrompt;
import androidx.core.content.ContextCompat;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.R;
import com.example.knockly.homePage.HomeActivity;
import com.example.knockly.shared.PageHeaderFragment;
import com.example.knockly.utils.LoginManager;
import com.google.android.material.snackbar.Snackbar;

import com.example.knockly.network.AuthInterceptor;
import com.example.knockly.network.repository.AuthRepository;
import com.example.knockly.network.dto.Token;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import java.util.Objects;
import java.util.concurrent.Executor;


public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_login);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Get login manager to use
        LoginManager loginManager = LoginManager.getInstance(this);

        // Check if biometrics can be used
        BiometricManager biometricManager = BiometricManager.from(this);
        switch (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG | BiometricManager.Authenticators.DEVICE_CREDENTIAL)) {
            case BiometricManager.BIOMETRIC_SUCCESS:
                break;
            default:
                removeBiometricsButton();
                break;
        }

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Knockly Login", false, false);
        getSupportFragmentManager().beginTransaction().replace(R.id.LoginHeaderFragment, pageHeader).commit();

        // Get needed layout elements
        EditText editUsername = findViewById(R.id.editUsername);
        EditText editPassword = findViewById(R.id.editPassword);
        Button btnLogin = findViewById(R.id.btnLogin);
        TextView linkRegister = findViewById(R.id.linkRegister);
        TextView linkResetPass = findViewById(R.id.linkForgotPass);

        Button biometricBtn = findViewById(R.id.biometricsButton);
        TextView biometricLabel = findViewById(R.id.biometricButtonLabel);

        btnLogin.setOnClickListener(v -> {
            String user = editUsername.getText().toString().trim();
            String pass = editPassword.getText().toString().trim();

            LoginManager lm = LoginManager.getInstance(this);

            AuthRepository repo = AuthRepository.create(lm); // TokenStore via lambda
            repo.login(user, pass).enqueue(new Callback<Token>() {
                @Override public void onResponse(Call<Token> c, Response<Token> rsp) {
                    if (rsp.isSuccessful() && rsp.body()!=null) {
                        lm.saveJwt(rsp.body().access_token);           // persist token
                        startActivity(new Intent(LoginActivity.this, HomeActivity.class));
                        finish();
                    } else {
                        Snackbar.make(v,"Login failed ("+rsp.code()+")",Snackbar.LENGTH_SHORT).show();
                    }
                }
                @Override public void onFailure(Call<Token> c, Throwable t) {
                    Snackbar.make(v,"Network error: "+t.getMessage(),Snackbar.LENGTH_SHORT).show();
                }
            });
        });

        // TODO: remove test code
        TextView testText = findViewById(R.id.testTextLogin);
        String ID = loginManager.getCurrentUserID();
        if (Objects.equals(ID, "")) {
            ID = "Not logged in";
        }
        testText.setText(ID);

        // Check if user can use biometric login
        // If not remove button
        if (loginManager.loginIsExpired()) {
            // Remove button & label
            removeBiometricsButton();
        } else {
            // Prefill username section if already logged in
            String username = loginManager.getCurrentUsername();
            editUsername.setText(username);
            // Add onClick function
            biometricBtn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    biometricLogin();
                }
            });
        }

        // Link to create account page
        linkRegister.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(LoginActivity.this, CreateAccountActivity.class);
                startActivity(intent);
            }
        });

        // Link to forgot password page
        linkResetPass.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(LoginActivity.this, ResetPasswordActivity.class);
                startActivity(intent);
            }
        });
    }
    private void removeBiometricsButton() {
        Button biometricBtn = findViewById(R.id.biometricsButton);
        TextView biometricLabel = findViewById(R.id.biometricButtonLabel);

        biometricBtn.setVisibility(View.GONE);
        biometricLabel.setVisibility(View.GONE);
    }

    private void biometricLogin(){
        Executor executor = ContextCompat.getMainExecutor(this);
        BiometricPrompt biometricPrompt = new BiometricPrompt(LoginActivity.this,
                executor, new BiometricPrompt.AuthenticationCallback() {

            @Override
            public void onAuthenticationError(int errorCode, @NonNull CharSequence errString) {
                super.onAuthenticationError(errorCode, errString);
                Log.d("Login Activity", "Authetication error: " + errString);
            }

            @Override
            public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult result) {
                super.onAuthenticationSucceeded(result);
                Intent intent = new Intent(LoginActivity.this, HomeActivity.class);
                startActivity(intent);
            }

            @Override
            public void onAuthenticationFailed() {
                super.onAuthenticationFailed();
                View view = findViewById(android.R.id.content);
                Snackbar.make(view, "Biometric login failed. Please try again", Snackbar.LENGTH_SHORT).show();
            }
        });

        BiometricPrompt.PromptInfo promptInfo = new BiometricPrompt.PromptInfo.Builder()
                .setTitle("Log in using biometrics")
                .setSubtitle("")
                .setNegativeButtonText("Use password instead")
                .build();

        biometricPrompt.authenticate(promptInfo);
    }
}