
all: test run

gummy.sqlite:
	.venv/bin/initialize_gummy_db development.ini

run:
	.venv/bin/pserve --reload development.ini

test:
	virtualenv .venv
	.venv/bin/python setup.py develop
	.venv/bin/pep8 --max-line-length 150 `find -name "*.py"` || true
	.venv/bin/nosetests -v --with-doctest --with-coverage --cover-package=gummy `find -name "*.py"`

clean:
	git clean -fdx
