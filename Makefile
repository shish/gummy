
all: .venv gummy.sqlite

.venv:
	virtualenv .venv
	.venv/bin/python setup.py develop

gummy.sqlite: .venv
	.venv/bin/initialize_gummy_db development.ini

run: .venv gummy.sqlite
	.venv/bin/pserve --reload development.ini

pep8: .venv
	.venv/bin/pep8 --max-line-length 150 `find -name "*.py"` | tee .pep8.out

test: .venv pep8
	.venv/bin/nosetests -v --with-doctest `find -name "*.py"` --with-coverage --cover-package=gummy

clean:
	rm -rf .venv gummy.sqlite
