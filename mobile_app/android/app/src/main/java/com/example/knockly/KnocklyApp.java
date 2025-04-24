package com.example.knockly;

import android.app.Application;

import com.example.knockly.utils.LoginManager;

// Custom application file to set up app wide components
public class KnocklyApp extends Application {

    // Runs when app starts to initialise any singletons etc.
    @Override
    public void onCreate(){
        super.onCreate();
        LoginManager.getInstance(this);
    }
}
