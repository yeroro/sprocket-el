# -*- coding: utf-8 -*-

import pyworld

from scipy import signal


class WORLD(object):
  """WORLD-based speech analyzer

    Parameters
    ----------
    fs : int, optional
        Sampling frequency
        Default set to 16000
    fftl : int, optional
        FFT length
        Default set to 1024
    shiftms : int, optional
        Shift lengs [ms]
        Default set to 5.0
    minf0 : int, optional
        Floor in f0 estimation
        Default set to 50
    maxf0 : int, optional
        Ceil in f0 estimation
        Default set to 500
    """

  def __init__(self,
               fs=16000,
               fftl=1024,
               shiftms=5.0,
               minf0=40.0,
               maxf0=500.0,
               med_filter_kernel=0,
               f0_fake=None):
    self.fs = fs
    self.fftl = fftl
    self.shiftms = shiftms
    self.minf0 = minf0
    self.maxf0 = maxf0
    self.med_filter_kernel = med_filter_kernel
    self.f0_fake = f0_fake

  def analyze(self, x):
    """Analyze acoustic features based on WORLD

        analyze F0, spectral envelope, aperiodicity

        Paramters
        ---------
        x : array, shape (`T`)
            monoral speech signal in time domain

        Returns
        ---------
        f0 : array, shape (`T`,)
            F0 sequence
        spc : array, shape (`T`, `fftl / 2 + 1`)
            Spectral envelope sequence
        ap: array, shape (`T`, `fftl / 2 + 1`)
            aperiodicity sequence

        """
    f0, time_axis = pyworld.harvest(
        x,
        self.fs,
        f0_floor=self.minf0,
        f0_ceil=self.maxf0,
        frame_period=self.shiftms)

    if self.f0_fake is not None:
      # TODO(yero): Consider using f0_fake only when f0 is non-zero.
      print("Using fake F0 {:.2f}".format(self.f0_fake))
      f0.fill(self.f0_fake)
    elif self.med_filter_kernel > 0:
      print("Using median filter of kernel size {}".format(
          self.med_filter_kernel))
      f0 = signal.medfilt(f0, self.med_filter_kernel)

    spc = pyworld.cheaptrick(x, f0, time_axis, self.fs, fft_size=self.fftl)

    ap = pyworld.d4c(
        x, f0, time_axis, self.fs, fft_size=self.fftl, threshold=0.0)

    assert spc.shape == ap.shape
    return f0, spc, ap

  def analyze_f0(self, x):
    """Analyze decomposes a speech signal into F0:

        Paramters
        ---------
        x: array, shape (`T`)
            monoral speech signal in time domain

        Returns
        ---------
        f0 : array, shape (`T`,)
            F0 sequence

        """

    f0, time_axis = pyworld.harvest(
        x,
        self.fs,
        f0_floor=self.minf0,
        f0_ceil=self.maxf0,
        frame_period=self.shiftms)

    return f0

  def synthesis(self, f0, spc, ap):
    """Synthesis re-synthesizes a speech waveform from:

        Parameters
        ----------
        f0 : array, shape (`T`)
            F0 sequence
        spc : array, shape (`T`, `dim`)
            Spectral envelope sequence
        ap: array, shape (`T`, `dim`)
            Aperiodicity sequence

        """

    return pyworld.synthesize(f0, spc, ap, self.fs, frame_period=self.shiftms)
