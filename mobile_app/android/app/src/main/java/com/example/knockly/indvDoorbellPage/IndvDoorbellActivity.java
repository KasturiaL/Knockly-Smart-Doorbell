package com.example.knockly.indvDoorbellPage;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.constraintlayout.widget.ConstraintSet;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.example.knockly.R;
import com.example.knockly.network.dto.LinkedUser;
import com.example.knockly.shared.PageHeaderFragment;
import com.example.knockly.utils.SSHUtils;
import com.google.android.material.snackbar.Snackbar;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;

public class IndvDoorbellActivity extends AppCompatActivity implements LiveFeedFragment.FragmentCallback, DoorControlFragment.FragmentCallback {

    private Insets systemBars;
    private  LiveFeedFragment liveFeedFragment;
    private Context context;
    private final String username = "pi";
    private final String password = "raspberry";
    private String piHost = "";
    private Session sshSession;
    private String commandDir = "cm2211-project-group-8/edge_device/Doorbell/working_prototype/pi";
    private String openCmd = "\nchmod +x open.sh\n./open.sh\n";
    private String closeCmd = "\nchmod +x close.sh\n./close.sh\n";

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

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance(doorbellName, true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellHeaderFragment, pageHeader).commit();

        // Add options tab at bottom
        DoorbellOptionsTabFragment tabFragment = DoorbellOptionsTabFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.IndvDoorbellOptionsFragment, tabFragment).commit();

        // Add live feed fragment
        liveFeedFragment = LiveFeedFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.LiveFeedContainer, liveFeedFragment).commit();

        // Add door control fragment
        DoorControlFragment doorControlFragment = DoorControlFragment.newInstance(doorbellID);
        getSupportFragmentManager().beginTransaction().replace(R.id.DoorControlContainer, doorControlFragment).commit();

        context = getApplicationContext();

        if (piHost.isBlank()) {

            final Thread networkThread = new Thread(new Runnable() {
                @Override
                public void run() {
                    piHost = SSHUtils.getPiIP(context, username, password);
                    System.out.println(piHost);

                    try {
                        sshSession = SSHUtils.startSSH(username, piHost, password);
                    } catch (JSchException e) {
                        System.out.println(e.getMessage());
                    }
                }
            });
            networkThread.start();
        } else {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        sshSession = SSHUtils.startSSH(username, piHost, password);
                    } catch (JSchException e) {
                        System.out.println(e.getMessage());
                    }
                }
            }).start();
        }
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

    private int returnStatus = -1;

    @Override
    public void openDoor() {
        if (sshSession != null) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    String command = "\ncd "+commandDir+"\n"+openCmd+"\n";
                    returnStatus = SSHUtils.execSSHCmd(command, sshSession);
                }
            }).start();
        }

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

        returnStatus = -1;
    }

    @Override
    public void closeDoor() {
        if (sshSession != null) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    String command = "\ncd "+commandDir+"\n"+closeCmd+"\n";
                    returnStatus = SSHUtils.execSSHCmd(command, sshSession);
                }
            }).start();
        }


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

        returnStatus = -1;
    }
}