import simplesbml


def test_model():
    model = None
    assert model is None
    model = simplesbml.SbmlModel()
    assert model is not None


def test_model_with_attributes():
    model = None
    assert model is None
    model = simplesbml.SbmlModel(time_units="other_unit")
    assert model is not None


def test_add_compartment():
    model = simplesbml.SbmlModel()
    compartment = model.addCompartment()
    assert compartment is not None
    volume = compartment.getVolume()
    assert volume == 1.0
    compartment_id = compartment.getId()
    assert compartment_id == "c2"


def test_add_compartment_with_attributes():
    model = simplesbml.SbmlModel()
    compartment = model.addCompartment(2.3, "compartment")
    assert compartment is not None
    volume = compartment.getVolume()
    assert volume == 2.3
    compartment_id = compartment.getId()
    assert compartment_id == "compartment"
