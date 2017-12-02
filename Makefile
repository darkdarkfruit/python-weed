files = weed/conf.py weed/__init__.py weed/master.py weed/operation.py weed/_test_weed_pytest.py weed/util.py weed/version.py weed/volume.py
file_pytest_genscript = weed/_test_weed_pytest.py

default: test
	echo ''


test_python_setup: ${file_pytest_genscript}
	echo '==> generating "py.test file for packaging in dist"'
	py.test --genscript=${file_pytest_genscript}


test: ${files} test_python_setup
	echo ''
	echo '==> use "py.test test" directly: '
	pytest test
	echo ''
	echo '==> use "python setup.py test": '
	python setup.py test

# just py.test weed
stest: 
	py.test test 


# make a source distribution in dist/
sdist: ${files} test
	python setup.py sdist


# upload to pypi
upload: sdist
	python setup.py sdist upload


install : test
	python setup.py install


# git push to github
# do `git remote add origin https://github.com/darkdarkfruit/python-weed.git` first
git_push:
	git push 


# git push with tags
git_push_tags:
	git push --tags
