#
# Copyright 2008-2009 Sergio Pascual
# 
# This file is part of PyEmir
# 
# PyEmir is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyEmir is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PyEmir.  If not, see <http://www.gnu.org/licenses/>.
# 

# $Id$

'''Recipe for image simulation'''


import logging

import numpy

from numina.recipes import RecipeBase
from numina.simulation import RunCounter
from numina.simulation.storage import FITSCreator
from emir.instrument.detector import EmirDetector
from emir.simulation.headers import default_fits_headers

from darkimaging import Result

__version__ = "$Revision$"

_logger = logging.getLogger("emir.recipes")

class Recipe(RecipeBase):
    '''Recipe to simulate EMIR images.
    
    Here starts the long description...
    It continues several lines'''
    def __init__(self):
        optusage = "usage: %prog [options] recipe [recipe-options]"
        super(Recipe, self).__init__(optusage=optusage)
        
        # Default values. This can be read from a file
        self.iniconfig.add_section('readout')
        self.iniconfig.set('readout', 'mode', 'cds')
        self.iniconfig.set('readout', 'reads', '3')
        self.iniconfig.set('readout', 'repeat', '1')
        self.iniconfig.set('readout', 'scheme', 'perline')
        self.iniconfig.set('readout', 'exposure', '0')
        self.iniconfig.add_section('detector')
        self.iniconfig.set('detector', 'shape', '(2048,2048)')
        self.iniconfig.set('detector', 'ron',' 2.16')
        self.iniconfig.set('detector', 'dark', '0.37')
        self.iniconfig.set('detector', 'gain', '3.028')
        self.iniconfig.set('detector', 'flat', '1')
        self.iniconfig.set('detector', 'well', '65536')
        #
        self.detector = None
        self.input = None
        self.creator = None
        self.runcounter = None
        
    def setup(self):
        detector_conf = {}
        detector_conf['shape'] = eval(self.iniconfig.get('detector', 'shape'))
        for i in ['ron', 'dark', 'gain', 'flat', 'well']:
            detector_conf[i] = self.iniconfig.getfloat('detector', i)

        self.detector = EmirDetector(**detector_conf)
        _logger.info('Created detector')
    
        readout_opt = {}
                
        for i in ['exposure']:
            readout_opt[i] = self.iniconfig.getfloat('readout', i)
        for i in ['reads', 'repeat']:
            readout_opt[i] = self.iniconfig.getint('readout', i)
        for i in ['mode', 'scheme']:
            readout_opt[i] = self.iniconfig.get('readout', i)
        
        self._repeat = readout_opt['repeat']
        
        _logger.info('Detector configured')
        self.detector.configure(readout_opt)
        
        self.input = numpy.zeros(detector_conf['shape'])
        self.detector.exposure(readout_opt['exposure'])
        
        _logger.info('FITS builder created')
        self.creator = FITSCreator(default_fits_headers)
        _logger.info('Run counter created')
        self.runcounter = RunCounter("r%05d")
        
        
    def _process(self):
        _logger.info('Creating simulated array')    
        output = self.detector.lpath(self.input)
        run, cfile = self.runcounter.runstring()
        headers = {'RUN': run}
        
        _logger.info('Collecting detector metadata')
        headers.update(self.detector.metadata())
        
        _logger.info('Building FITS structure')
        hdulist = self.creator.create(output, headers)
        return Result(hdulist, cfile)
        


