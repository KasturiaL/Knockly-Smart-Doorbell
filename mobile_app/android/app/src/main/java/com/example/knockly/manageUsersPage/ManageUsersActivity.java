package com.example.knockly.manageUsersPage;

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
import com.example.knockly.blocklistPage.BlocklistActivity;
import com.example.knockly.createRolePage.CreateRoleActivity;
import com.example.knockly.shared.PageHeaderFragment;

public class ManageUsersActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_manage_users);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Manage Users", true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.ManageUsersHeaderFragment, pageHeader).commit();

        // Simple button to link to create role page
        // Feel free to delete/change when developing the actual UI
        Button button = findViewById(R.id.CreateRoleButton);
        button.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(ManageUsersActivity.this, CreateRoleActivity.class);
                startActivity(intent);
            }
        });

        // Simple button to link to blocklist page
        // Feel free to delete/change when developing the actual UI
        Button button2 = findViewById(R.id.UsersBlocklistButton);
        button2.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(ManageUsersActivity.this, BlocklistActivity.class);
                startActivity(intent);
            }
        });
    }
}