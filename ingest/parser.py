from lark import Lark


class GameEventParser(object):
    def __init__(self):
        self.parser = Lark(r"""
        update: (LETS_GO | PLAY_BALL | top_of_inning | bottom_of_inning | inning_over | batter_up | ball | strike | foul | strikeout | flyout | ground_out | single | double | triple | quadruple) (scores free_refill?)? NEWLINE?
        
        LETS_GO: "Let's Go!"
        PLAY_BALL: "Play ball!"
        
        // Game phase events
        top_of_inning: "Top of " INNING_NUMBER ", " NAME " batting."
        bottom_of_inning: "Bottom of " INNING_NUMBER ", " NAME " batting."
        batter_up: NAME " batting for the " NAME "."
        inning_over: "Inning " INNING_NUMBER " is now an Outing."
        
        // Pitches you didn't hit good or bad
        ball: "Ball. " count
        strike: "Strike, looking. " count
              | "Strike, swinging. " count
        foul: "Very "? "Foul Ball. " count
        
        // Outs
        strikeout: NAME " strikes out looking."
                 | NAME " strikes out swinging."
        flyout: NAME " hit a flyout to " NAME "."
        ground_out: NAME " hit a ground out to " NAME "."
        
        // Hits
        single: NAME " hits a Single!"
        double: NAME " hits a Double!"
        triple: NAME " hits a Triple!"
        quadruple: NAME " hits a Quadruple!"
        
        // Scores
        scores: NAME " scores!"
        free_refill: NAME " used their Free Refill." NEWLINE NAME " Refills the In!"
        
        // Segments
        count: INT "-" INT
        
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
        return self.parser.parse(text)
