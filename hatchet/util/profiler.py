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
import io


# class for profiling
class Profiler:
    def __init__(self):
        self._profile_stack = []
        self._times = OrderedDict()
        self._profiles = OrderedDict()

    def start(self, phase):
        """
            Description: Place before the block of code to be profiled.
            Argument - phase (string): The name associated with this profile attempt
        """
        prf = None

        if phase in self._profiles:
            prf = self._profiles[phase]
        else:
            prf = cProfile.Profile()

        prf.enable()
        self._profile_stack.append((prf, phase))

    def end(self):
        """
            Description: Place at the end of the block of code being profiled.
            Return: The total runtime of the last profile attempt
        """
        prf, phase = self._profile_stack.pop(-1)
        prf.disable()
        self._profiles[phase] = prf
        self._times[phase] = pstats.Stats(prf).__dict__["total_tt"]

        return pstats.Stats(prf).__dict__["total_tt"]

    def __str__(self):
        out = StringIO()
        out.write("Times:\n")
        for phase, delta in self._times.items():
            out.write("    %-20s %.2fs\n" % (phase + ":", delta))
        return out.getvalue()

    # sorting options
    # 'calls', 'cumulative', 'filename', 'ncalls', 'pcalls', 'line', 'name', 'nfl' (name file line), 'stdname', 'time'
    def write_to_file(self, sortby="cumulative", filename="prof.txt"):
        """
            Description: Dump the total statistics from this current profile organized
            by phase
        """

        with open(filename, "w") as f:
            pass

        for profile in self._profiles:
            with open(profile+"_temp.txt", "w") as f:
                sts = pstats.Stats(self._profiles[profile], stream=f)
                sts.sort_stats(sortby)
                sts.print_stats()
                # sts.print_callers()
            with open(profile+"_temp.txt", "r") as f:
                lines = f.readlines()

            output = []
            for i, line in enumerate(lines):
                if line == '\n':
                    continue
                elif i == 0 or i == 2:
                    output.append("# " + line)
                elif i == 4:
                    cols = line.split()
                    cols.insert(0, "phase")
                    line = "\t".join(cols) + '\n'
                    output.append(line)
                else:
                    cols = line.split()
                    new_cols = []
                    for i in range(len(cols)):
                        if cols[i] == "{":
                            single_name = ""
                            single_name += cols[i]
                            i += 1
                            while cols[i] != "}":
                                single_name += cols[i] + " "
                            single_name += cols[i]
                            new_cols.append(single_name)
                        else:
                            new_cols.append(cols[i])
                    new_cols.insert(0,profile)
                    line = "\t".join(new_cols) + '\n'
                    output.append(line)

            with open(filename, "a") as f:
                f.writelines(output)






    @contextmanager
    def phase(self, name):
        self.start(name)
        yield
        self.end()

    # def calcAvgStatsHelper(self, obj, num_of_runs):
    #     for stat in obj:
    #         lst = []
    #         for val in range(0, 4):
    #             if val < 2:
    #                 var = int(obj[stat][val]) // num_of_runs
    #                 lst.append(var)
    #             else:
    #                 lst.append(obj[stat][val] / num_of_runs)
    #         if len(obj[stat]) > 4:
    #             lst.append(obj[stat][4])
    #
    #         obj[stat] = tuple(lst)
    #         if len(obj[stat]) > 4 and obj[stat][4] is not {}:
    #             self.calcAvgStatsHelper(obj[stat][4], num_of_runs)

    # def dumpAverageStats(
    #     self, sortby="cumulative", filename="avg_prof.txt", num_of_runs=1
    # ):
    #     """
    #         Description: Dump the average runtime statistics from this current profile to a
    #         file. Cleared by calls to reset. All runtimes and statistics for every function call
    #         is averaged over num_of_runs.
    #     """
    #     with open(filename, "w") as f:
    #         f.write("\n\n Averaged over {} trials \n\n".format(num_of_runs))
    #         sts = pstats.Stats(self.prf, stream=f)
    #         if num_of_runs != 1:
    #             self.calcAvgStatsHelper(sts.__dict__["stats"], num_of_runs)
    #             sts.__dict__["total_tt"] = sts.__dict__["total_tt"] / num_of_runs
    #             sts.__dict__["total_calls"] = sts.__dict__["total_calls"] // num_of_runs
    #             sts.__dict__["prim_calls"] = sts.__dict__["prim_calls"] // num_of_runs
    #         sts.sort_stats(sortby)
    #         sts.print_stats()
