from lark import Lark


class GameEventParser(object):
    def __init__(self):
        self.parser = Lark(r"""
        update: (PLAY_BALL | top_of_inning | bottom_of_inning | batter_up | flyout | ground_out | strikeout | strike | single) NEWLINE?
        
        PLAY_BALL: "Play ball!"
        
        // Game phase events
        top_of_inning: "Top of " INNING_NUMBER ", " NAME " batting."
        bottom_of_inning: "Bottom of " INNING_NUMBER ", " NAME " batting."
        batter_up: NAME " batting for the " NAME "."
        
        // Strikes
        strike: "Strike, looking. " INT "-" INT
        
        // Outs
        flyout: NAME " hit a flyout to " NAME "."
        ground_out: NAME " hit a ground out to " NAME "."
        strikeout: NAME " strikes out looking."
        
        // Hits
        single: NAME " hits a Single!"
        
        // Primitives
        INNING_NUMBER: INT
        NAME: (WORD WS)* WORD
            
        %import common.INT
        %import common.WS
        %import common.WORD
        %import common.NEWLINE
        %ignore WS
        """, start='update', debug=True, lexer='dynamic_complete',
                           ambiguity='explicit')

    def parse(self, text: str):
        if len(text) == 0:
            return None

        return self.parser.parse(text)
