package com.example.knockly.indvDoorbellPage;

import android.content.Intent;
import android.os.Bundle;

import androidx.constraintlayout.widget.ConstraintLayout;
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

        for (int m = 0; m < buttons.length; m++){
            Button currentButton = buttons[m];
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