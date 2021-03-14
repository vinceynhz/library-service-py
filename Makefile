dev-init:
	python -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt
	pip install -e .
	python db-init.py

init:
	pip install -r requirements.txt
	pip install .
	python db-init.py

test:
	coverage run --omit="venv/*,*test_*.py" -m unittest -v tests/test_*.py
	coverage report
	coverage html

dev:
	. venv/bin/activate
