import sys
import traceback
import functools
import platform
import os

from .core import get_code_context, get_file_context, serialise_state


# Enables Windows terminal to support ANSI codes.
os.system('')

YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"

DEFAULT_CONTEXT_WINDOW = 25
MASK_SECRETS = True


def promptlog_local(context_window=DEFAULT_CONTEXT_WINDOW, mask_secrets=MASK_SECRETS):
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
                print(f'Location: {func.__name__} at line {line_num}')
                print(f'System: Python {platform.python_version()} on {platform.system()}')

                print(f'Code Context:')
                print(get_code_context(func, line_num, context_window))

                print('Local Variable State:')
                print(serialise_state(frame.f_locals, mask_secrets))

                print(f'Full Traceback:')
                traceback.print_exc(file=sys.stdout)

                # Flush stdout to ensure the error report has finished printing.
                sys.stdout.flush()

                print(f"{'=' * 76}{RESET}\n")

                # Re-raise the error.
                raise e

        return wrapper
    return decorator


def promptlog_global(context_window=DEFAULT_CONTEXT_WINDOW, mask_secrets=MASK_SECRETS):
    def global_handler(exc_type, exc_value, tb):
        # Get the last frame (where the actual crash happened)
        last_traceback = list(traceback.walk_tb(tb))[-1]
        frame, line_num = last_traceback
        filename = frame.f_code.co_filename

        print(f'\n{YELLOW}{"=" * 30} LLM DEBUG REPORT {"=" * 30}')
        print(f'Error: {exc_type.__name__}: {exc_value}')
        print(f'Location: {filename} at line {line_num}')
        print(f'System: Python {platform.python_version()} on {platform.system()}')

        print(f'Code Context:')
        print(get_file_context(filename, line_num, context_window))

        print(f'Local Variable State:')
        print(serialise_state(frame.f_locals, mask_secrets))

        print(f'Full Traceback:')
        traceback.print_exception(exc_type, exc_value, tb)

        print(f"{'=' * 78}{RESET}\n")
    sys.excepthook = global_handler
