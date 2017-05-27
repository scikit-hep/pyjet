import numpy as np
from pyjet import cluster, DTYPE_PTEPM
from pyjet.utils import ep2ptepm
from pyjet.testdata import get_event

sequence = cluster(get_event(), R=0.6, p=-1, ep=True)
jets = sequence.inclusive_jets()

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

# plot the jet areas
event = ep2ptepm(get_event())
# add grid of infinitely soft particles
eta = np.linspace(-5, 5, 100)
phi = np.linspace(-np.pi, np.pi, 100)
X, Y = np.meshgrid(eta, phi)
ghosts = np.zeros(eta.shape[0] * phi.shape[0], dtype=DTYPE_PTEPM)
ghosts['pT'] = 1e-8
ghosts['eta'] = X.ravel()
ghosts['phi'] = Y.ravel()
event = np.concatenate([event, ghosts], axis=0)
sequence = cluster(event, R=0.6, p=-1)
jets = sequence.inclusive_jets(ptmin=1)

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111)
constits = jets[1].constituents_array()
ax.hist2d(constits['eta'], constits['phi'], bins=(eta, phi), weights=constits['pT'],
          norm=LogNorm(vmin=constits['pT'].min(), vmax=constits['pT'].max()))
fig.tight_layout()
fig.savefig('jets.png')
