import unittest
import shutil
from textmining.extract import *


class TestTools(unittest.TestCase):
    def setUp(self):
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
        shutil.rmtree('empty_folder')
        files = list(self.zip_contents.keys())
        files.extend([self.badzipfile, self.zipfile])
        for file in files:
            os.remove(file)

    def handle_zip_file(self, path, text):
        self.found_zip_contents[path] = text

    def test_parse_zip_file(self):
        self.found_zip_contents = {}
        parse_zip_file(self.zipfile, self.handle_zip_file)
        for file in self.found_zip_contents:
            self.assertTrue(file in self.zip_contents)
        for file in self.zip_contents:
            self.assertTrue(file in self.found_zip_contents)
            self.assertEqual(self.zip_contents[file], self.found_zip_contents[file])

    def test_parse_zip_file_badzipfile(self):
        with self.assertRaises(zipfile.BadZipfile):
            parse_zip_file(self.badzipfile, self.handle_zip_file)
        with self.assertRaises(zipfile.BadZipfile):
            parse_zip_file('unknown_file', self.handle_zip_file)
        with self.assertRaises(zipfile.BadZipfile):
            parse_zip_file('empty_folder', self.handle_zip_file)


if __name__ == '__main__':
    unittest.main()
