class _ClampBuilder(object):
    def __getitem__(self, slc):
        assert isinstance(slc, slice)
        return _Clamp(slc.start, slc.stop)


clamp = _ClampBuilder()


class _Clamp(object):
    def __init__(self, at_least, at_most):
        self.at_least = at_least
        self.at_most = at_most

    def __repr__(self):
        return 'clamp[%s:%s]' % (
            '' if self.at_least is None else self.at_least,
            '' if self.at_most is None else self.at_most)

    def __call__(self, value):
        if self.at_least and value < self.at_least:
            return self.at_least
        elif self.at_most and value > self.at_most:
            return self.at_most
        else:
            return value
