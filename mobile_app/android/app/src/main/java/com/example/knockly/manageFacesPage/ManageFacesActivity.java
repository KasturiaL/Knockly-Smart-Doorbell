package com.example.knockly.manageFacesPage;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.R;
import com.example.knockly.addFacePage.AddNewFaceActivity;
import com.example.knockly.blocklistPage.BlocklistActivity;
import com.example.knockly.shared.PageHeaderFragment;

public class ManageFacesActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_manage_faces);
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
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Manage Faces", true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.ManageFacesHeaderFragment, pageHeader).commit();

        // Simple button to link to add new face page
        // Feel free to change when developing actual UI
        Button button = findViewById(R.id.AddFacesButton);
        button.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(ManageFacesActivity.this, AddNewFaceActivity.class);
                intent.putExtra("Doorbell_ID", doorbellId);
                intent.putExtra("Doorbell_Name", doorbellName);
                startActivity(intent);
            }
        });

        // Simple button to link to blocklist page
        // Feel free to change when developing actual UI
        Button button2 = findViewById(R.id.FacesBlocklistButton);
        button2.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(ManageFacesActivity.this, BlocklistActivity.class);
                intent.putExtra("Doorbell_ID", doorbellId);
                intent.putExtra("Doorbell_Name", doorbellName);
                startActivity(intent);
            }
        });
    }
}