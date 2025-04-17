#!/bin/bash
cd G:/project/python_door
COMMAND=1
python -c "import win32file; h=win32file.CreateFile(r'\\\\.\\pipe\\doorpipe', win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None); win32file.WriteFile(h, bytes('$COMMAND', 'utf-8')); win32file.CloseHandle(h)"