"""Utility functions for pmcollection package."""

from datetime import datetime
from typing import Union

from rxml import Node, SearchType


def find_tag_or_none(node: Node, tag: str) -> Node:
    """Find a child element or return None."""
    _node = node.search(SearchType.Tag, tag)
    return _node[0].text if _node else None


def define_datetime_from_node(nodes: list[Node]) -> Union[datetime, None]:
    """Get datetime string from a child element."""
    _year, _month, _day = None, None, None
    for node in nodes:
        match node.name:
            case "Year":
                _year = node.text
            case "Month":
                _month = node.text
            case "Day":
                _day = node.text

    if not _year or not _month:
        return None
    elif not _day:
        return datetime(int(_year), int(_month), 1)
    else:
        return datetime(int(_year), int(_month), int(_day))
