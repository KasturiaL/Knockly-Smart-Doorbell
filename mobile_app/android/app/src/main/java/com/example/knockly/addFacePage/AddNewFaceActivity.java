package com.example.knockly.addFacePage;

import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.knockly.R;
import com.example.knockly.shared.PageHeaderFragment;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import org.apache.commons.net.ftp.FTP;
import org.apache.commons.net.ftp.FTPClient;

import java.io.File;
import java.io.FileInputStream;


public class AddNewFaceActivity extends AppCompatActivity {

    private static final int VIDEO_REQUEST = 101; // just an ID to recognize the video intent later
    private EditText etName;
    private File savedVideoFile;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_add_new_face);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Add header fragment
        PageHeaderFragment pageHeader = PageHeaderFragment.newInstance("Add Face", true, true);
        getSupportFragmentManager().beginTransaction().replace(R.id.AddFaceHeaderFragment, pageHeader).commit();

        // request camera and mic permissions (REALLY important or nothing works)
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this,
                    new String[]{
                            Manifest.permission.CAMERA,
                            Manifest.permission.RECORD_AUDIO
                    }, 1); // 1 is the request code we just made up
        }

        etName = findViewById(R.id.etName); // input field for the user to type their name
        Button btnRecord = findViewById(R.id.btnRecord);
        Button btnUpload = findViewById(R.id.btnUpload);

        // record when record button is clicked
        btnRecord.setOnClickListener(v -> recordVideo());

        // upload when upload button is clicked
        btnUpload.setOnClickListener(v -> uploadToFTP());
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == VIDEO_REQUEST) {
            if (resultCode == RESULT_OK) {
                Toast.makeText(this, "Video saved successfully.", Toast.LENGTH_SHORT).show();
                // optionally: enable the upload button here if you want
            } else if (resultCode == RESULT_CANCELED) {
                Toast.makeText(this, "Video recording cancelled.", Toast.LENGTH_SHORT).show();
                savedVideoFile = null; // clear the file if recording was canceled
            } else {
                Toast.makeText(this, "Failed to record video.", Toast.LENGTH_SHORT).show();
                savedVideoFile = null;
            }
        }
    }

    // This method launches the camera to record a video
    private void recordVideo() {
        String name = etName.getText().toString().trim(); // grab name from the input field
        if (name.isEmpty()) {
            Toast.makeText(this, "Enter a name first", Toast.LENGTH_SHORT).show(); // no name? no go.
            return;
        }

        // create or get directory in app's private Movies folder for our videos
        File dir = new File(getExternalFilesDir(Environment.DIRECTORY_MOVIES), "FaceVideos");
        if (!dir.exists()) dir.mkdirs(); // make sure directory exists

        savedVideoFile = new File(dir, name + ".mp4"); // create a file for the new video

        // Android requires FileProvider to safely share file URIs with other apps (like camera)
        Uri videoUri = FileProvider.getUriForFile(
                this,
                getPackageName() + ".provider", // must match the provider set in manifest
                savedVideoFile
        );

        Intent intent = new Intent(MediaStore.ACTION_VIDEO_CAPTURE); // open default camera
        intent.putExtra(MediaStore.EXTRA_DURATION_LIMIT, 30); // limit video to 30 seconds
        intent.putExtra(MediaStore.EXTRA_OUTPUT, videoUri); // save directly to our file
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);

        // start camera intent
        startActivityForResult(intent, VIDEO_REQUEST);
    }

    // this uploads the video we just recorded to our Raspberry Pi via FTP
    private void uploadToFTP() {
        // check if we even have a video file to upload
        if (savedVideoFile == null || !savedVideoFile.exists()) {
            Toast.makeText(this, "Record a video first", Toast.LENGTH_SHORT).show();
            return;
        }

        // use a separate thread for FTP because we don’t wanna block the UI
        new Thread(() -> {
            try {
                FTPClient ftp = new FTPClient();

                // FTP server info (this should match Pi’s settings)
                String ftpHost = "192.168.0.18"; // IP of Raspberry Pi
                int ftpPort = 2121;
                String ftpUser = "pi";
                String ftpPass = "raspberry";

                ftp.connect(ftpHost, ftpPort);
                boolean login = ftp.login(ftpUser, ftpPass); // try to log in

                if (!login) throw new Exception("FTP login failed.");

                ftp.enterLocalActiveMode(); // passive mode is usually safer for mobile uploads
                ftp.setFileType(FTP.BINARY_FILE_TYPE); // binary = raw file mode, good for video

                // upload the actual file
                FileInputStream fis = new FileInputStream(savedVideoFile);
                boolean success = ftp.storeFile("/" + savedVideoFile.getName(), fis); // uploads it
                fis.close();
                ftp.logout(); // done
                ftp.disconnect();

                // update UI based on upload result
                runOnUiThread(() -> {
                    if (success) {
                        Toast.makeText(AddNewFaceActivity.this, "Upload Successful", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(AddNewFaceActivity.this, "Upload Failed", Toast.LENGTH_SHORT).show();
                    }
                });

            } catch (Exception e) {
                e.printStackTrace();
                // show error message on the UI if something goes wrong
                runOnUiThread(() ->
                        Toast.makeText(AddNewFaceActivity.this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show()
                );
            }
        }).start(); // don’t forget to start the thread!
    }

}