from functools import wraps


def dict_decorator(method):
    """print each dictionary key-value on newline"""

    @wraps(method)
    def impl(*method_args, **method_kwargs):
        method_output = method(*method_args, **method_kwargs)
        # omit list brackets from output
        return "\n".join(f'{k} : {str(v)[1:-1]}' for k, v in method_output.items())
    return impl


def round_output(method):
    @wraps(method)
    def decorate(*method_args, **method_kwargs):
        method_output = method(*method_args, **method_kwargs)
        x = [i.round(2) if i is not None else i for i in method_output]
        print(*x, sep='\n')
    return decorate
