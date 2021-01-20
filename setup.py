from setuptools import setup, find_packages

# from weed.version import __version__

DESCRIPTION = "A python module for seaweedfs(old name: weed-fs)"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except Exception as e:
    print(e)

CLASSIFIERS = [
    'Development Status :: 4 - Beta',  # https://pypi.org/classifiers/
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(name='python-weed',
      version="0.6.0",
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
