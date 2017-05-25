.. -*- mode: rst -*-

pyjet: The interface between FastJet and NumPy
==============================================

pyjet allows you to perform jet clustering with `FastJet <http://fastjet.fr/>`_
on `NumPy <http://www.numpy.org/>`_ arrays.

By default pyjet only depends on NumPy and internally uses FastJet's standalone
fjcore release.

pyjet provides the ``cluster()`` function that takes a NumPy array as input
and returns the jets as lists of ``PyPseudoJet`` or an array of four-momenta.
The dtype of the input array can be either:

.. code-block:: python

   np.dtype([('pT', 'f8'), ('eta', 'f8'), ('phi', 'f8'), ('mass', 'f8')])

or if ``cluster(..., ep=True)``:

.. code-block:: python

   np.dtype([('E', 'f8'), ('px', 'f8'), ('py', 'f8'), ('pz', 'f8')])


Standalone Installation
-----------------------

To simply use the built-in FastJet source::

   pip install --user pyjet

And you're good to go!

Get example.py and run it::

	curl -O https://raw.githubusercontent.com/ndawe/pyjet/master/example.py
	python example.py
	jet#          pT        eta        phi       mass  #constit.
	1        983.280     -0.868      2.905     36.457         34
	2        901.745      0.221     -0.252     51.850         34
	3         67.994     -1.194     -0.200     11.984         32
	4         12.465      0.433      0.673      5.461         13
	5          6.568     -2.629      1.133      2.099          9
	6          6.498     -1.828     -2.248      3.309          6

	The 6th jet has the following constituents:
	PyPseudoJet(pt=0.096, eta=-2.166, phi=-2.271, mass=0.000)
	PyPseudoJet(pt=2.200, eta=-1.747, phi=-1.972, mass=0.140)
	PyPseudoJet(pt=1.713, eta=-2.037, phi=-2.469, mass=0.940)
	PyPseudoJet(pt=0.263, eta=-1.682, phi=-2.564, mass=0.140)
	PyPseudoJet(pt=1.478, eta=-1.738, phi=-2.343, mass=0.940)
	PyPseudoJet(pt=0.894, eta=-1.527, phi=-2.250, mass=0.140)


Using an External FastJet Installation
---------------------------------------

To take advantage of the full FastJet library and optimized O(NlnN) kt
and anti-kt algorithms, first install FastJet and then install pyjet with the
``--external-fastjet`` flag.

First install `CGAL <http://www.cgal.org/>`_ and `GMP <https://gmplib.org/>`_:

On a Debian-based system (Ubuntu)::

   sudo apt-get install libcgal-dev libcgal11v5 libgmp-dev libgmp10

On an RPM-based system (Fedora)::

   sudo dnf install gmp.x86_64 gmp-devel.x86_64 CGAL.x86_64 CGAL-devel.x86_64

On Mac OS::

   brew install cgal gmp wget

Then run pyjet's ``install-fastjet.sh`` script::

   curl -O https://raw.githubusercontent.com/ndawe/pyjet/master/install-fastjet.sh
   chmod +x install-fastjet.sh
   sudo ./install-fastjet.sh

Now install pyjet like::

   pip install --user pyjet --install-option="--external-fastjet"

pyjet will now use the external FastJet installation on your system.
