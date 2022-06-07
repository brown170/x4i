x4i - The EXFOR Interface
=========================

**Date**:   20 May 2022

**Author**: David Brown

**Description**:
x4i provides a "simple" python interface to the EXFOR library, allowing users to
search for and then translate EXFOR files into an easy to understand (and then plot) form.

Detailed instructions are provided in https://github.com/brown170/x4i/blob/main/doc/x4i/user-guide/x4i.pdf

Please ensure your `git` installation has large file support (see https://git-lfs.github.com).



Easiest installation: using pip & git
=====================================

    > $ pip install git+https://github.com/brown170/x4i

This version of the installation process automatically installs the 2021-03-08 version of the EXFOR database.


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

  * For site-wide installation.  Assuming you are in the directory containing x4i's `setup.py` file (You can delete the x4i project once this is complete):
      > $ sudo python setup.py install



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

3. To get the EXFOR library from the IAEA, run the install script.  This will install the 2021-03-08 version.  Assuming you are in the directory containing x4i's `setup.py` file, do:
   > $ ./install.py



How do I import new EXFOR data?
===============================
The IAEA distributes zipfiles containing the entire EXFOR database, one entry per file, at https://www-nds.iaea.org/exfor-master/x4toc4/.
x4i can ben updated with the contents of this file.  Assuming you just downloaded the EXFOR file X4-2010-12-31.zip,
do:

> $ python bin/x4i/setup-exfor-db.py --x4c4-master X4-2010-12-31.zip

Please read the help message (`python setup-exfor-db.py -h`) for more information.  After you finish this step,
be sure to update the information in the `x4i/data/database_info.json` file.



Changes since LLNL release (x4i-1.0)
====================================

0.     Update installation instructions (David Brown <dbrown@bnl.gov>, 2021-06-16T12:22:06)
