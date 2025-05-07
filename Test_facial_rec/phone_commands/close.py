#########################################################
#
#  Code to send "Close door" command to middleman
#
#########################################################

from pathlib import Path

command_file = Path(__file__).parent.parent / "command.txt"

with open(command_file, "w") as f:
    f.write("2")
