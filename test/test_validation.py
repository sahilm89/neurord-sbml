from src.neurord_sbml.neurord_sbml import validateSBML


def test_basic_sbml():
    validator = validateSBML(True, True)
    file_name = 'resources/basicSBML.xml'
    errors = validator.validate(file_name)
    assert (errors == 0)
