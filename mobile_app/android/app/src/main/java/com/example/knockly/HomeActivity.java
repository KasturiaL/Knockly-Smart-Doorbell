package com.example.knockly;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.utils.JsonUtils;

import org.json.JSONArray;
import org.json.JSONObject;

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

        // Get relevant doorbells from database
        // TODO: Implement actual API call
        // Creates example JSON object with data to use while database is implemented
        String currentDoorbellsString = "{\"Doorbells\": [{\"ID\": \"550e8400-e29b-41d4-a716-446655440000\", \"Name\": \"Home Doorbell\"}, {\"ID\": \"9b4d4b9f-6a5d-4b6b-91b6-d53196e438b2\", \"Name\": \"Jane\'s Doorbell\"}, {\"ID\": \"a1234567-89ab-4cde-f012-3456789abcde\", \"Name\": \"John\'s Doorbell\"}] }";
        JSONObject doorbellsObject;
        doorbellsObject = JsonUtils.safeParseStringToJsonObject(currentDoorbellsString);
        JSONArray currentDoorbells = doorbellsObject.optJSONArray("Doorbells");
        System.out.println((currentDoorbells == null));

        // Add doorbell buttons
        HomePageButtonsFragment buttonsFragment = HomePageButtonsFragment.newInstance(currentDoorbells);
        getSupportFragmentManager().beginTransaction().replace(R.id.HomeButtonsFragment, buttonsFragment).commit();

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Welcome <username>", false);
        getSupportFragmentManager().beginTransaction().replace(R.id.HomeHeaderFragment, pageHeader).commit();

        // Button to link to app settings
        Button appSettingsButton = findViewById(R.id.AppSettingsButton);
        appSettingsButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(HomeActivity.this, AppSettingsActivity.class);
                startActivity(intent);
            }
        });
    }
}