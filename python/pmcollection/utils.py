"""Utility functions for pmcollection package."""

import xml.etree.ElementTree as ET


def find_or_none(element: ET.Element, tag: str) -> ET.Element:
    """Find a child element or return None."""
    return element.find(tag).text if element.find(tag) is not None else None
