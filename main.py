import sys
import time
import os
import subprocess

"""
todo:
-check/uncheck runs program
-check for file format and run appropriately
-open terminal on check/uncheck
-delete file after running
-unchecking program kills the process
"""

path = "/home/bror/.local/share/evolution/tasks/system/tasks.ics"


def run():
    with open(path, "r+") as file:
        data = file.readlines()

    for i, dat in enumerate(data):
        if "DESCRIPTION:" in dat:
            code = data[i][12:].strip().split("\\n")
        if "SUMMARY:" in dat:
            program = data[i][8:-1]
    with open(f"{program}", "w+") as file:
        for line in code:
            file.write(f"{line}\n")
    subprocess.run(["python3", program])


# prototype for check-loop
size = os.path.getsize(path)
while True:
    if size != os.path.getsize(path):
        print("CHECK!")
        run()
        size = os.path.getsize(path)
    time.sleep(0.2)

# args = [int(a) for a in sys.argv[1:]]


print(code)
print(program)
