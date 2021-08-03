from blaseball_mike import chronicler, database

from ingest.GameState import GameState
from ingest.ThisDictDoesNotExist import ThisDictDoesNotExist
from ingest.parser import GameEventParser

season = 12

NON_GAME_EVENTS = [
    106,  # Added modifier
    107,  # Removed modifier
]


def ingest_game(parser: GameEventParser, game_data: dict):
    updates = chronicler.get_game_updates(game_ids=game_data['id'], lazy=False)
    feed = database.get_feed_game(game_data['id'], sort=1, limit=500)

    # TODO Paginate. A good test case is the bicentennial game
    assert len(feed) < 500

    if not updates:
        print("No updates for game", game_data['id'])
        return

    if not (updates[0]['data']['inning'] == 0 and
            updates[0]['data']['topOfInning']):
        print("Updates for game", game_data['id'],
              "do not begin at the beginning")
        return

    updates_by_play = {u['data']['playCount']: u for u in updates}

    game_state = GameState(parser)
    for feed_event in feed:
        if feed_event['type'] in NON_GAME_EVENTS:
            continue

        play = feed_event['metadata']['play']

        update = updates_by_play.get(0 if play == 0 else play + 1,
                                     ThisDictDoesNotExist())

        game_state.apply(feed_event, update['data'])


def ingest_new_games(parser: GameEventParser):
    print("Looking for new games")

    games = chronicler.get_games(season=season, finished=True, order='asc')

    for game in games:
        ingest_game(parser, game['data'])
