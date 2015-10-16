#

"""
Utils for testing
"""

import os
import shutil
import subprocess
import tempfile
from functools import wraps


def in_directory(file_, *components):
    """
    A decorator to execute a function in a directory relative to the current
    file.

    __file__ must be passed as first argument to determine the directory to
    start with.

    For preserving the ability to import aloe_django in child processes,
    the original directory is added to PYTHONPATH.
    """

    target = os.path.join(os.path.dirname(file_), *components)

    def decorate(func):
        """
        Decorate a function to execute in the given directory.
        """

        @wraps(func)
        def wrapped(*args, **kwargs):
            """
            Execute the function in the given directory.
            """

            oldpath = os.environ.get('PYTHONPATH', '')
            cwd = os.getcwd()

            os.chdir(target)
            os.environ['PYTHONPATH'] = cwd + oldpath

            try:
                return func(*args, **kwargs)
            finally:
                os.chdir(cwd)
                os.environ['PYTHONPATH'] = oldpath

        return wrapped

    return decorate


def in_temporary_directory(func):
    """
    A decorator to run a function in a temporary directory, cleaning up
    afterwards.
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        """Execute the function in the temporary directory."""

        oldpath = os.environ.get('PYTHONPATH', '')
        cwd = os.getcwd()

        target = tempfile.mkdtemp()
        os.chdir(target)
        os.environ['PYTHONPATH'] = cwd + oldpath

        try:
            return func(*args, **kwargs)
        finally:
            os.chdir(cwd)
            os.environ['PYTHONPATH'] = oldpath
            shutil.rmtree(target)

    return wrapped


def run_scenario(application=None, feature=None, scenario=None, **opts):
    """
    Run a scenario and return the exit code and output.
    """

    args = ['python', 'manage.py', 'harvest']

    if feature:
        feature = '{0}.feature'.format(feature)

    if application:
        if feature:
            args.append('{0}/features/{1}'.format(application, feature))
        else:
            args.append(application)

    if scenario:
        args += ['-n', '{0:d}'.format(scenario)]

    opts.setdefault('-v', 3)

    for opt, val in opts.items():
        args.append(str(opt))
        if val:
            args.append(str(val))

    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text, _ = proc.communicate()
    text = text.decode().rstrip()

    return proc.returncode, text
