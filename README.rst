Creating images with radmc3d
============================

This repository serves as a template for using radmc3d to create FITS
images/data-cubes from your model data.

We're only using radmc3d to produce the image itself.  This assumes that
you already have temperature data for your model.  If not, you will
instead need to specify a luminosity source and use radmc3d mctherm.

Software requirements
---------------------
The scripts require Python >= 3.7

radmc3d may be obtained from https://www.ita.uni-heidelberg.de/~dullemond/software/radmc-3d/

For creating FITS files, ``to_fits.py`` uses the radmc3dPy library which
is included in the radmc3d distribution.  If you haven't already you can
install it, for example, with:

.. code::

    pip3 install --editable /path/to/radmc3d-2.0/python/radmc3dPy

See https://www.ita.uni-heidelberg.de/~dullemond/software/radmc-3d/manual_radmc3d/installation.html#how-to-install-and-use-the-python-radmc3dpy-library for more info.

radmc3dPy also depends on astropy:

.. code::

    pip3 install astropy

Required data
-------------

The model
.........

You'll need to provide the temperature, gas velocity, dust density, and
gas number density fields for your model to ``to_radmc3d.py`` in CGS
units.

The example ``to_radmc3d.py`` creates a dummy protoplanetary disk model
to serve as a guide to show what goes where.  Edit the script to replace
it with your own data.

Molecular data
..............

Molecular data may be downloaded from https://home.strw.leidenuniv.nl/~moldata/

The ``download_molecules`` script will do this for you.  For example,
run

.. code::

    $ ./download_molecules co 13co c18o

to download common isotopologues of CO.

Dust opacity data
.................

The radmc3d distribution contains some sample dust opacities which may
be used:

.. code::

    $ cp /path/to/radmc3d-2.0/examples/run_1dpp_dust/dustkappa_silicate.inp .

Alternatively, see https://www.ita.uni-heidelberg.de/~dullemond/software/radmc-3d/manual_radmc3d/opacitieswww.html
for how to convert other dust opacity data into the required format.

Running the scripts
-------------------

Once all the data is in place, run ``to_radmc3d.py``:

.. code::

    $ python3 to_radmc3d.py

This will put radmc3d input files into the directory ``out`` (or
whatever you have set ``odir`` to)

To create a multi-wavelength 400x400 px image at 30 degree inclination
with 10 5 km/s channels (between ±25 km/s), centered around the first
molecular line of the first molecule specified in ``to_radmc3d.py``, you
can run:

.. code::

    $ cd out
    $ radmc3d image imolspec 1 iline 1 widthkms 25 linenlam 10 incl 30 npix 400

This will produce an image.out file.

If you want to create a FITS image, ``to_fits.py`` is a convenient
command-line wrapper script over the ``radmc3dPy`` library.  To create a
FITS file with the default options:

.. code::

    $ python3 ../to_fits.py image.out -o image.fits

This will produce the file ``image.fits``

For more options, run ``to_fits.py --help``
