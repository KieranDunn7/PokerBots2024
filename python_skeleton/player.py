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
        self.pr = (0.51, 0.55, 0.58, 0.61, 0.64, 0.67, 0.69, 0.72, 0.75, 0.78, 0.8, 0.83, 0.85)
        
        self.sr = {12: (0.59, 0.6, 0.61, 0.62, 0.62, 0.63, 0.63, 0.64, 0.66, 0.66, 0.67, 0.68),
                    11: (0.55, 0.56, 0.57, 0.58, 0.58, 0.59, 0.6, 0.61, 0.63, 0.64, 0.64),
                    10: (0.52, 0.53, 0.54, 0.55, 0.55, 0.56, 0.58, 0.59, 0.61, 0.61),
                    9: (0.5, 0.5, 0.51, 0.52, 0.53, 0.54, 0.56, 0.57, 0.59),
                    8: (0.47, 0.48, 0.49, 0.49, 0.51, 0.53, 0.54, 0.56),
                    7: (0.45, 0.46, 0.46, 0.48, 0.5, 0.51, 0.53),
                    6: (0.43, 0.43, 0.45, 0.47, 0.49, 0.5),
                    5: (0.41, 0.43, 0.45, 0.46, 0.48),
                    4: (0.4, 0.42, 0.44, 0.46),
                    3: (0.41, 0.43, 0.44),
                    2: (0.4, 0.42),
                    1: (0.39),
                   }
        
        self.nr = {12: (0.57, 0.58, 0.59, 0.6, 0.59, 0.6, 0.61, 0.62, 0.64, 0.65, 0.65, 0.66),
                   11: (0.53, 0.54, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.61, 0.62, 0.62),
                   10: (0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.57, 0.59, 0.59),
                   9: (0.47, 0.48, 0.48, 0.49, 0.5, 0.52, 0.53, 0.55, 0.57),
                   8: (0.44, 0.45, 0.46, 0.47, 0.48, 0.5, 0.52, 0.53),
                   7: (0.42, 0.43, 0.43, 0.45, 0.47, 0.48, 0.5),
                   6: (0.4, 0.4, 0.42, 0.44, 0.46, 0.47),
                   5: (0.37, 0.39, 0.41, 0.43, 0.45),
                   4: (0.37, 0.39, 0.41, 0.43),
                   3: (0.37, 0.39, 0.41),
                   2: (0.36, 0.38),
                   1: (0.35)
                  }
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
        my_cards = round_state.hands[active]  # your cards
        self.big_blind = bool(active)  # True if you are the big blind

        self.pair = False
        self.suited = False

        self.rank1,self.rank2 = ranks[my_cards[0][0]],ranks[my_cards[1][0]]
        self.suit1,self.suit2 = self.my_cards[0][1],self.my_cards[1][1]

        if self.rank1 == self.rank2:
            self.pair = True
        elif self.rank1 < self.rank2:
            self.rank1,self.rank2 = self.rank2,self.rank1
            self.suit1,self.suit2 = self.suit2,self.suit1
        if self.suit1 == self.suit2:
            self.suited = True

        if self.pair:
            self.pfp = self.pr[self.rank1]
        elif self.suited:
            self.pfp = self.sr[self.rank1][self.rank2]
        else:
            self.pfp = self.nr[self.rank1][self.rank2]



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

        

        #### HANDLE AUCTION
        if BidAction in legal_actions:
            



        if RaiseAction in legal_actions:
           min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
           min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
           max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        
        if RaiseAction in legal_actions and random.random() < 0.3:
            return RaiseAction(random.randint(min_raise, max_raise))
        if CheckAction in legal_actions:
            return CheckAction()
        elif BidAction in legal_actions:
            return BidAction(my_stack) # random bid between 0 and our stack
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
