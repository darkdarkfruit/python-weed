import os

from setuptools import setup, find_packages

DESCRIPTION = "A python module for seaweedfs(old name: weed-fs)"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except Exception as e:
    print(e)

#  https://github.com/navdeep-G/setup.py/blob/master/setup.py
here = os.path.abspath(os.path.dirname(__file__))
NAME = 'python-weed'
# Load the package's __version__.py module as a dictionary.
VERSION = ''
about = {}
if not VERSION:
    with open(os.path.join(here, "weed", 'version.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

CLASSIFIERS = [
    'Development Status :: 4 - Beta',  # https://pypi.org/classifiers/
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(name=NAME,
      version=about['__version__'],
      packages=find_packages(),
      author='darkdarkfruit',
      author_email='darkdarkfruit@gmail.com',
      url='https://github.com/darkdarkfruit/python-weed',
      license='MIT',
      include_package_data=True,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      platforms=['any'],
      classifiers=CLASSIFIERS,
      install_requires=['requests'],
      requires=['requests'],
      # cmdclass = {'test' : PyTest},
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],  # https://pythonhosted.org/distutils-pytest/

      # https://stackoverflow.com/questions/17001010/how-to-run-unittest-discover-from-python-setup-py-test
      # https://pythonhosted.org/distutils-pytest/
      # test_suite="tests",

      #      test_suite='py.test',
      )
