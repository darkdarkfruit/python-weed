1.4.4 Integrating with distutils / python setup.py test
=========================================================
(one section of pytest.pdf)


You can integrate test runs into your distutils or setuptools based project. Use the genscript method to generate a standalone py.test script:

py.test --genscript=runtests.py

# ------------------------------------------------------------------
from distutils.core import setup, Command
# you can also import from setuptools
class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, âruntest.pyâ])
        raise SystemExit(errno)
setup(
#...,
cmdclass = {âtestâ: PyTest},
#...,
)
# ------------------------------------------------------------------

If you now type:
    python setup.py test
this will execute your tests using runtest.py. As this is a standalone version of py.test no prior installation
whatsoever is required for calling the test command. You can also pass additional arguments to the subprocess-calls
such as your test directory or other options.
