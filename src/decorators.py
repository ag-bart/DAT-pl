from functools import wraps


def dict_decorator(method):
    """print each dictionary key-value on newline"""

    @wraps(method)
    def wrapper(*method_args, **method_kwargs):
        method_output = method(*method_args, **method_kwargs)
        # omit list brackets from output
        print("\n".join(f'{k} : {str(v)[1:-1]}'
                        for k, v in method_output.items()))
    return wrapper


def round_output(method):
    @wraps(method)
    def wrapper(*method_args, **method_kwargs):
        method_output = method(*method_args, **method_kwargs)
        x = [i.round(2) if i is not None else i for i in method_output]
        print(*x, sep='\n')
    return wrapper