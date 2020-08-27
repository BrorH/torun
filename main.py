import sys
import time
import os
import subprocess


def usr_name():
    proc = subprocess.run(["pwd"], stdout=subprocess.PIPE)
    path = proc.stdout.decode("utf-8")
    usr = path.split("/")[2]
    return usr


tasksPath = f"/home/{usr_name()}/.local/share/evolution/tasks/system/tasks.ics"


def get_script_ext(scriptname):
    """Returns the script extension.
    This function is usefull if we wish to support several programming languanges"""
    try:
        if scriptname[-3:] == ".py":
            return "python"
    except IndexError:
        return


def readTasks():
    """Reads the tasks.ics file and returns all its content"""
    with open(tasksPath, "r+") as file:
        lines = file.readlines()
    return lines


def parseTasks():
    """Parses the lines from the tasks.ics file and for each todo-list returns three objects:
        (1) program name, (2) activation status, (3) program code,
    """
    lines = readTasks()
    parsed = []
    subparse = {}
    statusDict = {"COMPLETED": 1, "NEEDS-ACTION": 0}
    iterable = iter(enumerate(lines))
    for i, line in iterable:
        if "SUMMARY:" in line:
            subparse["name"] = line[8:-1]  # drop search-key and newline
        elif "STATUS:" in line:
            subparse["status"] = statusDict[line[7:-1]]  # drop search-key and newline
        elif "DESCRIPTION:" in line:
            # if the program is multi-lined, we need to know where the code stops
            j = 1
            while True:
                if "END:VTODO" in lines[i + j]:
                    break
                j += 1
            program_text = ""
            for a in lines[i : i + j]:
                program_text += a[:-1]  # drop newline
            program_text = (
                program_text.replace("\\n", "§").replace("\\", "").replace("§", "\\n")
            )
            subparse["code"] = program_text[12:]
        if len(subparse) == 3:
            parsed.append(subparse)
            subparse = {}
    return sorted(parsed, key=lambda i: i["name"])


def retrieve_activated_program(prev_allPrograms):
    """ When a program is activated, we need to know which one has been activated.
        This function returns a tuple that contains (1) the filename, and (2) the program code.
        The current parse is compared to the passed parse of earlier programs to locate with program has been toggled
    """
    allPrograms = parseTasks()
    # print(allPrograms)
    for i, program in enumerate(allPrograms):
        if prev_allPrograms[i]["status"] != program["status"] == 1:
            return program


def retrieve_all_active_programs():
    """ Returns a list of all programs that are currently active"""
    allPrograms = parseTasks()
    programsToRun = []
    for i, program in enumerate(allPrograms):
        if program["status"] == 1:
            programsToRun.append(program)
    return programsToRun


def create_and_fill_script(parsed):
    scriptname = parsed["name"]
    scriptcode = parsed["code"]
    with open(f"{scriptname}", "w+") as script:
        for line in scriptcode.split("\\n"):
            script.write(line + "\n")


def run_script(scriptname):
    ext = get_script_ext(scriptname)
    if ext == "python":
        subprocess.run(["python3", scriptname])
        subprocess.run(["rm", scriptname])


def loop():
    # the main loop.
    # prevparse is the previous parse with a activation toggle, needed to find which program was toggled
    size = os.path.getsize(tasksPath)
    prev_allPrograms = parseTasks()
    while True:
        if size != os.path.getsize(tasksPath):
            activated_program = retrieve_activated_program(prev_allPrograms)
            if (
                activated_program
            ):  #  is None if program was turned off instead of activated
                create_and_fill_script(activated_program)
                run_script(activated_program["name"])
            prev_allPrograms = parseTasks()
            size = os.path.getsize(tasksPath)
        time.sleep(0.2)


def init():
    # initiallizes the code. Any program that is checked, has to be run
    all_active_programs = retrieve_all_active_programs()
    if len(all_active_programs) > 0:
        for program in all_active_programs:
            create_and_fill_script(program)
            run_script(program["name"])


init()
loop()

