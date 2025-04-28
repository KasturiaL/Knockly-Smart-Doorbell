package com.example.knockly.homePage;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.loginPage.LoginActivity;
import com.example.knockly.shared.PageHeaderFragment;
import com.example.knockly.R;
import com.example.knockly.utils.JsonUtils;
import com.example.knockly.utils.LoginManager;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Objects;

public class HomeActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_home);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // TODO: delete testing code
        // Add test info to screen
        LoginManager loginManager = LoginManager.getInstance(this);
        TextView testText = findViewById(R.id.testTextHome);
        String testUsername = loginManager.getCurrentUsername();
        if (Objects.equals(testUsername, "")){
            testUsername =  "Not logged in";
        }
        testText.setText(testUsername);
        Button testButton = findViewById(R.id.testButtonHome);
        testButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loginManager.logout();
                Intent intent = new Intent(HomeActivity.this, LoginActivity.class);
                startActivity(intent);
            }
        });

        // Get relevant doorbells from database
        // TODO: Implement actual API call
        // Creates example JSON object with data to use while database is implemented
        String currentDoorbellsString = "{\"Doorbells\": [{\"ID\": \"550e8400-e29b-41d4-a716-446655440000\", \"Name\": \"Home Doorbell\"}, {\"ID\": \"9b4d4b9f-6a5d-4b6b-91b6-d53196e438b2\", \"Name\": \"Jane\'s Doorbell\"}, {\"ID\": \"a1234567-89ab-4cde-f012-3456789abcde\", \"Name\": \"John\'s Doorbell\"}] }";
        JSONObject doorbellsObject;
        doorbellsObject = JsonUtils.safeParseStringToJsonObject(currentDoorbellsString);
        JSONArray currentDoorbells = doorbellsObject.optJSONArray("Doorbells");

        // Add doorbell buttons
        HomePageButtonsFragment buttonsFragment = HomePageButtonsFragment.newInstance(currentDoorbells);
        getSupportFragmentManager().beginTransaction().replace(R.id.HomeButtonsFragment, buttonsFragment).commit();

        // Add header fragment
        // TODO: Change the username to whatever the display name (if set)/username (if no display name) is in the headerTitle param
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Welcome <username>", false, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.HomeHeaderFragment, pageHeader).commit();

    }
}