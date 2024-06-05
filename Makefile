PYTHON=python3

.PHONY: clean realclean data check test install 

all: venv x4i/data/index.tbl

test: check

check:
	. venv/bin/activate; pytest; deactivate

venv:
	$(PYTHON) -m venv venv --system-site-packages; . venv/bin/activate; $(PYTHON) -m pip install --upgrade pip; pip install -r requirements.txt ; deactivate

x4i/data/index.tbl:
	$(PYTHON) install.py 

realclean:
	rm -rf venv

clean: 
