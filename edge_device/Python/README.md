# Python

## Setup

You will need to have set up the Arduino according to the README file there, and have connected the Arduino to the Pi itself for the system to recognize the Arduino.

You will need to have activated the API on your system so that the Python script can run the notification system correctly.

## Usage

Please run these bash scripts in /edge_device/Startup Scripts in this sequence as to ensure every single component works:

1. ngrok.sh
2. uvicorn.sh
3. auto.sh

While the system is in use, the ranger must be placed sensor down so that the system will not trigger the alarm function (or change the disableAlarm flag to true).

The message outputs will be sent to the Serial Monitor in the Arduino IDE and the auto.sh terminal as well if you want to see them somewhere other than the log.txt.

The button on D4 is the button that triggers the open and close cycle of the door.

The button on D8 is the button that triggers the doorbell ring.

## Common Problems

**Arduino not detected by system?**

It may be a hardware issue on the Arduino, you will need to buy a new Arduino, or you may have changed the setup code in the Arduino and/or the Python code.

**System displays "Device busy" error?**

You may have already have a program running the camera and will need to stop that program.

**There seems to be a file flickering in the directory when the system is running?**

That is just the system creating and deleting the command.txt file to send commands from the facial recogition or the app to the python loop.

**The system still recognizes a face even though I deleted the face video from the processed_videos folder?**

The face id encodings are stored on the database on the pi.

**The system is not training off of the video I sent from my phone?**

You may have named the video with an existing name in processed_videos.