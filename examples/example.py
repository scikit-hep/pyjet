from pyjet import cluster
from pyjet.testdata import get_event
from numpy.lib.recfunctions import append_fields
from numpy.testing import assert_array_equal
import numpy as np

# event's dtype=np.dtype([('E', 'f8'), ('px', 'f8'), ('py', 'f8'), ('pz', 'f8')])
# this is the sample event shipped with FastJet with E moved to the first column
event = get_event()

# You can associate arbitrary additional information to each particle
# and this information can be accessed as attributes of the PseudoJets
event = append_fields(event, 'id', data=np.arange(len(event)))

sequence = cluster(event, R=0.6, p=-1)
jets = sequence.inclusive_jets()

ids = []
for jet in jets:
    for constit in jet:
        ids.append(constit.id)
ids.extend([p.id for p in sequence.unclustered_particles()])
# Are all particles accounted for?
assert_array_equal(sorted(ids), np.arange(len(event)))

# Printing a few things here as a demonstration of the basic functionality
print("{0: <5} {1: >10} {2: >10} {3: >10} {4: >10} {5: >10}".format(
    "jet#", "pT", "eta", "phi", "mass", "#constit."))
for i, jet in enumerate(jets[:6]):
    print("{0: <5} {1: 10.3f} {2: 10.3f} {3: 10.3f} {4: 10.3f} {5: 10}".format(
        i + 1, jet.pt, jet.eta, jet.phi, jet.mass, len(jet)))

print("\nThe 6th jet has the following constituents:")
for constit in jets[5]:
    print(constit)
print("\nGet the constituents as an array (pT, eta, phi, mass):")
print(jets[5].constituents_array())
print("\nor (E, px, py, pz):")
print(jets[5].constituents_array(ep=True))

# Look at substructure with exclusive jets
print("\n\nReclustering the constituents of the hardest jet with the kt algorithm")
cs2 = cluster(jets[0].constituents_array(), R=0.6, p=1)
print(cs2.inclusive_jets())
print("\nGo back in the clustering sequence to when there were two jets")
for subj in cs2.exclusive_jets(2):
    print(subj)
print("\nAsk how many jets there are with a given dcut")
dcut = 0.5
njets = cs2.n_exclusive_jets(dcut)
print("There are {0} jets with a dcut of {1}".format(njets, dcut))
print("\nGet the jets with the given dcut")
ejets_dcut = cs2.exclusive_jets_dcut(dcut)
for i, jet in enumerate(ejets_dcut):
    print(i + 1, jet)
