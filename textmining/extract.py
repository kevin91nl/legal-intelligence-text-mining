"""
This file contains tools for handling text documents and extracting features from it.
"""
import zipfile
import os
from xml.etree import cElementTree as ET


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


def extract_text_from_xml(xml_string):
    """
    Extract text from an XML file.

    Parameters
    ----------
    xml_string : str
        XML formatted string to extract text from.

    Returns
    -------
    str
        Text found in XML.
    """
    #def text_in_node
    tree = ET.fromstring(xml_string)
    for child in tree:
        if child.text is not None:
            return False


extract_text_from_xml('<archive><page>1</page><page><subnode>2</subnode></page></archive>')
