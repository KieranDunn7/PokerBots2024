'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction, BidAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import random
import eval7
from collections import Counter


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
        self.forfeit = False # decides whether the bot can win by folding/checking every future action

        self.opp_bids = []
        self.my_bids = []
        self.opp_bids_sum = 0
        self.opp_bids_num = 0
        self.opp_bid_avg = 0
        self.opp_bid_cv = 1
        self.opp_bid_var = 2500
        
        self.opp_bluffs = 0 # times opponent reveals cards and bluffs
        self.opp_sandbags = 0 # times opponent reveals cards and doesn't bluff
        
        self.opp_pre_flop_actions = []
        self.opp_flop_actions = []
        self.opp_turn_actions = []
        self.opp_river_actions = []
        
        self.opp_pre_flop_bets = []
        self.opp_flop_bets = []
        self.opp_turn_bets = []
        self.opp_river_bets = []
        
        self.total_opp_pre_flop_actions = []
        self.total_opp_flop_actions = []
        self.total_opp_turn_actions = []
        self.total_opp_river_actions = []
        
        self.pre_flop_aggression = 0
        self.flop_aggression = 0
        self.turn_aggression = 0
        self.river_aggression = 0



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
        big_blind = bool(active)  # True if you are the big blind
        
        ranks_dict = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}
        
        total_suited_percentages = {12: (0.544, 0.5515, 0.5585, 0.5675, 0.566, 0.572, 0.5775, 0.5825, 0.602, 0.6095, 0.615, 0.621),
                 11: (0.51, 0.5185, 0.53, 0.539, 0.5425, 0.5505, 0.5525, 0.5655, 0.5835, 0.5925, 0.5985),
                 10: (0.493, 0.5035, 0.5115, 0.5185, 0.524, 0.5255, 0.5415, 0.556, 0.5785, 0.5865),
                 9: (0.4795, 0.4865, 0.4965, 0.5065, 0.5075, 0.519, 0.5375, 0.55, 0.568),
                 8: (0.4655, 0.474, 0.478, 0.4845, 0.5, 0.5125, 0.529, 0.544),
                 7: (0.4535, 0.46, 0.4625, 0.4795, 0.498, 0.5065, 0.5255),
                 6: (0.439, 0.444, 0.4605, 0.4795, 0.4915, 0.508),
                 5: (0.4265, 0.445, 0.4635, 0.4775, 0.4955),
                 4: (0.428, 0.4455, 0.4625, 0.4795),
                 3: (0.4375, 0.451, 0.4645),
                 2: (0.424, 0.4435),
                 1: (0.416,)}
        # averages from sp and spp

        total_nonsuited_percentages = {12: (0.5135, 0.525, 0.532, 0.5415, 0.539, 0.5475, 0.5565, 0.5605, 0.5795, 0.5875, 0.592, 0.602),
                 11: (0.4825, 0.492, 0.5, 0.5115, 0.5165, 0.522, 0.526, 0.5435, 0.5625, 0.5705, 0.577),
                 10: (0.4615, 0.472, 0.4805, 0.4885, 0.497, 0.501, 0.5165, 0.5315, 0.5505, 0.5565),
                 9: (0.446, 0.453, 0.464, 0.474, 0.479, 0.493, 0.508, 0.5245, 0.543),
                 8: (0.432, 0.441, 0.4505, 0.4565, 0.472, 0.4875, 0.5035, 0.5205),
                 7: (0.418, 0.4275, 0.4325, 0.452, 0.4655, 0.4825, 0.498),
                 6: (0.406, 0.412, 0.43, 0.4475, 0.4655, 0.4815),
                 5: (0.3905, 0.4115, 0.4305, 0.449, 0.463),
                 4: (0.394, 0.412, 0.4295, 0.451),
                 3: (0.4005, 0.4195, 0.4365),
                 2: (0.3895, 0.4095),
                 1: (0.379,)}
        # averages from np and npp

        total_pair_percentages = (0.4815, 0.508, 0.541, 0.567, 0.591, 0.616, 0.6405, 0.666, 0.6925, 0.715, 0.7375, 0.755, 0.7855)
        # averages from pp and ppp

    
        if my_bankroll > (NUM_ROUNDS-round_num)*1.5 + 4 and not self.forfeit:
            self.forfeit = True
            print(f"Forfeit in Round #{round_num}")
        if not self.forfeit:
             print()
             print("Round Num:", round_num)
             print()
            
        rank1,rank2 = ranks_dict[my_cards[0][0]], ranks_dict[my_cards[1][0]]
        suit1,suit2 = my_cards[0][1], my_cards[1][1]

        pair = rank1 == rank2
        suited = suit1 == suit2

        if rank1 < rank2:
            rank1,rank2 = rank2,rank1
            suit1,suit2 = suit2,suit1

        if pair:
            self.total_percentage = total_pair_percentages[rank1]
        elif suited:
            self.total_percentage = total_suited_percentages[rank1][rank2]
        else:
            self.total_percentage = total_nonsuited_percentages[rank1][rank2]
        self.rank1, self.rank2 = rank1, rank2
        self.pair, self.suited = pair, suited
        self.suit1, self.suit2 = suit1, suit2
        
        self.high_cards_or_pair_likely = False
        
        self.double_flush_draw = False
        self.flush_draw = False
        self.flush = False
        self.flush_suit = -1
        self.my_flush = set() # cards in our hand for a flush
        self.board_flush = set() # cards on the board for a flush
        self.my_num_in_suit = 0 # number we have in the suit
        self.my_flush_high = -1 # high in the flush for tie-break
        
        self.double_straight_draw = False
        self.straight_draw = False
        self.straight = False
        self.my_straight = set() # cards in our hand for a straight
        self.board_straight = set() # cards on the board for a straight
        self.straight_high = -1
        self.draw_needed = set() # cards needed for a draw
        self.double_draw_needed = set() # pairs of cards needed for a double draw
        self.my_num_in_straight = 0 # number we have making up the straight
        self.my_straight_high = -1
        
        self.trips = False
        self.trips_rank = -1
        
        self.pair = False
        self.pair_rank = -1
        
        self.two_pair = False
        self.two_pair_ranks = -1, -1 # higher rank first
        
        self.full_house = False
        self.full_house_ranks = -1, -1 # three of a kind first
        
        self.quads = False
        self.quads_rank = -1
        
        self.my_high_card = -1
        
        self.high_hand = 0 # string representing the best hand we have
        self.high_hand_numbers = -1
        
        self.straight_flush = False
        
        self.street_num = 0 # used for checking if hand strength has already been calculated
        
        self.board_trips = False
        self.board_trips_rank = -1
        
        self.board_pair = False
        self.board_pair_rank = -1
        
        self.board_two_pair = False
        self.board_two_pair_ranks = -1, -1 # higher rank first
        
        self.board_full_house = False
        self.board_full_house_ranks = -1, -1 # three of a kind first
        
        self.board_quads = False
        self.board_quads_rank = -1
        
        self.board_high_card = -1
        
        self.board_straight_need_3 = False
        self.board_straight_need_2 = False
        self.board_straight_need_1 = False
        self.board_straight_need_0 = False # straight on board
        self.board_straight_high = -1
        self.board_straight_needed = set() # opp cards needed for a board straight
        
        self.board_flush_need_3 = False
        self.board_flush_need_2 = False
        self.board_flush_need_1 = False
        self.board_flush_need_0 = False # flush on board
        
        self.board_flush_suit = -1
        
        self.board_straight_flush = False
        
        self.opp_pre_flop_bet = 0
        self.opp_river_bet = 0
        self.opp_turn_bet = 0
        self.opp_flop_bet = 0
        
        self.on_board_hands = set()
        
        self.flop_cards = []
        self.turn_cards = []
        self.river_cards = []
        self.opp_cards = []
        
        self.pre_flop_aggression = 1, 0.66, 0.4, 0.166
        self.flop_aggression = 1, 0.66, 0.4, 0.166
        self.turn_aggression = 1, 0.66, 0.4, 0.166
        self.river_aggression = 1, 0.66, 0.4, 0.166
        
        
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
        big_blind = bool(active)  # True if you are the big blind
        my_stack = previous_state.stacks[active]  # the number of chips you have remaining
        opp_stack = previous_state.stacks[1-active]  # the number of chips your opponent has remaining
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        final_pot_size = my_contribution + opp_contribution # pot size at the end of the round
        my_pip = previous_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = previous_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        round_num = game_state.round_num
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        
        if not self.forfeit:
            self.opp_pre_flop_actions.append(self.opp_pre_flop_bet)
            if self.opp_pre_flop_bet > 0:
                self.opp_pre_flop_bets.append(self.opp_pre_flop_bet)
            self.total_opp_pre_flop_actions.append(round(self.opp_pre_flop_bet, 3))
            # if len(self.opp_pre_flop_actions) > 30:
            #     if self.opp_pre_flop_actions[0] != 0:
            #         self.opp_pre_flop_bets.pop(0)
            #     self.opp_pre_flop_actions.pop(0)
            if street >= 3:
                self.opp_flop_actions.append(self.opp_flop_bet)
                if self.opp_flop_bet > 0:
                    self.opp_flop_bets.append(self.opp_flop_bet)
                self.total_opp_flop_actions.append(round(self.opp_flop_bet, 3))
                # if len(self.opp_flop_actions) > 30:
                #     if self.opp_flop_actions[0] != 0:
                #         self.opp_flop_bets.pop(0)
                #     self.opp_flop_actions.pop(0)
            if street >= 4:
                self.opp_turn_actions.append(self.opp_turn_bet)
                if self.opp_turn_bet > 0:
                    self.opp_turn_bets.append(self.opp_turn_bet)
                self.total_opp_turn_actions.append(round(self.opp_turn_bet, 3))
                # if len(self.opp_turn_actions) > 30:
                #     if self.opp_turn_actions[0] != 0:
                #         self.opp_turn_bets.pop(0)
                #     self.opp_turn_actions.pop(0)
                    
            if street >= 5:
                self.opp_river_actions.append(self.opp_river_bet)
                if self.opp_river_bet > 0:
                    self.opp_river_bets.append(self.opp_river_bet)
                self.total_opp_river_actions.append(round(self.opp_river_bet, 3))
                # if len(self.opp_river_actions) > 30:
                #     if self.opp_river_actions[0] != 0:
                #         self.opp_river_bets.pop(0)
                #     self.opp_river_actions.pop(0)
                    
                    
        def calculate_std_dev(numbers):
            n = len(numbers)
            if n < 2:
                return 0  # Standard deviation is not defined for less than two elements
            
            mean = sum(numbers) / n
            squared_diff = [(x - mean) ** 2 for x in numbers]
            variance = sum(squared_diff) / n
            std_dev = variance ** (1/2)
            
            return std_dev
        
        
        
        if street >= 3 and not self.all_in:
            opp_bid = previous_state.bids[1-active]
            if opp_bid != 0:
                self.opp_bid_avg = self.opp_bids_sum/self.opp_bids_num
                self.opp_bid_var = sum((x - self.opp_bid_avg) ** 2 for x in self.opp_bids)/self.opp_bids_num
                try:
                    self.opp_bid_cv = (self.opp_bid_var**(1/2))/self.opp_bid_avg
                except ZeroDivisionError:
                    self.opp_bid_cv = 100
                    
                    
        if len(self.opp_pre_flop_bets) != 0 and len(self.opp_pre_flop_actions) >= 10:
            opp_pre_flop_bet_rate = len(self.opp_pre_flop_bets) / len(self.opp_pre_flop_actions)
            average_opp_pre_flop_bet = min(1, max(0.66, sum(self.opp_pre_flop_bets) / len(self.opp_pre_flop_bets))) + 0.1
            opp_pre_flop_bet_stdv = min(max(0.2, calculate_std_dev(self.opp_pre_flop_bets)), average_opp_pre_flop_bet/3)
        else:
            opp_pre_flop_bet_rate = 0.25
            average_opp_pre_flop_bet = 0.66
            opp_pre_flop_bet_stdv = 0.2
            
        if len(self.opp_flop_bets) != 0 and len(self.opp_flop_actions) >= 10:
            opp_flop_bet_rate = len(self.opp_flop_bets) / len(self.opp_flop_actions)
            average_opp_flop_bet = min(1, max(0.66, sum(self.opp_flop_bets) / len(self.opp_flop_bets))) + 0.1
            opp_flop_bet_stdv = min(max(0.2, calculate_std_dev(self.opp_flop_bets)), average_opp_flop_bet/3)
        else:
            opp_flop_bet_rate = 0.25
            average_opp_flop_bet = 0.66
            opp_flop_bet_stdv = 0.2
            
        if len(self.opp_turn_bets) != 0 and len(self.opp_turn_actions) >= 10:
            opp_turn_bet_rate = len(self.opp_turn_bets) / len(self.opp_turn_actions)
            average_opp_turn_bet = min(1, max(0.66, sum(self.opp_turn_bets) / len(self.opp_turn_bets))) + 0.1
            opp_turn_bet_stdv = min(max(0.2, calculate_std_dev(self.opp_turn_bets)), average_opp_turn_bet/3)
        else:
            opp_turn_bet_rate = 0.25
            average_opp_turn_bet = 0.66
            opp_turn_bet_stdv = 0.2
            
        if len(self.opp_river_bets) != 0 and len(self.opp_river_actions) >= 10:
            opp_river_bet_rate = len(self.opp_river_bets) / len(self.opp_river_actions)
            average_opp_river_bet = min(1, max(0.66, sum(self.opp_river_bets) / len(self.opp_river_bets))) + 0.1
            opp_river_bet_stdv = min(max(0.2, calculate_std_dev(self.opp_river_bets)), average_opp_river_bet/3)
        else:
            opp_river_bet_rate = 0.25
            average_opp_river_bet = 0.66
            opp_river_bet_stdv = 0.2
        
        if opp_pre_flop_bet_rate >= 0.25:
            self.pre_flop_aggression = round(average_opp_pre_flop_bet + opp_pre_flop_bet_stdv, 3), round(average_opp_pre_flop_bet, 3), round(average_opp_pre_flop_bet - opp_pre_flop_bet_stdv, 3), round(min(average_opp_pre_flop_bet - 3 * opp_pre_flop_bet_stdv, 0.1), 3)
        else:
            self.pre_flop_aggression = round(average_opp_pre_flop_bet, 3), round(average_opp_pre_flop_bet- opp_pre_flop_bet_stdv, 3), round(average_opp_pre_flop_bet - 2*opp_pre_flop_bet_stdv, 3), round(min(average_opp_pre_flop_bet - 3 * opp_pre_flop_bet_stdv, 0.08), 3)

        if opp_flop_bet_rate >= 0.25:
            self.flop_aggression = round(average_opp_flop_bet + opp_flop_bet_stdv, 3), round(average_opp_flop_bet, 3), round(average_opp_flop_bet - opp_flop_bet_stdv, 3), round(min(average_opp_flop_bet - 3 * opp_flop_bet_stdv, 0.1), 3)
        else:
            self.flop_aggression = round(average_opp_flop_bet, 3), round(average_opp_flop_bet - opp_flop_bet_stdv, 3), round(average_opp_flop_bet - 2*opp_flop_bet_stdv, 3), round(min(average_opp_flop_bet - 3 * opp_flop_bet_stdv, 0.08), 3)

        if opp_turn_bet_rate >= 0.25:
            self.turn_aggression = round(average_opp_turn_bet + opp_turn_bet_stdv, 3), round(average_opp_turn_bet, 3), round(average_opp_turn_bet - opp_turn_bet_stdv, 3), round(min(average_opp_turn_bet - 3 * opp_turn_bet_stdv, 0.1), 3)
        else:
            self.turn_aggression = round(average_opp_turn_bet, 3), round(average_opp_turn_bet - opp_turn_bet_stdv, 3), round(average_opp_turn_bet - 2*opp_turn_bet_stdv, 3), round(min(average_opp_turn_bet - 3 * opp_turn_bet_stdv, 0.08), 3)
        
        if opp_river_bet_rate >= 0.25:
            self.river_aggression = round(average_opp_river_bet + opp_river_bet_stdv, 3), round(average_opp_river_bet, 3), round(average_opp_river_bet - opp_river_bet_stdv, 3), round(min(average_opp_river_bet - 3 * opp_river_bet_stdv, 0.1), 3)
        else:
            self.river_aggression = round(average_opp_river_bet, 3), round(average_opp_river_bet - opp_river_bet_stdv, 3), round(average_opp_river_bet - 2*opp_river_bet_stdv, 3), round(min(average_opp_river_bet - 3 * opp_river_bet_stdv, 0.08), 3)

        
        print("Pre-flop aggression:", self.pre_flop_aggression)
        print("Flop aggression:", self.flop_aggression)
        print("Turn aggression:", self.turn_aggression)
        print("River aggression:", self.river_aggression)
        
                    
        if round_num == NUM_ROUNDS:
            print("Final Time:", game_clock)
            print("Opp pre-flop actions: ", self.total_opp_pre_flop_actions)
            print("Opp flop actions: ", self.total_opp_flop_actions)
            print("Opp turn actions: ", self.total_opp_turn_actions)
            print("Opp river actions: ", self.total_opp_river_actions)
        

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
        ranks_dict = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}
        suits_dict = {"s": 3, "h": 2, "c": 1, "d": 0}
        
        
        def check_for_straight(board_cards, num_needed):
            """
            Takes the board cards as a list of strings and the number in a straight
            needed and returns a dictionary with straight high rank indexes as keys
            and a tuple with sets of cards in and cards out as values if there are more
            than num_needed in that straight
            """
            ranks_dict = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}
            ranks = set()
            for card in board_cards:
                ranks.add(ranks_dict[card[0]])
            starts_in = {}
            
            num_in = 0
            ace_low_straight = (12, 0, 1, 2, 3)
            cards_in = set()
            cards_needed = set()
            for card in ace_low_straight:
                if card in ranks:
                    num_in += 1
                    cards_in.add(card)
                else:
                    cards_needed.add(card)
            if num_in >= num_needed:
                starts_in[3] = cards_in, cards_needed
            for starting_card in range(9):
                num_in = 0
                cards_in = set()
                cards_needed = set()
                for card in range(starting_card, starting_card + 5):
                    if card in ranks:
                        num_in += 1
                        cards_in.add(card)
                    else:
                        cards_needed.add(card)
                if num_in >= num_needed:
                    starts_in[starting_card+4] = cards_in, cards_needed

            return starts_in


        def check_for_flush(board_cards, num_needed):
            """
            Takes the board cards as a list of strings and the number in one suit
            needed and returns a dictionary with suit indexes as keys and a set of ranks
            in that suit as values if there are at least num_needed of that suit
            """
            ranks_dict = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}
            suits_dict = {"s": 3, "h": 2, "c": 1, "d": 0}
            suits = [set(), set(), set(), set()]
            for card in board_cards:
                rank, suit = ranks_dict[card[0]], suits_dict[card[1]]
                suits[suit].add(rank)
            suits_in = {}
            for suit_index, suit in enumerate(suits):
                if len(suit) >= num_needed:
                    suits_in[suit_index] = suit
            return suits_in


        def check_for_pair(board_cards):
            """
            Takes the board cards as a list of strings returns a dictionary with rank
            indexes as keys and number of that rank as values if there is more than
            one card with that rank
            """
            ranks_dict = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}
            ranks = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
            for card in board_cards:
                ranks[ranks_dict[card[0]]] += 1
            ranks_in = {}
            for rank, num in ranks.items():
                if num >= 2:
                    ranks_in[rank] = num
            return ranks_in
        
        
        def simulate_auction(my_cards, board_cards, num_sims):
            """
            Takes my_cards and board_cards as lists of strings and num_sims as
            an int and uses montecarlo to return the probability of winning
            with and without winning the auction
            """
            hole_cards = [eval7.Card(card) for card in my_cards]
            flop_cards = [eval7.Card(card) for card in board_cards]
            revealed_cards = hole_cards + flop_cards
            def compare(score1, score2):
                if score1 > score2:
                    return 1
                elif score1 == score2:
                    return 0.5
                return 0
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)
            my_wins_w_auction, my_wins_wo_auction, my_wins_both_auction = 0, 0, 0
            for trial in range(num_sims):
                deck.shuffle()
                for drawing in range(9):
                    draw = deck[drawing:drawing+5]
                    opp_hole = draw[0:2]
                    r_and_t = draw[2:4]
                    auction = [draw[4]]
                    my_hand = revealed_cards + r_and_t
                    my_hand_p = revealed_cards + r_and_t + auction
                    opp_hand = opp_hole + flop_cards + r_and_t
                    opp_hand_p = opp_hole + flop_cards + r_and_t + auction
                    my_score = eval7.evaluate(my_hand)
                    my_score_p = eval7.evaluate(my_hand_p)
                    opp_score = eval7.evaluate(opp_hand)
                    opp_score_p = eval7.evaluate(opp_hand_p)
                    my_wins_w_auction += compare(my_score_p, opp_score)
                    my_wins_wo_auction += compare(my_score, opp_score_p)
    
            return my_wins_w_auction/(num_sims*9), my_wins_wo_auction/(num_sims*9)


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
        big_blind = bool(active)  # True if you are the big blind
        pot_size = my_contribution + opp_contribution - continue_cost # total pot size excluding new opponent betting
        
        
        if self.forfeit:
            if BidAction in legal_actions:
                return BidAction(0)
            if CheckAction in legal_actions:
                return CheckAction()
            self.folded = True
            return FoldAction()

        self.all_in = my_stack == 0
        self.opp_all_in = opp_stack == 0
        
        if continue_cost > pot_size * self.flop_aggression[0]:
            high_flop_bet, medium_flop_bet, small_flop_bet, tiny_flop_bet = False, False, False, False
        elif continue_cost > pot_size * self.flop_aggression[1]:
            high_flop_bet, medium_flop_bet, small_flop_bet, tiny_flop_bet = True, False, False, False
        elif continue_cost > pot_size * self.flop_aggression[2]:
            high_flop_bet, medium_flop_bet, small_flop_bet, tiny_flop_bet = True, True, False, False
        elif continue_cost > pot_size * self.flop_aggression[3]:
            high_flop_bet, medium_flop_bet, small_flop_bet, tiny_flop_bet = True, True, True, False
        else:
            high_flop_bet, medium_flop_bet, small_flop_bet, tiny_flop_bet = True, True, True, True
            
        if continue_cost > pot_size * self.turn_aggression[0]:
            high_turn_bet, medium_turn_bet, small_turn_bet, tiny_turn_bet = False, False, False, False
        elif continue_cost > pot_size * self.turn_aggression[1]:
            high_turn_bet, medium_turn_bet, small_turn_bet, tiny_turn_bet = True, False, False, False
        elif continue_cost > pot_size * self.turn_aggression[2]:
            high_turn_bet, medium_turn_bet, small_turn_bet, tiny_turn_bet = True, True, False, False
        elif continue_cost > pot_size * self.turn_aggression[3]:
            high_turn_bet, medium_turn_bet, small_turn_bet, tiny_turn_bet = True, True, True, False
        else:
            high_turn_bet, medium_turn_bet, small_turn_bet, tiny_turn_bet = True, True, True, True
            
        if continue_cost > pot_size * self.river_aggression[0]:
            high_river_bet, medium_river_bet, small_river_bet, tiny_river_bet = False, False, False, False
        elif continue_cost > pot_size * self.river_aggression[1]:
            high_river_bet, medium_river_bet, small_river_bet, tiny_river_bet = True, False, False, False
        elif continue_cost > pot_size * self.river_aggression[2]:
            high_river_bet, medium_river_bet, small_river_bet, tiny_river_bet = True, True, False, False
        elif continue_cost > pot_size * self.river_aggression[3]:
            high_river_bet, medium_river_bet, small_river_bet, tiny_river_bet = True, True, True, False
        else:
            high_river_bet, medium_river_bet, small_river_bet, tiny_river_bet = True, True, True, True
    
        if BidAction in legal_actions:
            if self.all_in:
                # all in pre-flop, need to bid 0
                return BidAction(0)
            
            prob_win_w_auction, prob_win_wo_auction = simulate_auction(my_cards, board_cards,200)
            diff = round(prob_win_w_auction - prob_win_wo_auction, 4)
                # self.diffs.append(diff)
            if self.opp_bids_num < 3:
                opp_bid_avg = 75
                opp_bid_stdv = 25
            else:
                opp_bid_avg = self.opp_bid_avg
                opp_bid_stdv = self.opp_bid_var**(1/2)
            bid = int(opp_bid_avg + opp_bid_stdv * 1.96 * (diff-0.3) * 10) - 10 - int(opp_bid_stdv)
            return BidAction(min(150, my_stack, max(bid, 2*pot_size)))
        
        if self.all_in:
            return CheckAction()

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
            can_raise = True
        else:
            min_raise, max_raise = 0, 0
            can_raise = False

        if street == 0:
            if continue_cost > BIG_BLIND - SMALL_BLIND:
                self.opp_pre_flop_bet = continue_cost / pot_size
            if CheckAction in legal_actions:
                # opponent calls as small bind
                if self.total_percentage > 0.54 and can_raise:
                    return RaiseAction(int(max(min_raise, min(1.38 * pot_size, max_raise))))
                return CheckAction()
            self.high_cards_or_pair_likely = not(continue_cost == BIG_BLIND - SMALL_BLIND)
            if self.total_percentage * (continue_cost + pot_size) - (1-self.total_percentage) * continue_cost < 0 and self.total_percentage < 0.52:
                return FoldAction()
            if continue_cost == BIG_BLIND - SMALL_BLIND:
                # small blind
                if self.total_percentage > 0.52 and can_raise:
                    return RaiseAction(int(max(min_raise, min(1.27 * pot_size, max_raise))))
                return CallAction()
            # opp raised
            necessary_pct = 0.54 + pot_size/100
            if self.total_percentage > necessary_pct and can_raise:
                return RaiseAction(int(max(min_raise, min(necessary_pct/(1-necessary_pct) * pot_size, max_raise))))
            return CallAction()
        
        high_hand_dict = {8: "Straight Flush", 7: "Quads", 6: "Full House", 5: "Flush", 4: "Straight", 3: "Trips", 2: "Two Pair", 1: "Pair", 0: "High Card"}
        
        opp_auction = opp_bid >= my_bid
        if opp_auction:
            opp_hand_size = 3
        else:
            opp_hand_size = 2
        
        if self.street_num < street: # new card dealt
        
            if street == 3:
                if opp_bid != 0:
                    self.opp_bids.append(opp_bid)
                    if len(self.opp_bids) > 15:
                        self.opp_bids.pop(0)
                    self.opp_bids_num += 1
                    self.opp_bids_sum += opp_bid
                    self.my_bids.append(my_bid)
        
            self.board_ranks = []
            self.board_suits = []
            
            self.my_hand_ranks = []
            self.my_hand_suits = []
            
            # analyzing our hand
            
            self.street_num = street
            our_total_cards = my_cards + board_cards
            
            for card in my_cards: # find hand high card
                rank, card_suit_index = ranks_dict[card[0]], suits_dict[card[1]]
                self.my_hand_ranks.append(rank)
                self.my_hand_suits.append(card_suit_index)
                if rank > self.my_high_card:
                    self.my_high_card = rank
                    
            for card in board_cards:
                rank, card_suit_index = ranks_dict[card[0]], suits_dict[card[1]]
                self.board_ranks.append(rank)
                self.board_suits.append(card_suit_index)
                if rank > self.board_high_card:
                    self.board_high_card = rank
                    
            self.sorted_board_ranks = sorted(self.board_ranks)
            
            our_pairs = check_for_pair(our_total_cards)
            pairs = set()
            trips = set()
            quads = set()
            for rank, num in our_pairs.items():
                if num == 4:
                    quads.add(rank)
                if num == 3:
                    trips.add(rank)
                if num == 2:
                    pairs.add(rank)
                    
            if quads: # quads
                self.quads = True
                self.quads_rank = max(quads)
                print(self.quads_rank, "quads on street", street)
                
            elif len(trips) > 1 or trips and pairs: # full house
                self.full_house = True
                if len(trips) > 1 and pairs:
                    self.full_house_ranks = max(trips), max(min(trips), max(pairs))
                elif pairs:
                    self.full_house_ranks = max(trips), max(pairs)
                else:
                    self.full_house_ranks = max(trips), min(trips)
                print(self.full_house_ranks, "full house on street", street)
                    
            elif trips: # trips
                self.trips = True
                self.trips_rank = max(trips)
                print(self.trips_rank, "trips on street", street)
                
            elif len(pairs) > 1: # two pair
                self.two_pair = True
                high_pair = max(pairs)
                pairs.remove(max(pairs))
                low_pair = max(pairs)
                self.two_pair_ranks = high_pair, low_pair
                print(self.two_pair_ranks, "two pair on street", street)
                
            elif pairs: # pair
                self.pair = True
                self.pair_rank = max(pairs)
                print(self.pair_rank, "pair on street", street)
             
                    
            our_flush = check_for_flush(our_total_cards, street)
            if our_flush:
                for suit_index, cards_in in our_flush.items():
                    if len(cards_in) >= 5: # full flush
                        print("Flush on street", street)
                        self.flush = True
                        self.flush_suit = suit_index
                        self.my_flush, self.board_flush = set(), set()
                        for card in our_total_cards:
                            rank, card_suit_index = ranks_dict[card[0]], suits_dict[card[1]]
                            if card_suit_index == suit_index:
                                if card in my_cards:
                                    self.my_flush.add(rank)
                                else:
                                    self.board_flush.add(rank)
                        self.my_num_in_suit = 5 - len(self.board_flush) # number of cards in suit we have necessary for flush
                        if self.my_flush:
                            self.my_flush_high = max(self.my_flush)
                                
                        
                    elif len(cards_in) == 4: # four in a suit
                        print("Flush draw on street", street)
                        self.flush_draw = True
                        self.flush_suit = suit_index
                        self.my_flush, self.board_flush = set(), set()
                        for card in our_total_cards:
                            rank, card_suit_index = ranks_dict[card[0]], suits_dict[card[1]]
                            if card_suit_index == suit_index:
                                if card in my_cards:
                                    self.my_flush.add(rank)
                                else:
                                    self.board_flush.add(rank)
                        if self.my_flush:
                            self.my_num_in_suit = len(self.my_flush) # number in our hand for suit
                            self.my_flush_high = max(self.my_flush)
                        
                    else: # three in a suit
                        self.double_flush_draw = True
                        print("Flush double draw on street", street)
                        if len(our_flush) == 2: # three in a suit for two suits
                            self.flush_suit = []
                            for suit_index in our_flush:
                                self.flush_suit.append(suit_index)
                            first_suit_index = self.flush_suit[0]
                            self.my_flush = [set(), set()]
                            self.board_flush = [set(), set()]
                            self.my_num_in_suit = [0, 0]
                            for card in our_total_cards:
                                rank, card_suit_index = ranks_dict[card[0]], suits_dict[card[1]]
                                if card_suit_index == first_suit_index:
                                    if card in my_cards:
                                        self.my_flush[0].add(rank)
                                    else:
                                        self.board_flush[0].add(rank)
                                else:
                                    if card in my_cards:
                                        self.my_flush[1].add(rank)
                                    else:
                                        self.board_flush[1].add(rank)
                            self.my_flush_high = [-1, -1]
                            if self.my_flush[0]:
                                self.my_flush_high[0] = max(self.my_flush[0])
                                self.my_num_in_suit[0] = len(self.my_flush[0]) # number in our hand for first suit
                            if self.my_flush[1]:
                                self.my_flush_high[1] = max(self.my_flush[1])
                                self.my_num_in_suit[1] = len(self.my_flush[1]) # number in our hand for second suit
                             
                        else: # three in a suit for one suit
                            self.flush_suit = suit_index
                            self.my_flush, self.board_flush = set(), set()
                            for card in our_total_cards:
                                rank, card_suit_index = ranks_dict[card[0]], suits_dict[card[1]]
                                if card_suit_index == suit_index:
                                    if card in my_cards:
                                        self.my_flush.add(rank)
                                    else:
                                        self.board_flush.add(rank)
                            if self.my_flush:
                                self.my_num_in_suit = len(self.my_flush) # number in our hand for suit
                                self.my_flush_high = max(self.my_flush)
                        
                        
            our_straight = check_for_straight(our_total_cards, street)
            if our_straight:
                for high_card, (cards_in, cards_out) in our_straight.items():
                    if len(cards_in) == 5: # full straight
                        if self.flush:
                            if cards_in.issubset(self.my_flush.union(self.board_flush)):
                                self.straight_flush = True
                                self.straight_flush_high = high_card
                                print(high_card, "high straight flush on street", street)
                        else:
                            print(high_card, "high straight on street", street)
                            self.straight = True
                            if high_card > self.straight_high:
                                self.straight_high = high_card
                                self.my_straight, self.board_straight = set(), set()
                                for card in our_total_cards:
                                    rank = ranks_dict[card[0]]
                                    if rank in cards_in:
                                        if card in my_cards:
                                            self.my_straight.add(rank)
                                        else:
                                            self.board_straight.add(rank)
                                if self.my_straight:
                                    self.my_num_in_straight = len(self.my_straight)
                                    self.my_straight_high = max(self.my_straight)
                                        
                    elif len(cards_in) == 4 and not self.straight: # four in straight with no full straight
                        print(high_card, "high straight draw on street", street)
                        if not self.straight_draw: # clear extra cards from double straight draw
                            self.my_straight, self.board_straight = set(), set()
                        self.straight_draw = True
                        self.draw_needed.add(*cards_out)
                        for card in our_total_cards:
                            rank = ranks_dict[card[0]]
                            if rank in cards_in:
                                if card in my_cards:
                                    self.my_straight.add(rank)
                                else:
                                    self.board_straight.add(rank)
                        if self.my_straight:
                            self.my_num_in_straight = len(self.my_straight)
                            self.my_straight_high = max(self.my_straight)
                        
                    elif not self.straight and not self.straight_draw: # three in a straight with no straight draw or full straight
                        print(high_card, "high straight double draw on street", street)
                        self.double_straight_draw = True
                        self.double_draw_needed.add(tuple(cards_out))
                        num_in = 0
                        for card in our_total_cards:
                            rank = ranks_dict[card[0]]
                            if rank in cards_in:
                                if card in my_cards:
                                    self.my_straight.add(rank)
                                    num_in += 1
                                else:
                                    self.board_straight.add(rank)
                        if self.my_straight:
                            self.my_num_in_straight = len(self.my_straight)
                            self.my_straight_high = max(self.my_straight)
                            
                            
            if self.straight_flush:
                self.high_hand = 8
                self.high_hand_numbers = self.straight_flush_high
            elif self.quads:
                self.high_hand = 7
                self.high_hand_numbers = self.quads_rank
            elif self.full_house:
                self.high_hand = 6
                self.high_hand_numbers = self.full_house_ranks
            elif self.flush:
                self.high_hand = 5
                self.high_hand_numbers = self.my_flush_high
            elif self.straight:
                self.high_hand = 4
                self.high_hand_numbers = self.straight_high
            elif self.trips:
                self.high_hand = 3
                self.high_hand_numbers = self.trips_rank
                self.high_hand = 3
            elif self.two_pair:
                self.high_hand = 2
                self.high_hand_numbers = self.two_pair_ranks
            elif self.pair:
                self.high_hand = 1
                self.high_hand_numbers = self.pair_rank
            else:
                self.high_hand_numbers = self.my_high_card
                
            if street == 5:
                print("Final Hand:", self.high_hand_numbers, high_hand_dict[self.high_hand])
                
                
            # analyzing their hand
            
            self.opp_outs = {} # ints representing high hands as keys and important rank(s) as values
            
            board_pairs = check_for_pair(board_cards)
            pairs = set()
            trips = set()
            quads = set()
            for rank, num in board_pairs.items():
                if num == 4:
                    quads.add(rank)
                if num == 3:
                    trips.add(rank)
                if num == 2:
                    pairs.add(rank)
                    
            if quads: # quads
                self.board_quads = True
                self.board_quads_rank = max(quads)
                self.opp_outs[7] = self.board_quads_rank
                self.on_board_hands.add(7)
                
            elif len(trips) > 1 or trips and pairs: # full house
                self.board_full_house = True
                if len(trips) > 1 and pairs:
                    self.board_full_house_ranks = max(trips), max(min(trips), max(pairs))
                elif pairs:
                    self.board_full_house_ranks = max(trips), max(pairs)
                else:
                    self.board_full_house_ranks = max(trips), min(trips)
                self.opp_outs[6] = self.board_full_house_ranks
                self.opp_outs[8] = self.board_full_house_ranks
                self.on_board_hands.add(6)
                    
            elif trips: # trips
                self.board_trips = True
                self.board_trips_rank = max(trips)
                self.opp_outs[8] = self.board_trips_rank
                self.opp_outs[6] = self.board_trips_rank, None
                self.on_board_hands.add(3)
                
            elif len(pairs) > 1: # two pair
                self.board_two_pair = True
                high_pair = max(pairs)
                pairs.remove(max(pairs))
                low_pair = max(pairs)
                self.board_two_pair_ranks = high_pair, low_pair
                self.opp_outs[6] = self.board_two_pair_ranks
                self.opp_outs[7] = self.board_two_pair_ranks
                self.on_board_hands.add(2)
                
                
            elif pairs: # pair
                self.board_pair = True
                self.board_pair_rank = max(pairs)
                self.opp_outs[2] = self.board_pair_rank, None
                self.opp_outs[3] = self.board_pair_rank
                self.opp_outs[6] = self.board_pair_rank, None
                self.opp_outs[7] = self.board_pair_rank
                self.on_board_hands.add(1)
                
            if street == 5:
                need = 5 - opp_hand_size
            else:
                need = 2
                
            board_flush = check_for_flush(board_cards, need)
            if board_flush:
                for suit_index, cards_in in board_flush.items():
                    if len(cards_in) == 5: # full flush on board
                        self.board_flush_need_0 = True
                        self.on_board_hands.add(5)
                        self.board_flush_suit = suit_index
                        self.board_flush_max = max(cards_in)
                        self.board_flush_min= min(cards_in)
                        
                    elif len(cards_in) == 4: # four in a suit on board
                        self.board_flush_need_1 = True
                        self.board_flush_suit = suit_index
                        self.board_flush_max = max(cards_in)
                        self.board_flush_min= min(cards_in)
                        
                    elif len(cards_in) == 3: # three in a suit on board
                        self.board_flush_need_2 = True
                        self.flush_suit = suit_index
                        self.board_flush_max = max(cards_in)
                        self.board_flush_min= min(cards_in)
                            
                    else: # two in a suit on board
                        self.board_flush_need_3 = True
                        self.board_flush_suit = suit_index
                        self.board_flush_max = max(cards_in)
                        self.board_flush_min= min(cards_in)
                self.opp_outs[5] = self.board_flush_suit
                        
           
            board_straight = check_for_straight(board_cards, need)
            if board_straight:
                for high_card, (cards_in, cards_out) in board_straight.items():
                    if len(cards_in) == 5: # full straight on board
                        if self.board_flush:
                            self.board_straight_flush = True
                            self.on_board_hands.add(9)
                            self.board_straight_flush_max = self.board_flush_max
                            self.opp_outs[8] = self.board_flush_suit
                        else:
                            self.board_straight = True
                            self.board_straight_high = high_card # easy to win if higher card
                            self.on_board_hands.add(4)
                            self.opp_outs[4] = high_card, high_card + 1, high_card + 2
                                        
                    elif len(cards_in) == 4 and not self.board_straight_need_0: # four in straight on board
                        if not self.board_straight_need_1: # clear needed from last turn
                            self.board_straight_needed = set()
                        self.board_straight_need_1 = True
                        self.board_straight_needed.add(*cards_out)
                        self.opp_outs[4] = self.board_straight_needed
                        
                    elif len(cards_in) == 3 and not self.board_straight_need_1 and not self.board_straight_need_0: # three in a straight on board
                        if not self.board_straight_need_2: # clear needed from last turn
                            self.board_straight_needed = set()
                        self.board_straight_need_2 = True
                        self.board_straight_needed.add(tuple(cards_out))
                        self.opp_outs[4] = self.board_straight_needed
                            
                    elif not self.board_straight_need_2 and not self.board_straight_need_1 and not self.board_straight_need_0: # two in a straight on board
                        self.board_straight_need_3 = True
                        self.board_straight_needed.add(tuple(cards_out))
                        self.opp_outs[4] = self.board_straight_needed
                        
            print()
            print("Opp outs on street", street, self.opp_outs)
            print()





################# FLOP #########################



                
        
        if street == 3: # flop post-auction
        
            self.flop_cards = board_cards
        
            if continue_cost >= max(5, pot_size/25): # check whether opponent is bluffing after showdown
                self.opp_flop_bet = continue_cost / pot_size
        
            
            if continue_cost == 0 and big_blind:
                
                print("Start betting on flop")
                
                # starting betting
                
                if pot_size > 120:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(35, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(20, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(12, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CheckAction(), CheckAction(), CheckAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(20, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(12, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(8, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CheckAction(), CheckAction(), CheckAction()
                
                if self.high_hand == 8:
                    return medium_raise
                
                if self.high_hand == 7:
                    if self.board_trips:
                        return small_raise # sand bag
                    return medium_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return small_raise # sand bag
                        return medium_raise
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return small_raise # sand bag
                        
                    return medium_raise
                       
                if self.high_hand == 5:
                    if self.board_flush_need_1:
                        if self.my_flush_high >= 9 or self.my_flush_high >= 7 and not self.high_cards_or_pair_likely:
                            return small_raise # sand bag
                        return medium_raise
                    
                    if self.board_flush_need_2:
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 4:
                    if self.board_flush_need_2 and self.flush_draw:
                        return small_raise # sand bag
                    return medium_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        return CheckAction()
                    if self.board_flush_need_2 or self.board_straight_need_2:
                        return high_raise
                    if self.board_pair:
                        return small_raise
                    return medium_raise
                
                if self.flush_draw:
                    if self.board_flush_need_2:
                        return CheckAction()
                    return small_raise
                    
                if self.straight_draw:
                    if self.board_straight_need_2:
                        return CheckAction()
                    if len(self.draw_needed) == 2:
                        return medium_raise
                    return CheckAction()
                
                if self.high_hand == 2:
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank:
                            return small_raise
                        return CheckAction()
                    if self.board_flush_need_2 or self.board_straight_need_2:
                        return small_raise
                    return medium_raise
                    
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_2 or self.board_straight_need_2:
                        return CheckAction()
                    if self.board_pair == self.sorted_board_ranks[0]:
                        return medium_raise
                    return small_raise
                    
                return CheckAction()
                
            if my_pip == 0 and continue_cost <= max(5, pot_size/25):
                
                # opponent checks (or makes small bet)
                
                print("Opponent checks on flop")
                
                if continue_cost == 0:
                    action = CheckAction()
                else:
                    action = CallAction()
                    
                if pot_size > 120:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(28, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(15, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(10, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(18, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(11, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(6, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                
                if self.high_hand == 8:
                    return small_raise
                
                if self.high_hand == 7:
                    return small_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return small_raise
                        return high_raise
                    return small_raise
                       
                if self.high_hand == 5:
                    return small_raise
                
                if self.high_hand == 4:
                    if self.board_flush_need_2:
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if self.my_high_card >= 9 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return medium_raise
                    if self.board_flush_need_2 or self.board_straight_need_2:
                        return medium_raise
                    if self.board_pair:
                        return medium_raise
                    return small_raise
                
                if self.flush_draw and self.straight_draw:
                    return medium_raise
                
                if self.flush_draw:
                    if self.board_flush_need_2:
                        return action
                    return small_raise
                    
                if self.straight_draw:
                    if self.board_straight_need_2 or self.board_flush_need_2:
                        return action
                    return small_raise
                
                if self.high_hand == 2:
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank:
                            return small_raise
                        return action
                    return small_raise
                    
                if self.high_hand == 1:
                    return small_raise
                    
                return action
            
            if continue_cost < 5 or tiny_flop_bet:
                action = CallAction()
            else:
                action = FoldAction()
            
            if not big_blind and continue_cost >= min(5,pot_size/25):
                ### Opponent bets
                
                print("Opponent bet on flop")
                  
                if continue_cost == 0:
                    action = CheckAction()
                else:
                    action = FoldAction()

                if pot_size > 120:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(28, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(15, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(10, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(18, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(11, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(6, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                
                if self.high_hand == 8:
                    return small_raise
                
                if self.high_hand == 7:
                    return small_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return small_raise
                        return high_raise
                    return small_raise
                       
                if self.high_hand == 5:
                    return small_raise
                
                if self.high_hand == 4:
                    if self.board_flush_need_2:
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if self.my_high_card >= 9 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return medium_raise
                    if self.board_flush_need_2 or self.board_straight_need_2:
                        return medium_raise
                    if self.board_pair:
                        return medium_raise
                    return small_raise
                
                if self.flush_draw and self.straight_draw:
                    return medium_raise
                
                if self.flush_draw:
                    if self.board_flush_need_2:
                        if self.my_flush_high >= 10 or self.my_flush_high >= 8 and not self.high_cards_or_pair_likely:
                            return CallAction()
                        return action
                    return small_raise
                    
                if self.straight_draw:
                    if self.board_flush_need_2 and not medium_flop_bet:
                        return action
                    if self.board_straight_need_2:
                        if self.my_straight_high > self.board_straight_high or medium_flop_bet:
                            return CallAction()
                        return action
                    return small_raise
                
                if self.high_hand == 2:
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank:
                            return small_raise
                        if medium_flop_bet and self.two_pair_ranks[1] >= self.sorted_board_ranks[2]:
                            return CallAction()
                        return action
                    return small_raise
                    
                if self.high_hand == 1:
                    if self.board_pair:
                        return CheckAction() if CheckAction in legal_actions else FoldAction()
                    if pot_size > 100:
                        if CallAction() in legal_actions:
                            return CallAction()
                        elif CheckAction() in legal_actions:
                            return CheckAction()
                    if self.pair_rank >= self.sorted_board_ranks[0]:
                        return high_raise
                    if medium_flop_bet and self.pair_rank >= self.sorted_board_ranks[2] or small_flop_bet: 
                        return CallAction()
                    return action
                    
                return action
                
            if my_pip != 0:
                
                print("Opponent raises on flop")
                
                # we bet and opponent raised
                
                if pot_size > 120:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(120, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(30, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(20, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(80, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(20, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(15, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                
                if self.high_hand == 8:
                    return high_raise
                
                if self.high_hand == 7:
                    high_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[0] > self.board_trips_rank:
                            return high_raise
                        if self.full_house_ranks[1] > self.sorted_board_ranks[3] and self.board_trips_rank == self.sorted_board_ranks[3] or self.full_house_ranks[1] > self.sorted_board_ranks[0]:
                            return medium_raise
                        return CallAction()
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return medium_raise
                        return CallAction()
                    return medium_raise
                       
                if self.high_hand == 5:
                    
                    if self.board_flush_need_2 and (self.my_flush_high >= 8 or self.my_flush_high >= 6 and not self.high_cards_or_pair_likely):
                        return medium_raise
                    
                    if self.board_flush_need_2:
                        return CallAction()
                    
                    return small_raise
                
                if self.high_hand == 4:
                    
                    if self.board_flush_need_2:
                        if medium_flop_bet:
                            return CallAction()
                        return action
                        
                    if self.board_trips: # need auction
                        return medium_raise
                    
                    if self.board_straight_need_2:
                        if self.my_straight_high > self.board_straight_high:
                            return medium_raise
                        return small_raise
                    
                    if self.board_pair:
                        return medium_raise
                    
                    return small_raise
                
                if self.high_hand == 3:
                    if self.flush_draw or self.straight_draw:
                        return small_raise
                    if self.board_trips:
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if (self.board_flush_need_2 or self.board_straight_need_2):
                        if medium_flop_bet:
                            return CallAction()
                        return action
                    if self.board_pair:
                        return CallAction()
                    
                if self.flush_draw:
                    if self.board_flush_need_2:
                        if medium_flop_bet or high_flop_bet and self.my_flush_high >= 10:
                            return CallAction()
                    if self.board_trips: # need auction
                        if high_flop_bet:
                            return CallAction()
                        return action
                    return CallAction()
                    
                if self.straight_draw:
                    if len(self.draw_needed) == 2:
                        if self.board_straight_need_2 or self.board_flush_need_2:
                            if high_flop_bet:
                                return action
                            if self.my_straight_high > self.board_straight_high and medium_flop_bet:
                                return CallAction()
                    if small_flop_bet:
                        return CallAction()
                    return action
                
                if self.high_hand == 2:
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank and medium_flop_bet:
                            return CallAction()
                    if self.board_flush_need_2 or self.board_flush_need_2 :
                        if small_flop_bet:
                            return CallAction()
                        return action
                    if medium_flop_bet:
                        return CallAction()
                
                
                    
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_2 or self.board_straight_need_2:
                        return action
                    if self.pair_rank == self.sorted_board_ranks[0]:
                        return CallAction()
                    if small_flop_bet or self.pair_rank == self.sorted_board_ranks[1] and medium_flop_bet:
                        return CallAction()
                    return action
                    
                return action
            
            # opponent bet
            
            print("Opponent bet on flop")
            
            if pot_size > 120:
                if can_raise:
                    high_raise = RaiseAction(max(min_raise,min(150, max_raise)))
                    medium_raise = RaiseAction(max(min_raise,min(60, max_raise)))
                    small_raise = RaiseAction(max(min_raise, min(30, max_raise)))
                else:
                    high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
            else:
                if can_raise:
                    high_raise = RaiseAction(max(min_raise,min(80, max_raise)))
                    medium_raise = RaiseAction(max(min_raise,min(40, max_raise)))
                    small_raise = RaiseAction(max(min_raise, min(20, max_raise)))
                else:
                    high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
            
            if self.high_hand == 8:
                return high_raise
            
            if self.high_hand == 7:
                return high_raise
            
            if self.high_hand == 6:
                if self.board_trips:
                    if self.full_house_ranks[0] > self.board_trips_rank:
                        return high_raise
                    if self.full_house_ranks[1] > self.sorted_board_ranks[3] and self.board_trips_rank == self.sorted_board_ranks[3] or self.full_house_ranks[1] > self.sorted_board_ranks[0]:
                        return medium_raise
                    return CallAction()
                return medium_raise
                   
            if self.high_hand == 5:
        
                if self.board_flush_need_2 and (self.my_flush_high >= 7 or self.my_flush_high >= 5 and not self.high_cards_or_pair_likely):
                    return medium_raise
                
                if self.board_flush_need_2:
                    return CallAction()
                
                return small_raise
            
            if self.high_hand == 4:
                
                if self.board_flush_need_2:
                    if medium_flop_bet:
                        return CallAction()
                    return action
                    
                if self.board_trips: # need auction
                    return medium_raise
                
                if self.board_two_pair: # need auction
                    return medium_raise
                
                if self.board_straight_need_2:
                    if self.my_straight_high > self.board_straight_high:
                        return medium_raise
                    return small_raise
                
                if self.board_pair:
                    return medium_raise
                
                return small_raise
            
            if self.high_hand == 3:
                if self.flush_draw or self.straight_draw:
                    return small_raise
                if self.board_trips:
                    return action
                if self.board_flush_need_2 or self.board_straight_need_2:
                    if medium_flop_bet:
                        return CallAction()
                    return action
                if self.board_pair:
                    return CallAction()
                
            if self.flush_draw:
                if self.board_flush_need_2:
                    if self.my_flush_high >= 10 or self.my_flush_high >= 8 and not self.high_cards_or_pair_likely:
                        return CallAction()
                    return action
                if self.board_pair and high_flop_bet:
                    return action
                return CallAction()
                
            if self.straight_draw:
                if self.board_flush_need_2:
                    if medium_flop_bet:
                        return CallAction()
                    return action
                if self.board_straight_need_2:
                    if self.my_straight_high > self.board_straight_high or medium_flop_bet:
                        return CallAction()
                    if len(self.draw_needed) == 2:
                        return CallAction()
                    return action
                if self.board_pair:
                    if len(self.draw_needed) == 2:
                        return CallAction()
                    if medium_flop_bet:
                        return CallAction()
                    return action
                if high_flop_bet:
                    return CallAction()
                return action
            
            if self.high_hand == 2:
                if self.board_two_pair:
                    if self.my_high_card == 12 and medium_flop_bet:
                        return CallAction()
                    return action
                if self.board_flush_need_1 or self.board_straight_need_1:
                    return action
                if self.board_pair:
                    if self.two_pair_ranks[0] > self.board_pair_rank and medium_flop_bet:
                        return CallAction()
                    return action
                if self.board_flush_need_2 or self.board_flush_need_2 and medium_flop_bet:
                    return CallAction()
                if self.two_pair_ranks[0] >= self.sorted_board_ranks[0] or self.two_pair_ranks[0] >= self.sorted_board_ranks[2] and medium_flop_bet:
                    return CallAction()
                if small_flop_bet:
                    return CallAction()
                return action
                
            if self.high_hand == 1:
                if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1 or self.board_flush_need_2 or self.board_straight_need_2:
                    return action
                if self.pair_rank == self.sorted_board_ranks[0]:
                    return CallAction()
                return action
                
            return action
        






###################### TURN ##########################



        
        if street == 4: # turn
        
            self.turn_cards = board_cards
        
            if continue_cost >= 5 and continue_cost >= pot_size/2: # check whether opponent is bluffing after showdown
                self.opp_turn_bet = continue_cost / pot_size
            
            if continue_cost == 0 and big_blind:
                # starting betting
                print("Start betting on turn")
                
                action = CheckAction()
                if pot_size > 160:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise, min(50, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(25, max_raise)))
                        small_raise = RaiseAction(max(min_raise,min(15, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(20, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(12, max_raise)))
                        small_raise = RaiseAction(max(min_raise,min(7, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                
                if self.high_hand == 8:
                    return small_raise
                
                if self.high_hand == 7:
                    if self.board_quads:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return small_raise
                        return medium_raise
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return small_raise
                       
                if self.high_hand == 5:
                    if self.board_flush_need_1:
                        if self.my_flush_high >= 9 or self.my_flush_high >= 7 and not self.high_cards_or_pair_likely:
                            return high_raise
                        
                    if self.board_trips: # need auction
                        return small_raise
                    
                    if self.board_two_pair: # need auction
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 4:
                    if self.board_flush_need_1:
                        return small_raise
                    
                    if self.board_flush_need_2:
                        return medium_raise
                    
                    if self.board_straight_need_1:
                        if self.my_straight_high > self.board_straight_high and pot_size > 200:
                            return high_raise
                        return medium_raise
                        
                    if self.board_trips: # need auction
                        return high_raise
                    
                    if self.board_two_pair: # need auction
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return medium_raise
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return CheckAction()
                    if self.board_flush_need_2 or self.board_straight_need_2:
                        return small_raise
                    if self.board_pair:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 2:
                    if self.board_two_pair:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return medium_raise
                        return CheckAction()
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return CheckAction()
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank:
                            return small_raise
                        return CheckAction()
                    if self.board_flush_need_2 or self.board_flush_need_2:
                        return small_raise
                    return medium_raise
                
                if self.flush_draw and self.straight_draw:
                    return small_raise
                
                if self.flush_draw:
                    if self.board_flush_need_1:
                        return CheckAction()
                    if self.my_flush_high >= 10:
                        return small_raise
                    return CheckAction()
                    
                if self.straight_draw:
                    if len(self.draw_needed) == 2 and self.my_straight_high > self.board_straight_high and not self.board_straight_need_1:
                        return small_raise
                    return CheckAction()
                    
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1 or self.board_flush_need_2 or self.board_straight_need_2:
                        return CheckAction()
                    if self.board_pair == max(self.board_ranks):
                        return small_raise
                    return CheckAction()
                    
                return CheckAction()
                
            if my_pip == 0 and continue_cost <= max(5, pot_size/25):
                
                print("Opponent checks on turn")
                
                # opponent checks (or makes small bet)
                if continue_cost == 0:
                    action = CheckAction()
                else:
                    action = CallAction()
                    
                if pot_size > 160:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(40, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(20, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(10, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(16, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(10, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(5, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                
                if self.high_hand == 8:
                    return small_raise
                
                if self.high_hand == 7:
                    if self.board_quads:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return small_raise
                    if self.board_two_pair:
                        if self.full_house_ranks[0] == self.board_two_pair_ranks[0]:
                            return high_raise
                        return small_raise
                            
                    return medium_raise
                        
                if self.board_two_pair:
                    if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                        return small_raise
                       
                if self.high_hand == 5:
                    
                    if self.board_flush_need_1:
                        if self.my_flush_high >= 9 or self.my_flush_high >= 7 and not self.high_cards_or_pair_likely:
                            return high_raise
                        return small_raise
                        
                    if self.board_trips: # need auction
                        return small_raise
                    
                    if self.board_two_pair: # need auction
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 4:
                    
                    if self.board_flush_need_1:
                        return small_raise
                    
                    if self.board_flush_need_2:
                        return medium_raise
                    
                    if self.board_straight_need_1:
                        if self.my_straight_high > self.board_straight_high and pot_size > 200:
                            return high_raise
                        return medium_raise
                        
                    if self.board_trips: # need auction
                        return high_raise
                    
                    if self.board_two_pair: # need auction
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return small_raise
                    
                    return medium_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return medium_raise
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.board_flush_need_2 or self.board_straight_need_2:
                        return small_raise
                    if self.board_pair:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 2:
                    if self.board_two_pair:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return medium_raise
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank:
                            return small_raise
                        return action
                    if self.board_flush_need_2 or self.board_flush_need_2:
                        return small_raise
                    return medium_raise
                
                if self.flush_draw and self.straight_draw:
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.my_flush_high >= 10 or len(self.draw_needed) >= 2 and self.my_straight_high > self.board_straight_high:
                        return small_raise
                    return action
                
                if self.flush_draw:
                    if self.board_flush_need_1:
                        return CheckAction()
                    if self.my_flush_high >= 10:
                        return small_raise
                    return CheckAction()
                    
                if self.straight_draw:
                    if len(self.draw_needed) >= 2 and self.my_straight_high > self.board_straight_high and not self.board_straight_need_1:
                        return small_raise
                    return CheckAction()
                    
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1 or self.board_flush_need_2 or self.board_straight_need_2:
                        return action
                    if self.board_pair == max(self.board_ranks):
                        return small_raise
                    return action
                    
                return action
            
            if continue_cost < 5 or tiny_turn_bet:
                action = CallAction()
            else:
                action = FoldAction()
            
            if big_blind and my_pip == 0:
                
                print("Opponent bet on turn after we checked")
                
                # we checked and opponent bet
                
                if pot_size > 160:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise, min(75, max_raise)))
                        medium_raise = RaiseAction(max(min_raise, min(50, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(25, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise, min(40, max_raise)))
                        medium_raise = RaiseAction(max(min_raise, min(30, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(15, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                
                if self.high_hand >= 4:
                    return high_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if (self.board_flush_need_2 or self.board_straight_need_2):
                        if medium_turn_bet:
                            return CallAction()
                        return action
                    if self.board_pair:
                        if self.my_high_card >= 10 or self.my_high_card >= 8 and not self.high_cards_or_pair_likely:
                            return small_raise
                    return CallAction()
                
                if self.high_hand == 2:
                    if self.board_two_pair:
                        if self.my_high_card == 12 and medium_turn_bet:
                            return CallAction()
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank and medium_turn_bet:
                            return CallAction()
                        return action
                    if self.board_flush_need_2 or self.board_flush_need_2 and medium_turn_bet:
                        return CallAction()
                    return action
                
                if self.flush_draw and self.straight_draw:
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        if small_turn_bet:
                            return CallAction()
                        return action
                    if medium_turn_bet:
                        return CallAction()
                    return action
                    
                if self.flush_draw:
                    if self.board_flush_need_1 or self.board_two_pair:
                        return action
                    if self.board_straight_need_1:
                        if small_turn_bet:
                            return CallAction()
                        return action
                    if medium_turn_bet:
                        return CallAction()
                    return action
                    
                if self.straight_draw:
                    if self.board_straight_need_1 or self.board_two_pair:
                        return action
                    if len(self.draw_needed) == 2:
                        return CallAction()
                    return action
                    
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1 or self.board_flush_need_2 or self.board_straight_need_2:
                        return action
                    if self.pair_rank == self.sorted_board_ranks[0]:
                        return CallAction()
                    return action
                    
                return action
                
            if my_pip != 0:
                
                # we bet and opponent raised
                
                print("Opponent raised on turn")
                
                if pot_size > 160:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise, min(120, max_raise)))
                        medium_raise = RaiseAction(max(min_raise, min(65, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(30, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise, min(80, max_raise)))
                        medium_raise = RaiseAction(max(min_raise, min(40, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(20, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                
                if self.high_hand == 8:
                    return high_raise
                
                if self.high_hand == 7:
                    if self.board_quads:
                        return CallAction()
                    return high_raise
                
                if self.high_hand == 6:
                    if self.board_trips:
                        if self.full_house_ranks[0] > self.board_trips_rank:
                            return high_raise
                        if self.full_house_ranks[1] > self.sorted_board_ranks[3] and self.board_trips_rank == self.sorted_board_ranks[3] or self.full_house_ranks[1] > self.sorted_board_ranks[0]:
                            return medium_raise
                        return CallAction()
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return small_raise
                        return CallAction()
                    return medium_raise
                       
                if self.high_hand == 5:
                    
                    if self.board_flush_need_1:
                        if self.my_flush_high >= 10 or self.my_flush_high >= 8 and not self.high_cards_or_pair_likely:
                            return small_raise
                        if medium_turn_bet or self.my_flush_high >= 8 or self.my_flush_high >= 6 and not self.high_cards_or_pair_likely:
                            return CallAction()
                        return action
                        
                    if self.board_trips: # need auction
                        return CallAction()
                    
                    if self.board_two_pair: # need auction
                        return CallAction()
                    
                    if self.board_straight_need_1:
                        return medium_raise
                    
                    if self.board_flush_need_2 and (self.my_flush_high >= 7 or self.my_flush_high >= 5 and not self.high_cards_or_pair_likely):
                        return medium_raise
                    
                    if self.board_flush_need_2:
                        return CallAction()
                    
                    return small_raise
                
                if self.high_hand == 4:
                    
                    if self.board_flush_need_1:
                        return action
                    
                    if self.board_flush_need_2:
                        if medium_turn_bet:
                            return CallAction()
                        return action
                    
                    if self.board_straight_need_1:
                        if self.my_straight_high > self.board_straight_high:
                            return high_raise
                        return CallAction()
                        
                    if self.board_trips: # need auction
                        return medium_raise
                    
                    if self.board_two_pair: # need auction
                        return medium_raise
                    
                    if self.board_straight_need_2:
                        if self.my_straight_high > self.board_straight_high:
                            return medium_raise
                        return small_raise
                    
                    if self.board_pair:
                        return medium_raise
                    
                    return small_raise
                
                if self.high_hand == 3:
                    if self.flush_draw or self.straight_draw:
                        return small_raise
                    if self.board_trips:
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if (self.board_flush_need_2 or self.board_straight_need_2):
                        if medium_turn_bet:
                            return CallAction()
                        return action
                    if self.board_pair:
                        return CallAction()
                
                if self.high_hand == 2:
                    if self.board_two_pair:
                        if self.my_high_card == 12 and medium_turn_bet:
                            return CallAction()
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.board_pair:
                        if self.two_pair_ranks[0] > self.board_pair_rank and medium_turn_bet:
                            return CallAction()
                        return action
                    if self.board_flush_need_2 or self.board_flush_need_2 and medium_turn_bet:
                        return CallAction()
                    if small_turn_bet:
                        return CallAction()
                    return action
                
                if self.flush_draw and self.straight_draw:
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        if small_turn_bet:
                            return CallAction()
                        return action
                    if medium_turn_bet:
                        return CallAction()
                    return action
                
                if self.flush_draw:
                    if self.board_flush_need_1 or self.board_two_pair:
                        return action
                    if self.board_straight_need_1:
                        if small_turn_bet:
                            return CallAction()
                        return action
                    if self.board_trips: # need auction
                        return action
                    if self.board_two_pair:
                        return action
                    if medium_turn_bet:
                        return CallAction()
                    return action
                    
                if self.straight_draw:
                    if self.board_straight_need_1 or self.board_two_pair or self.board_flush_need_1 or self.board_trips:
                        return action
                    if len(self.draw_needed) == 2:
                        return small_raise
                    return CallAction()
                    
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1 or self.board_flush_need_2 or self.board_straight_need_2:
                        return action
                    if self.pair_rank == self.sorted_board_ranks[0]:
                        return CallAction()
                    return action
                    
                return action
            
            # opponent bet
            
            print("Opponent bet on turn")
            
            if pot_size > 160:
                if can_raise:
                    high_raise = RaiseAction(max(min_raise, min(140, max_raise)))
                    medium_raise = RaiseAction(max(min_raise, min(85, max_raise)))
                    small_raise = RaiseAction(max(min_raise, min(45, max_raise)))
                else:
                    high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
            else:
                if can_raise:
                    high_raise = RaiseAction(max(min_raise, min(100, max_raise)))
                    medium_raise = RaiseAction(max(min_raise, min(55, max_raise)))
                    small_raise = RaiseAction(max(min_raise, min(25, max_raise)))
                else:
                    high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
            
            if self.high_hand == 8:
                return high_raise
            
            if self.high_hand == 7:
                if self.board_quads:
                    return CallAction()
                return high_raise
            
            if self.high_hand == 6:
                if self.board_trips:
                    if self.full_house_ranks[0] > self.board_trips_rank:
                        return high_raise
                    if self.full_house_ranks[1] > self.sorted_board_ranks[3] and self.board_trips_rank == self.sorted_board_ranks[3] or self.full_house_ranks[1] > self.sorted_board_ranks[0]:
                        return medium_raise
                    return CallAction()
                    
                if self.board_two_pair:
                    if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                        return small_raise
                    return CallAction()
                return medium_raise
                   
            if self.high_hand == 5:
                
                if self.board_flush_need_1:
                    if self.my_flush_high >= 10 or self.my_flush_high >= 8 and not self.high_cards_or_pair_likely:
                        return small_raise
                    if medium_turn_bet or self.my_flush_high >= 8 or self.my_flush_high >= 6 and not self.high_cards_or_pair_likely:
                        return CallAction()
                    return action
                    
                if self.board_trips: # need auction
                    return CallAction()
                
                if self.board_two_pair: # need auction
                    return CallAction()
                
                if self.board_straight_need_1:
                    return medium_raise
                
                if self.board_flush_need_2 and (self.my_flush_high >= 7 or self.my_flush_high >= 5 and not self.high_cards_or_pair_likely):
                    return medium_raise
                
                if self.board_flush_need_2:
                    return CallAction()
                
                return small_raise
            
            if self.high_hand == 4:
                
                if self.board_flush_need_1:
                    return action
                
                if self.board_flush_need_2:
                    if medium_turn_bet:
                        return CallAction()
                    return action
                
                if self.board_straight_need_1:
                    if self.my_straight_high > self.board_straight_high:
                        return high_raise
                    return CallAction()
                    
                if self.board_trips: # need auction
                    return medium_raise
                
                if self.board_two_pair: # need auction
                    return medium_raise
                
                if self.board_straight_need_2:
                    if self.my_straight_high > self.board_straight_high:
                        return medium_raise
                    return small_raise
                
                if self.board_pair:
                    return medium_raise
                
                return small_raise
            
            if self.high_hand == 3:
                if self.flush_draw or self.straight_draw:
                    return small_raise
                if self.board_trips:
                    return action
                if self.board_flush_need_1 or self.board_straight_need_1:
                    return action
                if (self.board_flush_need_2 or self.board_straight_need_2):
                    if medium_turn_bet:
                        return CallAction()
                    return action
                if self.board_pair:
                    return CallAction()
            
            if self.high_hand == 2:
                if self.board_two_pair:
                    if self.my_high_card == 12 and medium_turn_bet:
                        return CallAction()
                    return action
                if self.board_flush_need_1 or self.board_straight_need_1:
                    return action
                if self.board_pair:
                    if self.two_pair_ranks[0] > self.board_pair_rank and medium_turn_bet:
                        return CallAction()
                    return action
                if self.board_flush_need_2 or self.board_flush_need_2 and medium_turn_bet:
                    return CallAction()
                if self.two_pair_ranks[0] >= self.sorted_board_ranks[0] or self.two_pair_ranks[2] >= self.sorted_board_ranks[0] and medium_turn_bet:
                    return CallAction()
                if small_turn_bet:
                    return CallAction()
                return action
            
            if self.flush_draw and self.straight_draw:
                if self.board_flush_need_1 or self.board_straight_need_1:
                    if medium_turn_bet:
                        return CallAction()
                    return action
                if small_turn_bet:
                    return CallAction()
                return action
            
            if self.flush_draw:
                if self.board_flush_need_1 or self.board_two_pair:
                    return action
                if self.board_straight_need_1:
                    if small_turn_bet:
                        return CallAction()
                    return action
                if self.board_trips: # need auction
                    return action
                if self.board_two_pair:
                    return action
                if medium_turn_bet:
                    return CallAction()
                return action
                
            if self.straight_draw:
                if self.board_straight_need_1 or self.board_two_pair or self.board_flush_need_1 or self.board_trips:
                    return action
                if len(self.draw_needed) == 2:
                    return small_raise
                return CallAction()
                
            if self.high_hand == 1:
                if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1 or (self.board_flush_need_2 or self.board_straight_need_2) and not small_turn_bet:
                    return action
                if self.pair_rank == self.sorted_board_ranks[0]:
                    return CallAction()
                if self.pair_rank == self.sorted_board_ranks[1] and medium_turn_bet:
                    return CallAction()
                
                
            return action
        




###################### RIVER ############################





        
        if street == 5: # river
        
            self.river_cards = board_cards
        
        
            if continue_cost >= max(5, pot_size/8): # check whether opponent is bluffing after showdown
                self.opp_river_bet = continue_cost / pot_size
                
            if continue_cost == 0 and big_blind:
                
                print("Start betting on river")
                
                if pot_size > 200:
                    if can_raise:
                        high_raise = RaiseAction(max_raise)
                        medium_raise = RaiseAction(max(min_raise,min(100, max_raise)))
                        small_raise = RaiseAction(max(min_raise,min(50, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CheckAction(), CheckAction(), CheckAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(100, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(50, max_raise)))
                        small_raise = RaiseAction(max(min_raise,min(20, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CheckAction(), CheckAction(), CheckAction()
                
                if self.high_hand == 8:
                    return high_raise
                
                if self.high_hand == 7:
                    if self.board_quads:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return high_raise
                        return small_raise
                    if self.board_full_house or self.board_trips:
                        return high_raise
                    return medium_raise
                
                if self.high_hand == 6:
                    if self.board_full_house:
                        if self.full_house_ranks == self.board_full_house_ranks:
                            if self.full_house_ranks[0] > self.full_house_ranks[1] and pot_size > 200: # no danger from opponent having three of a kind on the pair
                                return high_raise
                            return medium_raise
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return high_raise
                        return medium_raise
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return high_raise
                       
                if self.high_hand == 5:
                    if self.board_flush:
                        if self.my_flush_high > self.board_flush_min and self.my_flush_high > 4:
                            return high_raise
                        return small_raise
                    
                    if self.board_flush_need_1:
                        if self.my_flush_high > 9:
                            return high_raise
                        
                    if self.board_trips:
                        return small_raise
                    
                    if self.board_two_pair:
                        return small_raise
                    
                    if self.board_flush_need_2 and self.my_flush_high > 5 and pot_size > 200:
                        return high_raise
                    
                    if self.board_flush_need_2:
                        return medium_raise
                    
                    return high_raise
                
                if self.high_hand == 4:
                    if self.board_straight:
                        if self.my_straight_high > self.board_straight_high:
                            return high_raise
                        return CheckAction()
                    if self.board_flush_need_1:
                        return small_raise
                    
                    if self.board_straight_need_1:
                        if self.my_straight_high > self.board_straight_high and pot_size > 200:
                            return high_raise
                        return medium_raise
                        
                    if self.board_trips:
                        return medium_raise
                    
                    if self.board_two_pair:
                        return medium_raise
                    
                    if self.board_straight_need_2 and self.board_straight_high and pot_size > 200:
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return medium_raise
                    
                    return high_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return small_raise
                        return CheckAction()
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return CheckAction()
                    if self.board_pair:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 2:
                    if self.board_two_pair:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return small_raise
                        return CheckAction()
                
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1:
                        return CheckAction()
                    if self.board_pair >= self.sorted_board_ranks[1]:
                        return small_raise
                    return CheckAction()
                    
                return CheckAction()
                    
            if my_pip == 0 and continue_cost <= max(5, pot_size/25):
                if continue_cost == 0:
                    action = CheckAction()
                else:
                    action = CallAction()
                    
                print("Opponent checks on river")
                # opponent checks (or makes small bet)
                
                if pot_size > 200:
                    if can_raise:
                        high_raise = RaiseAction(max_raise)
                        medium_raise = RaiseAction(max(min_raise,min(50, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(28, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(60, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(35, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(20, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = action, action, action
                
                if self.high_hand == 8:
                    return high_raise
                
                if self.high_hand == 7:
                    if self.board_quads:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return high_raise
                        return action
                    if self.board_full_house or self.board_trips:
                        return high_raise
                    return medium_raise
                
                if self.high_hand == 6:
                    if self.board_full_house:
                        if self.full_house_ranks == self.board_full_house_ranks:
                            if self.full_house_ranks[0] > self.full_house_ranks[1]: # no danger from opponent having three of a kind on the pair
                                return high_raise
                            return medium_raise
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            return high_raise
                        return medium_raise
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return small_raise
                        return medium_raise
                    return small_raise
                       
                if self.high_hand == 5:
                    
                    if self.board_flush:
                        if self.my_flush_high > self.board_flush_min and self.my_flush_high > 4:
                            return small_raise
                        return action
                    
                    if self.board_flush_need_1:
                        if self.my_flush_high > 9:
                            return high_raise
                        
                    if self.board_trips:
                        return small_raise
                    
                    if self.board_two_pair:
                        return small_raise
                    
                    if self.board_flush_need_2 and self.my_flush_high > 5:
                        return high_raise
                    
                    if self.board_flush_need_2:
                        return medium_raise
                    
                    return high_raise
                
                if self.high_hand == 4:
                    
                    if self.board_straight:
                        if self.my_straight_high > self.board_straight_high:
                            return high_raise
                        return action
                    if self.board_flush_need_1:
                        return small_raise
                    
                    if self.board_straight_need_1:
                        if self.my_straight_high > self.board_straight_high:
                            return high_raise
                        return medium_raise
                        
                    if self.board_trips:
                        return small_raise
                    
                    if self.board_two_pair:
                        return small_raise
                    
                    if self.board_straight_need_2 and self.board_straight_high and pot_size > 200:
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return medium_raise
                    
                    return high_raise
                
                if self.high_hand == 3:
                    
                    if self.board_trips:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return small_raise
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.board_pair:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 2:
                    
                    if self.board_two_pair:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return small_raise
                        return action
                    if self.board_pair:
                        if self.two_pair_ranks[1] == self.board_pair_rank:
                            return medium_raise
                        return small_raise
                    if self.two_pair_ranks[0] >= self.sorted_board_ranks[1]:
                        return medium_raise
                    return small_raise
                
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.pair_rank == self.sorted_board_ranks[0]:
                        return small_raise
                    return action
                    
                return action
            
            if continue_cost < 5 or tiny_river_bet:
                action = CallAction()
            else:
                action = FoldAction()
                
            if big_blind and my_pip == 0:
                
                print("Opponent bets on river after we checked")
                
                # we checked and opponent bet
                
                if pot_size > 200:
                    if can_raise:
                        high_raise = RaiseAction(max_raise)
                        medium_raise = RaiseAction(max(min_raise,min(50, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(25, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(60, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(35, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(15, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                
                    
                if self.high_hand >= 4:
                    return CallAction()
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if continue_cost < 10 or continue_cost < pot_size/8:
                            return CallAction()
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        if continue_cost < 10 or continue_cost < pot_size/8:
                            return CallAction()
                        return action
                
                if self.high_hand == 2:
                    if continue_cost < 8 or continue_cost < pot_size/8:
                        return CallAction()
                    return action
                
                if self.high_hand == 1:
                    if continue_cost < 5 or continue_cost < pot_size/8:
                        return CallAction()
                    return action
                
                return action
            
            if my_pip != 0:
                
                # we bet and opponent raised
                
                print("Opponent raised on river")
                
                if pot_size > 200:
                    if can_raise:
                        high_raise = RaiseAction(max_raise)
                        medium_raise = RaiseAction(max(min_raise,min(50, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(25, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                else:
                    if can_raise:
                        high_raise = RaiseAction(max(min_raise,min(60, max_raise)))
                        medium_raise = RaiseAction(max(min_raise,min(35, max_raise)))
                        small_raise = RaiseAction(max(min_raise, min(15, max_raise)))
                    else:
                        high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
                
                if self.high_hand == 8:
                    return high_raise
                
                if self.high_hand == 7:
                    if self.board_quads:
                        if self.my_high_card >= 10 or self.my_high_card >= 8 and not self.high_cards_or_pair_likely:
                            return CallAction()
                        return action
                    return high_raise
                
                if self.high_hand == 6:
                    if self.board_full_house:
                        if self.full_house_ranks == self.board_full_house_ranks:
                            if self.full_house_ranks[0] > self.full_house_ranks[1] and pot_size > 200: # no danger from opponent having three of a kind on the pair
                                return high_raise
                            return CallAction()
                    if self.board_trips:
                        if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                            if can_raise:
                                return high_raise
                            return CallAction()
                        return CallAction()
                        
                    if self.board_two_pair:
                        if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]: # we have three of a kind on the high card
                            return CallAction()
                       
                if self.high_hand == 5:
                    
                    if self.board_flush:
                        if self.my_flush_high > self.board_flush_min and self.my_flush_high > 4:
                            return high_raise
                        if medium_river_bet:
                            return CallAction()
                        return action
                    
                    if self.board_flush_need_1:
                        if self.my_flush_high > 9:
                            return high_raise
                        
                    if self.board_trips:
                        if medium_river_bet:
                            return CallAction()
                        return action
                    if self.board_two_pair:
                        if medium_river_bet:
                            return CallAction()
                        return action
                    
                    if self.board_flush_need_2 and self.my_flush_high > 5:
                        return high_raise
                    
                    return CallAction()
                
                if self.high_hand == 4:
                    if self.board_straight:
                        if self.my_straight_high > self.board_straight_high:
                            return high_raise
                        if medium_river_bet:
                            return CallAction()
                        return action
                    if self.board_flush_need_1:
                        return small_raise
                    
                    if self.board_straight_need_1:
                        if self.my_straight_high > self.board_straight_high and pot_size > 200:
                            return high_raise
                        return small_raise
                        
                    if self.board_trips:
                        return small_raise
                    
                    if self.board_two_pair:
                        return medium_raise
                    
                    if self.board_straight_need_2 and self.board_straight_high and pot_size > 200:
                        return high_raise
                    
                    if self.board_straight_need_2:
                        return medium_raise
                    
                    return high_raise
                
                if self.high_hand == 3:
                    if self.board_trips:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return CallAction()
                        return action
                    if self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.board_pair:
                        return small_raise
                    return medium_raise
                
                if self.high_hand == 2:
                    if self.board_two_pair:
                        if self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely:
                            return small_raise
                        if medium_river_bet:
                            return CallAction()
                        return action
                
                if self.high_hand == 1:
                    if self.board_pair or self.board_flush_need_1 or self.board_straight_need_1:
                        return action
                    if self.pair_rank == self.sorted_board_ranks[0]:
                        return small_raise
                    if self.board_pair == self.sorted_board_ranks[1] and medium_river_bet:
                        return CallAction()
                    return action
                
            # opponent bet
            
            print("Opponent bet on river")
        
            if pot_size > 200:
                if can_raise:
                    high_raise = RaiseAction(max_raise)
                    medium_raise = RaiseAction(max(min_raise,min(50, max_raise)))
                    small_raise = RaiseAction(max(min_raise, min(25, max_raise)))
                else:
                    high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()
            else:
                if can_raise:
                    high_raise = RaiseAction(max(min_raise,min(60, max_raise)))
                    medium_raise = RaiseAction(max(min_raise,min(35, max_raise)))
                    small_raise = RaiseAction(max(min_raise, min(15, max_raise)))
                else:
                    high_raise, medium_raise, small_raise = CallAction(), CallAction(), CallAction()

            if self.high_hand == 8:
                return high_raise
            
            if self.high_hand == 7:
                
                if self.board_quads:
                    if self.my_high_card >= 11 or self.my_high_card >= 9 and not self.high_cards_or_pair_likely:
                        return CallAction()
                    return action
                return high_raise
            
            if self.high_hand == 6:
                
                if self.board_full_house:
                    if self.full_house_ranks == self.board_full_house_ranks:
                        if self.full_house_ranks[0] > self.full_house_ranks[1] and medium_river_bet: # no danger from opponent having three of a kind on the pair
                            return CallAction()
                        return high_raise
                    
                if self.board_trips:
                    if self.full_house_ranks[0] > self.board_trips_rank:
                        return high_raise
                    if self.full_house_ranks[1] >= self.sorted_board_ranks[1]:
                        return medium_raise
                    return CallAction()
                    
                if self.board_two_pair:
                    if self.full_house_ranks[0] >= self.board_two_pair_ranks[0]:
                        return medium_raise
                
                return high_raise
                   
            if self.high_hand == 5:
                
                if self.board_flush:
                    if self.my_flush_high > self.board_flush_min and self.my_flush_high > 6:
                        return high_raise
                    if medium_river_bet:
                        return CallAction()
                    return action
                
                if self.board_flush_need_1:
                    if self.my_flush_high >= 10 or self.my_flush_high >= 8 and not self.high_cards_or_pair_likely:
                        return CallAction()
                    
                if self.board_trips:
                    return action
                
                if self.board_two_pair:
                    return action
                
                if self.board_flush_need_2 and self.my_flush_high > 5:
                    return CallAction()
                
                return small_raise
            
            if self.high_hand == 4:
                
                if self.board_straight:
                    if self.board_straight_high == 12:
                        return CallAction()
                    if self.my_straight_high > self.board_straight_high:
                        return high_raise
                    if medium_river_bet:
                        return CallAction()
                    return action
                
                if self.board_flush_need_1:
                    return action
                
                if self.board_straight_need_1:
                    if self.my_straight_high > self.board_straight_high:
                        return high_raise
                    return CallAction()
                    
                if self.board_trips:
                    return action
                
                if self.board_two_pair:
                    return action
                
                if self.board_straight_need_2 and self.my_straight_high > self.board_straight_high:
                    return high_raise
                
                if self.board_straight_need_2 and self.my_straight_high > self.board_straight_high:
                    return high_raise
                
                return CallAction()
            
            if self.high_hand == 3:
                
                if self.board_trips:
                    if self.my_high_card >= 10 and medium_river_bet:
                        return CallAction()
                    return action
                if self.board_flush_need_1 or self.board_straight_need_1:
                    return action
                if self.board_pair:
                    return small_raise
                return CallAction()
            
            if self.high_hand == 2:
                
                if self.board_two_pair:
                    if (self.my_high_card >= 10 or self.my_high_card >= 7 and not self.high_cards_or_pair_likely) and medium_river_bet:
                        return CallAction()
                    return action
                
            return action
                
    
        if CheckAction in legal_actions:
            return CheckAction()
        return FoldAction()

if __name__ == '__main__':
    run_bot(Player(), parse_args())
    