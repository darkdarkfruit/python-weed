files = weed/conf.py weed/__init__.py weed/master.py weed/operation.py weed/_test_weed_pytest.py weed/util.py weed/version.py weed/volume.py weed/weed.py
file_pytest_genscript = weed/_test_weed_pytest.py

default: test
	echo ''


test_python_setup: ${file_pytest_genscript}
	echo '==> generating "py.test file for packaging in dist"'
	py.test --genscript=${file_pytest_genscript}


test: ${files} test_python_setup
	echo ''
	echo '==> use "py.test test" directly: '
	py.test test 
	echo ''
	echo '==> use "python setup.py test": '
	python setup.py test

# just py.test weed
stest: 
	py.test test 


# make a source distribution in dist/
sdist: ${files} test_python_setup
	python setup.py sdist
