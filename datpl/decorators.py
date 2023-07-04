from functools import wraps


def format_dict_output(method):
    """
    Decorator to print each key-value pair on a newline.
    key:
        Index of the participant's answer increased by 1
            to reflect the ID in the input file.
    value:
        List of incorrect words, printed without brackets.
    """
    @wraps(method)
    def wrapper(*method_args, **method_kwargs):
        method_output = method(*method_args, **method_kwargs)
        print("\n".join(f'{index+1} : {str(word_list)[1:-1]}'
                        for index, word_list in method_output.items()))
    return wrapper


def round_output(method):
    """
    Rounds the output to two decimal places and prints it on newline.

    Parameters:
        method (callable): The method to be decorated.
            Method's output should be a list of floating-point numbers.
    """
    @wraps(method)
    def wrapper(*method_args, **method_kwargs):
        method_output = method(*method_args, **method_kwargs)
        rounded_output = [value.round(2) if value is not None
                          else value for value in method_output]
        print(*rounded_output, sep='\n')
    return wrapper
