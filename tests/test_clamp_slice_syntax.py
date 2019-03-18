from black_python_magic.clamp_slice_syntax import clamp


def test_clamp_slice_syntax():
    assert clamp[:](2) == 2
    assert clamp[:](3) == 3
    assert clamp[:](4) == 4
    assert clamp[:](5) == 5
    assert clamp[:](6) == 6
    assert clamp[:5](2) == 2
    assert clamp[:5](3) == 3
    assert clamp[:5](4) == 4
    assert clamp[:5](5) == 5
    assert clamp[:5](6) == 5
    assert clamp[3:](2) == 3
    assert clamp[3:](3) == 3
    assert clamp[3:](4) == 4
    assert clamp[3:](5) == 5
    assert clamp[3:](6) == 6
    assert clamp[3:5](2) == 3
    assert clamp[3:5](3) == 3
    assert clamp[3:5](4) == 4
    assert clamp[3:5](5) == 5
    assert clamp[3:5](6) == 5
