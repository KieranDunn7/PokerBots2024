 if continue_cost > pot_size:
            high_bet, medium_bet, small_bet, tiny_bet = False, False, False, False
        elif continue_cost > pot_size/3:
            high_bet, medium_bet, small_bet, tiny_bet = True, False, False, False
        elif continue_cost > pot_size/5:
            high_bet, medium_bet, small_bet, tiny_bet = True, True, False, False
        elif continue_cost > pot_size/8:
            high_bet, medium_bet, small_bet, tiny_bet = True, True, True, False
        else:
            high_bet, medium_bet, small_bet, tiny_bet = True, True, True, True



def bet_behaviour(integer):
    if continue_cost > pot_size:
        high_bet, medium_bet, small_bet, tiny_bet = False, False, False, False
    elif continue_cost > pot_size/3:
        high_bet, medium_bet, small_bet, tiny_bet = True, False, False, False
    elif continue_cost > pot_size/5:
        high_bet, medium_bet, small_bet, tiny_bet = True, True, False, False
    elif continue_cost > pot_size/8:
        high_bet, medium_bet, small_bet, tiny_bet = True, True, True, False
    else:
        high_bet, medium_bet, small_bet, tiny_bet = True, True, True, True