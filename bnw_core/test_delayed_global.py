# coding: utf-8
from delayed_global import DelayedGlobal

def test_delayed_global():
    a = DelayedGlobal()
    b = dict({100:200})

    try:
        c = a.get(100)
    except AttributeError:
        pass
    else:
        assert 0, "Got result from empty DelayedGlobal"
    
    a.register(b)
    assert a.get(100) == 200

