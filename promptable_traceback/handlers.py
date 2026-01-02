import sys
import traceback
import functools
import platform
import os

from .core import get_code_context, get_file_context, serialise_state


# todo: imported package versions, print obj instances by value rather than reference

# Enables Windows terminal to support ANSI codes.
if platform.system() == "Windows":
    os.system('')


YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"

DEFAULT_CONTEXT_WINDOW = 25
MASK_SECRETS = True


def catch(context_window=DEFAULT_CONTEXT_WINDOW, mask_secrets=MASK_SECRETS):
    """
    Decorator that captures program state upon an exception.
    :param context_window: Number of lines to capture around the error (bounded by start and end of the function the error occurred in).
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
                frame, line_num = list(traceback.walk_tb(tb))[-1]

                # Print the error report.
                print(f'{YELLOW}{BOLD}{"=" * 30} ERROR REPORT {"=" * 30}{RESET}')
                print(f'{YELLOW}{BOLD}Error:{RESET} {exc_type.__name__}: {exc_value}')
                print(f'{YELLOW}{BOLD}Location:{RESET} {func.__name__} at line {line_num}')
                print(f'{YELLOW}{BOLD}System:{RESET} Python {platform.python_version()} on {platform.system()}')

                print(f'{YELLOW}{BOLD}Code Context:{RESET}')
                print(get_code_context(func, line_num, context_window))

                print(f'{YELLOW}{BOLD}Local Variable State: {RESET}')
                print(serialise_state(frame.f_locals, mask_secrets))

                print(f'{YELLOW}{BOLD}Full Traceback:{RESET}{RED}')
                traceback.print_exc(file=sys.stdout)
                print(f'{RESET}')

        return wrapper
    return decorator


def hook(context_window=DEFAULT_CONTEXT_WINDOW, mask_secrets=MASK_SECRETS):
    """
    Overrides the system-wide exception hook to capture program state upon an exception.
    :param context_window: Number of lines to capture around the error (bounded by start and end of file).
    :param mask_secrets: Whether to redact sensitive variable names.
    :return: None.
    """
    def global_handler(exc_type, exc_value, tb):
        # The last entry in the traceback is where the error happened.
        frame, line_num = list(traceback.walk_tb(tb))[-1]
        filename = frame.f_code.co_filename

        # Print the error report.
        print(f'{YELLOW}{BOLD}{"=" * 30} ERROR REPORT {"=" * 30}{RESET}')
        print(f'{YELLOW}{BOLD}Error:{RESET} {exc_type.__name__}: {exc_value}')
        print(f'{YELLOW}{BOLD}Location:{RESET} {filename} at line {line_num}')
        print(f'{YELLOW}{BOLD}System:{RESET} Python {platform.python_version()} on {platform.system()}')

        print(f'{YELLOW}{BOLD}Code Context:{RESET}')
        print(get_file_context(filename, line_num, context_window))

        print(f'{YELLOW}{BOLD}Local Variable State: {RESET}')
        print(serialise_state(frame.f_locals, mask_secrets))

        print(f'{YELLOW}{BOLD}Full Traceback:{RESET}{RED}')
        traceback.print_exception(exc_type, exc_value, tb, file=sys.stdout)
        print(f'{RESET}')

    sys.excepthook = global_handler
