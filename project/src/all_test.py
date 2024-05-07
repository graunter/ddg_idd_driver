import pytest
import main as main_mod

def test_first():
    print('T First')

def test_second(capfd):
    main_mod.verbose = True
    main_mod.debug("Dbg msg")
    out, err = capfd.readouterr()
    assert out == "Dbg msg\n\n"
    print('T2')
