package com.example.knockly.indvDoorbellPage;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.constraintlayout.widget.ConstraintSet;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import androidx.fragment.app.FragmentContainer;

import com.example.knockly.doorbellLogsPage.DoorbellLogsActivity;
import com.example.knockly.feedHistoryPage.FeedHistoryActivity;
import com.example.knockly.manageDoorbellPage.ManageDoorbellActivity;
import com.example.knockly.manageFacesPage.ManageFacesActivity;
import com.example.knockly.manageUsersPage.ManageUsersActivity;
import com.example.knockly.R;
import com.example.knockly.network.dto.LinkedUser;
import com.example.knockly.network.dto.PermissionResponse;
import com.example.knockly.network.repository.AuthRepository;
import com.example.knockly.shared.PageHeaderFragment;
import com.example.knockly.indvDoorbellPage.DoorbellOptionsTabFragment;
import com.example.knockly.utils.LoginManager;
import com.google.android.material.snackbar.Snackbar;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class IndvDoorbellActivity extends AppCompatActivity implements LiveFeedFragment.FragmentCallback, DoorControlFragment.FragmentCallback {

    private AuthRepository repo = AuthRepository.getInstance(LoginManager.getInstance(this));

    private Insets systemBars;
    private  LiveFeedFragment liveFeedFragment;

    private PermissionResponse[] userPerms;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_indv_doorbell);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Get data about current doorbell from intent that started the activity
        Intent intent = getIntent();
        String doorbellID = intent.getStringExtra("doorbell_ID");
        String doorbellName = intent.getStringExtra("doorbell_name");
        String ownerID = intent.getStringExtra("owner_id");
        LinkedUser[] linkedUsers = (LinkedUser[]) intent.getSerializableExtra("linked_users");

        // Get information about users current permissions from API
        repo.getUserPerms(doorbellID).enqueue(new Callback<PermissionResponse[]>() {
            @Override
            public void onResponse(Call<PermissionResponse[]> call, Response<PermissionResponse[]> response) {
                // If API call is successful
                if (response.isSuccessful() && response.body()!=null){
                    userPerms = response.body();

                    // Add options tab at bottom of page
                    DoorbellOptionsTabFragment tabFragment = DoorbellOptionsTabFragment.newInstance(doorbellID, doorbellName, userPerms);
                    getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellOptionsFragment, tabFragment).commit();
                }
                // If API call is unsuccessful
                else{
                    Log.d("Indv Doorbell Activity", "Error fetching user perms" + response.code());
                    Toast.makeText(IndvDoorbellActivity.this, "Error fetching user permissions" + response.code(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<PermissionResponse[]> call, Throwable t) {
                Log.d("Indv Doorbell Activity", "Error fetching user perms" + t.getMessage());
                Toast.makeText(IndvDoorbellActivity.this, "Error fetching user permissions" + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance(doorbellName, true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellHeaderFragment, pageHeader).commit();

        // Add live feed fragment
        liveFeedFragment = LiveFeedFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.LiveFeedContainer, liveFeedFragment).commit();

        // Add door control fragment
        DoorControlFragment doorControlFragment = DoorControlFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.DoorControlContainer, doorControlFragment).commit();
    }

    @Override
    public void expandLiveFeed(){
        View headerFragment = findViewById(R.id.IndvDoorbellHeaderFragment);
        View controlsFragment = findViewById(R.id.DoorControlContainer);
        View optionsFragment = findViewById(R.id.IndvDoorbellOptionsFragment);

        ConstraintLayout feedConstraint = findViewById((R.id.feedConstraint));

        controlsFragment.setVisibility(View.GONE);
        optionsFragment.setVisibility(View.GONE);
        headerFragment.setVisibility(View.GONE);

        ConstraintSet constraints = new ConstraintSet();
        constraints.clone(feedConstraint);
        constraints.clear(R.id.feedConstraint, ConstraintSet.BOTTOM);
        constraints.connect(R.id.feedConstraint, ConstraintSet.BOTTOM, ConstraintSet.PARENT_ID, ConstraintSet.BOTTOM);
        constraints.constrainHeight(R.id.feedConstraint, ConstraintSet.MATCH_CONSTRAINT);
        constraints.applyTo(feedConstraint);

        ViewGroup.MarginLayoutParams params = (ViewGroup.MarginLayoutParams) feedConstraint.getLayoutParams();
        params.topMargin = 0;
        params.bottomMargin = 0;
        feedConstraint.setLayoutParams(params);

        View view = findViewById(R.id.main);
        view.setPadding(0,0,0,0);

        WindowInsetsControllerCompat controller = new WindowInsetsControllerCompat(getWindow(), getWindow().getDecorView());
        controller.hide(WindowInsetsCompat.Type.systemBars());
        controller.hide(WindowInsetsCompat.Type.navigationBars());
        controller.hide(WindowInsetsCompat.Type.statusBars());
    }

    @Override
    public void shrinkLiveFeed(){
        View headerFragment = findViewById(R.id.IndvDoorbellHeaderFragment);
        View controlsFragment = findViewById(R.id.DoorControlContainer);
        View optionsFragment = findViewById(R.id.IndvDoorbellOptionsFragment);

        ConstraintLayout feedConstraint = findViewById((R.id.feedConstraint));

        controlsFragment.setVisibility(View.VISIBLE);
        optionsFragment.setVisibility(View.VISIBLE);
        headerFragment.setVisibility(View.VISIBLE);

        ConstraintSet constraints = new ConstraintSet();
        constraints.clone(feedConstraint);
        constraints.clear(R.id.feedConstraint, ConstraintSet.BOTTOM);
        constraints.connect(R.id.feedConstraint, ConstraintSet.BOTTOM, R.id.DoorControlContainer, ConstraintSet.BOTTOM);
        constraints.constrainHeight(R.id.feedConstraint, ConstraintSet.MATCH_CONSTRAINT);
        constraints.applyTo(feedConstraint);

        ViewGroup.MarginLayoutParams params = (ViewGroup.MarginLayoutParams) feedConstraint.getLayoutParams();
        params.topMargin = 64;
        params.bottomMargin = 24;
        feedConstraint.setLayoutParams(params);

        View view = findViewById(R.id.main);
        view.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);

        WindowInsetsControllerCompat controller = new WindowInsetsControllerCompat(getWindow(), getWindow().getDecorView());
        controller.show(WindowInsetsCompat.Type.systemBars());
        controller.show(WindowInsetsCompat.Type.navigationBars());
        controller.show(WindowInsetsCompat.Type.statusBars());
    }

    @Override
    public void openDoor(){
        // TODO: Add API call to actually open the door

        // Variable declaration to assume that api has returned success status
        int returnStatus = 200;

        View view = findViewById(R.id.main);
        // If door opened successfully then change door status button to open
        if (returnStatus == 200){
            liveFeedFragment.setToggleButtonOn();
            Snackbar.make(view, "Door opened successfully!", Snackbar.LENGTH_SHORT).show();
        }
        // If error occurred
        else{
            Snackbar.make(view, "Error opening door, please try again", Snackbar.LENGTH_SHORT).show();
        }
    }

    @Override
    public void closeDoor(){
        // TODO: Add API call to actually close the door

        // Variable declaration to assume that api has returned success status
        int returnStatus = 200;

        View view = findViewById(R.id.main);
        // If door opened successfully then change door status button to open
        if (returnStatus == 200){
            liveFeedFragment.setToggleButtonOff();
            Snackbar.make(view, "Door closed successfully!", Snackbar.LENGTH_SHORT).show();
        }
        // If error occurred
        else{
            Snackbar.make(view, "Error closing door, please try again", Snackbar.LENGTH_SHORT).show();
        }
    }
}