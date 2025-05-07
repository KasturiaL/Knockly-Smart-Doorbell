Requirments for README.md

1. Explain how we organized the code
2. Explain folder/file structures
3. Add details of any 3rd party software and framework

*Should have sufficient details so that a 3rd party can replicate our iot system without any misunderstandings*

# Group Project Repository

This repository is the main folder where our group stores all the nessesary scripts and files that we made in this group project.

## How we organized our code

For the sake of us not confusing which folder belongs to which team, we made multiple folders with the names of different sections. That was, we would not add code from our team to another part.

For the edge_device folder, we split the folder into sections of Python and Arduino since they are techincally different types of projects. We did try to split the notification script from the main python code, but we weren't able to split the facial recogntion since we merge them together without thinking fo the future.

## Folder directory

> api
    - Files related to the API (refer to README.md there for more information)

> docs
    - Texts files, PDFs and other files for the group project (no effect on scripts)

> edge_device
    - Files related to the doorbell

    > Arduino
        - Arduino file for the doorbell

    > Python
        - Python files and required libraries for the doorbell

    > Startup Scripts
        - Bash files that could automate the activation process of the doorbell

> mobile_app
    - Files related to the app (refer to README.md there for more information)

> README.md

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