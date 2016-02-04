"""
This file contains tools for handling text documents and extracting features from it.
"""
import zipfile
import os


def parse_zip_file(path, handler):
    """
    Parse all files contained in a zip file (specified by the path parameter).

    Parameters
    ----------
    path : str
        The path to the zip file.
    handler: function
        When looping through all the files contained in the zip file, this method will be called every time
        a new file is found. Two arguments are passed. The first argument is the name of the discovered file
        and the second argument is the UTF-8 text found in the document.

    Returns
    -------
    None
        Nothing is returned.

    Raises
    ------
    zipfile.BadZipfile
        If the given path is not a zip file.
    """
    if not os.path.exists(path) or os.path.isdir(path) or not zipfile.is_zipfile(path):
        raise zipfile.BadZipfile
    with zipfile.ZipFile(path, 'r') as zip:
        for file in zip.namelist():
            with zip.open(file, 'r') as file_handle:
                text = file_handle.read().decode('utf-8')
                handler(file, text)
