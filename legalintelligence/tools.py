"""
This file builds upon the Text Mining tools for extracting and handling Legal Intelligence specific information.
"""
from xml.etree import cElementTree as xmltree
from textmining.extract import *
from random import shuffle
import random
import numpy as np
import re
import pickle


class Bunch(dict):
    """Container object for datasets
    Dictionary-like object that exposes its keys as attributes.
    >>> b = Bunch(a=1, b=2)
    >>> b['b']
    2
    >>> b.b
    2
    >>> b.a = 3
    >>> b['a']
    3
    >>> b.c = 6
    >>> b['c']
    6
    """

    def __init__(self, **kwargs):
        super(Bunch, self).__init__(kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass


class LegalIntelligenceExtractor:
    def __init__(self):
        self.separator = "\n"
        self.data = Bunch(files=[], data=[], target1=[], target2=[], target1_names=[], target2_names=[])

    def handle_xml_file(self, path, content):
        """
        Parameters
        ----------
        path : str
            Path of the XML file.
        content : str
            Content of the XML file.

        Returns
        -------
        None
            Nothing to return.
        """
        try:
            root_node = xmltree.fromstring(content)
            text = extract_text_from_xml(root_node, separator=self.separator)
            subjects = extract_subjects(root_node)
            if len(subjects) == 1 or len(subjects) == 2:
                self.data.files.append(path)
                self.data.data.append(text)
                subject1 = subjects[0]
                if subject1 not in self.data.target1_names:
                    self.data.target1_names.append(subject1)
                self.data.target1.append(self.data.target1_names.index(subject1))
                if len(subjects) == 2:
                    subject2 = subjects[1]
                    if subject2 not in self.data.target2_names:
                        self.data.target2_names.append(subject2)
                    self.data.target2.append(self.data.target2_names.index(subject2))
                else:
                    self.data.target2.append(None)
        except xmltree.ParseError:
            return None


def extract_subjects(node):
    """
    Extract subjects from an XML tree.

    Parameters
    ----------
    node : xml.etree.ElementTree.ElementTree
        An XML tree.

    Returns
    -------
        Found subjects.
    """
    namespace = {
        "dcterms": "http://purl.org/dc/terms/"
    }
    subject_nodes = node.findall(".//dcterms:subject", namespace)
    subjects = []
    for subject_node in subject_nodes:
        subject_text = subject_node.text
        subject_text = re.sub(r"\s*;\s*", ";", subject_text)
        subjects.extend(subject_text.split(";"))
    return subjects


def store_dataset(data, file):
    """
    Store a dataset.

    Parameters
    ----------
    data : Bunch
        Dataset to store.
    file : str
        Path of the file in which the dataset will be stored.

    Returns
    -------
    None
        Nothing.
    """
    with open(file, "wb") as handle:
        pickle.dump(data, handle)


def load_dataset(path):
    """
    Load a dataset.

    Parameters
    ----------
    path : str
        Path to the file to load in which the dataset is stored.

    Returns
    -------
    Bunch
        The dataset.
    """
    with open(path, "rb") as handle:
        data = pickle.load(handle)
    return data


def remove_indices(dataset, indices_to_remove):
    """
    Remove indices from a dataset.

    Parameters
    ----------
    dataset : Bunch
        Dataset from which to remove certain indices.
    indices_to_remove
        Indices which will be removed.

    Returns
    -------
    Bunch
        Dataset which does not have the indices specified in the remove_indices parameter.
    """
    all_indices = list(range(0, len(dataset.files)))
    indices = list(set(all_indices) - set(indices_to_remove))
    result = Bunch(files=[], data=[], target1=[], target2=[], target1_names=[], target2_names=[])
    result.files = [dataset.files[index] for index in indices]
    result.data = [dataset.data[index] for index in indices]
    result.target1 = [dataset.target1[index] for index in indices]
    result.target2 = [dataset.target2[index] for index in indices]
    result.target1, result.target1_names = cleanup_target_names(result.target1, dataset.target1_names)
    result.target2, result.target2_names = cleanup_target_names(result.target2, dataset.target2_names)
    return result


def cleanup_target_names(targets, target_names):
    """
    Sometimes, some target names are not used anymore (after removing indices). This method cleans up unused
    target names.

    Parameters
    ----------
    targets : list
        List of all targets.
    target_names : list
        List of all target names

    Returns
    -------
    targets : list
        List of all cleaned up targets.
    target_names : list
        List of all cleaned up target names.
    """
    unique_targets = list(set(targets))
    new_names = [list(target_names)[target] for target in unique_targets]
    new_targets = [unique_targets.index(target) for target in targets]
    return new_targets, new_names


def filter_incomplete_subjects(dataset):
    """
    Filter second level subjects which were not specified.

    Parameters
    ----------
    dataset : Bunch
        Dataset to filter.

    Returns
    -------
    Bunch
        Filtered dataset.
    """
    indices = [index for index in range(0, len(dataset.files)) if dataset.target2[index] is None]
    return remove_indices(dataset, indices)


def filter_small_subjects(dataset, min_support):
    """
    Filter small subjects which have < min_support documents.

    Parameters
    ----------
    dataset : Bunch
        The dataset.
    min_support : int
        Minimum number of documents.

    Returns
    -------
    Bunch
        Dataset without subjects which have less than min_support documents.
    """
    support = {}
    for index in range(len(dataset.target2)):
        target = dataset.target2[index]
        if target not in support:
            support[target] = []
        support[target].append(index)
    indices = []
    for target in support:
        if len(support[target]) < min_support:
            indices.extend(support[target])
    return remove_indices(dataset, indices)


def chop_large_subjects(dataset, max_documents):
    """
    Chop subjects which have >= max_documents such that they contain at most max_documents documents.

    Parameters
    ----------
    dataset : Bunch
        The dataset.
    max_documents : int
        The maximum number of documents per subject.

    Returns
    -------
    Bunch
        Filtered dataset.
    """
    support = {}
    for index in range(len(dataset.target2)):
        target = dataset.target2[index]
        if target not in support:
            support[target] = []
        support[target].append(index)
    indices = []
    for target in support:
        if len(support[target]) > max_documents:
            indices.extend(support[target][max_documents:])
    return remove_indices(dataset, indices)


def get_indices(dataset):
    """
    Get indices per target1_name and per target2_name.

    Parameters
    ----------
    dataset : Bunch
        Dataset to get indices from.

    Returns
    -------
    dict
        Dictionary d such that d[target1_name][target2_name] is a list containing all indices that belong to that
        subject.
    """
    mapping = {}
    for index in range(len(dataset.target2)):
        target1 = dataset.target1[index]
        target1_name = dataset.target1_names[target1]
        if target1_name not in mapping:
            mapping[target1_name] = {}
        target2 = dataset.target2[index]
        target2_name = dataset.target2_names[target2]
        if target2_name not in mapping[target1_name]:
            mapping[target1_name][target2_name] = []
        mapping[target1_name][target2_name].append(index)
    return mapping


def shuffle_dataset(dataset, seed=None):
    """
    Shuffle a dataset.

    Parameters
    ----------
    dataset : Bunch
        Dataset to shuffle.
    seed : Optional[int]
        Seed for randomizer.

    Returns
    -------
    Bunch
        Shuffled dataset.
    """
    if seed is not None:
        random.seed(seed)
    index_shuffle = np.arange(0, len(dataset.target1))
    shuffle(index_shuffle)
    result = Bunch(files=[], data=[], target1=[], target2=[], target1_names=[], target2_names=[])
    for index in index_shuffle:
        result.files.append(dataset.files[index])
        result.data.append(dataset.data[index])
        result.target1.append(dataset.target1[index])
        result.target2.append(dataset.target2[index])
    result.target1_names = dataset.target1_names
    result.target2_names = dataset.target2_names
    return result
