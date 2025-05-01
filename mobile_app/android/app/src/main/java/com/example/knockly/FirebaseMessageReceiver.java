import android.util.Log;

import androidx.annotation.NonNull;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

// Code adapted from Geeks for Geeks. 2025. How to Push Notification in Android using Firebase Cloud Messaging?
// Available at https://www.geeksforgeeks.org/how-to-push-notification-in-android-using-firebase-cloud-messaging/

public class FirebaseMessageReceiver extends FirebaseMessagingService {

    // Override onNewToken to get new token
    @Override
    public void onNewToken(@NonNull String token)
    {
        Log.d("Firebase Message Reciever", "Refreshed token: " + token);
    }

    // Override onMessageReceived() method to extract the
    // title and
    // body from the message passed in FCM
    @Override
    public void
    onMessageReceived(RemoteMessage remoteMessage) {
        // First case when notifications are received via
        // data event
        // Here, 'title' and 'message' are the assumed names
        // of JSON
        // attributes. Since here we do not have any data
        // payload, This section is commented out. It is
        // here only for reference purposes.
        if(remoteMessage.getData().size()>0){
            String title = remoteMessage.getData().get("title");
            String message = remoteMessage.getData().get("message");
        }

        }
    }
}