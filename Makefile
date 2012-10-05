
all: .venv gummy.sqlite

.venv:
	virtualenv .venv
	.venv/bin/python setup.py develop

gummy.sqlite: .venv
	.venv/bin/initialize_gummy_db development.ini

run: .venv gummy.sqlite
	.venv/bin/pserve --reload development.ini

clean:
	rm -rf .venv gummy.sqlite
