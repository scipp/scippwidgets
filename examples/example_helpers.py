# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import scipp as sc
import numpy as np


def fake_load(filepath):
    dim = 'tof'
    num_spectra = 10
    return sc.Dataset(
        {
            'sample':
            sc.Variable(['spectrum', dim],
                        values=np.random.rand(num_spectra, 10),
                        variances=0.1 * np.random.rand(num_spectra, 10)),
            'background':
            sc.Variable(['spectrum', dim],
                        values=np.arange(0.0, num_spectra, 0.1).reshape(
                            num_spectra, 10),
                        variances=0.1 * np.random.rand(num_spectra, 10))
        },
        coords={
            dim:
            sc.Variable([dim], values=np.arange(11.0), unit=sc.units.us),
            'spectrum':
            sc.Variable(['spectrum'],
                        values=np.arange(num_spectra),
                        unit=sc.units.one),
            'source-position':
            sc.Variable(value=np.array([1., 1., 10.]),
                        dtype=sc.dtype.vector_3_float64,
                        unit=sc.units.m),
            'sample-position':
            sc.Variable(value=np.array([1., 1., 60.]),
                        dtype=sc.dtype.vector_3_float64,
                        unit=sc.units.m),
            'position':
            sc.Variable(['spectrum'],
                        values=np.arange(3 * num_spectra).reshape(
                            num_spectra, 3),
                        unit=sc.units.m,
                        dtype=sc.dtype.vector_3_float64)
        })


def fake_filepath_converter(input):
    return 'filepath'
