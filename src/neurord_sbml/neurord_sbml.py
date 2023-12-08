import argparse
import os
import sys
import time
from xml.etree import ElementTree as ET

import libsbml
import simplesbml

micron_cube_to_litre = 1e-15


# Validation
class validateSBML:
    def __init__(self, ucheck, silent):
        self.reader = libsbml.SBMLReader()
        self.ucheck = ucheck
        self.silent = silent
        self.numinvalid = 0

    def validate(self, file):
        if not os.path.exists(file):
            if not self.silent:
                print("[Error] %s : No such file." % file)
            self.numinvalid += 1
            return

        start = time.time()
        sbmlDoc = libsbml.readSBML(file)
        stop = time.time()
        timeRead = (stop - start) * 1000
        errors = sbmlDoc.getNumErrors()

        seriousErrors = False

        numReadErr = 0
        numReadWarn = 0
        errMsgRead = ""

        if errors > 0:
            for i in range(errors):
                severity = sbmlDoc.getError(i).getSeverity()
                if (severity == libsbml.LIBSBML_SEV_ERROR) or (
                    severity == libsbml.LIBSBML_SEV_FATAL
                ):
                    seriousErrors = True
                    numReadErr += 1
                else:
                    numReadWarn += 1

                errMsgRead = sbmlDoc.getErrorLog().toString()

        # If serious errors are encountered while reading an SBML document, it
        # does not make sense to go on and do full consistency checking because
        # the model may be nonsense in the first place.

        numCCErr = 0
        numCCWarn = 0
        errMsgCC = ""
        skipCC = False
        timeCC = 0.0

        if seriousErrors:
            skipCC = True
            errMsgRead += "Further consistency checking and validation aborted."
            self.numinvalid += 1
        else:
            sbmlDoc.setConsistencyChecks(
                libsbml.LIBSBML_CAT_UNITS_CONSISTENCY, self.ucheck
            )
            start = time.time()
            failures = sbmlDoc.checkConsistency()
            stop = time.time()
            timeCC = (stop - start) * 1000

            if failures > 0:
                isinvalid = False
                for i in range(failures):
                    severity = sbmlDoc.getError(i).getSeverity()
                    if (severity == libsbml.LIBSBML_SEV_ERROR) or (
                        severity == libsbml.LIBSBML_SEV_FATAL
                    ):
                        numCCErr += 1
                        isinvalid = True
                    else:
                        numCCWarn += 1

                if isinvalid:
                    self.numinvalid += 1

                errMsgCC = sbmlDoc.getErrorLog().toString()

        # print results
        #
        if not self.silent:
            print("                 filename : %s" % file)
            print("         file size (byte) : %d" % (os.path.getsize(file)))
            print("           read time (ms) : %f" % timeRead)

            if not skipCC:
                print("        c-check time (ms) : %f" % timeCC)
            else:
                print("        c-check time (ms) : skipped")

            print("      validation error(s) : %d" % (numReadErr + numCCErr))
            if not skipCC:
                print("    (consistency error(s)): %d" % numCCErr)
            else:
                print("    (consistency error(s)): skipped")

            print("    validation warning(s) : %d" % (numReadWarn + numCCWarn))
            if not skipCC:
                print("  (consistency warning(s)): %d" % numCCWarn)
            else:
                print("  (consistency warning(s)): skipped")

            if errMsgRead or errMsgCC:
                print()
                print("===== validation error/warning messages =====\n")
                if errMsgRead:
                    print(errMsgRead)
                if errMsgCC:
                    print("*** consistency check ***\n")
                    print(errMsgCC)
        return numCCErr + numCCWarn + numReadErr + numReadWarn



def main(args):
    rx = ET.parse(args.reactions_file)
    ic = ET.parse(args.initial_conditions_file)
    root = rx.getroot()
    ic_root = ic.getroot()

    ## Concentration in nanomolar
    concDict = {}
    for child in ic_root:
        if child.tag == "ConcentrationSet":
            for child2 in child:
                concDict[child2.attrib["specieID"]] = float(
                    child2.attrib["value"]
                )  # Nanomolarity to Molarity

    # Create SBML model from the NeuroRD model
    comp = "compartment"
    size_micron_cubed = 0.5  # micron-cube
    size = size_micron_cubed * micron_cube_to_litre  # micron-cube to litres
    # comp = 'c1' # Using the default SBML compartment
    isConc = True  # Input will be in concentration units (mol/L)
    model = simplesbml.SbmlModel(sub_units="nM", time_units="ms")
    compartment = model.addCompartment(size, comp)
    #   compartment.setVolume(size)
    #   compartment.setId(comp)
    #   compartment.setName(comp)

    ### Units

    ## ms
    ms = model.model.createUnitDefinition()
    ms.setId("ms")
    unit = ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_SECOND)
    unit.setScale(-3)
    unit.setExponent(1)
    unit.setMultiplier(1)

    ## nM
    nM = model.model.createUnitDefinition()
    nM.setId("nM")
    unit = nM.createUnit()
    unit.setKind(libsbml.UNIT_KIND_MOLE)
    unit.setScale(-9)
    unit.setExponent(1)
    unit.setMultiplier(1)

    ## ms^{-1}
    per_ms = model.model.createUnitDefinition()
    per_ms.setId("per_ms")
    unit = per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_SECOND)
    unit.setScale(-3)
    unit.setExponent(-1)
    unit.setMultiplier(1)

    ## nM^{-1} ms^{-1}
    per_nM_per_ms = model.model.createUnitDefinition()
    per_nM_per_ms.setId("per_nM_per_ms")
    unit = per_nM_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_MOLE)
    unit.setScale(-9)
    unit.setExponent(-1)
    unit.setMultiplier(1)

    unit = per_nM_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_SECOND)
    unit.setScale(-3)
    unit.setExponent(-1)
    unit.setMultiplier(1)

    ## nM^{-2} ms^{-1}
    per_nM2_per_ms = model.model.createUnitDefinition()
    per_nM2_per_ms.setId("per_nM2_per_ms")
    unit = per_nM2_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_MOLE)
    unit.setScale(-9)
    unit.setExponent(-2)
    unit.setMultiplier(1)

    unit = per_nM2_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_SECOND)
    unit.setScale(-3)
    unit.setExponent(-1)
    unit.setMultiplier(1)

    ## nM^{-3} ms^{-1}
    per_nM3_per_ms = model.model.createUnitDefinition()
    per_nM3_per_ms.setId("per_nM3_per_ms")
    unit = per_nM3_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_MOLE)
    unit.setScale(-9)
    unit.setExponent(-3)
    unit.setMultiplier(1)

    unit = per_nM3_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_SECOND)
    unit.setScale(-3)
    unit.setExponent(-1)
    unit.setMultiplier(1)

    ## nM^{-4} ms^{-1}
    per_nM4_per_ms = model.model.createUnitDefinition()
    per_nM4_per_ms.setId("per_nM4_per_ms")
    unit = per_nM4_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_MOLE)
    unit.setScale(-9)
    unit.setExponent(-3)
    unit.setMultiplier(1)

    unit = per_nM4_per_ms.createUnit()
    unit.setKind(libsbml.UNIT_KIND_SECOND)
    unit.setScale(-3)
    unit.setExponent(-1)
    unit.setMultiplier(1)

    units = {
        0: per_ms,
        1: per_nM_per_ms,
        2: per_nM2_per_ms,
        3: per_nM3_per_ms,
        4: per_nM4_per_ms,
    }

    # create species
    species = {}
    reacNum = 0
    for i, child in enumerate(root):
        #     print(i)
        if child.tag == "Specie":
            if not child.attrib["id"][0].isdigit():
                specie = child.attrib["id"]
                if isConc:
                    spec_name = "[{}]".format(specie)
                else:
                    spec_name = specie
                # print(i, spec_name, specie)
                model.addSpecies(spec_name, concDict[child.attrib["name"]], comp=comp)

            else:
                specie = "_" + child.attrib["id"]
                if isConc:
                    spec_name = "[{}]".format(specie)
                else:
                    spec_name = specie
                # print(i, spec_name, specie)
                model.addSpecies(spec_name, concDict[child.attrib["name"]], comp=comp)

            species.update({child.attrib["id"]: specie})

        elif child.tag == "Reaction":
            reacNum += 1
            reactants, products = [], []
            local_params = {}
            rorder, porder = {}, {}
            for reactant in child:
                if reactant.tag == "Reactant":
                    reac_id = species[reactant.attrib["specieID"]]
                    reactants.append(reac_id)
                    if "power" in reactant.attrib:
                        rorder[reac_id] = reactant.attrib["power"]
                    else:
                        rorder[reac_id] = "1"
                elif reactant.tag == "Product":
                    reac_id = species[reactant.attrib["specieID"]]
                    products.append(reac_id)
                    if "power" in reactant.attrib:
                        porder[reac_id] = reactant.attrib["power"]
                    else:
                        porder[reac_id] = "1"
                elif reactant.tag == "forwardRate":
                    # local_params.update({'kon':float(reactant.text)})
                    reac_ord = [
                        r + "^" + rorder[r] if rorder[r] != "1" else r
                        for r in reactants
                    ]

                    total_rord = sum(int(rorder[r]) for r in rorder.keys()) - 1

                    # print(reac_ord)

                    kin_law = "{}*(kon_{}*{} )".format(
                        comp, reacNum, "*".join(reac_ord)
                    )  #'comp*(kon*E*S-koff*ES)'

                    model.addParameter(
                        "kon_{}".format(reacNum),
                        float(reactant.text),
                        units=units[total_rord].id,
                    )

                elif reactant.tag == "reverseRate":
                    # local_params.update({'koff':float(reactant.text)})
                    prod_ord = [
                        r + "^" + porder[r] if r in porder[r] != "1" else r
                        for r in products
                    ]

                    total_pord = sum(int(porder[r]) for r in porder.keys()) - 1
                    # print(prod_ord)
                    kin_law = "{}*(kon_{}*{} - koff_{}*{})".format(
                        comp, reacNum, "*".join(reac_ord), reacNum, "*".join(prod_ord)
                    )  #'comp*(kon*E*S-koff*ES)'

                    model.addParameter(
                        "koff_{}".format(reacNum),
                        float(reactant.text),
                        units=units[total_pord].id,
                    )

            # print(reactants, products, kin_law, local_params)
            model.addReaction(
                reactants,
                products,
                kin_law,
                local_params=local_params,
                rxn_id="r{}".format(reacNum),
            )

    # serialization
    if args.display_only:
        print(model.toSBML())
    else:
        with open(args.output_file, "w") as f:
            f.write(model.toSBML())

    if args.validate:
        if args.unit_validation:
            enableUnitCCheck = True
        else:
            enableUnitCCheck = False

        validator = validateSBML(enableUnitCCheck)

        fnum = 0

        validator.validate(args.output_file)
        numinvalid = validator.numinvalid

        print(
            "---------------------------------------------------------------------------"
        )
        print(
            "Validated %d files, %d valid files, %d invalid files"
            % (fnum, fnum - numinvalid, numinvalid)
        )
        if not enableUnitCCheck:
            print("(Unit consistency checks skipped)")

        if numinvalid > 0:
            sys.exit(1)


def get_parser():
    ### Command line input parsing here. ###########
    parser = argparse.ArgumentParser(
        prog="python " + sys.argv[0],
        description="Combines NeuroRD files and units into an SBML file",
    )

    neurord_group = parser.add_argument_group("neuroRD files")
    neurord_group.add_argument(
        "-r", "--reactions-file", help="NeuroRD file with reactions.", default=""
    )
    neurord_group.add_argument(
        "-ic",
        "--initial-conditions-file",
        help="NeuroRD file with initial conditions for the model",
        default="",
    )

    sbml_group = parser.add_argument_group("Output")
    sbml_group.add_argument(
        "-d",
        "--display-only",
        help="Use to display SBML only",
        default=False,
        action="store_true",
    )
    sbml_group.add_argument(
        "-v",
        "--validate",
        help="Validate SBML file",
        default=False,
        action="store_true",
    )
    sbml_group.add_argument(
        "-u",
        "--unit-validation",
        help="Validate units",
        default=False,
        action="store_true",
    )
    sbml_group.add_argument(
        "-o", "--output-file", type=str, help="SBML file to output model"
    )

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    # if args.signature_file:
    #    with open (args.signature_file, 'r') as f:
    #        args.signatures.extend(f.read().splitlines())

    # if not args.cspace_files and not args.signatures:
    #    parser.error ('Either --files or --signatures is required.')
    main(args)
