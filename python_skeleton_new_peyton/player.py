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
        self.bid_pot_sum = 0
        self.opp_bids_sum = 0
        self.opp_bids_num = 0
        self.opp_bid_avg = 0
        self.opp_bid_cv = 1
        self.opp_bid_var = 2500



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
        self.flush_high = -1 # high in the flush for tie-break
        
        self.double_straight_draw = False
        self.straight_draw = False
        self.straight = False
        self.my_straight = set() # cards in our hand for a straight
        self.board_straight = set() # cards on the board for a straight
        self.straight_high = -1
        self.draw_needed = set() # cards needed for a draw
        self.double_draw_needed = set() # pairs of cards needed for a double draw
        self.my_num_in_straight = 0 # number we have making up the straight
        
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
        
        self.high_hand = "High Card" # string representing the best hand we have
        
        self.street_num = 0 # used for checking if hand strength has already been calculated
        
        
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

        def simulate_rest_of_game(my_cards, board_cards, opp_auction, num_sims):
            """
            Takes my_cards and board_cards as lists of strings, opp_auction as
            a bool representing whether the opponent won the auction, and
            num_sims as an int and uses montecarlo to return the probability
            of winning
            """
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
        pot_size = my_contribution + opp_contribution # total pot size including new opp betting
        
        if self.forfeit:
            if BidAction in legal_actions:
                return BidAction(0)
            if CheckAction in legal_actions:
                return CheckAction()
            self.folded = True
            return FoldAction()

        all_in = my_stack == 0
    
        if BidAction in legal_actions:
            if all_in:
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
        
        if all_in:
            return CheckAction()

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        else:
            min_raise, max_raise = 0, 0

        if street == 0:
            if CheckAction in legal_actions:
                # opponent calls as small bind
                if self.total_percentage > 0.58 and RaiseAction in legal_actions:
                    return RaiseAction(max(min_raise, min(1.38 * pot_size, max_raise)))
                return CheckAction()
            self.high_cards_likely = continue_cost == BIG_BLIND - SMALL_BLIND
            if self.total_percentage * pot_size - (1-self.total_percentage) * continue_cost < 0:
                return FoldAction()
            if continue_cost == BIG_BLIND - SMALL_BLIND:
                # small blind
                if self.total_percentage > 0.56 and RaiseAction in legal_actions:
                    return RaiseAction(max(min_raise, min(1.27 * pot_size, max_raise)))
                return CheckAction()
            # opp raised
            necessary_pct = 0.54 + pot_size/100
            if self.total_percentage > necessary_pct and RaiseAction in legal_actions:
                return RaiseAction(max(min_raise, min(necessary_pct/(1-necessary_pct) * pot_size, max_raise)))
            return CallAction()
        
        
        if self.street_num < street: # new card dealt
            
            # analyzing our hand
            
            self.street_num = street
            our_total_cards = my_cards + board_cards
            
            for card in my_cards: # find hand high card
                rank = ranks_dict[card[0]]
                if rank > self.my_high_card:
                    self.my_high_card = rank
            
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
                
            elif len(trips) > 1 or trips and pairs: # full house
                self.full_house = True
                if len(trips) > 1 and pairs:
                    self.full_house_ranks = max(trips), max(min(trips), max(pairs))
                elif pairs:
                    self.full_house_ranks = max(trips), max(pairs)
                else:
                    self.full_house_ranks = max(trips), min(trips)
                    
            elif trips: # trips
                self.trips = True
                self.trips_rank = max(trips)
                
            elif len(pairs) > 1: # two pair
                self.two_pair = True
                high_pair = pairs.pop(max(pairs))
                low_pair = max(pairs)
                self.two_pair_ranks = high_pair, low_pair
                
            elif pairs: # pair
                self.pair = True
                self.pair_rank = max(pairs)
             
                    
            our_flush = check_for_flush(our_total_cards, street)
            if our_flush:
                for suit_index, cards_in in our_flush.items():
                    if len(cards_in) >= 5: # full flush
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
                        self.flush_high = max(self.my_flush)
                                
                        
                    elif len(cards_in) == 4: # four in a suit
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
                        self.my_num_in_suit = len(self.my_flush) # number in our hand for suit
                        self.flush_high = max(self.my_flush)
                        
                    else: # three in a suit
                        self.double_flush_draw = True
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
                            self.my_num_in_suit[0] = len(self.my_flush[0]) # number in our hand for first suit
                            self.my_num_in_suit[1] = len(self.my_flush[1]) # number in our hand for second suit
                            self.flush_high = max(self.my_flush[0]), max(self.my_flush[1])
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
                            self.my_num_in_suit = len(self.my_flush) # number in our hand for suit
                            self.flush_high = max(self.my_flush)
                        
                        
            our_straight = check_for_straight(our_total_cards, street)
            if our_straight:
                for high_card, (cards_in, cards_out) in our_straight.items():
                    if len(cards_in) == 5: # full straight
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
                            self.my_num_in_straight = len(self.my_straight)
                                        
                    elif len(cards_in) == 4 and not self.straight: # four in straight with no full straight
                        if not self.straight_draw: # clear extra cards from double straight draw
                            self.my_straight, self.board_straight = set(), set()
                        self.straight_draw = True
                        self.draw_needed.add(cards_out.pop())
                        for card in our_total_cards:
                            rank = ranks_dict[card[0]]
                            if rank in cards_in:
                                if card in my_cards:
                                    self.my_straight.add(rank)
                                else:
                                    self.board_straight.add(rank)
                        self.my_num_in_straight = len(self.my_straight)
                        
                        
                        
                    elif not self.straight and not self.straight_draw: # three in a straight with no straight draw or full straight
                        self.double_straight_draw = True
                        self.double_draw_needed.add(cards_out)
                        num_in = 0
                        for card in our_total_cards:
                            rank = ranks_dict[card[0]]
                            if rank in cards_in:
                                if card in my_cards:
                                    self.my_straight.add(rank)
                                    num_in += 1
                                else:
                                    self.board_straight.add(rank)
                        self.my_num_in_straight = len(self.my_straight)
            
            # analyzing their hand
                
        
        if street == 3: # flop post-auction
            if continue_cost == 0 and big_blind:
                # starting betting
                pass
            if continue_cost == 0:
                # opponent checks
                pass
            if big_blind and my_pip == 0:
                # we checked and opponent bet
                pass
            if big_blind:
                # we bet and opponent raised
                pass
            # opponent bet, we raised, opponent raised again
            pass
        
        if street == 4: # turn
            if continue_cost == 0 and big_blind:
                # starting betting
                pass
            if continue_cost == 0:
                # opponent checks
                pass
            if big_blind and my_pip == 0:
                # we checked and opponent bet
                pass
            if big_blind:
                # we bet and opponent raised
                pass
            # opponent bet, we raised, opponent raised again
            pass
        
        if street == 5: # river
            if continue_cost == 0 and big_blind:
                # starting betting
                pass
            if continue_cost == 0:
                # opponent checks
                pass
            if big_blind and my_pip == 0:
                # we checked and opponent bet
                pass
            if big_blind:
                # we bet and opponent raised
                pass
            # opponent bet, we raised, opponent raised again
            pass
                
    
        if CheckAction in legal_actions:
            return CheckAction()
        self.folded = True
        return FoldAction()

if __name__ == '__main__':
    run_bot(Player(), parse_args())