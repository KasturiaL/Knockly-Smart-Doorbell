package com.example.knockly.utils;

import android.content.Context;

public class ViewUtils {
    public static float dpToPx(float dp, Context context){
        return dp * context.getResources().getDisplayMetrics().density;
    }
}
