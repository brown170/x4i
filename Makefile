PYTHON=python3
CURL=curl

.PHONY: clean realclean data check test install 

all: venv x4i/data/index.tbl x4i/dicts/dict_arc_all.json

test: check

check:
	. venv/bin/activate; pytest; deactivate

venv:
	$(PYTHON) -m venv venv --system-site-packages; . venv/bin/activate; $(PYTHON) -m pip install --upgrade pip; pip install -r requirements.txt ; deactivate

x4i/data/index.tbl:
	$(PYTHON)  install-exfor-db.py

x4i/dicts/dict_arc_all.json:
	$(CURL) https://www-nds.iaea.org/nrdc/file/dict_arc_all.9929.json > $@

realclean:
	rm -rf venv

clean: 
