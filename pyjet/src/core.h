#ifndef CORE_H
#define CORE_H

#ifdef PYJET_STANDALONE

#define _USING_EXTERNAL_FASTJET 0
#include "fjcore.h"
namespace fastjet = fjcore;

#else

#define _USING_EXTERNAL_FASTJET 1
#include "fastjet/PseudoJet.hh"
#include "fastjet/ClusterSequence.hh"

#endif

#include <vector>


void silence() {
    fastjet::ClusterSequence::set_fastjet_banner_stream(NULL);
}


fastjet::ClusterSequence* cluster_genkt(std::vector<fastjet::PseudoJet>& inputs, double R, int p) {
    // TODO: cythonize this and wrap JetDefinition
    fastjet::JetDefinition def(fastjet::JetDefinition(fastjet::genkt_algorithm, R, p));
    return new fastjet::ClusterSequence(inputs, def);
}


inline bool jet_has_area(fastjet::PseudoJet* jet) {
#ifdef PYJET_STANDALONE
    return false;
#else
    return jet->has_area();
#endif
}


inline double jet_area(fastjet::PseudoJet* jet) {
#ifdef PYJET_STANDALONE
    return -1;
#else
    return jet->area();
#endif
}


inline double jet_area_error(fastjet::PseudoJet* jet) {
#ifdef PYJET_STANDALONE
    return -1;
#else
    return jet->area_error();
#endif
}

#endif
