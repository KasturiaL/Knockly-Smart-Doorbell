package com.example.knockly.indvDoorbellPage;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.example.knockly.R;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LiveFeedFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LiveFeedFragment extends Fragment {

    // the fragment initialization parameters for doorbellID
    private static final String ARG_DOORBELL_ID = "000000";

    private String doorbellID;

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

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            doorbellID = getArguments().getString(ARG_DOORBELL_ID);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_live_feed, container, false);
    }
}