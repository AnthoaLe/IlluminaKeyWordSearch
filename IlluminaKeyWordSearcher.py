# IlluminaKeyWordSearcher.py

import csv                                          # Used to read and write csv files
import PySimpleGUI as sg                            # Needed to create simple interactive GUIs
import os                                           # Helps when working with folder and file paths
from datetime import datetime, timezone, timedelta  # Immensely useful for anything regarding dates and time
import re                                           # Simplifies some string operations by utilizing patterns
from typing import Tuple, List                      # Personal preference, helps with function syntax


def findFirstFindLastDates(filePath: str, firstKeyWord: str, lastKeyWord: str) -> Tuple[str, str]:
    """Finds the first occurrence of firstKeyWord and last occurrence of lastKeyWord.

    filePath - (string) - the path of the file.
    firstKeyWord - (string) - the first key word we are interested in.
    lastKeyWord - (string) - the last key word we are interested in.

    Given a file path to a tab delimited csv type file and two key words, search for the first \
    occurrence of the first keyword and the last occurrence of the last keyword. Return a 2-tuple \
    of strings which are the dates of the first, and last occurrence in ISO 8601 format.

    [1] If newline='' is not specified, newlines embedded inside quoted fields will not be interpreted \
    correctly, and on platforms that use \r\n line endings on write an extra \r will be added. It should \
    always be safe to specify newline='', since the csv module does its own (universal) newline handling.
    """

    firstDate = None                # Will use to check that the first occurrence and last occurrence
    lastDate = None                 # actually exist.
    # mode='r' reads the file with UTF-8 BOM encoding
    with open(filePath, mode='r', encoding='utf-8-sig', newline='') as csvDataFile:     # [1]
        csvReader = csv.reader(csvDataFile, delimiter='\t')                 # csv.reader of tab delimited file
        for line in csvReader:                                              # Read each line
            if firstKeyWord in line[3]:                                     # Index 3 is the message contents
                firstDate = line[0]                                         # Index 0 is the date
                break;                                                      # Only care about first occurrence
        for line in csvReader:
            if lastKeyWord in line[3]:
                lastDate = line[0]                                          # Care about the last occurrence

    return (firstDate, lastDate)


def userInputWindowLayOut() -> sg.Window:
    """Creates an interactive window and returns the Window object.

    Contains the data for the layout of a PySimpleGUI window. Creates the window using the layout \
    information and returns it as a PySimpleGUI.Window object.
    """

    layout = [[sg.Text("Select a folder containing all of the log reports")],
              [sg.Text("File(s)", size=(10, 1)), sg.Input(visible=False, key='-FILES-'),
               sg.FilesBrowse(button_text='Browse',enable_events=True)],
              [sg.Text("Input the first keyword to search for the first occurrence")],
              [sg.Text("Key Word 1", size=(10, 1)), sg.Input(default_text="ix_lgm_power_set_blocking",
                                                             key='-FIRSTKEYWORD-')],
              [sg.Text("Input the last keyword to search for the last occurrence")],
              [sg.Text("Key Word 2", size=(10, 1)), sg.Input(default_text="ix_lgm_power_rsp",
                                                             key='-LASTKEYWORD-')],
              [sg.Submit(button_text="Search", tooltip="Runs a search with the given parameters"),
               sg.Exit(tooltip="Closes and exits the program")]]

            # 'ix_lgm_power_set_blocking' and 'ix_lgm_power_rsp' are set as default values for
            # key word 1 and key word 2. EDIT LATER

    return sg.Window('Key Words Search', layout)        # Window is titled, and has the given layout


def formatTime() -> str:
    """Finds the system's local time and returns it adjusted against UTC+00.

    Create an 'aware,' meaning it contains timezone information to locate itself relative to other \
    'aware' objects, datetime object with respect to system's local time. Returns the date and time \
    as a string in ISO 8601 format: YYYY-MM-DDTHHMMSSZ.
    """

    localTime = datetime.now(timezone.utc).astimezone()         # Local time with respect to UTC+00

    # Replaced ':' with '' as we are later using this information to name and date the Time Stamp file.
    return localTime.isoformat(timespec='seconds').replace(':', '')


def readLogs(listOfLogStringPaths: list, firstKeyWord: str, lastKeyWord: str) -> List[Tuple[str, str]]:
    """Given a list of log file string paths and two keywords, creates and returns a list of \
    all of the occurrences of the two keywords (first occurrence and last occurrence respectively).

    listOfLogStringPaths - (list) - list of string paths to selected log files.
    firstKeyWord - (string) - the first key word we are interested in.
    lastKeyWord - (string) -the last key word we are interested in.

    Iterate through the log files string paths in the given list calling findFirstFindLastDates() on each log.
    Store each set of occurrences and return a list of 2-tuples of the first and last occurrences.
    """

    listOfOccurrences = []
    for logStringPath in listOfLogStringPaths:
        if os.path.isfile(logStringPath) and logStringPath.endswith('.log'):  # ensures path is to a .log file
            occurrence = findFirstFindLastDates(logStringPath, firstKeyWord, lastKeyWord)
            if None not in occurrence:  # checks that both occurrences exist
                listOfOccurrences.append(occurrence)
        # with os.scandir(logStringPath) as logFile:
        #     for logFile in filePath:               # iterates over the log files in the directory
        #         if logFile.is_file() and logFile.name.endswith('.log'):     # ensures logFile is a .log file
        #             occurrence = findFirstFindLastDates(logFile, firstKeyWord, lastKeyWord)
        #             if None not in occurrence:      # checks that both occurrences exist
        #                 listOfOccurrences.append(occurrence)

    return listOfOccurrences    # returns a list of 2-tuples containing the string dates of the occurrences


def findTimeDifference(occurrence: Tuple[str, str]) -> timedelta:
    """Given 2 string dates convert and return a timedelta object.

    occurrence - (Tuple[str, str]) - 2-tuple of the dates of both occurrences in string ISO 8601 format.

    Given the 2-tuple of string dates, convert them into a list of ints in date and time format: \
    [year, month, day, military hour, minutes, seconds, milliseconds] \
    Must adjust values due to year inputs being the last 2 digits of the current year (+2000) and \
    given milliseconds (*1000). Creates two datetime objects and returns the difference between the \
    two as a timedelta object.
    """

    # slice the string [:-4] to remove the UTC offset which is format: ' +00'
    # split the string into a list with delimiters: '-', ':', '.', ' '
    # newly split string should be in the date and time format:
    # [year, month, day, military hour, minutes, seconds, milliseconds]
    stringListOfFirst = re.split('-|:|\.| ', occurrence[0][:-4])    # list of strings in date and time format
    stringListOfLast = re.split('-|:|\.| ', occurrence[1][:-4])
    # re.split creates a list of strings, must convert into a list of ints
    intListOfFirst = [int(timeValue) for timeValue in stringListOfFirst]    # convert values to ints
    intListOfSecond = [int(timeValue) for timeValue in stringListOfLast]
    intListOfFirst[0] += 2000       # Given input is the last 2 digits of the current year
    intListOfSecond[0] += 2000      # Convert by adding 2000
    intListOfFirst[6] *= 1000       # Given input is milli (10^-3), but requested units is micro (10^-6)
    intListOfSecond[6] *= 1000      # Convert by multiplying by 10^3
    firstDateTime = datetime(*intListOfFirst)       # unpack list and create datetime class object
    lastDateTime = datetime(*intListOfSecond)
    # !!!
    # ASSUMES LAST DATE ALWAYS OCCURS AFTER FIRST DATE
    # !!!
    return lastDateTime - firstDateTime             # Difference is timedelta object


def writeTimeStampsToFile(listOfOccurrences: List[Tuple[str, str]]) -> None:
    """Given a list of occurrences write the differences in time to a text file.

    listOfOccurrences - (List[Tuple[str, str]]) - list of 2-tuples containing the string dates of the \
    occurrences.

    Creates an output text file in the current working directory named "Time Stamps YYYY-MM-DDTHHMMSSZ.txt" \
    with UTF BOM encoding. Iterates over each occurrence, calls findTimeDifference() to create a timedelta \
    object and typecasts the timedelta object to a string, which returns a difference in time in ISO 8601 \
    format. Finally, it writes the difference in time to the output text file.

    [1] If newline='' is not specified, newlines embedded inside quoted fields will not be interpreted \
    correctly, and on platforms that use \r\n line endings on write an extra \r will be added. It should \
    always be safe to specify newline='', since the csv module does its own (universal) newline handling.
    """

    outputTextFile = "Time Stamps " + formatTime() + ".txt"       # Generates the name of the text file
    # mode='x' creates a new file and prepares to write into it with UTF-8 BOM encoding
    with open(outputTextFile, mode='x', encoding='utf-8-sig', newline= '') as outputTextFile:   # [1]
        for occurrence in listOfOccurrences:                # Iterates over the occurrences in each file
            # Writes the time difference to the file and separates each one with newline character '\n'
            outputTextFile.write(str(findTimeDifference(occurrence)) + '\n')


def runGUIWindow() -> None:
    """a"""

    window = userInputWindowLayOut()
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Search':
            selectedFiles = values['-FILES-'].split(';')
            firstKeyWord = values['-FIRSTKEYWORD-']
            lastKeyWord = values['-LASTKEYWORD-']
            listOfOccurrences = readLogs(selectedFiles, firstKeyWord, lastKeyWord)
            writeTimeStampsToFile(listOfOccurrences)


if __name__ == "__main__":
    runGUIWindow()