.. -*- mode: rst -*-

pyjet: The interface between FastJet and NumPy
==============================================

.. image:: https://img.shields.io/pypi/v/pyjet.svg
   :target: https://pypi.python.org/pypi/pyjet

pyjet allows you to perform jet clustering with `FastJet <http://fastjet.fr/>`_
on `NumPy <http://www.numpy.org/>`_ arrays. By default pyjet only depends on
NumPy and internally uses FastJet's standalone fjcore release. The interface
code is written in `Cython <http://cython.org/>`_ that then becomes compiled
C++, so it's fast. Remember that if you use pyjet then you are using FastJet
and should cite the papers listed `here <http://fastjet.fr/about.html>`_.

pyjet provides the ``cluster()`` function that takes a NumPy array as input
and returns a ``ClusterSequence`` from which you can access the jets:

.. code-block:: python

   from pyjet import cluster
   from pyjet.testdata import get_event

   vectors = get_event()
   sequence = cluster(vectors, R=1.0, p=-1)
   jets = sequence.inclusive_jets()  # list of PseudoJets

The first four fields of the input array ``vectors`` must be either:

.. code-block:: python

   np.dtype([('pT', 'f8'), ('eta', 'f8'), ('phi', 'f8'), ('mass', 'f8')])

or if ``cluster(..., ep=True)``:

.. code-block:: python

   np.dtype([('E', 'f8'), ('px', 'f8'), ('py', 'f8'), ('pz', 'f8')])

Note that the field names of the input array need not match 'pT', 'eta', 'phi',
'mass' etc. pyjet only assumes that the first four fields are those quantities.
This array may also have additional fields of any type. Additional fields will
then become attributes of the ``PseudoJet`` objects.

See the `examples <https://github.com/ndawe/pyjet/tree/master/examples>`_ to
get started:

.. image:: https://github.com/ndawe/pyjet/raw/master/examples/jet_areas.png


Standalone Installation
-----------------------

To simply use the built-in FastJet source::

   pip install --user pyjet

And you're good to go!

Get example.py and run it::

	curl -O https://raw.githubusercontent.com/ndawe/pyjet/master/examples/example.py
	python example.py
	jet#          pT        eta        phi       mass  #constit.
	1        983.280     -0.868      2.905     36.457         34
	2        901.745      0.221     -0.252     51.850         34
	3         67.994     -1.194     -0.200     11.984         32
	4         12.465      0.433      0.673      5.461         13
	5          6.568     -2.629      1.133      2.099          9
	6          6.498     -1.828     -2.248      3.309          6

	The 6th jet has the following constituents:
	PseudoJet(pt=0.096, eta=-2.166, phi=-2.271, mass=0.000)
	PseudoJet(pt=2.200, eta=-1.747, phi=-1.972, mass=0.140)
	PseudoJet(pt=1.713, eta=-2.037, phi=-2.469, mass=0.940)
	PseudoJet(pt=0.263, eta=-1.682, phi=-2.564, mass=0.140)
	PseudoJet(pt=1.478, eta=-1.738, phi=-2.343, mass=0.940)
	PseudoJet(pt=0.894, eta=-1.527, phi=-2.250, mass=0.140)

	Get the constituents as an array (pT, eta, phi, mass):
	[( 0.09551261, -2.16560157, -2.27109083,   4.89091390e-06)
	 ( 2.19975694, -1.74672746, -1.97178728,   1.39570000e-01)
	 ( 1.71301882, -2.03656511, -2.46861524,   9.39570000e-01)
	 ( 0.26339374, -1.68243005, -2.56397904,   1.39570000e-01)
	 ( 1.47781519, -1.7378898 , -2.34304346,   9.39570000e-01)
	 ( 0.89353864, -1.52729244, -2.24973202,   1.39570000e-01)]

	or (E, px, py, pz):
	[( 0.42190436, -0.06155242, -0.07303395, -0.41095089)
	 ( 6.50193926, -0.85863306, -2.02526044, -6.11692764)
	 ( 6.74203628, -1.33952806, -1.06775374, -6.45273802)
	 ( 0.74600384, -0.22066287, -0.1438199 , -0.68386087)
	 ( 4.43164941, -1.0311407 , -1.05862485, -4.07096881)
	 ( 2.15920027, -0.56111108, -0.69538886, -1.96067711)]


Using an External FastJet Installation
---------------------------------------

To take advantage of the full FastJet library and optimized O(NlnN) kt and
anti-kt algorithms you can first build and install FastJet and then install
pyjet with the ``--external-fastjet`` flag. Before building FastJet you will
need to install `CGAL <http://www.cgal.org/>`_ and `GMP
<https://gmplib.org/>`_.

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
