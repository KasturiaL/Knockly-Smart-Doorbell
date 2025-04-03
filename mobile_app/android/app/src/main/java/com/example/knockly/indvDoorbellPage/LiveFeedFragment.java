package com.example.knockly.indvDoorbellPage;

import android.content.Context;
import android.os.Bundle;

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
        changeViewButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (liveFeedExpanded){
                    callback.shrinkLiveFeed();
                    changeViewButton.setImageResource(R.drawable.fullscreen_arrows);
                }
                else{
                    callback.expandLiveFeed();
                    changeViewButton.setImageResource(R.drawable.minimize_arrows);
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
}