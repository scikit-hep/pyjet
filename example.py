from pyjet import cluster
from pyjet.testdata import get_event

print("{0: <5} {1: >10} {2: >10} {3: >10} {4: >10}".format("jet#", "pT", "eta", "phi", "mass"))
# R=0.6 anti-kt (p=-1)
for i, jet in enumerate(cluster(get_event(), 0.6, -1, ep=True)[:6]):
    print("{0: <5} {1: 10.3f} {2: 10.3f} {3: 10.3f} {4: 10.3f}".format(i, jet.pt, jet.eta, jet.phi, jet.mass))
