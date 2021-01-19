files = weed/conf.py weed/__init__.py weed/master.py weed/operation.py weed/util.py weed/version.py weed/volume.py

default: test
	echo ''
	pytest .



test: ${files}
	echo ''
	echo '==> use "pytest ." directly: '
	pytest .
	# echo ''
	# echo '==> use "python setup.py test": '
	# python setup.py test

test_with_setup: ${files}
	echo ''
	echo '==> use "python setup.py test": '
	python3.9 setup.py test

# just pytest weed
stest: 
	pytest .


# make a source distribution in dist/
sdist: ${files} test
	python3.9 setup.py sdist


# upload to pypi
upload: sdist
	# python setup.py sdist upload
	# pip3.9 install twine
	twine upload dist/*


install : test
	python3.9 setup.py install


# git push to github
# do `git remote add origin https://github.com/darkdarkfruit/python-weed.git` first
git_push:
	git push 


# git push with tags
git_push_tags:
	git push --tags
