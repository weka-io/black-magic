#!/usr/bin/python
from threading import RLock, Event
from collections import Counter
from contextlib import contextmanager

import logging
_logger = logging.getLogger(__name__)


def _get_my_ident():
    import threading
    return threading.current_thread().ident


class TeamsLock(object):
    """The lock always belong to one "team"(or no team), and new team members can join the lock"""

    def __init__(self, *teams):
        self._teams = set(teams)
        self._owner_team = None
        self._lock = RLock()
        self._release_event = Event()
        self._release_event.set()
        self._owners = Counter()

    def __repr__(self):
        owners = ", ".join(map(str, sorted(self._owners.keys())))
        return "<TeamsLock-{:X}, owned by team {} [{}]>".format(id(self._lock), self._owner_team, owners)

    @contextmanager
    def acquire_for_team(self, team):
        assert team in self._teams
        self._lock_for_team(team)
        try:
            yield
        finally:
            self._release_for_team(team)

    def _lock_for_team(self, team):
        my_ident = _get_my_ident()
        while True:
            with self._lock:
                if self._owner_team == team:
                    self._owners[my_ident] += 1
                    return
                elif self._owner_team is None:
                    self._owner_team = team
                    self._release_event.clear()
                    self._owners[my_ident] += 1
                    _logger.debug("%s(team %s) acquired %s", my_ident, team, self)
                    return
                else:
                    _logger.debug("%s(team %s) waiting on %s", my_ident, team, self)
            self._release_event.wait(timeout=15)

    def _release_for_team(self, team):
        assert self._owner_team == team
        my_ident = _get_my_ident()
        with self._lock:
            assert 0 < self._owners[my_ident]
            self._owners[my_ident] -= 1
            if not self._owners[my_ident]:
                self._owners.pop(my_ident)
                if not self._owners:
                    self._owner_team = None
                    _logger.debug("%s(team %s) realeased %s", my_ident, team, self)
                    self._release_event.set()


if __name__ == '__main__':
    from threading import Thread
    from time import sleep
    from itertools import groupby
    lock = TeamsLock('a', 'b')

    result = []

    def team_player(player, team):
        for _ in range(4):
            with lock.acquire_for_team(team):
                result.append((player, team))
                sleep(0.1)

    players_and_teams = [(1, 'a'), (2, 'a'), (3, 'a'),
                         (4, 'b'), (5, 'b'), (6, 'b')]

    threads = []
    for player, team in players_and_teams:
        threads.append(Thread(target=team_player, args=(player, team)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    for player, team in players_and_teams:
        assert 4 == sum(1 for p, t in result if p == player and t == team)

    assert 2 == len(list(groupby(result, lambda r: r[1])))
