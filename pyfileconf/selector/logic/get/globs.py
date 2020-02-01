import inspect


def iter_globals():
    """
    Generator which first returns globals for current module, then next level up, and so on
    """
    for frame in _iter_frames():
        yield frame.f_globals
    for frame in _iter_frames():
        yield frame.f_locals

def _iter_frames():
    """
    Generator which first returns current code frame, then next level up, and so on
    """
    frame = inspect.currentframe()
    while frame is not None:
        yield frame
        frame = frame.f_back  # get next level up frame


