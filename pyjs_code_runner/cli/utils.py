import typer


def require_option(*args, **kwargs):
    return typer.Option(..., *args, **kwargs)


def make_names(name, short_name=None):
    if short_name is None:
        short_name = name[0]
    return f"--{name}", f"-{short_name}"
