VENV_PATH = $(VENV_PATH)

ifeq ($(OS),Windows_NT)
	VENV_PATH = venv/Scripts
endif

venv: $(VENV_PATH)/activate
$(VENV_PATH)/activate: requirements.txt
	test -d venv || python -m venv venv
	$(VENV_PATH)/pip install -Ur requirements.txt
	$(VENV_PATH)/pip install install -e .
	touch $(VENV_PATH)/activate
	test -d database || mkdir database

clean:
	rm -rRf database/library.db

db: venv
	$(VENV_PATH)/python db-init.py

test: venv
	$(VENV_PATH)/coverage run --omit="venv/*,*test_*.py" -m unittest -v tests/test_*.py
	$(VENV_PATH)/coverage report
	$(VENV_PATH)/coverage html

run: db
	$(eval NPROC := $(shell nproc))
	$(eval WORKERS := $(shell expr 2 \* ${NPROC} + 1))
	$(VENV_PATH)/gunicorn "service:start()" -w ${WORKERS} --timeout 1000 --log-config logging.conf

cli: venv
	$(VENV_PATH)/python cli.py

ui: venv
	$(VENV_PATH)/python ./src/main/python/main.py