
# Copyright 2018 Universidad Complutense de Madrid
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

from __future__ import division
from __future__ import print_function

import argparse
from astropy.io import fits
from datetime import datetime
import logging
import numpy as np
import sys
import time

from numina.array.wavecalib.resample import resample_image2d_flux
from numina.tools.arg_file_is_new import arg_file_is_new

from emirdrp.instrument.dtu_configuration import DtuConfiguration
from emirdrp.products import RectWaveCoeff
from emirdrp.tools.nscan_minmax_frontiers import nscan_minmax_frontiers

from .islitlet_progress import islitlet_progress
from .set_wv_parameters import set_wv_parameters
from .slitlet2d import Slitlet2D

from numina.array.display.pause_debugplot import DEBUGPLOT_CODES
from emirdrp.core import EMIR_NAXIS2
from emirdrp.core import EMIR_NBARS

def apply_rectwv_coeff(reduced_image,
                       rectwv_coeff,
                       args_resampling=2,
                       args_ignore_dtu_configuration=True,
                       debugplot=0):
    """Compute rectification and wavelength calibration coefficients.

        Parameters
        ----------
        reduced_image : HDUList object
            Image with preliminary basic reduction: bpm, bias, dark and
            flatfield.
        rectwv_coeff : RectWaveCoeff instance
            Rectification and wavelength calibration coefficients for the
            particular CSU configuration.
        args_resampling : int
            1: nearest neighbour, 2: flux preserving interpolation.
        args_ignore_dtu_configuration : bool
            If True, ignore differences in DTU configuration.
        debugplot : int
            Debugging level for messages and plots. For details see
            'numina.array.display.pause_debugplot.py'.

        Returns
        -------
        rectwv_image : HDUList object
            Rectified and wavelength calibrated image.

        """

    logger = logging.getLogger(__name__)

    # header and data array
    header = reduced_image[0].header
    image2d = reduced_image[0].data

    # check grism and filter
    filter_name = header['filter']
    logger.debug('Filter: ' + filter_name)
    if filter_name != rectwv_coeff.tags['filter']:
        raise ValueError('Filter name does not match!')
    grism_name = header['grism']
    logger.debug('Grism: ' + grism_name)
    if grism_name != rectwv_coeff.tags['grism']:
        raise ValueError('Grism name does not match!')

    # read the DTU configuration from the image header
    dtu_conf = DtuConfiguration.define_from_header(header)
    logger.debug(dtu_conf)

    # retrieve DTU configuration from RectWaveCoeff object
    dtu_conf_calib = DtuConfiguration.define_from_dictionary(
        rectwv_coeff.meta_info['dtu_configuration']
    )
    # check that the DTU configuration employed to obtain the calibration
    # corresponds to the DTU configuration in the input FITS file
    if dtu_conf != dtu_conf_calib:
        logger.info('DTU configuration from image header:')
        logger.info(dtu_conf)
        logger.info('DTU configuration from master calibration:')
        logger.info(dtu_conf_calib)
        if args_ignore_dtu_configuration:
            logger.warning('DTU configuration differences found!')
        else:
            raise ValueError("DTU configurations do not match!")
    else:
        logger.info('DTU configuration match!')

    # valid slitlet numbers
    list_valid_islitlets = list(range(1, EMIR_NBARS + 1))
    for idel in rectwv_coeff.missing_slitlets:
        list_valid_islitlets.remove(idel)
    logger.debug('Valid slitlet numbers:\n' + str(list_valid_islitlets))

    # ---

    # relevant wavelength calibration parameters for rectified and wavelength
    # calibrated image
    wv_parameters = set_wv_parameters(filter_name, grism_name)
    crpix1_enlarged = wv_parameters['crpix1_enlarged']
    crval1_enlarged = wv_parameters['crval1_enlarged']
    cdelt1_enlarged = wv_parameters['cdelt1_enlarged']
    naxis1_enlarged = wv_parameters['naxis1_enlarged']

    # initialize rectified and wavelength calibrated image
    image2d_rectwv = np.zeros((EMIR_NAXIS2, naxis1_enlarged))

    # main loop
    logger.info('Computing rectification and wavelength calibration')
    for islitlet in list_valid_islitlets:
        if abs(debugplot) >= 10:
            if islitlet == list_valid_islitlets[0]:
                print(time.ctime())
            islitlet_progress(islitlet, EMIR_NBARS)
            if islitlet == list_valid_islitlets[-1]:
                print(' ')
                print(time.ctime())

        # define Slitlet2D object
        slt = Slitlet2D(islitlet=islitlet,
                        rectwv_coeff=rectwv_coeff,
                        debugplot=debugplot)

        # extract (distorted) slitlet from the initial image
        slitlet2d = slt.extract_slitlet2d(image2d)

        # rectify slitlet
        slitlet2d_rect = slt.rectify(slitlet2d, resampling=args_resampling)

        # wavelength calibration of the rectifed slitlet
        slitlet2d_rect_wv = resample_image2d_flux(
            image2d_orig=slitlet2d_rect,
            naxis1=naxis1_enlarged,
            cdelt1=cdelt1_enlarged,
            crval1=crval1_enlarged,
            crpix1=crpix1_enlarged,
            coeff=slt.wpoly
        )

        # minimum and maximum useful scan (pixel in the spatial direction)
        # for the rectified slitlet
        nscan_min, nscan_max = nscan_minmax_frontiers(
            slt.y0_frontier_lower,
            slt.y0_frontier_upper,
            resize=False
        )
        ii1 = nscan_min - slt.bb_ns1_orig
        ii2 = nscan_max - slt.bb_ns1_orig + 1
        i1 = slt.bb_ns1_orig - 1 + ii1
        i2 = i1 + ii2 - ii1
        image2d_rectwv[i1:i2, :] = slitlet2d_rect_wv[ii1:ii2, :]

        # include scan range in FITS header
        header['sltmin' + str(islitlet).zfill(2)] = i1
        header['sltmax' + str(islitlet).zfill(2)] = i2 - 1

    # modify upper limit of previous slitlet in case of overlapping:
    # note that the overlapped scans have been overwritten with the
    # information from the current slitlet!
    for islitlet in list_valid_islitlets:
        cprevious = 'SLTMAX' + str(islitlet - 1).zfill(2)
        if cprevious in header.keys():
            sltmax_previous = header[cprevious]
            cslitlet = 'SLTMIN' + str(islitlet).zfill(2)
            sltmin_current = header[cslitlet]
            if sltmax_previous >= sltmin_current:
                print('WARNING: ' + cslitlet + '=' +
                      str(sltmin_current).zfill(4) +
                      ' overlaps with ' + cprevious + '=' +
                      str(sltmax_previous).zfill(4) + ' ==> ' + cslitlet +
                      ' set to ' + str(sltmin_current - 1).zfill(4))
                header[cprevious] = sltmin_current - 1

    logger.info('Updating image header')
    # update wavelength calibration in FITS header
    header.remove('crval1')
    header.remove('crpix1')
    header.remove('crval2')
    header.remove('crpix2')
    header['crpix1'] = (crpix1_enlarged, 'reference pixel')
    header['crval1'] = (crval1_enlarged, 'central wavelength at crpix1')
    header['cdelt1'] = (cdelt1_enlarged, 'linear dispersion (Angstrom/pixel)')
    header['cunit1'] = ('Angstrom', 'units along axis1')
    header['ctype1'] = 'WAVELENGTH'
    header['crpix2'] = (0.0, 'reference pixel')
    header['crval2'] = (0.0, 'central value at crpix2')
    header['cdelt2'] = (1.0, 'increment')
    header['ctype2'] = 'PIXEL'
    header['cunit2'] = ('Pixel', 'units along axis2')
    header.remove('cd1_1')
    header.remove('cd1_2')
    header.remove('cd2_1')
    header.remove('cd2_2')
    header.remove('PCD1_1')
    header.remove('PCD1_2')
    header.remove('PCD2_1')
    header.remove('PCD2_2')
    header.remove('PCRPIX1')
    header.remove('PCRPIX2')
    header['history'] = 'Boundary parameters uuid:' + \
                        rectwv_coeff.meta_info['origin']['bound_param'][4:]
    if 'master_rectwv' in rectwv_coeff.meta_info['origin']:
        header['history'] = \
            'MasterRectWave uuid:' + \
            rectwv_coeff.meta_info['origin']['master_rectwv'][4:]
    header['history'] = 'RectWaveCoeff uuid:' + rectwv_coeff.uuid
    header['history'] = 'Rectification and wavelength calibration time ' \
                        + datetime.now().isoformat()

    logger.info('Generating rectified and wavelength calibrated image')

    rectwv_image = fits.PrimaryHDU(data=image2d_rectwv, header=header)

    return rectwv_image


def main(args=None):
    # parse command-line options
    parser = argparse.ArgumentParser(
        description='description: apply rectification and wavelength '
                    'calibration polynomials for the CSU configuration of a '
                    'particular image'
    )

    # required arguments
    parser.add_argument("fitsfile",
                        help="Input FITS file",
                        type=argparse.FileType('rb'))
    parser.add_argument("--rectwv_coeff", required=True,
                        help="Input JSON file with rectification and "
                             "wavelength calibration coefficients",
                        type=argparse.FileType('rt'))
    parser.add_argument("--outfile", required=True,
                        help="Output FITS file with rectified and "
                             "wavelength calibrated image",
                        type=lambda x: arg_file_is_new(parser, x, mode='wb'))

    # optional arguments
    parser.add_argument("--resampling",
                        help="Resampling method: 1 -> nearest neighbor, "
                             "2 -> linear interpolation (default)",
                        default=2, type=int,
                        choices=(1, 2))
    parser.add_argument("--ignore_dtu_configuration",
                        help="Ignore DTU configurations differences between "
                             "transformation and input image",
                        action="store_true")
    parser.add_argument("--debugplot",
                        help="Integer indicating plotting & debugging options"
                             " (default=0)",
                        default=0, type=int,
                        choices=DEBUGPLOT_CODES)
    parser.add_argument("--echo",
                        help="Display full command line",
                        action="store_true")
    args = parser.parse_args(args)

    if args.echo:
        print('\033[1m\033[31m% ' + ' '.join(sys.argv) + '\033[0m\n')

    # generate RectWaveCoeff object
    rectwv_coeff = RectWaveCoeff._datatype_load(
        args.rectwv_coeff.name)

    # generate HDUList object
    # read FITS image and its corresponding header
    hdulist = fits.open(args.fitsfile)

    # rectification and wavelength calibration
    reduced_arc = apply_rectwv_coeff(
        hdulist,
        rectwv_coeff,
        args_resampling=args.resampling,
        args_ignore_dtu_configuration=args.ignore_dtu_configuration,
        debugplot=args.debugplot
    )

    # save result
    reduced_arc.writeto(args.outfile, overwrite=True)


if __name__ == "__main__":
    main()