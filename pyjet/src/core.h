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


void silence() {
    fastjet::ClusterSequence::set_fastjet_banner_stream(NULL);
}


fastjet::ClusterSequence* cluster_genkt(std::vector<fastjet::PseudoJet>& inputs, double R, int p) {
  // Run Fastjet algorithm and sort jets in pT order
  fastjet::JetDefinition def(fastjet::JetDefinition(fastjet::genkt_algorithm, R, p));
  fastjet::ClusterSequence* sequence = new fastjet::ClusterSequence(inputs, def);
  return sequence;
}

#endif
