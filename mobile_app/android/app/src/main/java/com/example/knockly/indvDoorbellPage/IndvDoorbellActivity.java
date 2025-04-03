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
import androidx.fragment.app.FragmentContainer;

import com.example.knockly.doorbellLogsPage.DoorbellLogsActivity;
import com.example.knockly.feedHistoryPage.FeedHistoryActivity;
import com.example.knockly.manageDoorbellPage.ManageDoorbellActivity;
import com.example.knockly.manageFacesPage.ManageFacesActivity;
import com.example.knockly.manageUsersPage.ManageUsersActivity;
import com.example.knockly.R;
import com.example.knockly.shared.PageHeaderFragment;
import com.example.knockly.indvDoorbellPage.DoorbellOptionsTabFragment;

public class IndvDoorbellActivity extends AppCompatActivity implements LiveFeedFragment.FragmentCallback {

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

        // Get data of current doorbell from intent that started the activity
        Intent intent = getIntent();
        String doorbellID = intent.getStringExtra("Doorbell_ID");

        // Add header fragment
        // TODO: Change headerTitle to the doorbell's name, same with the other button intents' values
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Doorbell #...", true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellHeaderFragment, pageHeader).commit();

        // Add options tab at bottom
        DoorbellOptionsTabFragment tabFragment = DoorbellOptionsTabFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellOptionsFragment, tabFragment).commit();

        LiveFeedFragment liveFeedFragment = LiveFeedFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.LiveFeedContainer, liveFeedFragment).commit();
    }

    @Override
    public void expandLiveFeed(){
        View headerFragment = findViewById(R.id.IndvDoorbellHeaderFragment);
        View controlsFragment = findViewById(R.id.DoorControlContainer);
        View optionsFragment = findViewById(R.id.IndvDoorbellOptionsFragment);

        controlsFragment.setVisibility(View.GONE);
        optionsFragment.setVisibility(View.GONE);
        headerFragment.setVisibility(View.GONE);
    }

    @Override
    public void shrinkLiveFeed(){
        View headerFragment = findViewById(R.id.IndvDoorbellHeaderFragment);
        View controlsFragment = findViewById(R.id.DoorControlContainer);
        View optionsFragment = findViewById(R.id.IndvDoorbellOptionsFragment);

        controlsFragment.setVisibility(View.VISIBLE);
        optionsFragment.setVisibility(View.VISIBLE);
        headerFragment.setVisibility(View.VISIBLE);
    }
}