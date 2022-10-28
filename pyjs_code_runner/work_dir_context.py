from contextlib import contextmanager
import os
@contextmanager
def work_dir_context(tmp_cwd):
    base_work_dir = os.getcwd()
    os.chdir(tmp_cwd)
    yield
    os.chdir(base_work_dir)
