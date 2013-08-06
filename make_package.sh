#!/bin/sh
echo '** 1. ********* run tests first *******************************'
py.test weed
echo '*********** running tests ends  *******************************'

echo 
echo
echo
echo '** 2. ***** running: python setup.py sdist *********************'
python setup.py sdist

echo 

#echo '******* running: python setup.py bdist --formats*gztar *********'
#python setup.py bdist --formats*gztar 
