#!/bin/sh
python=python3.9
echo '** 1. ********* run tests first *******************************'
pytest .
echo '*********** running tests ends  *******************************'

echo 
echo
echo
echo '** 2. ***** running: python setup.py sdist *********************'
python setup.py sdist

echo 

#echo '******* running: python setup.py bdist --formats*gztar *********'
#python setup.py bdist --formats*gztar 
