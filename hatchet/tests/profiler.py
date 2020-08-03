from hatchet.util.profiler import Profiler


def f():
    for i in range(1000):
        for j in range(1000):
            i * j


def test_timer_funct():
    prf = Profiler()

    with prf.phase("test"):
        f()

    assert True


def test_write_file():
    assert True
