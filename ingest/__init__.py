from blaseball_mike import chronicler

from ingest.parser import GameEventParser
from ingest.GameState import GameState

season = 12


def ingest_game(parser: GameEventParser, game_data: dict):
    updates = chronicler.get_game_updates(game_ids=game_data['id'], lazy=False)

    if not updates:
        print("No updates for game", game_data['id'])
        return

    if not (updates[0]['data']['inning'] == 0 and
            updates[0]['data']['topOfInning']):
        print("Updates for game", game_data['id'],
              "do not begin at the beginning")
        return

    game_state = GameState(parser)
    for update in updates:
        game_state.apply(update['data'])


def ingest_new_games(parser: GameEventParser):
    print("Looking for new games")

    games = chronicler.get_games(season=season, finished=True, order='asc')

    for game in games:
        ingest_game(parser, game['data'])
