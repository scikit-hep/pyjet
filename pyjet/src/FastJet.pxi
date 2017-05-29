
cdef extern from "core.h" namespace "fastjet":
    cdef cppclass PseudoJet:
        PseudoJet(const double, const double, const double, const double)
        PseudoJet()
        vector[PseudoJet] constituents()
        double E()
        double Et()
        double e()
        double px()
        double py()
        double pz()
        double phi_std()
        double rapidity()
        double pseudorapidity()
        double perp()
        double m()
        double mperp()
        double kt_distance(PseudoJet&)
        double plain_distance(PseudoJet&)
        double squared_distance(PseudoJet&)
        double delta_R(PseudoJet&)
        double delta_phi_to(PseudoJet&)
        double beam_distance()
        bool contains(PseudoJet&)
        bool has_valid_cluster_sequence()
        ClusterSequence* associated_cluster_sequence()
        bool has_constituents()

    vector[PseudoJet] sorted_by_pt(vector[PseudoJet]& jets)

    cdef cppclass ClusterSequence:
        vector[PseudoJet] inclusive_jets(double ptmin)
        void delete_self_when_unused()

    cdef cppclass SharedPtr[T]:
        pass


cdef extern from "core.h" namespace "fastjet::PseudoJet":
    cdef cppclass UserInfoBase:
        pass


cdef extern from "core.h":
    void silence()
    ClusterSequence* cluster_genkt(vector[PseudoJet]&, double, int)
