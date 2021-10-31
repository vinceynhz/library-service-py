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
	venv/bin/gunicorn "service:start()" --timeout 1000 --log-config logging.conf