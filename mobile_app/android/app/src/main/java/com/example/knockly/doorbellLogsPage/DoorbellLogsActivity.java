package com.example.knockly.doorbellLogsPage;

import android.content.Intent;
import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.R;
import com.example.knockly.shared.PageHeaderFragment;

public class DoorbellLogsActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_doorbell_logs);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Get info about doorbell from intent that started activity
        Intent intent = getIntent();
        String doorbellId = intent.getStringExtra("Doorbell_ID");
        String doorbellName = intent.getStringExtra("Doorbell_Name");

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance(doorbellName + " Logs", true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.DoorbellLogsHeaderFragment, pageHeader).commit();
    }
}