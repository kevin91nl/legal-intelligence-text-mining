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
    with zipfile.ZipFile(path, 'r') as zip_handle:
        for file in zip_handle.namelist():
            with zip_handle.open(file, 'r') as file_handle:
                text = file_handle.read().decode('utf-8')
                handler(file, text)


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
