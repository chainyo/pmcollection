"""Utility functions for pmcollection package."""

from rxml import Node, SearchType


def find_or_none(node: Node, tag: str) -> str | None:
    """Find a child element or return None."""
    element = node.search(by=SearchType.Tag, value=tag)

    if element is None:
        return None

    return element.text
