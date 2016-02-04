import unittest
import shutil
from xml.etree import cElementTree
from textmining.extract import *


class TestTools(unittest.TestCase):
    def setUp(self):
        # Set up some files
        self.zipfile = 'testzip.zip'
        self.badzipfile = 'testzip_bad.zip'
        self.zip_contents = {
            'testfile.txt': 'some text',
            'testfile2.txt': 'some other text'
        }
        # Write the content to each file
        for file in self.zip_contents:
            with open(file, 'w') as handle:
                handle.write(self.zip_contents[file])
        # Create the zipfile
        with zipfile.ZipFile(self.zipfile, 'w') as testzip:
            for file in self.zip_contents:
                testzip.write(file)
        # Create the bad zipfile
        with open(self.badzipfile, 'w') as handle:
            handle.write('bad zip contents')
        # Create an empty folder
        if not os.path.exists('empty_folder'):
            os.mkdir('empty_folder')

    def tearDown(self):
        # Remove all of the created files
        shutil.rmtree('empty_folder')
        files = list(self.zip_contents.keys())
        files.extend([self.badzipfile, self.zipfile])
        for file in files:
            os.remove(file)

    def handle_zip_file(self, path, text):
        # Helper function for handling files within the zip file
        self.found_zip_contents[path] = text

    def test_parse_zip_file(self):
        # Test whether it is really possible to parse a zip file (and check if the found contents are indeed the stored
        # contents.
        self.found_zip_contents = {}
        parse_zip_file(self.zipfile, self.handle_zip_file)
        for file in self.found_zip_contents:
            self.assertTrue(file in self.zip_contents)
        for file in self.zip_contents:
            self.assertTrue(file in self.found_zip_contents)
            self.assertEqual(self.zip_contents[file], self.found_zip_contents[file])

    def test_parse_zip_file_badzipfile(self):
        # Test the exceptions for the zip file parsing
        with self.assertRaises(zipfile.BadZipfile):
            # A zip file with invalid contents (is not a valid zip file)
            parse_zip_file(self.badzipfile, self.handle_zip_file)
        with self.assertRaises(zipfile.BadZipfile):
            # A non-existing file (is not a valid zip file)
            parse_zip_file('unknown_file', self.handle_zip_file)
        with self.assertRaises(zipfile.BadZipfile):
            # A directory (is not a valid zip file)
            parse_zip_file('empty_folder', self.handle_zip_file)

    def test_extract_text_from_xml(self):
        # Test whether it is possible to extract text from an XML node
        xml = '<archive><page>page 1</page><page>page 2<subnode>node 1</subnode></page></archive>'
        node = cElementTree.fromstring(xml)
        # First text is simply without any separator
        text1 = extract_text_from_xml(node, "")
        self.assertEqual(text1, 'page 1page 2node 1')
        # The second text has a space as separator
        text2 = extract_text_from_xml(node, " ")
        self.assertEqual(text2, 'page 1 page 2 node 1')


if __name__ == '__main__':
    unittest.main()
