package com.example.knockly.indvDoorbellPage;

import android.content.Context;
import android.os.Bundle;

import androidx.appcompat.widget.Toolbar;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.constraintlayout.widget.ConstraintSet;
import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;

import com.example.knockly.R;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LiveFeedFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LiveFeedFragment extends Fragment {

    // the fragment initialization parameters for doorbellID
    private static final String ARG_DOORBELL_ID = "000000";

    private String mDoorbellID;
    private boolean liveFeedExpanded = false;
    private FragmentCallback callback;

    // Interface to get functions from main activity
    public interface FragmentCallback{
        void expandLiveFeed();
        void shrinkLiveFeed();
    }

    public LiveFeedFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param doorbellID Parameter 1.
     * @return A new instance of fragment LiveFeedFragment.
     */
    public static LiveFeedFragment newInstance(String doorbellID) {
        LiveFeedFragment fragment = new LiveFeedFragment();
        Bundle args = new Bundle();
        args.putString(ARG_DOORBELL_ID, doorbellID);
        fragment.setArguments(args);
        return fragment;
    }

    // Send activity functions to interface
    @Override
    public void onAttach(Context context){
        super.onAttach(context);

        try{
            callback = (FragmentCallback) context;
        }
        catch(ClassCastException e){
            // Error that will occur if activity does not implement the interface methods
            throw new ClassCastException(context.toString()
                    + " must implement FragmentCallback interface");
        }
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mDoorbellID = getArguments().getString(ARG_DOORBELL_ID);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        View view = inflater.inflate(R.layout.fragment_live_feed, container, false);

        ImageButton changeViewButton = view.findViewById(R.id.changeViewButton);
        Toolbar toolbar = view.findViewById(R.id.toolbar);
        ConstraintLayout feed = view.findViewById(R.id.FeedLayout);
        ConstraintLayout fragment = view.findViewById(R.id.LiveFeedFrame);
        changeViewButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (liveFeedExpanded){
                    shrinkFeed(changeViewButton, toolbar, feed, fragment);
                }
                else{
                   expandFeed(changeViewButton, toolbar, feed, fragment);
                }
                liveFeedExpanded = !liveFeedExpanded;
            }
        });

        return view;
    }

    // Prevent memory leaks by removing callback when fragment is destroyed
    @Override
    public void onDetach(){
        super.onDetach();
        callback = null;
    }

    private void shrinkFeed(ImageButton changeViewButton, Toolbar toolbar, ConstraintLayout feed, ConstraintLayout fragment){
        // Add other fragments back to the activity
        callback.shrinkLiveFeed();
        // Change the arrows on the button
        changeViewButton.setImageResource(R.drawable.fullscreen_arrows);

        // Stop toolbar hovering over feed
        // Reset elevation and z value
        toolbar.setElevation(0f);
        toolbar.setZ(10f);

        // Make toolbar opaque again
        toolbar.getBackground().setAlpha(255);

        // Reset constraints
        ConstraintSet constraints = new ConstraintSet();
        constraints.clone(fragment);
        constraints.clear(R.id.FeedLayout, ConstraintSet.TOP);
        constraints.clear(R.id.FeedLayout, ConstraintSet.BOTTOM);
        constraints.connect(R.id.FeedLayout, ConstraintSet.TOP, R.id.toolbar, ConstraintSet.BOTTOM);
        constraints.connect(R.id.FeedLayout, ConstraintSet.BOTTOM, ConstraintSet.PARENT_ID, ConstraintSet.BOTTOM);
        constraints.connect(R.id.FeedLayout, ConstraintSet.BOTTOM, ConstraintSet.PARENT_ID, ConstraintSet.BOTTOM);
        constraints.constrainHeight(R.id.FeedLayout, ConstraintSet.WRAP_CONTENT);
        constraints.constrainPercentWidth(R.id.toolbar, 1f);
        constraints.applyTo(fragment);

        // Move toolbar back up
        ViewGroup.MarginLayoutParams params = (ViewGroup.MarginLayoutParams) toolbar.getLayoutParams();
        params.topMargin = 0;
        toolbar.setLayoutParams(params);
    }

    private void expandFeed(ImageButton changeViewButton, Toolbar toolbar, ConstraintLayout feed, ConstraintLayout fragment){
        // Remove other fragments from the activity
        callback.expandLiveFeed();

        // Change arrows on the button
        changeViewButton.setImageResource(R.drawable.minimize_arrows);

        // Make toolbar hover over feed
        // Increase z of toolbar so it sits on top
        toolbar.setElevation(16f);

        // Make toolbar slightly transparent
        toolbar.getBackground().setAlpha(225);

        // Edit constraints
        ConstraintSet constraints = new ConstraintSet();
        constraints.clone(fragment);
        constraints.clear(R.id.FeedLayout, ConstraintSet.TOP);
        constraints.connect(R.id.FeedLayout, ConstraintSet.TOP, ConstraintSet.PARENT_ID, ConstraintSet.TOP);
        constraints.constrainPercentWidth(R.id.toolbar, 0.9f);
        constraints.applyTo(fragment);

        // Set z of feed so it sits under toolbar
        toolbar.setZ(10f);

        // Move toolbar down so it looks more like it is hovering
        ViewGroup.MarginLayoutParams params = (ViewGroup.MarginLayoutParams) toolbar.getLayoutParams();
        params.topMargin = 100;
        toolbar.setLayoutParams(params);
    }
}