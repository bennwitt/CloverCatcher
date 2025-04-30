# Last modified: 2024-12-08 11:08:48
# Version: 0.0.4
import json
import time
from functools import wraps
import sys
import os
import re
from datetime import datetime


def getNowDateTime():
    """
    Returns the current date and time.
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def getSeason(month):
    """
    Returns the season for a given month.
    """
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Fall"


def getNowDateTimeDayMonthSeason():
    """
    Returns the current date and time, including the month name, day of the week, and season.
    """
    now = datetime.now()
    month_name = now.strftime("%B")
    day_of_week = now.strftime("%A")
    season = getSeason(now.month)

    return now.strftime(
        f"%Y-%m-%d %H:%M:%S, {day_of_week}, {month_name}, Season: {season}"
    )


def getFileDateTime(fullFilePath):
    """
    Returns the created date and time, and the last modified date and time of a file.

    :param file_path: Path to the file
    :return: Tuple containing created and modified date and time as strings
    """
    if not os.path.exists(fullFilePath):
        return "File does not exist", "File does not exist"

    createdTime = os.path.getctime(fullFilePath)
    modifiedTime = os.path.getmtime(fullFilePath)

    createdDatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(createdTime))
    modifiedDatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modifiedTime))

    return createdDatetime, modifiedDatetime


# single function timer at a time.
def timerFunction(func):
    """
    Decorator to measure the execution time of a function.

    :param func: Function to measure
    :return: Wrapped function that prints the execution time
    """

    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        endTime = time.time()
        elapsedTime = endTime - startTime
        formattedTime = (
            time.strftime("%H:%M:%S", time.gmtime(elapsedTime))
            + f".{int((elapsedTime % 1) * 1000):03d}"
        )
        print(f"Execution time: {func.__name__} {formattedTime}")
        return result

    return wrapper


# Example usage
# @timer_function
# def sample_function():
#    time.sleep(2)  # Simulate a function that takes 2 seconds to run
# put on top of function


# Timer for multiple Functions at once
# Dictionary to store execution times
execution_times = {}


def timer_function(func):
    """
    Decorator to measure the execution time of a function and store it.

    :param func: Function to measure
    :return: Wrapped function that prints the execution time
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        endTime = time.time()
        elapsedTime = endTime - startTime
        formattedTime = (
            time.strftime("%H:%M:%S", time.gmtime(elapsedTime))
            + f".{int((elapsedTime % 1) * 1000):03d}"
        )
        print(f"Execution time of {func.__name__}: {formattedTime}")
        execution_times[func.__name__] = formattedTime
        return result

    return wrapper


# Example usage
# @timer_function
# def sample_function_1():
#    time.sleep(2)  # Simulate a function that takes 2 seconds to run

# @timer_function
# def sample_function_2():
#    time.sleep(3)  # Simulate a function that takes 3 seconds to run

# Call the functions
# sample_function_1()
# sample_function_2()

# Print stored execution times
# for func_name, exec_time in execution_times.items():
#    print(f"{func_name}: {exec_time}")
