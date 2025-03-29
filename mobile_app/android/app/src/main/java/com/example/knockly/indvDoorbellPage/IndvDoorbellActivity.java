package com.example.knockly.indvDoorbellPage;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.doorbellLogsPage.DoorbellLogsActivity;
import com.example.knockly.feedHistoryPage.FeedHistoryActivity;
import com.example.knockly.manageDoorbellPage.ManageDoorbellActivity;
import com.example.knockly.manageFacesPage.ManageFacesActivity;
import com.example.knockly.manageUsersPage.ManageUsersActivity;
import com.example.knockly.R;
import com.example.knockly.shared.PageHeaderFragment;

public class IndvDoorbellActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_indv_doorbell);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Doorbell #...", true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellHeaderFragment, pageHeader).commit();

        // Simple button to link to manage doorbell page
        // Feel free to delete/change when developing the actual UI
        Button button = findViewById(R.id.ManageDoorbellButton);
        button.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(IndvDoorbellActivity.this, ManageDoorbellActivity.class);
                intent.putExtra("Doorbell_Info", "Doorbell #1");
                startActivity(intent);
            }
        });

        // Simple button to link to feed history page
        // Feel free to delete/change when developing the actual UI
        Button button2 = findViewById(R.id.FeedHistoryButton);
        button2.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(IndvDoorbellActivity.this, FeedHistoryActivity.class);
                intent.putExtra("Doorbell_Info", "Doorbell #1");
                startActivity(intent);
            }
        });

        // Simple button to link to manage user profiles page
        // Feel free to delete/change when developing the actual UI
        Button button3 = findViewById(R.id.ManageUserProfsButton);
        button3.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(IndvDoorbellActivity.this, ManageUsersActivity.class);
                intent.putExtra("Doorbell_Info", "Doorbell #1");
                startActivity(intent);
            }
        });

        // Simple button to link to manage face profiles page
        // Feel free to delete/change when developing the actual UI
        Button button4 = findViewById(R.id.ManageFaceProfsButton);
        button4.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(IndvDoorbellActivity.this, ManageFacesActivity.class);
                intent.putExtra("Doorbell_Info", "Doorbell #1");
                startActivity(intent);
            }
        });

        // Simple button to link to doorbell logs page
        // Feel free to delete/change when developing the actual UI
        Button button5 = findViewById(R.id.DoorbellLogsButton);
        button5.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(IndvDoorbellActivity.this, DoorbellLogsActivity.class);
                intent.putExtra("Doorbell_Info", "Doorbell #1");
                startActivity(intent);
            }
        });
    }
}