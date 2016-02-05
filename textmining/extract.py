"""
This file contains tools for handling text documents and extracting features from it.
"""
import zipfile
import os
import datetime
import math
import sys


def parse_zip_file(path, file_handler, state_handler=None, max_files=math.inf):
    """
    Parse all files contained in a zip file (specified by the path parameter).

    Parameters
    ----------
    path : str
        The path to the zip file.
    file_handler : function
        When looping through all the files contained in the zip file, this method will be called every time
        a new file is found. Two arguments are passed. The first argument is the name of the discovered file
        and the second argument is the UTF-8 text found in the document.
    state_handler : Optional[function]
        This function is called every time after a new file is discovered. The first parameter of this function is the
        number of files that is already handled. The second parameter of this function is the expected total number of
        files that will be handled. The third parameter is the elapsed time since the parse_zip_file method was
        called.
    max_files : Optional[int]
        If this is specified, then only this amount of files is handled and the parser stops when this amount is
        reached.

    Returns
    -------
    None
        Nothing is returned.

    Raises
    ------
    zipfile.BadZipfile
        If the given path is not a zip file.
    """
    start_time = datetime.datetime.now()
    if not os.path.exists(path) or os.path.isdir(path) or not zipfile.is_zipfile(path):
        raise zipfile.BadZipfile
    with zipfile.ZipFile(path, 'r') as zip_handle:
        # Get the files and calculate statistics
        filenames = zip_handle.namelist()
        num_handled_files = 0
        num_files = min(len(filenames), max_files)
        for file in filenames:
            # Open the file inside the zip file
            with zip_handle.open(file, 'r') as file_handle:
                try:
                    text = file_handle.read().decode('utf-8')
                    file_handler(file, text)
                except UnicodeDecodeError:
                    pass
                num_handled_files += 1
                if state_handler is not None:
                    end_time = datetime.datetime.now()
                    state_handler(num_handled_files, num_files, end_time - start_time)
                if num_handled_files >= max_files:
                    break


def extract_text_from_xml(xml_node, separator="\n"):
    """
    Extract text from an XML node.

    Parameters
    ----------
    xml_node : xml.etree.ElementTree
        An XML node.
    separator : Optional[str]
        String that separates texts found in subtrees from each other.

    Returns
    -------
    str
        Found text.
    """
    text = ""
    main_text = xml_node.text
    if main_text is not None:
        text += main_text + separator
    for child in xml_node:
        subtext = extract_text_from_xml(child, separator=separator)
        if subtext is not None:
            text += subtext + separator
    return text.strip(separator)


def show_state(num_handled_files, num_total_files, elapsed_time):
    # Calculate the expected time
    time_per_file = elapsed_time / num_handled_files
    files_left = num_total_files - num_handled_files
    time_left = files_left * time_per_file
    # Show the state
    sys.stdout.write("\rExpected time left: {3}\t{0:.1f}%\t{1} / {2}".format(
        100 * num_handled_files / float(num_total_files), num_handled_files, num_total_files, time_left))
    sys.stdout.flush()
    if num_handled_files == num_total_files:
        sys.stdout.write("\rDone!\tHandled {0} files in {1}\n".format(num_total_files, elapsed_time))
