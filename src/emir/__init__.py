#
# Copyright 2008-2012 Universidad Complutense de Madrid
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

'''The EMIR Data Reduction Pipeline'''

import logging

from .simulator import EmirImageFactory as ImageFactory
from emir.simulator import Instrument

__all__ = ['Instrument', 'ImageFactory']

__version__ = '0.6.7'


# Top level NullHandler
logging.getLogger("emir").addHandler(logging.NullHandler())

