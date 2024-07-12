"""Benchmark for reading a YAML file."""

import time
import xml.etree.ElementTree as ET

import rxml
from rich.progress import track


def read_xml_with_rxml(file_path: str):
    """Read an XML file using rxml."""
    return rxml.read_file(file_path, "PubmedArticleSet")

def read_xml_with_et(file_path: str):
    """Read an XML file using ElementTree."""
    with open(file_path, "rb") as f:
        tree = ET.parse(f)
    return tree.getroot()

def measure_time(func, *args):
    """Measure the time taken by a function."""
    start_time = time.time()
    func(*args)
    end_time = time.time()
    return end_time - start_time

def run_benchmarks():
    file_path = "tmp/pubmed24n0001.xml"
    iterations = 100

    rxml_times = []
    et_times = []
    for _ in track(range(iterations)):
        rxml_times.append(measure_time(read_xml_with_rxml, file_path))
        et_times.append(measure_time(read_xml_with_et, file_path))

    rxml_time = sum(rxml_times) / len(rxml_times)
    et_time = sum(et_times) / len(et_times)

    print(f"rxml: {rxml_time:.4f} s")
    print(f"ElementTree: {et_time:.4f} s")
    

if __name__ == "__main__":
    run_benchmarks()