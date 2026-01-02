import inspect
import os
import linecache


def get_code_context(func, target_line_num, window_size):
    """
    Extracts the surrounding lines of code.
    :param func: Function where the error occurred.
    :param target_line_num: Line number where the error occurred.
    :param window_size: Window size of the code context window. Will be shrunk to the function boundaries if necessary.
    :return: A string of lines of code delimited new lines.
    """
    try:
        lines, start_line = inspect.getsourcelines(func)
        end_line = start_line + len(lines) - 1

        # Ensure we don't capture lines of code beyond the function's scope.
        start = max(start_line, target_line_num - window_size)
        end = min(end_line, target_line_num + window_size)

        # Padding based on largest line number.
        max_num_width = len(str(end))

        context_lines = []
        for i, line in enumerate(lines):
            current_line_no = start_line + i
            if start <= current_line_no <= end:
                prefix = " >> " if current_line_no == target_line_num else "    "
                context_lines.append(f"{current_line_no:>{max_num_width}}{prefix}{line.rstrip()}")

        return "\n".join(context_lines)
    except Exception:
        return "Could not retrieve source code context."


def get_file_context(filename, target_line_num, window_size):
    """
    Extracts the surrounding lines of code from the entire file.
    :param filename:
    :param target_line_num: Line number where the error occurred.
    :param window_size: Window size of the code context window. Will be shrunk to the function boundaries if necessary.
    :return: A string of lines of code delimited by new lines.
    """
    if not os.path.exists(filename):
        return "Could not retrieve source code (file not found)."

    start = max(1, target_line_num - window_size)
    end = target_line_num + window_size

    # Padding based on largest line number.
    max_num_width = len(str(end))

    context_lines = []
    for i in range(start, end + 1):
        line = linecache.getline(filename, i)
        if not line:
            break
        prefix = " >> " if i == target_line_num else "    "
        context_lines.append(f"{i:>{max_num_width}}{prefix}{line.rstrip()}")

    return "\n".join(context_lines)


def serialise_state(locals_dict, mask_keys=True):
    """
    Captures and formats variable values.
    :param locals_dict: Dictionary of local variables.
    :param mask_keys: Redacts sensitive data if set to True.
    :return: Formatted string of variables and their types/values.
    """
    report = []
    sensitive_keywords = {'key', 'token', 'pass', 'secret', 'auth', 'api'}

    for var, val in locals_dict.items():
        # Skip internal python variables.
        if var.startswith('__'): continue

        display_val = val
        if mask_keys and any(k in var.lower() for k in sensitive_keywords):
            display_val = "*REDACTED*"

        report.append(f' - {var} ({type(val).__name__}): {display_val}')

    return "\n".join(report) if report else "No local variables captured."
