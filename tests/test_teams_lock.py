from threading import Thread
from time import sleep
from itertools import groupby

from python.teams_lock import TeamsLock


def test_teams_lock():

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
