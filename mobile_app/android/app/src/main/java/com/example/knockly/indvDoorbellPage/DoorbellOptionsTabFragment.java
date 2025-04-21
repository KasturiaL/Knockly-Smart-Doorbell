package com.example.knockly.indvDoorbellPage;

import android.content.Intent;
import android.os.Bundle;

import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.example.knockly.R;
import com.example.knockly.doorbellLogsPage.DoorbellLogsActivity;
import com.example.knockly.feedHistoryPage.FeedHistoryActivity;
import com.example.knockly.manageDoorbellPage.ManageDoorbellActivity;
import com.example.knockly.manageFacesPage.ManageFacesActivity;
import com.example.knockly.manageUsersPage.ManageUsersActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.snackbar.Snackbar;

import org.json.JSONObject;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link DoorbellOptionsTabFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DoorbellOptionsTabFragment extends Fragment {

    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_BELL_ID = "DoorbellID";

    private String mDoorbellID;
    private boolean tabMinimised = false;
    private JSONObject permissions;

    public DoorbellOptionsTabFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param DoorbellID Parameter 1.
     * @return A new instance of fragment test.
     */
    public static DoorbellOptionsTabFragment newInstance(String DoorbellID) {
        DoorbellOptionsTabFragment fragment = new DoorbellOptionsTabFragment();
        Bundle args = new Bundle();
        args.putString(ARG_BELL_ID, DoorbellID);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mDoorbellID = getArguments().getString(ARG_BELL_ID);
        }

        //TODO: Implement actual API call (in main activity?)
        try {
            permissions = new JSONObject();
            permissions.put("manageUsers", true);
            permissions.put("manageFaces", false);
            permissions.put("manageDoorbell", true);
            permissions.put("viewFeedHistory", false);
            permissions.put("viewDoorbellLogs", true);
        }
        catch(Exception e) {
            System.out.println("Error getting user permissions:");
            System.out.println(e);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        // Inflate the layout for this fragment
        View view =  inflater.inflate(R.layout.fragment_doorbell_options_tab, container, false);

        // Add on click listeners to change activities to all the classes
        Button[] buttons = {
                view.findViewById(R.id.manageUsersButton),
                view.findViewById(R.id.manageFacesButton),
                view.findViewById(R.id.manageDoorbellButton),
                view.findViewById(R.id.feedHistoryButton),
                view.findViewById(R.id.doorbellLogsButton)
        };
        Class[] destinationActivites = {
                ManageUsersActivity.class,
                ManageFacesActivity.class,
                ManageDoorbellActivity.class,
                FeedHistoryActivity.class,
                DoorbellLogsActivity.class
        };

        final String[] permissionNames = {
                "manageUsers",
                "manageFaces",
                "manageDoorbell",
                "viewFeedHistory",
                "viewDoorbellLogs"
        };

        for (int m = 0; m < buttons.length; m++){
            Button currentButton = buttons[m];

            if (permissions.optBoolean(permissionNames[m])){
                Class currentActivity = destinationActivites[m];
                currentButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        Intent intent = new Intent(getActivity(), currentActivity);
                        intent.putExtra("Doorbell_ID", mDoorbellID);
                        startActivity(intent);
                    }
                });
            }
            else{
                currentButton.setBackgroundColor(ContextCompat.getColor(getContext(), R.color.grey));
                currentButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        Snackbar.make(view, "You don't have permission to access this page. Please contact the admin if you need to change this.", Snackbar.LENGTH_SHORT).show();

                    }
                });
            }
        }

        // Make minimise/expand button function
        MaterialButton minimiseButton = view.findViewById(R.id.minimiseButton);
        ConstraintLayout buttonContainer = view.findViewById(R.id.MinimiseTabButtonContainer);

        minimiseButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (tabMinimised) {
                    buttonContainer.setVisibility(View.VISIBLE);
                    minimiseButton.setText(R.string.buttonMinimiseOptionsTitle);
                    minimiseButton.setIconResource(R.drawable.down_arrow);
                }
                else {
                    buttonContainer.setVisibility(View.GONE);
                    minimiseButton.setText(R.string.buttonExpandOptionsTitle);
                    minimiseButton.setIconResource(R.drawable.up_arrow);
                }
                tabMinimised = !tabMinimised;
            }
        });

        return view;
    }
}