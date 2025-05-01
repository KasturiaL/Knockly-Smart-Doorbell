package com.example.knockly.utils;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class PermissionUtils {
    public static boolean hasNotifPerms(Context context){
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return false;
        }
        return true;
    }

    public static void getNotifPerms(Activity activity){
        ActivityCompat.requestPermissions(activity,
                new String[]{
                        Manifest.permission.POST_NOTIFICATIONS,
                }, 100);
    }
}
