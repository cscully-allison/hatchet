# Copyright 2017-2020 Lawrence Livermore National Security, LLC and other
# Hatchet Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: MIT

from collections import OrderedDict
from contextlib import contextmanager
from datetime import datetime
from io import StringIO

import cProfile
import pstats


class Timer(object):
    """Simple phase timer with a context manager."""

    def __init__(self):
        self._phase = None
        self._start_time = None
        self._times = OrderedDict()

    def start_phase(self, phase):
        now = datetime.now()
        delta = None

        if self._phase:
            delta = now - self._start_time
            self._times[self._phase] = delta

        self._phase = phase
        self._start_time = now
        return delta

    def end_phase(self):
        assert self._phase and self._start_time

        now = datetime.now()
        delta = now - self._start_time
        if self._times.get(self._phase):
            self._times[self._phase] = self._times.get(self._phase) + delta
        else:
            self._times[self._phase] = delta

        self._phase = None
        self._start_time = None

    def __str__(self):
        out = StringIO()
        out.write("Times:\n")
        for phase, delta in self._times.items():
            out.write("    %-20s %.2fs\n" % (phase + ":", delta.total_seconds()))
        return out.getvalue()

    @contextmanager
    def phase(self, name):
        self.start_phase(name)
        yield
        self.end_phase()


# Wrapper class around cProfile
# Exports a pstats file for
#  reading by hpctoolkit
class Profiler:
    """
        Wrapper class around cProfile.
        Exports a pstats file to be read by hpctoolkit.
    """

    def __init__(self):
        self._prf = cProfile.Profile()
        self._output = "htrun.prof"

    def start(self):
        """
            Description: Place before the block of code to be profiled.
            Argument - phase (string): The name associated with this profile
            attempt
        """
        self._prf.enable()

    def end(self):
        """
            Description: Place at the end of the block of code being profiled.
            Return: The total runtime of the last profile attempt
        """
        self._prf.disable()

    def reset(self):
        """
            Description: Resets the profilier.
        """
        self._prf = cProfile.Profile()

    def __str__(self):
        """
            Description: Writes stats object out as a string.
        """
        return pstats.Stats(self._prf).print_stats()

    def write_to_file(self, filename=""):
        """
            Description: Write the pstats object to a binary
            file to be read in by an appropriate source.
        """
        sts = pstats.Stats(self._prf)
        if filename == "":
            sts.dump_stats(self._output + ".prof")
        else:
            sts.dump_stats(filename)

    @contextmanager
    def phase(self, output):
        self._output = output
        self.start()
        yield
        self.end()
