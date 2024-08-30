PYTHON=python3
CURL=curl

.PHONY: clean realclean data check test install 

all: venv src/x4i/data/index.tbl

test: check

check:
	. venv/bin/activate; pip install pytest; pytest; deactivate

venv:
	$(PYTHON) -m venv venv --system-site-packages; . venv/bin/activate; $(PYTHON) -m pip install --upgrade pip; pip install -e . ; deactivate

src/x4i/data/index.tbl:
	. venv/bin/activate; install-exfor-db; deactivate

src/x4i/dicts/dict_arc_all.json:
	$(CURL) https://nds.iaea.org/nrdc/file/dict.9130.json > $@

realclean:
	rm -rf venv

clean: 
