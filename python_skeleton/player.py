'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        self.pp = (0.322, 0.353, 0.39, 0.423, 0.45, 0.482, 0.511, 0.542, 0.573, 0.602, 0.63, 0.652, 0.689)
        
        self.sp = {12: (0.389, 0.393, 0.404, 0.412, 0.411, 0.416, 0.423, 0.43, 0.452, 0.463, 0.47, 0.48),
                 11: (0.348, 0.357, 0.367, 0.379, 0.381, 0.39, 0.393, 0.409, 0.429, 0.444, 0.451),
                 10: (0.327, 0.337, 0.344, 0.352, 0.358, 0.36, 0.381, 0.396, 0.422, 0.433),
                 9: (0.309, 0.315, 0.324, 0.333, 0.337, 0.352, 0.37, 0.389, 0.41),
                 8: (0.29, 0.299, 0.307, 0.31, 0.329, 0.344, 0.364, 0.38),
                 7: (0.277, 0.286, 0.286, 0.304, 0.328, 0.335, 0.357),
                 6: (0.264, 0.267, 0.284, 0.304, 0.318, 0.338),
                 5: (0.25, 0.268, 0.287, 0.302, 0.323),
                 4: (0.251, 0.269, 0.288, 0.305),
                 3: (0.261, 0.275, 0.291),
                 2: (0.248, 0.268),
                 1: (0.239)}

        
        self.np = {12: (0.352, 0.365, 0.371, 0.38, 0.378, 0.388, 0.398, 0.403, 0.425, 0.436, 0.444, 0.458),
                 11: (0.316, 0.326, 0.333, 0.345, 0.351, 0.357, 0.363, 0.385, 0.406, 0.417, 0.427),
                 10: (0.29, 0.302, 0.309, 0.317, 0.326, 0.333, 0.35, 0.369, 0.391, 0.4),
                 9: (0.272, 0.278, 0.289, 0.298, 0.305, 0.32, 0.339, 0.36, 0.38),
                 8: (0.255, 0.264, 0.272, 0.278, 0.296, 0.314, 0.333, 0.353),
                 7: (0.239, 0.248, 0.252, 0.272, 0.29, 0.309, 0.328),
                 6: (0.226, 0.233, 0.25, 0.269, 0.291, 0.308),
                 5: (0.211, 0.233, 0.252, 0.271, 0.288),
                 4: (0.215, 0.234, 0.252, 0.273),
                 3: (0.223, 0.239, 0.258),
                 2: (0.211, 0.231),
                 1: (0.202)}

        self.ppp = (0.641, 0.663, 0.692, 0.711, 0.732, 0.75, 0.77, 0.79, 0.812, 0.828, 0.845, 0.858, 0.882)

        self.spp = {12: (0.699, 0.71, 0.717, 0.722, 0.721, 0.728, 0.732, 0.735, 0.752, 0.756, 0.76, 0.762),
                 11: (0.672, 0.68, 0.693, 0.699, 0.704, 0.711, 0.712, 0.722, 0.738, 0.741, 0.746),
                 10: (0.659, 0.669, 0.679, 0.687, 0.69, 0.691, 0.702, 0.716, 0.735, 0.74),
                 9: (0.65, 0.659, 0.668, 0.678, 0.678, 0.686, 0.699, 0.711, 0.726),
                 8: (0.641, 0.649, 0.657, 0.659, 0.672, 0.681, 0.696, 0.708),
                 7: (0.63, 0.634, 0.639, 0.655, 0.668, 0.678, 0.694),
                 6: (0.614, 0.621, 0.637, 0.655, 0.665, 0.678),
                 5: (0.603, 0.622, 0.64, 0.653, 0.667),
                 4: (0.605, 0.622, 0.637, 0.654),
                 3: (0.614, 0.627, 0.641),
                 2: (0.6, 0.619),
                 1: (0.594)}


        self.npp = {12: (0.675, 0.685, 0.693, 0.703, 0.7, 0.707, 0.715, 0.718, 0.734, 0.739, 0.74, 0.746),
                 11: (0.649, 0.658, 0.667, 0.678, 0.682, 0.687, 0.689, 0.702, 0.719, 0.724, 0.727),
                 10: (0.633, 0.642, 0.651, 0.66, 0.668, 0.669, 0.683, 0.694, 0.71, 0.713),
                 9: (0.62, 0.628, 0.639, 0.65, 0.653, 0.666, 0.677, 0.689, 0.706),
                 8: (0.609, 0.618, 0.629, 0.635, 0.648, 0.661, 0.674, 0.688),
                 7: (0.597, 0.607, 0.613, 0.632, 0.641, 0.656, 0.668),
                 6: (0.586, 0.591, 0.61, 0.626, 0.64, 0.655),
                 5: (0.57, 0.59, 0.609, 0.627, 0.638),
                 4: (0.573, 0.59, 0.607, 0.629),
                 3: (0.578, 0.6, 0.615),
                 2: (0.568, 0.588),
                 1: (0.556)}


        
        self.ranks = {"2":0, "3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "T":8, "J":9, "Q": 10, "K": 11, "A":12}

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        self.my_cards = round_state.hands[active]  # your cards
        self.big_blind = bool(active)  # True if you are the big blind

        self.pair = self.rank1 == self.rank2
        self.suited = self.suit1 == self.suit2

        self.rank1,self.rank2 = my_cards[0].rank, my_cards[1].rank
        self.suit1,self.suit2 = my_cards[0].suit, my_cards[1].suit
        if self.rank1 < self.rank2:
            self.rank1,self.rank2 = self.rank2,self.rank1
            self.suit1,self.suit2 = self.suit2,self.suit1

        if self.pair:
            self.pct = self.pp[self.rank1]
            self.pctp = self.ppp[self.rank1]
        elif self.suited:
            self.pct = self.sp[self.rank1][self.rank2]
            self.pctp = self.spp[self.rank1][self.rank2]
        else:
            self.pct = self.np[self.rank1][self.rank2]
            self.pctp = self.npp[self.rank1][self.rank2]



    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed


    def simulate_rest_of_game_postflop_preauction(self, flop, num_sims):
            revealed_cards = self.my_cards + flop

            my_wins_w_auction = 0
            my_wins_wo_auction = 0
            for _ in range(num_sims):
                deck = eval7.Deck()
                for card in revealed_cards:
                    deck.cards.remove(card)

                deck.shuffle()
                draw = deck.deal(6)

                opp_hole = draw[0:2]
                comm = draw[2:4]
                auction1,auction2 = [draw[4]],[draw[5]]

                my_hand_auction = self.my_cards + flop + comm + auction1
                opp_hand = opp_hole + flop + comm
                if eval7.evaluate(my_hand_auction) >= eval7.evaluate(opp_hand):
                    my_wins_w_auction += 1

                my_hand = self.my_cards + flop + comm
                opp_hand_auction = opp_hole + flop + comm + auction1
                if eval7.evaluate(my_hand) >= eval7.evaluate(opp_hand_auction):
                    my_wins_wo_auction += 1

            return my_wins_w_auction/num_sims, my_wins_wo_auction/num_sims

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''

        # May be useful, but you may choose to not use.
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_bid = round_state.bids[active]  # How much you bid previously (available only after auction)
        opp_bid = round_state.bids[1-active]  # How much opponent bid previously (available only after auction)
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot

        if street == 3: ### Post-flop, pre-bid
            prob_win_w_auction, prob_win_wo_auction = simulate_rest_of_game_postflop_preauction(board_cards, 1000)
        



        if BidAction in legal_actions:

            pass
        else:
            if RaiseAction in legal_actions:
                min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
                min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
                max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
                
            if street == 0:
                pct, pctp = self.pct, self.pctp
                tpct = (pct + pctp)/2
                if tpct < 0.5:
                    return FoldAction()
                elif tpct > 0.6:
                    return CallAction()
                elif my_pip == SMALL_BLIND:
                    return RaiseAction(min_raise)
                else:
                    return CallAction()
            if CheckAction in legal_actions:
                return CheckAction()
            return FoldAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
