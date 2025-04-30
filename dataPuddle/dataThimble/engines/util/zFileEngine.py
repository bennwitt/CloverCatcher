# Last modified: 2025-03-31 23:12:35
# Version: 0.0.22
import time
import os
import csv
import re
import uuid

import xml.etree.ElementTree as ET
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from collections import defaultdict


def writeToFile(fullFilePath, content):
    with open(fullFilePath, "a") as loggerfile:
        loggerfile.write(content + "\n")
        loggerfile.close()
    return fullFilePath


def list_all_files(folder_path):
    return [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]


def list_all_folders(folder_path):
    return [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, f))
    ]


def list_files_recursive(folder_path):
    file_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def find_files_by_extension(folder_path, extension):
    return [f for f in list_files_recursive(folder_path) if f.endswith(extension)]


def count_files_by_extension(folder_path, extension):
    return len(find_files_by_extension(folder_path, extension))


def search_file_by_name(folder_path, file_name):
    for root, _, files in os.walk(folder_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None


def get_folder_structure(folder_path):
    folder_dict = {}
    for root, dirs, files in os.walk(folder_path):
        folder_dict[root] = {"folders": dirs, "files": files}
    return folder_dict


def get_file_attributes(file_path):
    return {
        "size": os.path.getsize(file_path),
        "modified_time": os.path.getmtime(file_path),
        "created_time": os.path.getctime(file_path),
        "absolute_path": os.path.abspath(file_path),
    }


def get_folder_size(folder_path):
    total_size = 0
    for file in list_files_recursive(folder_path):
        total_size += os.path.getsize(file)
    return total_size


def find_largest_file(folder_path):
    files = list_files_recursive(folder_path)
    largest_file = max(files, key=lambda f: os.path.getsize(f), default=None)
    return largest_file, os.path.getsize(largest_file) if largest_file else (None, 0)


def find_smallest_file(folder_path):
    files = list_files_recursive(folder_path)
    smallest_file = min(files, key=lambda f: os.path.getsize(f), default=None)
    return smallest_file, os.path.getsize(smallest_file) if smallest_file else (None, 0)


def count_files_in_folder(folder_path):
    return len(list_all_files(folder_path))


def count_folders_in_directory(folder_path):
    return len(list_all_folders(folder_path))


def find_empty_folders(folder_path):
    empty_folders = []
    for root, dirs, files in os.walk(folder_path):
        if not dirs and not files:
            empty_folders.append(root)
    return empty_folders


def get_recently_modified_files(folder_path, days):
    cutoff_time = time.time() - (days * 86400)
    return [
        f
        for f in list_files_recursive(folder_path)
        if os.path.getmtime(f) > cutoff_time
    ]


def search_files_containing_text(folder_path, search_text):
    matching_files = []
    for file in list_files_recursive(folder_path):
        try:
            with open(file, "r") as f:
                if search_text in f.read():
                    matching_files.append(file)
        except:
            continue
    return matching_files


def find_files_larger_than(folder_path, size_in_bytes):
    return [
        f
        for f in list_files_recursive(folder_path)
        if os.path.getsize(f) > size_in_bytes
    ]


def group_files_by_extension(folder_path):
    file_groups = defaultdict(list)
    for file in list_files_recursive(folder_path):
        ext = os.path.splitext(file)[1]
        file_groups[ext].append(file)
    return dict(file_groups)


def rename_files_in_folder(folder_path, new_name_prefix):
    for i, file in enumerate(list_all_files(folder_path)):
        ext = os.path.splitext(file)[1]
        new_name = os.path.join(folder_path, f"{new_name_prefix}_{i}{ext}")
        os.rename(file, new_name)


def get_folder_depth(folder_path):
    return max(
        len(os.path.relpath(root, folder_path).split(os.sep))
        for root, _, _ in os.walk(folder_path)
    )


def get_filenames_without_extensions(folder_path):
    return [
        os.path.splitext(os.path.basename(f))[0] for f in list_all_files(folder_path)
    ]


def get_file_extensions(folder_path):
    return [os.path.splitext(f)[1] for f in list_all_files(folder_path)]


def get_parent_folder(file_path):
    return os.path.basename(os.path.dirname(file_path))


def get_root_folder(folder_path):
    return os.path.abspath(folder_path).split(os.sep)[0]


def split_path_parts(file_path):
    return file_path.split(os.sep)


def construct_path(*parts):
    return os.path.join(*parts)


# Read a text file as a whole string
def openFileAsWhole(entry_file):
    with open(entry_file, "r") as file:
        filecontent = file.read()
    return filecontent


# Write content to a text file
def writeFile(entry_file, content):
    with open(entry_file, "w") as file:
        file.write(content)


# Append content to a text file
def appendToFile(entry_file, content):
    with open(entry_file, "a") as file:
        file.write(content)


# Read a CSV file as a list of rows
def readCsvFile(entry_file):
    with open(entry_file, "r") as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
    return rows


# Write rows to a CSV file
def writeCsvFile(entry_file, rows):
    with open(entry_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


# Append rows to a CSV file
def appendToCsvFile(entry_file, rows):
    with open(entry_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def saveListToCsv(dataList, outputCsvFilePath):
    try:
        with open(outputCsvFilePath, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(dataList)  # Write each list as a row

    except Exception as e:
        print(f"Error saving CSV: {e}")

        return


# Open an image file
def openImage(entry_file):
    return Image.open(entry_file)


# Save an image to a new file
def saveImage(image, output_file):
    image.save(output_file)


# Convert an image to grayscale and save
def convertImageToGrayscale(entry_file, output_file):
    image = Image.open(entry_file).convert("L")
    image.save(output_file)


# Read a PDF file and return its text content
def readPdfFile(entry_file):
    reader = PdfReader(entry_file)
    text = "".join(page.extract_text() for page in reader.pages)
    return text


# Write a new PDF file with specified text
def writePdfFile(output_file, text):
    writer = PdfWriter()
    writer.add_blank_page(width=210, height=297)  # Add a blank page
    with open(output_file, "wb") as file:
        writer.write(file)


# Append pages from one PDF to another
def appendToPdfFile(source_file, target_file):
    reader = PdfReader(source_file)
    writer = PdfWriter()
    writer.append(source_file)
    with open(target_file, "wb") as file:
        writer.write(file)


def getFilenameAndPath(fullPathOfFile):
    fileName = os.path.basename(fullPathOfFile)
    folderPath = os.path.dirname(fullPathOfFile)
    return folderPath, fileName


def openFileAsWhole(entry_file):
    with open(entry_file, "r") as file:
        filecontent = file.read()
    return


def openFileEachLine(entry_file):
    with open(entry_file, "r") as file:
        # Read all lines and exclude lines starting with '#' in the first three lines
        lines = file.readlines()
        filtered_content = "".join(
            line
            for i, line in enumerate(lines)
            if i > 2 or not line.strip().startswith("#")
        )
    return


def processYTCaptionToTranscript(mediaCaptionContents):
    try:
        root = ET.fromstring(mediaCaptionContents)
        captionText = ""
        for text_element in root.findall("text"):
            captionText += f" {text_element.text}"
            captionText = captionText.strip()
        return captionText

    except Exception as e:
        errtext = f"Error Processing Caption {e}"
        return errtext


def getListOfAllFileType(baseFolder, fileType):
    filePaths = []
    for root, dirs, files in os.walk(baseFolder):
        for theFileName in files:
            if theFileName.lower().endswith(fileType):
                theFilePath = os.path.join(root, theFileName)
                filePaths.append(theFilePath)
    fileNames = files
    return fileNames, filePaths


def saniFileNameText(dirtytext: str):
    pattern = r"[^0-9a-zA-Z\s_.-]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace(" ", "_")
    steriletext = cleanertext.replace("__", "_").lower()
    return steriletext


def cleanFileNamesRecursive(root_directory):
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if "$$$$" in filename:
                # Delete the file
                file_path = os.path.join(dirpath, filename)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                sanitized_name = saniFileNameText(filename)
                if sanitized_name != filename:
                    # Rename the file
                    original_path = os.path.join(dirpath, filename)
                    new_path = os.path.join(dirpath, sanitized_name)
                    os.rename(original_path, new_path)
                    print(f"Renamed: {original_path} -> {new_path}")


def collectPngFiles(directory):
    workItems = []
    png_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".png"):
                full_path = os.path.join(root, file)
                png_files.append(full_path)
    for i in png_files:
        workItems.append({"workItems": i, "workStatus": "available"})
    return workItems


def makeFolderStructure(
    fullPathToRootFolder: str, nameOfParentFolder: str, listOfChildFolders: list
) -> dict:

    collectionRoot = os.path.join(fullPathToRootFolder, nameOfParentFolder)
    newFolders = {}

    for fldr in listOfChildFolders:
        folderPath = os.path.join(collectionRoot, fldr)
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        newFolders[fldr] = folderPath

    return newFolders


def makeGuid():
    unique_guid = uuid.uuid4()
    return str(unique_guid)


def getFilename(file_path):
    fileName = os.path.basename(file_path)
    return fileName


def sanitext(dirtytext: str):
    pattern = r"[^0-9a-zA-Z\s_,.$!%&@*+><:#='()-?]+"
    cleantext = re.sub(pattern, " ", dirtytext)
    cleanertext = cleantext.replace("\n", " ")
    cleanesttext = " ".join(cleanertext.split())
    steriletext = cleanesttext.strip()
    return steriletext


def prepFolderName(inputString):
    pattern = r"[^0-9a-zA-Z\s_.-]+"
    cleanString = re.sub(pattern, "", inputString)
    cleanerString = cleanString.replace(" ", "")
    folderName = cleanerString.lower()
    sterileFolderName = folderName.strip()
    return sterileFolderName
