# Group Project Repository

This repository is the main folder where our group stores all the nessesary scripts and files that we made in this group project.

## How we organized our code

For the sake of us not confusing which folder belongs to which team, we made multiple folders with the names of different sections. That was, we would not add code from our team to another part.

For the edge_device folder, we split the folder into sections of Python and Arduino since they are techincally different types of projects. We did try to split the notification script from the main python code, but we weren't able to split the facial recogntion since we merge them together without thinking fo the future.

## Folder directory

```
> api
    - Files related to the API

> docs
    - Texts files, PDFs and other documentation for the group project (no effect on scripts)

> edge_device
    - Files related to the doorbell hardware

    > Arduino
        - Arduino file for the doorbell

    > Databases
        - SQL file for the database

    > Live Feed
        - Files for the live feed

    > Python
        - Python files and required libraries for the doorbell

    > Startup Scripts
        - Bash files that could automate the activation process of the doorbell

> mobile_app
    - Files to build and the run associated app

> README.md
```

## Usage

There are 3 main aspects to the system:
- The doorbell
- The app
- The API

Each of these aspects must be run for the system to work. For more details on how to set these up please see their individual READ ME files linked below:
- Doorbell > Arduino - [README](edge_device/Arduino/README.md)
- Doorbell > Python - [README](edge_device/Python/README.md)
- App - [README](mobile_app/README.md)
- API - [README](api/README.md)


If the system runs correctly, it should be able to:

1. Open or close the door with the buttons in the app
2. See a live feed of the doorbell from the app
3. Ring the doorbell tune when the doorbell button is pressed
4. Open and close the door in a cycle when the manual override button is pressed/ when a stored face is recognised by the facial recognition system
5. Add a face from the app for the doorbell to recognise
6. Ring an alarm when the ultrasonic ranger senses a distance equal or larger than 3 centimetres between the ranger and the closest object in front of it

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

**Notifications not sending to the app?**

The 'Receive Motion Notifs' setting may not be turned on in the app

**Not getting a live feed?**

You may have not connected your phone to the same network as the doorbell.

**Not able to login to the app?**

You may have not activated the ngrok.sh and uvicorn.sh scripts.

**The alarm is not ringing when the closest object is too far?**

That is a hardware limit on the ultrasonic ranger that we could not fix.

**Unable to connect to the doorbell/Can't send commands from the phone to the doorbell?**

You may have not connected your phone to the same network as the doorbell.