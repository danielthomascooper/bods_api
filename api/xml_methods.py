from lxml import etree
from collections.abc import MutableMapping


def pretty_print(node: etree.Element) -> None:
    """Print the XML of the node"""
    xml = etree.tostring(node, pretty_print=True)
    print(xml.decode(), end='')

def local_xpath(tag: str) -> str:
    """Shorthand for local name check for use in xpaths. Ignores namespaces.

    Parameters
    ----------
    tag : str
        The local tag name to match.
    """
    return f"*[local-name() = '{tag}']"

def element_to_dict(root: etree.Element) -> dict:
    """Convert etree element to dictionary.

    Will not work for elements with non-unique children.

    Parameters
    ----------
    root : etree.Element
        The root to be converted to dictionary. Warning: only valid for elements with unique names.
    """
    if len(root) == 0:
        return root.text
    else:
        cur_node = {}
        for child in root:
            full_tag = etree.QName(child)
            cur_node[full_tag.localname] = element_to_dict(child)
        return cur_node


def flatten(dictionary, parent_key='', separator='_'):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)