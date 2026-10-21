import pytest
from tools.topdraft_screen import summarize_opponents


def game(opponent, seat, won, bank, enemy_bank, faults=0):
    return dict(opponent=opponent, seat=seat, won=won,
                our=dict(gems=bank, faults=faults, fuel_exhausted=0),
                foe=dict(gems=enemy_bank, faults=0))


def test_generated_only_schedule_finishes_without_a_starter_cohort():
    rows = [game('baseline', 0, True, 1000, 200),
            game('baseline', 1, False, 400, 1000, faults=1)]
    report = summarize_opponents(rows)
    assert set(report) == {'baseline'}
    assert report['baseline']['games'] == 2
    assert report['baseline']['wins'] == 1
    assert report['baseline']['faults'] == 1
    assert report['baseline']['mean_banked_gems'] == 700
    assert report['baseline']['mean_opponent_banked_gems'] == 600
    assert report['baseline']['by_seat']['1'] == dict(games=1, wins=0)


def test_mixed_schedule_keeps_opponents_separate():
    report = summarize_opponents([game('starter', 0, True, 1000, 0),
                                  game('baseline', 1, False, 0, 1000)])
    assert report['starter']['games'] == report['baseline']['games'] == 1
    assert report['starter']['wins'] == 1
    assert report['baseline']['wins'] == 0
    assert report['starter']['mean_banked_gems'] == 1000
    assert report['baseline']['mean_banked_gems'] == 0


def test_missing_or_unknown_captures_fail_loudly():
    with pytest.raises(ValueError, match='No completed games'):
        summarize_opponents([])
    with pytest.raises(ValueError, match='Unexpected opponent'):
        summarize_opponents([game('unrecognized', 0, True, 1000, 0)])
