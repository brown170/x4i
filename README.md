x4i - The EXFOR Interface
=========================

**Date**:   20 May 2022

**Author**: David Brown

**Description**:
x4i provides a python interface to the EXFOR library, allowing users to
search for and then translate EXFOR files into an easy to understand (and then plot) form.

Detailed instructions are provided in https://github.com/brown170/x4i/blob/main/doc/x4i/user-guide/x4i.pdf


Easiest installation: using pip & git
=====================================
1. Install the package:

    > $ pip install git+https://github.com/brown170/x4i -v

2. Acquire, install and index the EXFOR file

    > $ install-exfor-db.py

This version of the installation process automatically installs the 2021-03-08 version of the EXFOR database.  
As x4i must rebuild the database, installation may take some time.  `install-exfor-db.py` has other options that 
may be accessed with the built-in help (`install-exfor-db.py -h`).


Installation from a tarball distribution
========================================

1. Unpack the distribution

2. Installation options:
  * Old-fashioned local installation: put x4i in your $PYTHONPATH.  Assuming you are in the directory containing x4i's `setup.py` file:
      > $ export PYTHONPATH=$PYTHONPATH:\`pwd\`

  * Installation with pip (You can delete the x4i project once this is complete)
      > $ pip install path/to/x4i/setup.py/directory

  * Editable pip installation
      > $ pip install -e path/to/x4i/setup.py/directory


Source installation from git
============================
This assumes that you will be editing the project in some fashion.
This installation does not automatically include the IAEA data files.
You will need to download them yourself as described in step 3. below.

1. Clone the project
   > $ git clone https://github.com/brown170/x4i.git

2. Installation options:
   * Old-fashioned local installation: put x4i in your $PYTHONPATH.  Assuming you are in the directory containing x4i's `setup.py` file:
     > $ export PYTHONPATH=$PYTHONPATH:\`pwd\`

   * Editable installation using pip:
     > $ pip install -e path/to/x4i/setup.py/directory

3. Acquire, install and index the EXFOR file

    > $ install-exfor-db.py

This version of the installation process automatically installs the 2021-03-08 version of the EXFOR database.  
As x4i must rebuild the database, installation may take some time.  `install-exfor-db.py` has other options that 
may be accessed with the built-in help (`install-exfor-db.py -h`).


How do I import new EXFOR data?
===============================
The IAEA distributes the EXFOR files in a variety of ways as of the time of writing.  
At this time, all have equivalent content, but different arrangements of data:
  - https://github.com/IAEA-NDS/exfor_master.git
  - https://github.com/IAEA-NRDCNetwork/EXFOR-Archive.git
  - https://www-nds.iaea.org/nrdc/exfor-master/ - this is the main master, and all contents combined in one file
  - https://www-nds.iaea.org/nrdc/exfor-master/entry/, specifically https://www-nds.iaea.org/nrdc/exfor-master/entry/entry.zip
The repo at https://github.com/IAEA-NDS/exfor_master.git is our default scheme, as encoded in the 
`setup-exfor-db-index.py` script.  Other options have not been fully implemented.


Changes since LLNL release (x4i-1.0)
====================================

0.     Update installation instructions (David Brown <dbrown@bnl.gov>, 2021-06-16T12:22:06)
