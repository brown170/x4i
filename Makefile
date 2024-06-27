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
	$(PYTHON)  bin/install-exfor-db.py --skip-indexing
	$(PYTHON)  bin/setup-exfor-db-index.py

x4i/dicts/dict_arc_all.json:
	$(CURL) https://nds.iaea.org/nrdc/file/dict.9130.json > $@

realclean:
	rm -rf venv

clean: 
