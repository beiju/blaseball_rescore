from typing import Optional, Union, List

from lark import Tree, Token

from ingest import GameEventParser

BATTER_CHANGE_EVENTS = {'batter_up'}


def is_token_named(item: Union[Tree, Token], name: str):
    return isinstance(item, Token) and item.type == name


def is_tree_named(item: Union[Tree, Token], name: str):
    return isinstance(item, Tree) and item.data == name


def _get_prefixed(update: dict, name: str):
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

    def apply(self, update: dict):
        print("Event text:", update['lastUpdate'])
        event = self.parser.parse(update['lastUpdate'])
        print("Event:", event)
        self.apply_event(event, update)

        assert update['inning'] == self.inning
        assert update['topOfInning'] == self.top_of_inning
        assert update['awayScore'] == self.away_score
        assert update['homeScore'] == self.home_score
        assert update['atBatBalls'] == self.balls
        assert update['atBatStrikes'] == self.strikes
        assert update['halfInningOuts'] == self.outs

    def apply_event(self, tree: Optional[Tree], update: dict):
        if tree is None or not tree.children:
            return

        first = tree.children[0]

        if is_token_named(first, 'PLAY_BALL'):
            self._play_ball()
        elif is_tree_named(first, 'top_of_inning'):
            self._top_of_inning(first.children)
        elif is_tree_named(first, 'bottom_of_inning'):
            self._bottom_of_inning(first.children)
        elif is_tree_named(first, 'batter_up'):
            self._batter_up(update)
        elif is_tree_named(first, 'flyout') or \
                is_tree_named(first, 'ground_out'):
            self._out(update)
        elif is_tree_named(first, 'strikeout'):
            self._out(update)
        elif is_tree_named(first, 'strike'):
            self._strike(first.children, update)
        elif is_tree_named(first, 'single'):
            self._base_hit()
        else:
            breakpoint()

        print("end of func")

    def _play_ball(self):
        self.started = True
        self.inning = -1
        self.top_of_inning = False

    def _top_of_inning(self, children: List[Tree]):
        assert is_token_named(children[0], 'INNING_NUMBER')
        self.inning = int(children[0]) - 1
        self.top_of_inning = True

    def _bottom_of_inning(self, children: List[Tree]):
        assert is_token_named(children[0], 'INNING_NUMBER')
        self.inning = int(children[0]) - 1
        self.top_of_inning = False

    def _batter_up(self, update: dict):
        if not self.expects_batter_up:
            self._deduce_missing(update)

        # Make sure deduce_missing worked
        assert self.expects_batter_up

        self.batter = _get_prefixed(update, 'Batter')
        self.expects_batter_up = False

    def _out(self, update: dict):
        self.outs += 1
        self.strikes = 0
        self.balls = 0
        self.expects_batter_up = True

        # On the last out, the count and outs are cleared
        if self.outs >= _get_prefixed(update, "Outs"):
            self.outs = 0

    def _strike(self, count: List[Tree], update: dict):
        self.strikes += 1
        if self.strikes >= _get_prefixed(update, 'Strikes'):
            self._out(update)

        assert self.balls == int(count[0])
        assert self.strikes == int(count[1])

    def _base_hit(self):
        self.balls = 0
        self.strikes = 0
        self.expects_batter_up = True

    def _deduce_missing(self, update):
        if update['halfInningOuts'] == self.outs + 1:
            # Then we missed an out
            self._out(update)
        else:
            breakpoint()
