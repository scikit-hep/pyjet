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
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.colors import LinearSegmentedColormap, LogNorm

eta_min, eta_max = -4., 4.
extent = eta_min, eta_max, -np.pi, np.pi

event = ep2ptepm(get_event())
# create regular grid of ghosts
eta_edges = np.linspace(eta_min, eta_max, 101)
phi_edges = np.linspace(-np.pi, np.pi, 101)
eta = np.linspace(eta_min, eta_max, 101)[:-1] + (eta_max - eta_min) / 200
phi = np.linspace(-np.pi, np.pi, 101)[:-1] + (2*np.pi / 200)
X, Y = np.meshgrid(eta, phi)
ghosts = np.zeros(eta.shape[0] * phi.shape[0], dtype=DTYPE_PTEPM)
ghosts['pT'] = 1e-8
ghosts['eta'] = X.ravel()
ghosts['phi'] = Y.ravel()
# add ghosts to the event
event = np.concatenate([event, ghosts], axis=0)

fig = plt.figure(figsize=(9, 3))

for p in (-1, 0, 1):
    # cluster
    sequence = cluster(event, R=1.0, p=p)
    # plot jet areas
    jets = sequence.inclusive_jets(ptmin=10)
    colors = cm.rainbow(np.linspace(0, 1, len(jets)))
    cmap = LinearSegmentedColormap.from_list('cmap', colors, len(colors))
    ax = fig.add_subplot(1, 3, p + 2)
    area = np.zeros((eta_edges.shape[0] - 1, phi_edges.shape[0] - 1),
                    dtype=np.float64)
    for ijet, jet in enumerate(jets):
        constit = jet.constituents_array()
        jetarea, _, _ = np.histogram2d(constit['eta'], constit['phi'],
                                       bins=(eta_edges, phi_edges))
        area += (jetarea > 0) * (ijet + 1)
    ax.imshow(np.ma.masked_where(area == 0, area).T, cmap=cmap,
              extent=extent, aspect=(eta_max - eta_min) / (2*np.pi),
              interpolation='none', origin='lower')
    # overlay original event
    particles = ep2ptepm(get_event())
    ax.scatter(particles['eta'], particles['phi'],
               s=30 * particles['pT'] / particles['pT'].max())
    ax.set_xlim(extent[:2])
    ax.set_ylim(extent[2:])
fig.tight_layout()
fig.savefig('jets.png')
