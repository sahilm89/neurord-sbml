NeuroRD-SBML
-------------

Installation
==============

You can use neuro-sbml using command::

    $ python neurord-sbml -r <path/to/Reactions.xml> -ic <path/to/IC_singlecompartment.xml> -o </path/to/output_SBML_file.xml>

To turn on file validation, use the argument -v. To also add unit-checking, use -u::
    $ python neurord-sbml -v -u -r <path/to/Reactions.xml> -ic <path/to/IC_singlecompartment.xml> -o </path/to/output_SBML_file.xml>

More information can be found by ``python neurord-sbml help``

Basics
=========

This package converts combines NeuroRD files into SBML files. NeuroRD divides the model up into several sections in the form of XML files: Reacting species, Reactions and rate parameters, initital conditions and morphology files. Here, we take these files and use the simple0sbml package to construct a corresponding SBML file with appropriate units.
