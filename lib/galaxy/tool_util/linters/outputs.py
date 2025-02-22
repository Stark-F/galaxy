"""This module contains a linting functions for tool outputs."""
from galaxy.util import string_as_bool
from ._util import is_valid_cheetah_placeholder


def lint_output(tool_xml, lint_ctx):
    """Check output elements, ensure there is at least one and check attributes."""
    outputs = tool_xml.findall("./outputs")
    if len(outputs) == 0:
        lint_ctx.warn("Tool contains no outputs section, most tools should produce outputs.")
    if len(outputs) > 1:
        lint_ctx.warn("Tool contains multiple output sections, behavior undefined.")

    num_outputs = 0
    if len(outputs) == 0:
        lint_ctx.warn("No outputs found")
        return

    for output in list(outputs[0]):
        if output.tag not in ["data", "collection"]:
            lint_ctx.warn(f"Unknown element found in outputs [{output.tag}]")
            continue
        num_outputs += 1
        if "name" not in output.attrib:
            lint_ctx.warn("Tool output doesn't define a name - this is likely a problem.")
        else:
            if not is_valid_cheetah_placeholder(output.attrib["name"]):
                lint_ctx.warn("Tool output name [%s] is not a valid Cheetah placeholder.", output.attrib["name"])

        format_set = False
        if __check_format(output, lint_ctx):
            format_set = True
        if output.tag == "data":
            if "auto_format" in output.attrib and output.attrib["auto_format"]:
                format_set = True

        elif output.tag == "collection":
            if "type" not in output.attrib:
                lint_ctx.warn("Collection output with undefined 'type' found.")
            if "structured_like" in output.attrib and "inherit_format" in output.attrib:
                format_set = True
        for sub in output:
            if __check_pattern(sub):
                format_set = True
            elif __check_format(sub, lint_ctx, allow_ext=True):
                format_set = True

        if not format_set:
            lint_ctx.warn(f"Tool {output.tag} output {output.attrib.get('name', 'with missing name')} doesn't define an output format.")

    lint_ctx.info("%d outputs found.", num_outputs)


def __check_format(node, lint_ctx, allow_ext=False):
    """
    check if format/ext/format_source attribute is set in a given node
    issue a warning if the value is input
    return true (node defines format/ext) / false (else)
    """
    if "format_source" in node.attrib and ("ext" in node.attrib or "format" in node.attrib):
        lint_ctx.warn(f"Tool {node.tag} output {node.attrib.get('name', 'with missing name')} should use either format_source or format/ext")
    if "format_source" in node.attrib:
        return True
    # if allowed (e.g. for discover_datasets), ext takes precedence over format
    fmt = None
    if allow_ext:
        fmt = node.attrib.get("ext")
    if fmt is None:
        fmt = node.attrib.get("format")
    if fmt == "input":
        lint_ctx.warn(f"Using format='input' on {node.tag}, format_source attribute is less ambiguous and should be used instead.")
    return fmt is not None


def __check_pattern(node):
    """
    check if
    - pattern attribute is set and defines the extension or
    - from_tool_provided_metadata is true
    """
    if node.tag != "discover_datasets":
        return False
    if "from_tool_provided_metadata" in node.attrib and string_as_bool(node.attrib.get("from_tool_provided_metadata", "false")):
        return True
    if "pattern" not in node.attrib:
        return False
    if node.attrib["pattern"] == "__default__":
        return True
    if "ext" in node.attrib["pattern"] and node.attrib["pattern"].startswith("__") and node.attrib["pattern"].endswith("__"):
        return True
