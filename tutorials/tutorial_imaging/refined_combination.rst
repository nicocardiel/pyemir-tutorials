===============================
Improving the image combination
===============================

The image combination can be improved by tuning some of the parameters of the
recipe ``FULL_DITHERED_IMAGE`` (step 2 in the previous section).
In this sense, there is no need to repeat the basic reduction of the individual
exposures (step 1).

As previously mentioned, three are the problems that we want to solve:

1. **Improve the offsets between individual exposures:** this can be achieved
   in several ways:

   - By setting the requirement ``refine_offsets: True``: in this case a
     cross-correlation between subimage regions around bright targets is
     carried out to derive refined offsets. See subsection
     :ref:`improving_offsets_1` below.

   - By providing an ASCII file with a list of offsets measured independently 
     by the user and indicated with the requirement ``offsets:
     user_offsets.txt``. See subsection :ref:`improving_offsets_2` below.

   - By providing the same ASCII file with precomputed offsets (as in the
     previous item) and using, in addition, the cross-correlation method. In
     this case, both requirements ``refine_offsets: True`` and ``offsets:
     user_offsets.txt`` must be set. See subsection :ref:`improving_offsets_3`
     below.

2. **Improve the sky background level estimation:** the background level can be
   improved by:

   - Generating an object mask and iterating the combination process. See
     subsection :ref:`improving_skybackground_1` below.

   - Introducing an *ad hoc* fit to a low-order polynomial surface to the sky
     background. See subsection :ref:`improving_skybackground_2` below.

3. **Take into account the doughnut-like shape that appears in the
   superflatfield:** this can be done by fitting the doughnut-like shape by a
   smooth surface (using a smoothing kernel in polar coordinates that helps to
   fit the azimuthal shape). See subsection :ref:`improving_doughnut` below.

.. _improving_offsets_1:

Improving offsets (method #1)
-----------------------------

We can activate the use of 2D cross-correlation of subimages around bright
targets to obtain refined offsets. This method works only if the initial
offsets (either derived from the WCS information in the image headers or from
an external file provided by the user) are a reasonable approximation to the
refined values. To activate this option it it necessary to set the requirement
``refine_offsets: True`` in the observation result file.

This option is already set in line number 148 of the file ``dithered_v1.yaml``,
available in the downloaded package for this tutorial (note that the ``id`` in
line 127 has also been changed in order to avoid overwriting the ``work`` and
``results`` subdirectories from the execution of ``dithered_v0.yaml``).

.. literalinclude:: dithered_v1.yaml
   :lines: 127-149
   :emphasize-lines: 1, 22
   :linenos:
   :lineno-start: 127

The refined version of the combined image is then obtained by executing numina
again with this new observation result file:

.. code-block:: console

   (emir) $ numina run dithered_v1.yaml --link-files -r control.yaml

.. generada con --geometry 0,0,850,1200
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v1.png -trim combined_v1_trimmed.png
.. convert -delay 100 -loop 0 combined_v[01]_trimmed.png comparison_v1.gif

.. only:: html

   .. image:: comparison_v1.gif
      :width: 100%
      :alt: combined image, version 1 compared with version 0

.. only:: latex

   |pic_combined_v0_trimmed| |pic_combined_v1_trimmed|

   .. |pic_combined_v0_trimmed| image:: combined_v0_trimmed.png
      :width: 48%

   .. |pic_combined_v1_trimmed| image:: combined_v1_trimmed.png
      :width: 48%

.. generada con --geometry 0,0,850,1200 --bbox 1100,1600,800,1300
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v1_zoom.png -trim combined_v1_zoom_trimmed.png
.. convert -delay 100 -loop 0 combined_v[01]_zoom_trimmed.png comparison_v1_zoom.gif

.. only:: html

   .. image:: comparison_v1_zoom.gif
      :width: 100%
      :alt: combined image, version 1 compared with version 0

.. only:: latex

   |pic_combined_v0_zoom_trimmed| |pic_combined_v1_zoom_trimmed|

   .. |pic_combined_v0_zoom_trimmed| image:: combined_v0_zoom_trimmed.png
      :width: 48%

   .. |pic_combined_v1_zoom_trimmed| image:: combined_v1_zoom_trimmed.png
      :width: 48%

.. _improving_offsets_2:

Improving offsets (method #2)
-----------------------------

An alternative to the use of the offsets computed from the WCS information in
the image header is to provide a two-column ASCII file with the measured (X,Y)
coordinates of a reference object (i.e., the centroid of a bright star) in
every individual image. These values are employed to determine the relative
offsets between the individual exposures. The (arbitray) name of that file must
be provided through the requirement ``offsets:``. For this tutoral, we are
providing such a file with the name ``user_offsets.txt``. Note that this file
must be placed within the ``data`` subdirectory.

The observation result file ``dithered_v2.yaml`` is similar to the initial
``dithered_v0.yaml`` file, with the inclusion of the new requirement (line
number 148; note also the ``id`` change in line 127):

.. literalinclude:: dithered_v2.yaml
   :lines: 127-150
   :emphasize-lines: 1, 22
   :linenos:
   :lineno-start: 127

The contents of the ASCII file with the measured offsets is the following:

.. code-block:: console

   (emir) $ cat data/user_offsets.txt
   822 907
   730 660
   555 863
   620 998
   895 741
   545 674
   708 811
   830 911
   735 666
   561 868
   626 1003
   901 746
   551 679
   715 816

Execute numina to obtain the new version of the combined image:

.. code-block:: console

   (emir) $ numina run dithered_v2.yaml --link-files -r control.yaml

.. generada con --geometry 0,0,850,1200
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v2.png -trim combined_v2_trimmed.png
.. convert -delay 100 -loop 0 combined_v[02]_trimmed.png comparison_v2.gif

.. only:: html

   .. image:: comparison_v2.gif
      :width: 100%
      :alt: combined image, version 2 compared with version 0

.. only:: latex

   |pic_combined_v0_trimmed| |pic_combined_v2_trimmed|

   .. |pic_combined_v2_trimmed| image:: combined_v2_trimmed.png
      :width: 48%

.. generada con --geometry 0,0,850,1200 --bbox 1100,1600,800,1300
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v2_zoom.png -trim combined_v2_zoom_trimmed.png
.. convert -delay 100 -loop 0 combined_v[02]_zoom_trimmed.png comparison_v2_zoom.gif

.. only:: html

   .. image:: comparison_v2_zoom.gif
      :width: 100%
      :alt: combined image, version 2 compared with version 0

.. only:: latex

   |pic_combined_v0_zoom_trimmed| |pic_combined_v2_zoom_trimmed|

   .. |pic_combined_v2_zoom_trimmed| image:: combined_v2_zoom_trimmed.png
      :width: 48%



.. _improving_offsets_3:

Improving offsets (method #3)
-----------------------------

It is also possible to combine both the offsets provided by the user through an
external ASCII file, as well as the cross-correlation method to improve those
numbers.

The last lines of the new observation result file ``dithered_v3.yaml``, which
differs only in two lines with ``dithered_v2.yaml``, are the
following:

.. literalinclude:: dithered_v3.yaml
   :lines: 127-150
   :emphasize-lines: 1,23
   :linenos:
   :lineno-start: 127

In this case we have modified the ``id`` (line 127) and set
``refine_offsets: True`` (line 149).

Execute numina again with this new observation result file:

.. code-block:: console

   (emir) $ numina run dithered_v3.yaml --link-files -r control.yaml

The comparison with the result obtained by refining the offsets initially
computed from the WCS information indicates that both methods lead to basically
the same result.

.. generada con --geometry 0,0,850,1200
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v3.png -trim combined_v3_trimmed.png
.. convert -delay 100 -loop 0 combined_v[13]_trimmed.png comparison_v3.gif


.. only:: html

   .. image:: comparison_v3.gif
      :width: 100%
      :alt: combined image, version 3 compared with version 1

.. only:: latex

   |pic_combined_v1_trimmed| |pic_combined_v3_trimmed|

   .. |pic_combined_v3_trimmed| image:: combined_v3_trimmed.png
      :width: 48%

.. generada con --geometry 0,0,850,1200 --bbox 1100,1600,800,1300
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v3_zoom.png -trim combined_v3_zoom_trimmed.png
.. convert -delay 100 -loop 0 combined_v[13]_zoom_trimmed.png comparison_v3_zoom.gif

.. only:: html

   .. image:: comparison_v3_zoom.gif
      :width: 100%
      :alt: combined image, version 3 compared with version 1

.. only:: latex

   |pic_combined_v1_zoom_trimmed| |pic_combined_v3_zoom_trimmed|

   .. |pic_combined_v3_zoom_trimmed| image:: combined_v3_zoom_trimmed.png
      :width: 48%

.. note::

   The conclusion of these comparisons is that the user can rely on the offsets
   computed from the WCS information in the image headers as a
   reasonable initial guess, but that these offsets need to be refined. Unless
   something is really wrong with that WCS information, the user probabily will
   not need to measure the offsets manually. Anyway, this last option is always
   there just in case it is necessary.

.. _improving_skybackground_1:

Improving the sky background (problem #1)
-----------------------------------------

The first obvious way to improve the background computation is by masking the
objects present in the image. This masking process requires an initial object
detection, that must be carried out on the result of an initial image
combination.  For that reason, this masking requires to set ``iterations`` to a
number larger than zero. 

In addition, the user can indicate that the sky signal at each pixel must be
computed from the signal at the same pixel in a predefined number of images
(close in observing time).

The observation result file ``dithered_v4.yaml`` (which is the same as
``dithered_v1.yaml`` except for three modified lines) includes both options:

.. literalinclude:: dithered_v4.yaml
   :lines: 127-149
   :emphasize-lines: 1,20-21
   :linenos:
   :lineno-start: 127

In this example we are using:

  - ``iterations: 1``: after a first combination (that can be considered as
    iteration number zero) one iteration is performed (number 1), which
    allows the code to detect the objects in the image and make use of a mask
    of objects in order to compute a better sky background.

  - ``sky_images: 6``: this number (which must be even) indicates de total
    number of images employed to determine the sky background. In most cases
    this means that the code will make use of 3 images obtained before and 3
    images obtained after the one for which the sky background is being
    computed. Obviously, when considering the first (or the last) image in the
    sequence, no previous (or after) images are available: in these cases the 6
    images correspond to exposures obtained after (or before) the one
    considered. Since in our example we are using a sequence of exposures in 
    which a pattern of 7 dithered exposures was followed, only 6 images after
    (or before) any particular exposure correspond to different telescope
    pointings. That is the reason for choosing ``sky_images: 6`` (it is the
    maximum number of exposures before repeating the same dithering pointing).

Note that ``refine_offsets: True`` is also being used, but without setting
``offsets`` with an external ASCII file (i.e., the initial offsets will be
computed from the WCS information in the image headers).

Execute numina to start the reduction including object masking:

.. code-block:: console

   (emir) $ numina run dithered_v4.yaml --link-files -r control.yaml

It is useful to subtract the new result from the one derived previously:

.. code-block:: console

   (emir) $ numina-imath obsid_combined_v1_results/reduced_image.fits - \
      obsid_combined_v4_results/reduced_image.fits difference_v4.fits

.. generada con --geometry 0,0,850,1200
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v4.png -trim combined_v4_trimmed.png
.. convert difference_v4.png -trim difference_v4_trimmed.png
.. convert -delay 100 -loop 0 combined_v[14]_trimmed.png difference_v4_trimmed.png comparison_v4.gif

.. only:: html

   .. image:: comparison_v4.gif
      :width: 100%
      :alt: combined image, version 4 compared with version 1

.. only:: latex

   |pic_combined_v1_trimmed| |pic_combined_v4_trimmed|

   .. |pic_combined_v4_trimmed| image:: combined_v4_trimmed.png
      :width: 48%

   .. image:: difference_v4_trimmed.png
      :width: 48%
      :align: center

.. generada con --geometry 0,0,850,1200 --bbox 1100,1600,800,1300
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v4_zoom.png -trim combined_v4_zoom_trimmed.png
.. convert difference_v4_zoom.png -trim difference_v4_zoom_trimmed.png
.. convert -delay 100 -loop 0 combined_v[14]_zoom_trimmed.png difference_v4_zoom_trimmed.png comparison_v4_zoom.gif

.. only:: html

   .. image:: comparison_v4_zoom.gif
      :width: 100%
      :alt: combined image, version 4 compared with version 1

.. only:: latex

   |pic_combined_v1_zoom_trimmed| |pic_combined_v4_zoom_trimmed|

   .. |pic_combined_v4_zoom_trimmed| image:: combined_v4_zoom_trimmed.png
      :width: 48%

   .. image:: difference_v4_zoom_trimmed.png
      :width: 48%
      :align: center


.. _improving_skybackground_2:

Improving the sky background (problem #2, old EMIR detector)
------------------------------------------------------------

.. warning::

   This section explains how to improve the sky background in observations
   obtained with the original EMIR detector. The analogous explanation for the
   correction of images obtained with the latest H2RG detector can be found in
   Section :ref:`improving_skybackground_2_h2rg`.

In all the previous examples, the combined images always exhibit variations in
the sky background that are clearly visible at the image borders. The reason
for that is that some individual exposures (in this particular example the
first two individual images), have a wrong image background. 

The problem is more severe in the regions where the number of images used for
the combination is lower:

.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v4_npix.png -trim combined_v4_npix_trimmed.png
.. convert +smush 40 combined_v4_trimmed.png combined_v4_npix_trimmed.png data_npix_v4.png

.. image:: data_npix_v4.png
   :width: 100%
   :alt: combined data and number of pixels used in combination, version 4

.. See Jupyter notebook in
.. /Users/cardiel/w/GTC/emir/work/z_tutorials_201907/examine_combined_image.ipynb
.. (note that we have to execute dithered_v5.yaml first)
.. This notebook generates: statistics_v4.pdf and statistics_v5.pdf
.. convert statistics_v4.pdf -trim combined_v4_statistics.png
.. convert statistics_v5.pdf -trim combined_v5_statistics.png

.. only:: html

   .. image:: combined_v4_statistics.png
      :width: 100%
      :alt: combined data version 4, statistical analysis
   
.. only:: latex

   .. image:: combined_v4_statistics.png
      :width: 82%
      :alt: combined data version 4, statistical analysis
   
It is also possible to examine the sky-subtracted individual images (files
ending in ``_rfs_i?.fits`` within the ``work`` subdirectories):

.. cd obsid_combined_v4_work
.. numina-ximshow reduced_image_*_rfs_i1.fits --z1z2 [-200,300] --pdf skysub_v4.pdf --figuredict "{'figsize':(8, 10), 'dpi':100}"
.. convert -delay 50 -loop 0 skysub_v4.pdf skysub_v4.gif
.. convert skysub_v4.gif skysub_v4-%d.png

.. only:: html

   .. image:: skysub_v4.gif
      :width: 100%
      :alt: individual sky-subtracted images

.. only:: latex

   |pic_v4_0| |pic_v4_1| |pic_v4_2|
   |pic_v4_3| |pic_v4_4| |pic_v4_5|
   |pic_v4_6| |pic_v4_7| |pic_v4_8|
   |pic_v4_9| |pic_v4_10| |pic_v4_11|
   |pic_v4_12| |pic_v4_13|

   .. |pic_v4_0| image:: skysub_v4-0.png
      :width: 24%

   .. |pic_v4_1| image:: skysub_v4-1.png
      :width: 24%

   .. |pic_v4_2| image:: skysub_v4-2.png
      :width: 24%

   .. |pic_v4_3| image:: skysub_v4-3.png
      :width: 24%

   .. |pic_v4_4| image:: skysub_v4-4.png
      :width: 24%

   .. |pic_v4_5| image:: skysub_v4-5.png
      :width: 24%

   .. |pic_v4_6| image:: skysub_v4-6.png
      :width: 24%

   .. |pic_v4_7| image:: skysub_v4-7.png
      :width: 24%

   .. |pic_v4_8| image:: skysub_v4-8.png
      :width: 24%

   .. |pic_v4_9| image:: skysub_v4-9.png
      :width: 24%

   .. |pic_v4_10| image:: skysub_v4-10.png
      :width: 24%

   .. |pic_v4_11| image:: skysub_v4-11.png
      :width: 24%

   .. |pic_v4_12| image:: skysub_v4-12.png
      :width: 24%

   .. |pic_v4_13| image:: skysub_v4-13.png
      :width: 24%

In this case we realize that the first two images exhibit an unexpected
non-flat background (in the previous movie the first two images correspond to
``reduced_image_d58cea92-0cd9-11ed-9e29-3c15c2e3dc50_rfs_i1.fits`` and
``reduced_image_e45d0c32-0cd9-11ed-9e29-3c15c2e3dc50_rfs_i1.fits``; this can be
easily recognized by having a look to the output of the reduction procedure in
the terminal, or by examining the file
``obsid_combined_v4_results/processing.log``).

One possibility is to remove the first two images from the list of images to be 
reduced. This is undesirable because it obviously reduces the depth of the
combined image.

Another option is to apply an *ad hoc* correction, by fitting for example a
low-order 2D polynomial surface to the masked (i.e. removing objects)
sky-subtracted images. This option can be activated by using the requirement
``nside_adhoc_sky_correction``. We have incorporated that option in the
observation result file ``dithered_v5.yaml``, which also includes an iteration
to generate an object mask (as we did in ``dithered_v4.yaml``):

.. literalinclude:: dithered_v5.yaml
   :lines: 127-150
   :emphasize-lines: 1,23
   :linenos:
   :lineno-start: 127

Since the problem with the sky background is different for each quadrant of the
EMIR detector, the value of ``nside_adhoc_sky_correction`` indicates the number
of subdivisions (in X and Y) in which each quadrant is subdivided. In this case
we are using a pattern of 10 x 10 regions in each quadrant. The median value in
each of these 100 subregions is computed (masking pixels affected by objects)
and a smooth spline surface is fitted to that collection of points.

.. code-block:: console

   (emir) $ numina run dithered_v5.yaml --link-files -r control.yaml

.. generada con --geometry 0,0,850,1200
.. convert combined_v5.png -trim combined_v5_trimmed.png
.. convert -delay 50 -loop 0 combined_v[45]_trimmed.png comparison_v5.gif

.. only:: html

   .. image:: comparison_v5.gif
      :width: 100%
      :alt: combined image, version 5 compared with version 4

.. only:: latex

   |pic_combined_v4_trimmed| |pic_combined_v5_trimmed|

   .. |pic_combined_v5_trimmed| image:: combined_v5_trimmed.png
      :width: 48%

.. only:: html

   .. image:: combined_v5_statistics.png
      :width: 100%
      :alt: combined data version 5, statistical analysis

.. only:: latex

   .. image:: combined_v5_statistics.png
      :width: 82%
      :alt: combined data version 5, statistical analysis

In the last combination (v5) the sky background level is much flatter around
zero, except for those pixels in the combined image where only one single
exposure is available. By looking at the file ``result_i1_npix.fits`` it is
possible to check that those pixels are just at the borders of the combined
image.

.. _improving_skybackground_2_h2rg:

Improving the sky background (problem #2, new EMIR detector H2RG)
-----------------------------------------------------------------

.. warning::

   This section explains how to improve the sky background in observations
   obtained with the new EMIR detector H2RG. The analogous explanation for the
   correction of images obtained with original detector can be found in
   Section :ref:`improving_skybackground_2`.

Exposures taken with the new H2RG detector may show signal variations among the
32 channels of the detector (which are arrange vertically), as illustrated in
the following figure (we thank Alan Watson and Yuhan Yang for providing the
example data for the following screenshots):

.. cd w/GTC/emir/20241016_test_modo_imagen_H2RG
.. numina-ximshow obsid_combined_v4_results/reduced_image.fits --z1z2 "[-40,40]" --pdf skysub_v4_h2rg.pdf --figuredict "{'figsize':(8, 10), 'dpi':100}"
.. convert -density 100 skysub_v4_h2rg.pdf -trim skysub_v4_h2rg.png

.. only:: html

   .. image:: skysub_v4_h2rg.png
      :width: 100%
      :alt: combined data version 4, detector H2RG
   
.. only:: latex

   .. image:: skysub_v4_h2rg.png
      :width: 82%
      :alt: combined data version 4, detector H2RG

It is possible to correct this problem by determining and subtracting the
median value in the background signal in each of the channels. For that
purpose, you should include the requirement ``adhoc_sky_correction_h2rg: True``
(note that the requirement ``nside_adhoc_sky_correction: 10`` used with the
original EMIR detector is not valid for the H2RG detector, since the geometry
of the channels is different!).

.. literalinclude:: dithered_v5_h2rg.yaml
   :lines: 155-178
   :emphasize-lines: 1,23
   :linenos:
   :lineno-start: 155

.. numina-ximshow obsid_combined_v5_h2rg_results/reduced_image.fits --z1z2 "[-40,40]" --pdf skysub_v5_h2rg.pdf --figuredict "{'figsize':(8, 10), 'dpi':100}"
.. convert -density 100 skysub_v5_h2rg.pdf -trim skysub_v5_h2rg.png

.. only:: html

   .. image:: skysub_v5_h2rg.png
      :width: 100%
      :alt: combined data version 5, detector H2RG
   
.. only:: latex

   .. image:: skysub_v5_h2rg.png
      :width: 82%
      :alt: combined data version 5, detector H2RG

.. _improving_doughnut:

Improving the superflatfield
----------------------------

Here we are modifying the last observation result file (``dithered_v5.yaml``)
to generate ``dithered_v6.yaml``. The only change that we need to introduce
here is to set the requirement ``fit_doughnut: True`` (line 149; note also the
change in the ``id`` in line 127):

.. literalinclude:: dithered_v6.yaml
   :lines: 127-151
   :emphasize-lines: 1,23
   :linenos:
   :lineno-start: 127

**Note that this parameter** ``fit_doughnut`` **is assumed to be** ``False``
**by default, which means that the correction described next is not performed
unless splicitly stated.**

.. code-block:: console

   (emir) $ numina run dithered_v6.yaml --link-files -r control.yaml

The refined version of the superflatfield is then obtained by fitting a smooth
surface (preserving some azimuthal symmetry) which is applied to the initial
superflatfield (dividing by the fitted doughnut-like shape), which provides a
quite flat new superflatfield. 

In this example, the initial superflatfield computed in iteration 1 (masking
objects) is the following:

.. numina-ximshow obsid_combined_v6_work/superflat_comb_i1.fits --geometry 0,0,567,800 --z1z2 [0.80,1.20]
.. convert image.png -trim image_trimmed.png

.. image:: superflat_comb_i1_v6_trimmed.png
   :width: 100%
   :alt: initial superflatfield, version 6

The fitted doughnut-like model, displayed using the same cuts is:

.. numina-ximshow obsid_combined_v6_work/superflat_doughnut_i1.fits --geometry 0,0,567,800 --z1z2 [0.80,1.20]
.. convert image.png -trim image_trimmed.png

.. image:: superflat_doughnut_i1_v6_trimmed.png
   :width: 100%
   :alt: fitted doughnut-like surface, version 6

The resulting refined superflatfield, obtained after dividing the initial
superflatfield by the fitted surface, has the following aspect:

.. numina-ximshow obsid_combined_v6_work/superflat_comb_dc_i1.fits --geometry 0,0,567,800 --z1z2 [0.80,1.20]
.. convert image.png -trim image_trimmed.png

.. image:: superflat_comb_dc_i1_v6_trimmed.png
   :width: 100%
   :alt: refined superflatfield, version 6

In addition, since this doughnut-like shape is
present in every single exposure prior to the sky subtraction, the following
strategy is followed in order to perform this latter reduction step:

  - iteration 0: the sky background of each individual exposure is computed as
    the fitted doughnut-like shape scaled to the median signal (in order to
    match the sky background).

  - iteration >= 1: the sky background of every pixel is computed using the
    information of the same pixel in images close in observing time. In this
    case the signal of the doughnut-like shape is considered to be the same in
    all these images (which seems to be a reasonable assumption), and there is
    no need to make use of the fitted doughnut-like shape (except for the
    computation of the refined superflatfield itself).

We can easily compare the new result with the one obtained using
``dithered_v5.yaml``. For that purpose is useful to subtract the new result from the one derived previously:

.. code-block:: console

   (emir) $ numina-imath obsid_combined_v6_results/reduced_image.fits - \
      obsid_combined_v5_results/reduced_image.fits difference_v6.fits

.. generada con --geometry 0,0,850,1200
.. (--geometry 0,0,567,800 en el MacBook Pro)
.. convert combined_v6.png -trim combined_v6_trimmed.png
.. convert difference_v6.png -trim difference_v6_trimmed.png
.. convert -delay 100 -loop 0 combined_v[56]_trimmed.png difference_v6_trimmed.png comparison_v6.gif

.. only:: html

   .. image:: comparison_v6.gif
      :width: 100%
      :alt: combined image, version 6 compared with version 5

In this particular example, the introduction of the refined superflatfield
introduces changes in the signal of some objects that can be as large as 20%,
depending on the location of the targets relative to the doughnut-like shape
(which also changes from exposure to exposure when taking into account the
dithering pattern). In general, the signal of the objects falling close the the
peak of the doughnut-like shape is enhanced (in comparison with what it is
obtained when the refined superflatfield is not computed), while the contrary
is true for the objects closer to the center of the doughnut shape.
