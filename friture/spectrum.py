#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets
from numpy import log10, argmax, zeros, arange, floor, float64, append
from friture.audioproc import audioproc  # audio processing class
from friture.spectrum_settings import (Spectrum_Settings_Dialog,  # settings dialog
                                       DEFAULT_FFT_SIZE,
                                       DEFAULT_FREQ_SCALE,
                                       DEFAULT_MAXFREQ,
                                       DEFAULT_MINFREQ,
                                       DEFAULT_SPEC_MIN,
                                       DEFAULT_SPEC_MAX,
                                       DEFAULT_WEIGHTING,
                                       DEFAULT_RESPONSE_TIME,
                                       DEFAULT_SHOW_FREQ_LABELS)

from friture.logger import PrintLogger
from friture.audiobackend import SAMPLING_RATE
from friture.ring_buffer import RingBuffer
from friture.spectrumPlotWidget import SpectrumPlotWidget
from friture.exp_smoothing_conv import pyx_exp_smoothed_value_numpy


class Spectrum_Widget(QtWidgets.QWidget):

    def __init__(self, parent, logger=PrintLogger()):
        super().__init__(parent)

        self.logger = logger

        self.setObjectName("Spectrum_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneSpect = SpectrumPlotWidget(self, self.logger)
        self.PlotZoneSpect.setObjectName("PlotZoneSpect")
        self.gridLayout.addWidget(self.PlotZoneSpect, 0, 0, 1, 1)

        # initialize the class instance that will do the fft
        self.proc = audioproc(self.logger)

        self.maxfreq = DEFAULT_MAXFREQ
        self.proc.set_maxfreq(self.maxfreq)
        self.minfreq = DEFAULT_MINFREQ
        self.fft_size = 2 ** DEFAULT_FFT_SIZE * 32

        self.proc.set_fftsize(self.fft_size)
        self.spec_min = DEFAULT_SPEC_MIN
        self.spec_max = DEFAULT_SPEC_MAX
        self.weighting = DEFAULT_WEIGHTING
        self.dual_channels = False
        self.response_time = DEFAULT_RESPONSE_TIME
        self.spectrum_type = "Power"  # DEFAULT_SPECTRUM_TYPE = 2
        self.is_dB = True  # DEFAULT_INTENSITY_SCALE = 0

        self.update_weighting()
        self.freq = self.proc.get_freq_scale()

        self.overlap = 3. / 4.
        self.data_buffer = RingBuffer(1, 4 * self.fft_size)
        self.smoothing_buffer = RingBuffer(1, self.fft_size*self.overlap)


        self.update_display_buffers()

        # set kernel and parameters for the smoothing filter
        self.setresponsetime(self.response_time)

        self.PlotZoneSpect.setlogfreqscale()  # DEFAULT_FREQ_SCALE = 1 #log10
        self.PlotZoneSpect.setfreqrange(self.minfreq, self.maxfreq)
        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
        self.PlotZoneSpect.setweighting(self.weighting)
        self.PlotZoneSpect.set_peaks_enabled(False)
        self.PlotZoneSpect.set_baseline_displayUnits(0.)
        self.PlotZoneSpect.setShowFreqLabel(DEFAULT_SHOW_FREQ_LABELS)

        # initialize the settings dialog
        self.settings_dialog = Spectrum_Settings_Dialog(self, self.logger)

    def log_spectrogram(self, sp):
        # Note: implementing the log10 of the array in Cython did not bring
        # any speedup.
        # Idea: Instead of computing the log of the data, I could pre-compute
        # a list of values associated with the colormap, and then do a search...
        epsilon = 1e-30
        return 10. * log10(sp + epsilon)

    def handle_new_data(self, floatdata):
        self.data_buffer.push(floatdata)
        new_sample_points = self.data_buffer.num_unread_data_points()

        # if we have enough data to add a frequency column in the time-frequency plane, compute it
        needed = int(self.fft_size * (1. - self.overlap))
        realizable = int(floor(new_sample_points / needed))
        data = append(self.smoothing_buffer.unwound_data(), self.data_buffer.pop(realizable*needed))

        if realizable > 0:
            sp1n = zeros((len(self.freq), realizable), dtype=float64)
            sp2n = zeros((len(self.freq), realizable), dtype=float64)

            for i in range(realizable):
                floatdata = data[:, i*needed:i*needed + self.fft_size]
                self.smoothing_buffer.push(floatdata[:, (self.fft_size - needed):])

                # first channel
                # FFT transform
                sp1n[:, i] = self.proc.analyzelive(floatdata[0, :], self.spectrum_type)

                if self.dual_channels and floatdata.shape[0] > 1:
                    # second channel for comparison
                    sp2n[:, i] = self.proc.analyzelive(floatdata[1, :], self.spectrum_type)

            # compute the time_plot data
            sp1 = pyx_exp_smoothed_value_numpy(self.kernel, self.alpha, sp1n, self.dispbuffers1)
            sp2 = pyx_exp_smoothed_value_numpy(self.kernel, self.alpha, sp2n, self.dispbuffers2)
            # store result for next computation
            self.dispbuffers1 = sp1
            self.dispbuffers2 = sp2

            sp1.shape = self.freq.shape
            sp2.shape = self.freq.shape
            self.w.shape = self.freq.shape

            if self.dual_channels and floatdata.shape[0] > 1:
                if self.is_dB:
                    spectrogram = self.log_spectrogram(sp2) - self.log_spectrogram(sp1)
                else:
                    spectrogram = sp2 - sp1
                    spectrogram = spectrogram/max(abs(spectrogram))
            else:
                if self.is_dB:
                    spectrogram = self.log_spectrogram(sp1) + self.w
                else:
                    spectrogram = sp1/max(abs(sp1))

            # the log operation and the weighting could be deffered
            # to the post-weedening !

            i = argmax(spectrogram)
            fmax = self.freq[i]

            self.PlotZoneSpect.setdata(self.freq, spectrogram, fmax)

    # method
    def canvasUpdate(self):
        self.PlotZoneSpect.update()

    def pause(self):
        self.PlotZoneSpect.pause()

    def restart(self):
        self.PlotZoneSpect.restart()

    def setresponsetime(self, response_time):
        # time = SMOOTH_DISPLAY_TIMER_PERIOD_MS/1000. #DISPLAY
        # time = 0.025 #IMPULSE setting for a sound level meter
        # time = 0.125 #FAST setting for a sound level meter
        # time = 1. #SLOW setting for a sound level meter
        self.response_time = response_time

        # an exponential smoothing filter is a simple IIR filter
        # s_i = alpha*x_i + (1-alpha)*s_{i-1}
        # we compute alpha so that the N most recent samples represent 100*w percent of the output
        w = 0.65
        delta_n = self.fft_size * (1. - self.overlap)
        n = self.response_time * SAMPLING_RATE / delta_n
        N = 2 * 4096
        self.alpha = 1. - (1. - w) ** (1. / (n + 1))
        self.kernel = self.compute_kernel(self.alpha, N)

    def compute_kernel(self, alpha, N):
        kernel = (1. - alpha) ** arange(N - 1, -1, -1)
        return kernel

    def update_display_buffers(self):
        self.dispbuffers1 = zeros(len(self.freq))
        self.dispbuffers2 = zeros(len(self.freq))

    def setminfreq(self, minfreq):
        self.setMinMaxFreq(minfreq, self.maxfreq)

    def setmaxfreq(self, maxfreq):
        self.setMinMaxFreq(self.minfreq, maxfreq)

    def setMinMaxFreq(self, minfreq, maxfreq):
        self.minfreq = minfreq
        self.maxfreq = maxfreq

        realmin = min(self.minfreq, self.maxfreq)
        realmax = max(self.minfreq, self.maxfreq)

        self.proc.set_maxfreq(realmax)

        self.freq = self.proc.get_freq_scale()
        self.update_display_buffers()
        self.update_weighting()
        # reset kernel and parameters for the smoothing filter
        self.setresponsetime(self.response_time)

        self.PlotZoneSpect.setfreqrange(realmin, realmax)

    def setfftsize(self, fft_size):
        self.fft_size = fft_size
        self.proc.set_fftsize(self.fft_size)
        self.freq = self.proc.get_freq_scale()
        self.update_display_buffers()
        self.update_weighting()
        # reset kernel and parameters for the smoothing filter
        self.setresponsetime(self.response_time)

    def set_spectrum_type(self, type):
        self.spectrum_type = type

    def set_spect_min(self, value):
        self.spec_min = value
        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

    def set_spect_max(self, value):
        self.spec_max = value
        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)

    def setweighting(self, weighting):
        self.weighting = weighting
        self.PlotZoneSpect.setweighting(weighting)
        self.update_weighting()

    def update_weighting(self):
        A, B, C = self.proc.get_freq_weighting()
        if self.weighting is 0:
            self.w = zeros(A.shape)
        elif self.weighting is 1:
            self.w = A
        elif self.weighting is 2:
            self.w = B
        else:
            self.w = C

        self.w.shape = (1, self.w.size)

    def setdualchannels(self, dual_enabled):
        self.dual_channels = dual_enabled
        if dual_enabled:
            self.PlotZoneSpect.set_peaks_enabled(False)
            self.PlotZoneSpect.set_baseline_dataUnits(0.)
        else:
            self.PlotZoneSpect.set_peaks_enabled(False)
            self.PlotZoneSpect.set_baseline_displayUnits(0.)

    def setShowFreqLabel(self, showFreqLabel):
        self.PlotZoneSpect.setShowFreqLabel(showFreqLabel)

    def settings_called(self, checked):
        self.settings_dialog.show()

    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)

    def set_dB_scale(self):
        self.is_dB = True
        self.PlotZoneSpect.setspecrange(self.spec_min, self.spec_max)
        self.setdualchannels(self.dual_channels)

    def set_norm_intensity_scale(self):
        MIN_INTENSITY = -1.1
        MAX_INTENSITY = 1.1
        self.is_dB = False
        self.PlotZoneSpect.setspecrange(MIN_INTENSITY, MAX_INTENSITY)
        self.PlotZoneSpect.set_baseline_dataUnits(0.)
