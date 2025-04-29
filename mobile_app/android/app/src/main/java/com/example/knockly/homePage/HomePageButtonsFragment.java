package com.example.knockly.homePage;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.gridlayout.widget.GridLayout;

import com.example.knockly.R;
import com.example.knockly.addDoorbellPage.AddDoorbellActivity;
import com.example.knockly.indvDoorbellPage.IndvDoorbellActivity;
import com.example.knockly.network.dto.DoorbellOut;
import com.example.knockly.network.dto.LinkedUser;
import com.example.knockly.utils.ButtonUtils;
import com.example.knockly.utils.ViewUtils;
import com.google.android.material.button.MaterialButton;

/**
 * A {@link Fragment} subclass that takes an array of json objects representing
 * all doorbells the user is currently attached to.
 * It dynamically loads a button for each doorbell that links to the page to show the individual doorbell
 * Finally it add a button to allow the user to add a new doorbell
 * All content it within a scroll box so that the user can have as many buttons as they want
 */
public class HomePageButtonsFragment extends Fragment {

    // Parameter Initialisation
    private static final String ARG_DOORBELLS = "doorbells";

    private DoorbellOut[] mDoorbells;

    public HomePageButtonsFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param doorbells JSON Array where each element is a json object containing all relevant
     *                  information about each individual doorbell
     * @return A new instance of fragment HomePageButtonsFragment.
     */
    public static HomePageButtonsFragment newInstance(DoorbellOut[] doorbells) {
        HomePageButtonsFragment fragment = new HomePageButtonsFragment();
        Bundle args = new Bundle();
        args.putSerializable(ARG_DOORBELLS, doorbells);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mDoorbells = (DoorbellOut[]) getArguments().getSerializable(ARG_DOORBELLS);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_home_page_buttons, container, false);

        // Get layout to add buttons to
        GridLayout layout = view.findViewById(R.id.HomePageScrollLayout);
        layout.setAlignmentMode(GridLayout.ALIGN_BOUNDS);

        // For each doorbell create button and add to display
        DoorbellOut currentObject;



        try {
            // Calculate button dimensions based on screen size
            int screenWidth = getContext().getResources().getDisplayMetrics().widthPixels;
            int marginSize = (int) (ViewUtils.dpToPx(8, getContext()));
            int buttonWidth = (screenWidth / 2) - (4 * marginSize);
            int buttonHeight = (int) (ViewUtils.dpToPx(100, getContext()));
            for (int m = 0; m < mDoorbells.length; m++) {
                currentObject = mDoorbells[m];
                if (currentObject == null) {
                    continue;
                }
                String doorbellID = currentObject.doorbell_id;;
                String doorbellName = currentObject.doorbell_name;
                String ownerID = currentObject.owner_user_id;
                LinkedUser[] linkedUsers = currentObject.linked_users;

                // Create button for doorbell
                MaterialButton doorbellButton = ButtonUtils.createDynamicStyledButton(getContext(), doorbellName, buttonWidth, buttonHeight, marginSize);

                doorbellButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        Intent intent = new Intent(getActivity(), IndvDoorbellActivity.class);
                        intent.putExtra("doorbell_ID", doorbellID);
                        intent.putExtra("doorbell_name", doorbellName);
                        intent.putExtra("owner_id", ownerID);
                        intent.putExtra("linked_users", linkedUsers);
                        startActivity(intent);
                    }
                });

                // Add to screen
                layout.addView(doorbellButton);
            }

            // Make and add 'Add Doorbell' button
            MaterialButton addBellButton = createAddDoorbellButton(getContext(), buttonWidth, buttonHeight, marginSize);

            addBellButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Intent intent = new Intent(getActivity(), AddDoorbellActivity.class);
                    startActivity(intent);
                }
            });

            layout.addView(addBellButton);
        }
        catch (Exception e){
            System.out.println("Error creating buttons on home page");
            System.out.println(e);
        }
        return view;
    }
    private MaterialButton createAddDoorbellButton(Context context, int width, int height, int margins){
        MaterialButton button = ButtonUtils.createDynamicStyledButton(context, "Add Doorbell", width, height, margins);

        int padding = (int) (ViewUtils.dpToPx(12, context));

        button.setPadding(padding, padding, padding, padding);
        button.setIcon(ContextCompat.getDrawable(context, R.drawable.plus_icon));
        button.setIconSize((int) (ViewUtils.dpToPx(24, context)));
        button.setIconTint(null);
        return button;
    }
}