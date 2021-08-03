from typing import Union, List

from lark import Tree, Token

from ingest import GameEventParser
from ingest.ThisDictDoesNotExist import ThisDictDoesNotExist

MaybeDict = Union[dict, ThisDictDoesNotExist]

BATTER_CHANGE_EVENTS = {'batter_up'}


def is_token_named(item: Union[Tree, Token], name: str):
    return isinstance(item, Token) and item.type == name


def is_tree_named(item: Union[Tree, Token], name: str):
    return isinstance(item, Tree) and item.data == name


def _get_prefixed(update: dict, name: str):
    assert not isinstance(update, ThisDictDoesNotExist)

    if update['topOfInning']:
        return update['away' + name]
    else:
        return update['home' + name]


class GameState(object):
    started = False
    inning = 0
    top_of_inning = True

    balls = 0
    strikes = 0
    outs = 0

    home_score = 0
    away_score = 0

    batter = None
    expects_batter_up = False

    def __init__(self, parser: GameEventParser):
        self.parser = parser

    def apply(self, feed_event: dict, update: MaybeDict):
        assert (feed_event['description'] == update['lastUpdate']
                or (feed_event['description'] == "Let's Go!"
                    and update['lastUpdate'] == ""))

        print("Event text:", feed_event['description'])
        event = self.parser.parse(feed_event['description'])
        print("Event:", event)
        self.apply_event(event, feed_event, update)

        assert (update['inning'] == self.inning
                or is_token_named(event.children[0], "PLAY_BALL"))
        assert update['topOfInning'] == self.top_of_inning
        assert update['awayScore'] == self.away_score
        assert update['homeScore'] == self.home_score
        assert update['atBatBalls'] == self.balls
        assert update['atBatStrikes'] == self.strikes
        assert update['halfInningOuts'] == self.outs

    def apply_event(self, tree: Tree, feed_event: dict, update: MaybeDict):
        first = tree.children[0]
        rest = tree.children[1:]

        if is_token_named(first, 'LETS_GO'):
            self._lets_go()
        elif is_token_named(first, 'PLAY_BALL'):
            self._play_ball()
        elif is_tree_named(first, 'top_of_inning'):
            self._top_of_inning(first.children)
        elif is_tree_named(first, 'bottom_of_inning'):
            self._bottom_of_inning(first.children)
        elif is_tree_named(first, 'batter_up'):
            self._batter_up()
        elif is_tree_named(first, 'inning_over'):
            self._inning_over(first.children)
        elif is_tree_named(first, 'strike'):
            self._strike(first.children[0], update)
        elif is_tree_named(first, 'ball'):
            self._ball(first.children[0], update)
        elif is_tree_named(first, 'foul'):
            self._foul(first.children[0], update)
        elif is_tree_named(first, 'flyout') or \
                is_tree_named(first, 'ground_out'):
            self._out(update)
        elif is_tree_named(first, 'strikeout'):
            self._out(update)
        elif is_tree_named(first, 'single'):
            self._base_hit(rest)
        elif is_tree_named(first, 'double'):
            self._base_hit(rest)
        elif is_tree_named(first, 'triple'):
            self._base_hit(rest)
        elif is_tree_named(first, 'quadruple'):
            self._base_hit(rest)
        else:
            breakpoint()

        print("end of func")

    def _lets_go(self):
        pass

    def _play_ball(self):
        self.started = True
        self.inning = 0
        self.top_of_inning = False
        self.expects_batter_up = True

    def _top_of_inning(self, children: List[Tree]):
        # Batters should be out when inning turns over
        assert self.expects_batter_up

        assert is_token_named(children[0], 'INNING_NUMBER')
        self.inning = int(children[0]) - 1
        self.top_of_inning = True

    def _bottom_of_inning(self, children: List[Tree]):
        # Batters should be out when inning turns over
        assert self.expects_batter_up

        assert is_token_named(children[0], 'INNING_NUMBER')
        self.inning = int(children[0]) - 1
        self.top_of_inning = False

    def _batter_up(self):
        assert self.expects_batter_up

        self.expects_batter_up = False

    def _inning_over(self, children: List[Tree]):
        # Batters should be out when inning turns over
        assert self.expects_batter_up

        assert is_token_named(children[0], 'INNING_NUMBER')
        assert self.inning + 1 == int(children[0])

    def _out(self, update: dict):
        self.outs += 1
        self.strikes = 0
        self.balls = 0
        self.expects_batter_up = True

        # On the last out, the count and outs are cleared
        if self.outs >= _get_prefixed(update, "Outs"):
            self.outs = 0

    def _ball(self, count: Tree, update: dict):
        self.balls += 1
        if self.balls >= _get_prefixed(update, 'Balls'):
            self._out(update)

        assert self.balls == int(count.children[0])
        assert self.strikes == int(count.children[1])

    def _strike(self, count: Tree, update: dict):
        self.strikes += 1
        if self.strikes >= _get_prefixed(update, 'Strikes'):
            self._out(update)

        assert self.balls == int(count.children[0])
        assert self.strikes == int(count.children[1])

    def _foul(self, count: Tree, update: dict):
        if self.strikes < _get_prefixed(update, 'Strikes'):
            self.strikes += 1

        assert self.balls == int(count.children[0])
        assert self.strikes == int(count.children[1])

    def _base_hit(self, extras: List[Tree]):
        self.balls = 0
        self.strikes = 0
        self.expects_batter_up = True

        i = 0
        while i < len(extras):
            if is_tree_named(extras[i], 'scores'):
                i += 1
                self._score(1)

                if is_tree_named(extras[i], 'free_refill'):
                    i += 1
                    assert self.outs > 0
                    self.outs -= 1

    def _deduce_missing(self, update):
        if update['halfInningOuts'] == self.outs + 1:
            # Then we missed an out
            self._out(update)
        else:
            breakpoint()

    def _score(self, count: float):
        if self.top_of_inning:
            self.away_score += count
        else:
            self.home_score += count
