venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || python -m venv venv
	venv/bin/pip install -Ur requirements.txt
	venv/bin/pip install install -e .
	touch venv/bin/activate

clean:
	rm -rRf database/library.db

db: venv
	venv/bin/python db-init.py

test: venv
	venv/bin/coverage run --omit="venv/*,*test_*.py" -m unittest -v tests/test_*.py
	venv/bin/coverage report
	venv/bin/coverage html

run: db
	$(eval NPROC := $(shell nproc))
	$(eval WORKERS := $(shell expr 2 \* ${NPROC} + 1))
	venv/bin/gunicorn "service:start()" -w ${WORKERS} --timeout 1000 --log-config logging.conf

cli: venv
	venv/bin/python cli.py

ui: venv
	venv/bin/fbs run