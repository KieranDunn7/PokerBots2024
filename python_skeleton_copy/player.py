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
        
        self.pair_percentages = (0.322, 0.353, 0.39, 0.423, 0.45, 0.482, 0.511, 0.542, 0.573, 0.602, 0.63, 0.652, 0.689)
        # pairs with no extra card
        
        self.suited_percentages = {12: (0.389, 0.393, 0.404, 0.412, 0.411, 0.416, 0.423, 0.43, 0.452, 0.463, 0.47, 0.48),
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
                 1: (0.239,)}
        # suited with no extra card, high card is key, low card is index in tuple
        
        self.nonsuited_percentages = {12: (0.352, 0.365, 0.371, 0.38, 0.378, 0.388, 0.398, 0.403, 0.425, 0.436, 0.444, 0.458),
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
                 1: (0.202,)}
        # non-suited with no extra card, high card is key, low card is index in tuple

        self.pair_percentages_plus = (0.641, 0.663, 0.692, 0.711, 0.732, 0.75, 0.77, 0.79, 0.812, 0.828, 0.845, 0.858, 0.882)
        # pairs with extra card

        self.suited_percentages_plus = {12: (0.699, 0.71, 0.717, 0.722, 0.721, 0.728, 0.732, 0.735, 0.752, 0.756, 0.76, 0.762),
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
                 1: (0.594,)}
        # suited with extra card, high card is key, low card is index in tuple

        self.nonsuited_percentages_plus = {12: (0.675, 0.685, 0.693, 0.703, 0.7, 0.707, 0.715, 0.718, 0.734, 0.739, 0.74, 0.746),
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
                 1: (0.556,)}
        # non-suited with extra card, high card is key, low card is index in tuple

        self.total_suited_percentages = {12: (0.544, 0.5515, 0.5585, 0.5675, 0.566, 0.572, 0.5775, 0.5825, 0.602, 0.6095, 0.615, 0.621),
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

        self.total_nonsuited_percentages = {12: (0.5135, 0.525, 0.532, 0.5415, 0.539, 0.5475, 0.5565, 0.5605, 0.5795, 0.5875, 0.592, 0.602),
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

        self.total_pair_percentages = (0.4815, 0.508, 0.541, 0.567, 0.591, 0.616, 0.6405, 0.666, 0.6925, 0.715, 0.7375, 0.755, 0.7855)
        # averages from pp and ppp

        self.ranks = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}

        self.forfeit = False # decides whether the bot can win by folding/checking every future action
        
        self.pre_flop_folds = [] # preflop folds for opp
        self.pre_flop_folds_sum = 0
        self.pre_flop_folds_num = 0 # amount of preflop folds
        self.pre_flop_calls = [] # preflop calls for opp
        self.pre_flop_calls_sum = 0
        self.pre_flop_calls_num = 0 # amount of preflop calls
        self.pre_flop_raises = [] # preflop raises for opp
        self.pre_flop_raises_sum = 0
        self.pre_flop_raises_num = 0 # amount of preflop raises

        self.opp_bids = [] # For crazy opp auction mean calculation
        self.my_bids = []
        self.bid_pot_sum = 0
        self.opp_bids_sum = 0
        self.opp_bids_num = 0
        self.opp_bid_avg = 0
        self.opp_bid_cv = 1
        self.opp_bid_var = 2500

        self.diffs = []

        self.post_auction_pcts = []
        self.post_turn_pcts = []
        self.post_river_pcts = []
        self.win_loss_tie = []

        self.post_auction_pct = 0
        self.post_turn_pct = 0
        self.post_river_pct = 0
        

        self.pre_calc_win_pct = 0.6651
        self.calc_win_pct = 0.5
        # gives the calculated percentages on the flop, turn, river, and whether we won, lost, or tied (0.5 for tie)


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
        self.pre_flop_raise = 0
        self.all_in = False
        self.folded = False
        self.street3 = True
        self.street4 = True
        self.street5 = True

        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        if my_bankroll > (NUM_ROUNDS-round_num)*1.5 + 4 and not self.forfeit:
            self.forfeit = True
            print(f"Forfeit in Round #{round_num}")
        rank1,rank2 = self.ranks[my_cards[0][0]], self.ranks[my_cards[1][0]]
        suit1,suit2 = my_cards[0][1], my_cards[1][1]

        pair = rank1 == rank2
        suited = suit1 == suit2

        if rank1 < rank2:
            rank1,rank2 = rank2,rank1
            suit1,suit2 = suit2,suit1

        if pair:
            self.percentage = self.pair_percentages[rank1]
            self.percentage_plus = self.pair_percentages_plus[rank1]
        elif suited:
            self.percentage = self.suited_percentages[rank1][rank2]
            self.percentage_plus = self.suited_percentages_plus[rank1][rank2]
        else:
            self.percentage = self.nonsuited_percentages[rank1][rank2]
            self.percentage_plus = self.nonsuited_percentages_plus[rank1][rank2]
        self.rank1, self.rank2 = rank1, rank2
        self.pair, self.suited = pair, suited
        self.suit1, self.suit2 = suit1, suit2
        """
        if not self.forfeit:
            print()
            print(f"Round #{round_num}")
            #print("My cards:", my_cards)
            """

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
        
        if street >= 3 and not self.all_in:
            opp_bid = previous_state.bids[1-active]
            if opp_bid != 0:
                self.opp_bid_avg = self.opp_bids_sum/self.opp_bids_num
                self.opp_bid_var = sum((x - self.opp_bid_avg) ** 2 for x in self.opp_bids)/self.opp_bids_num
                try:
                    self.opp_bid_cv = (self.opp_bid_var**(1/2))/self.opp_bid_avg
                except ZeroDivisionError:
                    self.opp_bid_cv = 100
        """
        if street == 0 and not self.folded and opp_pip == BIG_BLIND:
            self.pre_flop_folds.append(my_pip-opp_pip)
            if not self.forfeit:
                print("Pre-flop Opponent Fold", my_pip-opp_pip)
        if self.folded and not self.forfeit:
            print("Fold")
            """
        if not self.forfeit and opp_cards and final_pot_size > 100:
            if my_delta == opp_contribution:
                self.win_loss_tie.append(1)
            elif my_delta == -1*my_contribution:
                self.win_loss_tie.append(0)
            else:
                self.win_loss_tie.append(0.5)
            self.post_auction_pcts.append(self.post_auction_pct)
            self.post_turn_pcts.append(self.post_turn_pct)
            self.post_river_pcts.append(self.post_river_pct)
            
            if len(self.win_loss_tie) > 10:
                self.calc_win_pct = sum(self.win_loss_tie)/len(self.win_loss_tie)

        if game_state.round_num == NUM_ROUNDS:
            print()
            print()
            print("opp_bids =", self.opp_bids)
            print("my_bids =", self.my_bids)
            #print("opp_pff =", self.pre_flop_folds)
            #print("opp_pfc =", self.pre_flop_calls)
            #print("opp_pfr =", self.pre_flop_raises)
            print("opp_bid_avg =", self.opp_bid_avg)
            print("opp_bid_cv =", self.opp_bid_cv)
            print("final_time =", game_state.game_clock)
            #print("diffs =", self.diffs)
            #print("avg_diff =", sum(self.diffs)/len(self.diffs))
            print("post_auction_pcts:", self.post_auction_pcts)
            print("post_turn_pcts:", self.post_turn_pcts)
            print("post_river_pcts:", self.post_river_pcts)
            print("win-loss-tie history:", self.win_loss_tie)
            print(len(self.post_auction_pcts))
            print(len(self.post_turn_pcts))
            print(len(self.post_river_pcts))
            print(len(self.win_loss_tie))
            print(sum(self.win_loss_tie)/len(self.win_loss_tie))
        

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
        def cards_needed_for_flush(cards):
            # Extract the suits from each card
            suits = [card[-1] for card in cards]
            
            # Count the occurrences of each suit
            suit_counts = Counter(suits)
            
            # Find the most common suit and the count
            most_common_suit, most_common_count = suit_counts.most_common(1)[0]
            
            # Calculate the number of cards needed for a flush
            cards_needed_for_flush = 5 - most_common_count
            
            return most_common_suit, cards_needed_for_flush
        
        def check_for_straight(board_cards):
            # Extract the ranks from each card
            ranks_dict = {"2": 0, "3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "T": 8, "J": 9, "Q": 10, "K": 11, "A": 12}
            ranks = [card[:-1] for card in board_cards]
            
            # Convert face cards to numeric values
            ranks = [ranks_dict[rank] for rank in ranks]
            
            # Sort the ranks in ascending order
            sorted_ranks = sorted(ranks)
            not_in_board = []
            index = 0
            for number in range(13):
                if sorted_ranks[index] == number:
                    if index != len(sorted_ranks)-1:
                        index += 1
                else:
                    not_in_board.append(number)
            max_num_in = 0
            max_start = [-1]
            starting_card = 12
            num_in = 0
            ace_low_straight = {12, 0, 1, 2, 3}
            for card in ace_low_straight:
                if card in sorted_ranks:
                    num_in += 1
                if num_in == max_num_in:
                    max_start.append(starting_card)
                if num_in > max_num_in:
                    max_num_in = num_in
                    max_start = [starting_card]
            for starting_card in range(9):
                num_in = 0
                for card in range(starting_card, starting_card + 5):
                    if card in sorted_ranks:
                        num_in += 1
                if num_in == max_num_in:
                    max_start.append(starting_card)
                if num_in > max_num_in:
                    max_num_in = num_in
                    max_start = [starting_card]
            
            return max_start, max_num_in
        

        def check_for_pair_on_board(board_cards):
            # suits_on_board = [card[1] for card in board_cards]
            ranks_on_board = [card[0] for card in board_cards]

            pair_on_board = False
            two_pair_on_board = False
            trips_on_board = False

            # Dictionary to store the count of each number
            count = {}
            # Counting the frequency of each number
            for number in ranks_on_board:
                if number in count:
                    if count[number] == 1:
                        if pair_on_board:
                            two_pair_on_board = True
                        else:
                            pair_on_board = True
                    if count[number] == 2:
                        trips_on_board = True
                    count[number] += 1
                else:
                    count[number] = 1

            return pair_on_board, two_pair_on_board, trips_on_board, count


        
        def simulate_auction(my_cards, board_cards, num_sims):
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

        def simulate_rest_of_game(my_cards, board_cards, opp_auction, num_sims):
            hole_cards = [eval7.Card(card) for card in my_cards]
            comm_cards = [eval7.Card(card) for card in board_cards]
            revealed_cards = hole_cards + comm_cards
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)
            my_wins = 0
            peek_max = 7 - len(board_cards)
            if opp_auction:
                peek_max += 1
                opp_hand_size = 3
            else:
                opp_hand_size = 2
            drawings_per_shuffle = (52 - (len(my_cards)+len(board_cards)))//peek_max
            for trial in range(num_sims):
                deck.shuffle()
                for drawing in range(drawings_per_shuffle):
                    draw = deck[peek_max*drawing:peek_max*(drawing+1)]
                    opp_hole = draw[0:opp_hand_size]
                    new_comm_cards = draw[opp_hand_size:]
                    my_hand = revealed_cards + new_comm_cards
                    opp_hand = opp_hole + comm_cards + new_comm_cards
                    my_score = eval7.evaluate(my_hand)
                    opp_score = eval7.evaluate(opp_hand)
                    if my_score > opp_score:
                        my_wins += 1
                    elif my_score == opp_score:
                        my_wins += 0.5
            return my_wins/(num_sims*drawings_per_shuffle)

        def crazy_opp_bid_behaviour(avg, var):
            return avg > 100 and 0 <= var <= 50 and game_state.round_num > 20

        def get_actual_post_auction_pct(post_auction_pct):
            if post_auction_pct > 0.95:
                return 43/(43+1)
            if post_auction_pct > 0.9:
                return 58/(58+6)
            if post_auction_pct > 0.85:
                return 106/(106+18)
            if post_auction_pct > 0.8:
                return 133/(133+24)
            if post_auction_pct > 0.75:
                return 90/(90+42)
            if post_auction_pct > 0.7:
                return 88/(88+41)
            if post_auction_pct > 0.65:
                return 114/(114+43)
            if post_auction_pct > 0.6:
                return 119/(119+59)
            if post_auction_pct > 0.55:
                return 77/(77+50)
            if post_auction_pct > 0.5:
                return 65/(65+43)
            if post_auction_pct > 0.45:
                return 42/(42+44)
            if post_auction_pct > 0.4:
                return 23/(23+38)
            if post_auction_pct > 0.35:
                return 13/(13+27)
            if post_auction_pct > 0.3:
                return 7/(7+22)
            if post_auction_pct > 0.25:
                return 4/(4+26)
            return 0

        def get_actual_post_turn_pct(post_turn_pct):
            if post_turn_pct > 0.95:
                return 124/(124+2)
            if post_turn_pct > 0.9:
                return 93/(93+6)
            if post_turn_pct > 0.85:
                return 127/(127+25)
            if post_turn_pct > 0.8:
                return 113/(113+25)
            if post_turn_pct > 0.75:
                return 99/(99+45)
            if post_turn_pct > 0.7:
                return 76/(76+31)
            if post_turn_pct > 0.65:
                return 77/(77+31)
            if post_turn_pct > 0.6:
                return 78/(78+41)
            if post_turn_pct > 0.55:
                return 64/(64+51)
            if post_turn_pct > 0.5:
                return 44/(44+33)
            if post_turn_pct > 0.45:
                return 28/(28+30)
            if post_turn_pct > 0.4:
                return 23/(23+39)
            if post_turn_pct > 0.35:
                return 16/(16+38)
            if post_turn_pct > 0.3:
                return 14/(14+38)
            if post_turn_pct > 0.25:
                return 6/(6+25)
            return 0

        def get_actual_post_river_pct(post_river_pct):
            if post_river_pct > 0.95:
                return 247/(247+5)
            if post_river_pct > 0.9:
                return 113/(113+9)
            if post_river_pct > 0.85:
                return 122/(122+17)
            if post_river_pct > 0.8:
                return 106/(106+15)
            if post_river_pct > 0.75:
                return 65/(65+27)
            if post_river_pct > 0.7:
                return 60/(60+37)
            if post_river_pct > 0.65:
                return 53/(53+38)
            if post_river_pct > 0.6:
                return 46/(46+28)
            if post_river_pct > 0.55:
                return 41/(41+28)
            if post_river_pct > 0.5:
                return 38/(38+27)
            if post_river_pct > 0.45:
                return 30/(30+33)
            if post_river_pct > 0.4:
                return 22/(22+29)
            if post_river_pct > 0.35:
                return 11/(11+29)
            if post_river_pct > 0.3:
                return 12/(12+28)
            if post_river_pct > 0.25:
                return 7/(7+25)
            return 0
        
            

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
        pot_size = my_contribution + opp_contribution
        
        if self.forfeit:
            if BidAction in legal_actions:
                return BidAction(0)
            if CheckAction in legal_actions:
                return CheckAction()
            self.folded = True
            return FoldAction()

        self.all_in = my_stack == 0
            
    
        if BidAction in legal_actions:
            #print("pot_size:", pot_size)
            """
            if pot_size > 2*BIG_BLIND and self.pre_flop_raise != 0:
                # opponent either called or raised on our pre-flop raise
                if pot_size == (self.pre_flop_raise + BIG_BLIND) * 2:
                    self.pre_flop_calls.append(self.pre_flop_raise)
                    self.pre_flop_calls_sum += self.pre_flop_raise
                    self.pre_flop_calls_num += 1
                    print("Pre-flop Opponent Call", self.pre_flop_raise)
                else:
                    self.pre_flop_raises.append(self.pre_flop_raise)
                    self.pre_flop_raises_sum += self.pre_flop_raise
                    self.pre_flop_raises_num += 1
                    print("Pre-flop Opponent Raise", self.pre_flop_raise)
                        """
            if self.all_in:
                # all in pre-flop, need to bid 0
                return BidAction(0)
            prob_win_w_auction, prob_win_wo_auction = simulate_auction(my_cards, board_cards,200)
            diff = round(prob_win_w_auction - prob_win_wo_auction, 4)
            """
            print("prob_win_w_auction:", prob_win_w_auction)
            print("prob_win_wo_auction:", prob_win_wo_auction)
            print("diff:", diff)
                """
                # self.diffs.append(diff)
            if self.opp_bids_num < 3:
                opp_bid_avg = 100
                opp_bid_stdv = 25
            else:
                opp_bid_avg = self.opp_bid_avg
                opp_bid_stdv = self.opp_bid_var**(1/2)
            bid = int(opp_bid_avg + opp_bid_stdv * 1.96 * (diff-0.3) * 10) - 1
            """
            print("My bid:", bid)
                """
            return BidAction(min(my_stack, max(bid, 25)))
        if self.all_in:
            return CheckAction()

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        else:
            min_raise, max_raise = 0, 0

        #if continue_cost > 1:
            #print("Opp raise:", continue_cost)
        #elif not big_blind and street != 0:
            #print("Opp check")
            
        if street == 0:
            percentage, percentage_plus = self.percentage, self.percentage_plus
            total_percentage = (percentage + percentage_plus)/2
            if (my_pip + continue_cost)/(continue_cost + pot_size) > total_percentage:
                if CheckAction in legal_actions:
                    return CheckAction()
                self.folded = True
                return FoldAction()
            if RaiseAction in legal_actions and total_percentage > 0.6:
                return RaiseAction(int(max(min_raise, min(max_raise, pot_size*0.6/(1 - 0.6)))))
            if CheckAction in legal_actions:
                return CheckAction()
            return CallAction()

            
        
        if street == 3 and self.street3:
            self.opp_auction = opp_bid >= my_bid
            if opp_bid != 0:
                self.opp_bids.append(opp_bid)
                self.my_bids.append(my_bid)
                self.opp_bids_sum += opp_bid
                self.opp_bids_num += 1
            self.prob_win = round(simulate_rest_of_game(my_cards, board_cards, self.opp_auction, 100), 3)
            self.post_auction_pct = self.prob_win
            self.street3 = False
            self.actual_win_pct = round(1-(1-get_actual_post_auction_pct(self.prob_win))*self.pre_calc_win_pct/self.calc_win_pct, 3)
            #print("Post-auction pct:", self.prob_win)
    
        if street == 4 and self.street4:
            #print("pot_size:", pot_size)
            self.prob_win = round(simulate_rest_of_game(my_cards, board_cards, self.opp_auction, 100), 3)
            self.street4 = False
            self.post_turn_pct = self.prob_win
            self.actual_win_pct = round(1-(1-get_actual_post_turn_pct(self.prob_win))*self.pre_calc_win_pct/self.calc_win_pct, 3)
            #print("Post-turn pct:", self.prob_win)
                
        if street == 5 and self.street5:
            #print("pot_size:", pot_size)
            self.prob_win = round(simulate_rest_of_game(my_cards, board_cards, self.opp_auction, 100), 3)
            self.street5 = False
            self.post_river_pct = self.prob_win
            self.actual_win_pct = round(1-(1-get_actual_post_river_pct(self.prob_win))*self.pre_calc_win_pct/self.calc_win_pct, 3)
            #print("Post-river pct:", self.prob_win)
        
        if continue_cost == 0 and not big_blind:
            # opponent starts betting and checks
            if RaiseAction not in legal_actions:
                return CheckAction()
            if self.actual_win_pct > 0.6:
                return RaiseAction(int(max(min_raise, min(max_raise, pot_size*0.6/(1 - 0.6))))) # using 0.6 as a baseline for the opp percent chance of winning
            return CheckAction()
                
        if continue_cost == 0 and big_blind:
            # we start betting and can raise or check
            if RaiseAction not in legal_actions:
                return CheckAction()
            if self.actual_win_pct > 0.7:
                return RaiseAction(int(max(min_raise, min(max_raise, pot_size*0.7/(1 - 0.7))))) # using 0.7 as a baseline for the opp percent chance of winning
            return CheckAction()
                
        if continue_cost != 0 and not big_blind:
            # opponent raised and started betting, but we may have also raised this round
            # and they raised again in response
            if (my_pip + continue_cost)/(continue_cost + pot_size) > self.actual_win_pct:
                self.folded = True
                return FoldAction()
            if RaiseAction in legal_actions:
                if self.actual_win_pct >= 0.95:
                    return RaiseAction(max_raise)
                if self.actual_win_pct > 0.85:
                    return RaiseAction(int(max(min_raise, min(max_raise, pot_size*0.85/(1 - 0.85))))) # using 0.7 as a baseline for the opp percent chance of winning
            if RaiseAction not in legal_actions: ##### Initially had Return CaLLACTION()
                return CallAction()
            else:
                return RaiseAction(min_raise)
            
                

        if continue_cost != 0 and big_blind:
            # we raised as big blind at least once, and opponent raised again in response
            if (my_pip + continue_cost)/(continue_cost + pot_size) > self.actual_win_pct:
                self.folded = True
                return FoldAction()
            if RaiseAction in legal_actions: 
                if self.actual_win_pct >= 0.95:
                    return RaiseAction(max_raise)
                if self.actual_win_pct > 0.9:
                    return RaiseAction(int(max(min_raise, min(max_raise, pot_size*0.9/(1 - 0.9))))) # using 0.7 as a baseline for the opp percent chance of winning
            if RaiseAction not in legal_actions: ##### Initially had Return CaLLACTION()
                return CallAction()
            else:
                return RaiseAction(min_raise)
            
        if CheckAction in legal_actions:
            return CheckAction()
        self.folded = True
        return FoldAction()

if __name__ == '__main__':
    run_bot(Player(), parse_args())
