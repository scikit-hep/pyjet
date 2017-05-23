#ifndef CORE_H
#define CORE_H
#ifdef PYJET_STANDALONE
#include "fjcore.h"
namespace fastjet = fjcore;
#else
#include "fastjet/PseudoJet.hh"
#include "fastjet/ClusterSequence.hh"
#endif

#include <cmath>
#include <vector>


fastjet::ClusterSequence* cluster_genkt(std::vector<fastjet::PseudoJet>& inputs, double R, int p) {
  fastjet::ClusterSequence::set_fastjet_banner_stream(NULL);
  // Run Fastjet algorithm and sort jets in pT order
  fastjet::JetDefinition def(fastjet::JetDefinition(fastjet::genkt_algorithm, R, p));
  fastjet::ClusterSequence* sequence = new fastjet::ClusterSequence(inputs, def);
  return sequence;
}


void array_to_pseudojets(unsigned int size, unsigned int fields, double* array,
                         std::vector<fastjet::PseudoJet>& output, double eta_max,
                         bool ep) {
    output.clear();
    fastjet::PseudoJet pseudojet;
    double* fourvect;
    double E, px, py, pz;
    for (unsigned int i = 0; i < size; ++i) {
        fourvect = &array[i * fields];
        // Note the constructor argument order is px, py, pz, E
        if (ep) {
            pseudojet = fastjet::PseudoJet(fourvect[1], fourvect[2], fourvect[3], fourvect[0]);
        } else {
            px = fourvect[0] * cos(fourvect[2]); // pt cos(phi)
            py = fourvect[0] * sin(fourvect[2]); // pt sin(phi)
            pz = fourvect[0] * sinh(fourvect[1]); // pt sinh(eta)
            E = sqrt(px*px + py*py + pz*pz + fourvect[3] * fourvect[3]);
            pseudojet = fastjet::PseudoJet(px, py, pz, E);
        }
        if ((eta_max > 0) && (abs(pseudojet.pseudorapidity()) > eta_max)) {
            continue;
        }
        output.push_back(pseudojet);
    }
}

#endif
