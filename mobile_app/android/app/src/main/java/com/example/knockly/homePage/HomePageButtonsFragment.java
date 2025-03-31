package com.example.knockly.homePage;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;

import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;

import android.util.TypedValue;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.gridlayout.widget.GridLayout;

import com.example.knockly.addDoorbellPage.AddDoorbellActivity;
import com.example.knockly.indvDoorbellPage.IndvDoorbellActivity;
import com.example.knockly.R;
import com.example.knockly.utils.JsonUtils;
import com.example.knockly.utils.ViewUtils;
import com.google.android.material.button.MaterialButton;

import org.json.JSONArray;
import org.json.JSONObject;

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

    private JSONArray mDoorbells;

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
    public static HomePageButtonsFragment newInstance(JSONArray doorbells) {
        HomePageButtonsFragment fragment = new HomePageButtonsFragment();
        Bundle args = new Bundle();
        args.putString(ARG_DOORBELLS, doorbells.toString());
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mDoorbells = JsonUtils.safeParseStringToJsonArray(getArguments().getString(ARG_DOORBELLS));
            System.out.println(getArguments().getString(ARG_DOORBELLS));
            System.out.println(mDoorbells);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_home_page_buttons, container, false);

        // Get layout to add buttons to
        GridLayout layout = view.findViewById(R.id.HomePageScrollLayout);

        // For each doorbell create button and add to display
        JSONObject currentObject;
        String doorbellName;
        try {
            for (int m = 0; m < mDoorbells.length(); m++) {
                currentObject = mDoorbells.optJSONObject(m);
                if (currentObject == null) {
                    continue;
                }
                doorbellName = currentObject.optString("Name", "Error: Name not found");
                final String doorbellID = currentObject.optString("ID", "ID_NOT_FOUND");

                // Create button for doorbell
                MaterialButton doorbellButton = createStyledDoorbellButton(getContext(), doorbellName);

                doorbellButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        Intent intent = new Intent(getActivity(), IndvDoorbellActivity.class);
                        intent.putExtra("Doorbell_ID", doorbellID);
                        startActivity(intent);
                    }
                });

                // Add to screen
                layout.addView(doorbellButton);
            }

            // Make and add 'Add Doorbell' button
            MaterialButton addBellButton = createAddDoorbellButton(getContext());

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

    // Helper method to style doorbell buttons dynamically
    private MaterialButton createStyledDoorbellButton(Context context, String text){
        MaterialButton button = new MaterialButton(context);

        // Set button text
        button.setText(text);
        button.setTextColor(ContextCompat.getColor(context, R.color.black));
        button.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);

        // Set button background
        button.setCornerRadius((int) (ViewUtils.dpToPx(5, context)));
        button.setStrokeWidth(3);
        button.setStrokeColorResource(R.color.black);
        button.setBackgroundTintList(ContextCompat.getColorStateList(context, R.color.colorSecondary));

        // Set layout parameters
        int screenWidth = context.getResources().getDisplayMetrics().widthPixels;
        int marginSize = (int) (ViewUtils.dpToPx(8, context));
        int buttonWidth = (screenWidth / 2) - (4 * marginSize);
        int buttonHeight = (int) (ViewUtils.dpToPx(100, context));

        GridLayout.LayoutParams params = new GridLayout.LayoutParams();
        params.width = buttonWidth;
        params.height = buttonHeight;
        params.setMargins(marginSize, marginSize, marginSize, marginSize);

        button.setLayoutParams(params);

        return button;
    }
    private MaterialButton createAddDoorbellButton(Context context){
        MaterialButton button = createStyledDoorbellButton(context, "Add Doorbell");

        int padding = (int) (ViewUtils.dpToPx(12, context));

        button.setPadding(padding, padding, padding, padding);
        button.setIcon(ContextCompat.getDrawable(context, R.drawable.plus_icon));
        button.setIconSize((int) (ViewUtils.dpToPx(24, context)));
        button.setIconTint(null);
        return button;
    }
}