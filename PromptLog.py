import inspect
import sys
import traceback
import functools
import platform
import os

# Enables Windows terminal to support ANSI codes.
os.system('')

YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"

class PromptLog:
    @staticmethod
    def get_code_context(func, target_line_num, window_size):
        """
        Extracts the surrounding lines of code.
        :param func: Function where the error occurred.
        :param target_line_num: Line number where the error occurred.
        :param window_size: Window size of the code context window. Will be shrunk to the function boundaries if necessary.
        :return: A string of lines of code delimited by new spaces.
        """
        try:
            lines, start_line = inspect.getsourcelines(func)
            end_line = start_line + len(lines) - 1

            # Ensure we don't capture lines of code beyond the function's scope.
            start = max(start_line, target_line_num - window_size)
            end = min(end_line, target_line_num + window_size)

            context_lines = []
            for i, line in enumerate(lines):
                current_line_no = start_line + i
                if start <= current_line_no <= end:
                    prefix = ">> " if current_line_no == target_line_num else "   "
                    context_lines.append(f"{current_line_no}{prefix}{line.rstrip()}")

            return "\n".join(context_lines)
        except Exception:
            return "Could not retrieve source code context."

    @staticmethod
    def serialise_state(locals_dict, mask_keys=True):
        """
        Captures and formats variable values.
        :param locals_dict: Dictionary of local variables.
        :param mask_keys: Redacts sensitive data if set to True.
        :return: Formatted string of variables and their types/values.
        """
        report = []
        sensitive_keywords = {'key', 'token', 'pass', 'secret', 'auth'}

        for var, val in locals_dict.items():
            # Skip internal python variables.
            if var.startswith('__'): continue

            display_val = val
            if mask_keys and any(k in var.lower() for k in sensitive_keywords):
                display_val = "*REDACTED*"

            report.append(f' - {var} ({type(val).__name__}): {display_val}')

        return "\n".join(report) if report else "No local variables captured."


def promptlog(context_window=25, mask_secrets=True):
    """
    Decorator that captures function state and code context upon an exception.
    :param context_window: Number of lines to capture around the error.
    :param mask_secrets: Whether to redact sensitive variable names.
    :return: The wrapped function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Capture the traceback and frame.
                exc_type, exc_value, tb = sys.exc_info()
                # The last entry in the traceback is where the error happened.
                last_traceback = traceback.walk_tb(tb)
                frame, line_num = list(last_traceback)[-1]

                # Print the error report.
                print(f'{YELLOW}{"=" * 30} ERROR REPORT {"=" * 30}')
                print(f'Error: {exc_type.__name__}: {exc_value}')
                print(f'Function: {func.__name__} at line {line_num}')

                print(f'Surrounding Code Context (Python {platform.python_version()}):')
                print(PromptLog.get_code_context(func, line_num, context_window))

                print('Local Variable State:')
                print(PromptLog.serialise_state(frame.f_locals, mask_secrets))

                print(f'Full Traceback:')
                traceback.print_exc(file=sys.stdout)

                # Flush stdout to ensure the error report has finished printing.
                sys.stdout.flush()

                print(f"{'=' * 76}{RESET}\n")

                # Re-raise the error.
                raise e

        return wrapper
    return decorator
