# -*- coding: utf-8 -*-
"""
This module implements the class StandardNetwork.
StandardNetwork creates a ring network as defined in Santhakumar et al. 2005
with some changes as in Yim et al. 2015.
See StandardNetwork docstring for details.
Created on Tue Nov 28 13:01:38 2017

@author: DanielM
"""

from ouropy import gennetwork
import numpy as np
from granulecell import GranuleCell
from mossycell_cat import MossyCell
from basketcell import BasketCell
from hippcell import HippCell


class TunedNetworkRobustness(gennetwork.GenNetwork):
    """ This model implements the ring model from Santhakumar et al. 2005.
    with some changes as in Yim et al. 2015.
    It features inhibition but omits the MC->GC connection.
    """
    name = "TunedNetworkRobustness"

    def __init__(self, seed=None, temporal_patterns=np.array([]),
                 spatial_patterns_gcs=np.array([]),
                 spatial_patterns_bcs=np.array([])):
        self.init_params = locals()
        self.init_params['self'] = str(self.init_params['self'])
        # Setup cells
        self.mk_population(GranuleCell, 2000)
        self.mk_population(MossyCell, 60)
        self.mk_population(BasketCell, 24)
        self.mk_population(HippCell, 24)

        # Add random variation to parameters for robustness analysis
        #gmax
        pp_to_gc_gmax = 1*10**(-3) + 1*10**(-3) * np.random.normal(0,0.2)
        pp_to_bc_gmax = 1*10**(-3) + 1*10**(-3) * np.random.normal(0,0.2)
        gc_to_bc_gmax = 2.5*10**(-2) + 2.5*10**(-2) * np.random.normal(0,0.2)
        gc_to_hc_gmax = 2.5*10**(-2) + 2.5*10**(-2) * np.random.normal(0,0.2)
        bc_to_gc_gmax = 1.2*10**(-3) + 1.2*10**(-3) * np.random.normal(0,0.2)
        hc_to_gc_gmax = 0.6*10**(-2) + 0.6*10**(-2) * np.random.normal(0,0.2)

        pp_to_gc_tau1 = 10 + 10 * np.random.normal(0,0.2)
        pp_to_bc_tau1 = 6.3 + 6.3 * np.random.normal(0,0.2)
        gc_to_bc_tau1 = 8.7 + 8.7 * np.random.normal(0,0.2)
        gc_to_hc_tau1 = 8.7 + 8.7 * np.random.normal(0,0.2)
        bc_to_gc_tau1 = 20 + 20 * np.random.normal(0,0.2)
        hc_to_gc_tau1 = 20 + 20 * np.random.normal(0,0.2)

        # Set seed for reproducibility
        if seed:
            self.set_numpy_seed(seed)

        # Setup recordings
        self.populations[0].record_aps()
        self.populations[1].record_aps()
        self.populations[2].record_aps()
        self.populations[3].record_aps()

        temporal_patterns = np.array(temporal_patterns)
        if (type(spatial_patterns_gcs) == np.ndarray and
           type(temporal_patterns) == np.ndarray):
            for pa in range(len(spatial_patterns_gcs)):
                # PP -> GC
                gennetwork.PerforantPathPoissonTmgsyn(self.populations[0],
                                                      temporal_patterns[pa],
                                                      spatial_patterns_gcs[pa],
                                                      'midd', 10, 0, 1, 0, 0,
                                                      1*10**(-3))

        if (type(spatial_patterns_bcs) == np.ndarray and
           type(temporal_patterns) == np.ndarray):
            for pa in range(len(spatial_patterns_bcs)):
                # PP -> BC
                gennetwork.PerforantPathPoissonTmgsyn(self.populations[2],
                                                      temporal_patterns[pa],
                                                      spatial_patterns_bcs[pa],
                                                      'ddend', 6.3, 0, 1, 0, 0,
                                                      1*10**(-3))

        # GC -> MC
        gennetwork.tmgsynConnection(self.populations[0], self.populations[1],
                                    12, 'proxd', 1, 7.6, 500, 0.1, 0, 0, 10,
                                    1.5, 0.2*10**(-2) * 10)

        # GC -> BC
        # Weight x4, target_pool = 2
        gennetwork.tmgsynConnection(self.populations[0], self.populations[2],
                                    8, 'proxd', 1, 8.7, 500, 0.1, 0, 0, 10,
                                    0.8, 2.5*10**(-2))

        # GC -> HC
        # Divergence x4; Weight doubled; Connected randomly.
        gennetwork.tmgsynConnection(self.populations[0], self.populations[3],
                                    24, 'proxd', 1, 8.7, 500, 0.1, 0, 0, 10,
                                    1.5, 2.5*10**(-2))

        # MC -> MC
        gennetwork.tmgsynConnection(self.populations[1], self. populations[1],
                                    24, 'proxd', 3, 2.2, 0, 1, 0, 0, 10,
                                    2, 0.5*10**(-3))

        # MC -> BC
        gennetwork.tmgsynConnection(self.populations[1], self.populations[2],
                                    12, 'proxd', 1, 2, 0, 1, 0, 0, 10,
                                    3, 0.3*10**(-3))

        # MC -> HC
        gennetwork.tmgsynConnection(self.populations[1], self.populations[3],
                                    20, 'midd', 2, 6.2, 0, 1, 0, 0, 10,
                                    3, 0.2*10**(-3))

        # BC -> GC
        # # synapses x3; Weight *1/4; tau from 5.5 to 20 (Hefft & Jonas, 2005)
        gennetwork.tmgsynConnection(self.populations[2], self.populations[0],
                                    560, 'soma', 400, 20, 0, 1, 0, -70, 10,
                                    0.85, 1.2*10**(-3))

        # We reseed here to make sure that those connections are consistent
        # between this and net_global which has a global target pool for
        # BC->GC.
        if seed:
            self.set_numpy_seed(seed+1)

        # BC -> MC
        gennetwork.tmgsynConnection(self.populations[2], self.populations[1],
                                    28, 'proxd', 3, 3.3, 0, 1, 0, -70, 10,
                                    1.5, 1.5*10**(-3))

        # BC -> BC
        gennetwork.tmgsynConnection(self.populations[2], self.populations[2],
                                    12, 'proxd', 2, 1.8, 0, 1, 0, -70, 10,
                                    0.8, 7.6*10**(-3))

        # HC -> GC
        # Weight x10; Nr synapses x4; tau from 6 to 20 (Hefft & Jonas, 2005)
        gennetwork.tmgsynConnection(self.populations[3], self.populations[0],
                                    2000, 'dd', 640, 20, 0, 1, 0, -70, 10,
                                    3.8, 0.6*10**(-2))

        # HC -> MC
        gennetwork.tmgsynConnection(self.populations[3], self.populations[1],
                                    60, ['mid1d', 'mid2d'], 4, 6, 0, 1, 0, -70,
                                    10, 1, 1.5*10**(-3))

        # HC -> BC
        gennetwork.tmgsynConnection(self.populations[3], self.populations[2],
                                    24, 'ddend', 4, 5.8, 0, 1, 0, -70, 10,
                                    1.6, 0.5*10**(-3))
