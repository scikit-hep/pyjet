#ifndef FASTJET_H
#define FASTJET_H

#ifdef PYJET_STANDALONE

#define _USING_EXTERNAL_FASTJET 0
#include "fjcore.h"
namespace fastjet = fjcore;

namespace fjcore {
enum  AreaType {
    invalid_area = -1,
    active_area = 0,
    active_area_explicit_ghosts = 1,
    one_ghost_passive_area = 10,
    passive_area = 11,
    voronoi_area = 20
};

class AreaDefinition {
    public:
    AreaDefinition(AreaType type) {}
    AreaDefinition() {}
};

class ClusterSequenceArea: public ClusterSequence {
    public:
    ClusterSequenceArea(std::vector<PseudoJet>, JetDefinition&, AreaDefinition&) {}
};
}

#else

#define _USING_EXTERNAL_FASTJET 1
#include "fastjet/PseudoJet.hh"
#include "fastjet/ClusterSequence.hh"
#include "fastjet/ClusterSequenceArea.hh"

#endif

#include <vector>


void silence() {
    fastjet::ClusterSequence::set_fastjet_banner_stream(NULL);
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
