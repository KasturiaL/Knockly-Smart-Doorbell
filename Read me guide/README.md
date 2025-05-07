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