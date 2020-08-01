import pstats
import cProfile
import os
from hatchet.util.profiler import Profiler


def f():
    for i in range(1000):
        for j in range(1000):
            i * j

def debug():
    prf = Profiler()

    with prf.phase("test"):
        f()

    with prf.phase("test-outer"):
        f()
        with prf.phase("test-inner"):
            f()
        with prf.phase("test-inner2"):
            f()

    prf.write_to_file()



def test_timer_funct():
    prf = Profiler()

    with prf.phase("test"):
        f()
    assert "test" in prf._times

    t1 = prf._times["test"]
    with prf.phase("test"):
        f()
    t2 = prf._times["test"]
    assert t1 < t2

    with prf.phase("test-outer"):
        f()
        with prf.phase("test-inner"):
            f()
        with prf.phase("test-inner2"):
            f()

    assert prf._times["test-inner"] + prf._times["test-inner2"] < prf._times["test-outer"]

def test_profiler_funct():
    prf = Profiler()

    with prf.phase("test"):
        f()
    assert "test" in prf._profiles
    assert type(prf._profiles["test"]) == type(cProfile.Profile())

    with prf.phase("test-outer"):
        f()
        with prf.phase("test-inner"):
            f()
        with prf.phase("test-inner2"):
            f()


debug()
