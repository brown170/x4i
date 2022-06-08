#! /usr/bin/env sh

export PYTHONPATH=`pwd`
python x4i/test/test_exfor_dataset.py
python x4i/test/test_exfor_manager.py
python x4i/test/test_exfor_entry.py
python x4i/test/test_exfor_reaction.py
python x4i/test/test_exfor_fields.py
python x4i/test/test_exfor_full_integration.py
