from pyjet import cluster
from pyjet.testdata import get_event

jets = cluster(get_event(), R=0.6, p=-1, ep=True)

print("{0: <5} {1: >10} {2: >10} {3: >10} {4: >10} {5: >10}".format(
    "jet#", "pT", "eta", "phi", "mass", "#constit."))
for i, jet in enumerate(jets[:6]):
    print("{0: <5} {1: 10.3f} {2: 10.3f} {3: 10.3f} {4: 10.3f} {5: 10}".format(
        i, jet.pt, jet.eta, jet.phi, jet.mass, len(jet)))
