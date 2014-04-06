files = weed/__init__.py weed/weed.py weed/test_weed.py
file_pytest_genscript = weed/test_weed_pytest.py

default: test
	echo ''


test_python_setup: ${file_pytest_genscript}
	echo '==> generating "py.test file for packaging in dist"'
	py.test --genscript=${file_pytest_genscript}


test: ${files} test_python_setup
	echo ''
	echo '==> use "py.test weed" directly: '
	py.test weed
	echo ''
	echo '==> use "python setup.py test": '
	python setup.py test

# just py.test weed
stest: 
	py.test weed


# make a source distribution in dist/
sdist: ${files} test_python_setup
	python setup.py sdist
