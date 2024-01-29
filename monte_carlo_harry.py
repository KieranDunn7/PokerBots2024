import eval7


# for _ in range(1):
#     deck = eval7.Deck()
#     deck.shuffle()
#     game_cards = deck.deal(11)
#     print(game_cards)
#     p1_hole = [game_cards[0], game_cards[2]]
#     p2_hole = [game_cards[1], game_cards[3]]
#     comm = game_cards[4:9]
#     auction1 = [game_cards[9]]
#     auction2 = [game_cards[10]]

#     print(p1_hole)
#     print(p2_hole)
#     print(comm)
#     print(auction1)
#     print(auction2)

#     p1_hand = p1_hole + comm
#     p2_hand = p2_hole + comm
    
#     p1_score = eval7.evaluate(p1_hole)
#     p2_score = eval7.evaluate(p2_hole)



def simulate_game(num_sims):
    for _ in range(num_sims):
        deck = eval7.Deck()
        deck.shuffle()
        draw = deck.deal(11)

        my_hole = draw[0:2]
        opp_hole = draw[2:4]
        comm = draw[4:9]

        my_hand = my_hole + comm
        opp_hand = opp_hole + comm
        if eval7.evaluate(my_hand) >= eval7.evaluate(opp_hand):
            my_wins += 1
    return my_wins/num_sims


hello = eval7.Deck()
hello.shuffle()
my_hole = hello.deal(2)
# print(my_hole)
# print(simulate_rest_of_game_preflop(my_hole))



def simulate_rest_of_game_postflop_preauction(my_hole, flop, num_sims):
    revealed_cards = [item for item in my_hole + flop]
    print(revealed_cards)

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

        # print(draw)

        my_hand_auction = my_hole + flop + comm + auction1
        opp_hand = opp_hole + flop + comm
        if eval7.evaluate(my_hand_auction) >= eval7.evaluate(opp_hand):
            my_wins_w_auction += 1

        my_hand = my_hole + flop + comm
        opp_hand_auction = opp_hole + flop + comm + auction1
        if eval7.evaluate(my_hand) >= eval7.evaluate(opp_hand_auction):
            my_wins_wo_auction += 1


    return my_wins_w_auction/num_sims, my_wins_wo_auction/num_sims



hello = eval7.Deck()
hello.shuffle()
drw = hello.deal(5)
my_hole = drw[0:2]
flop = drw[2:5]
# print(my_hole)
# print(flop)

# print(simulate_rest_of_game_postflop_preauction(my_hole, flop))


def simulate_rest_of_game_postauction(my_hole, flop, auction_card):
    """
    auction_card is list of card types, if empty, it means we lost the auction
    """

    revealed_cards = [item for item in my_hole + flop + auction_card]
    print(revealed_cards)

    my_wins = 0
    num_sims = 10000

    if auction_card:
        for _ in range(num_sims):
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)

            deck.shuffle()
            draw = deck.deal(4)

            opp_hole = draw[0:2]
            comm = draw[2:4]

            my_hand_auction = my_hole + flop + comm + auction_card
            opp_hand = opp_hole + flop + comm
            if eval7.evaluate(my_hand_auction) >= eval7.evaluate(opp_hand):
                my_wins += 1

    else:
        for _ in range(num_sims):
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)

            deck.shuffle()
            draw = deck.deal(5)

            opp_hole = draw[0:2]
            comm = draw[2:4]
            opp_auction = [draw[4]]

            my_hand = my_hole + flop + comm
            opp_hand_auction = opp_hole + flop + comm + opp_auction
            if eval7.evaluate(my_hand) >= eval7.evaluate(opp_hand_auction):
                my_wins += 1


    return my_wins/num_sims



hello = eval7.Deck()
hello.shuffle()
drw = hello.deal(6)
my_hole = drw[0:2]
flop = drw[2:5]
auction_card = [drw[5]]
# print(my_hole)
# print(flop)
# print(auction_card)

# print(simulate_rest_of_game_postauction(my_hole, flop, auction_card))



def simulate_rest_of_game_post_turn(my_hole, flop, auction_card, turn):
    revealed_cards = [item for item in my_hole + flop + auction_card + turn]
    my_wins = 0
    num_sims = 10000

    if auction_card:
        for _ in range(num_sims):
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)

            deck.shuffle()
            draw = deck.deal(3)

            opp_hole = draw[0:2]
            river = [draw[2]]

            my_hand_auction = my_hole + flop + auction_card + turn + river
            opp_hand = opp_hole + flop + turn + river
            if eval7.evaluate(my_hand_auction) >= eval7.evaluate(opp_hand):
                my_wins += 1

    else:
        for _ in range(num_sims):
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)

            deck.shuffle()
            draw = deck.deal(4)

            opp_hole = draw[0:2]
            river = [draw[2]]
            opp_auction = [draw[3]]

            my_hand = my_hole + flop + turn + river
            opp_hand_auction = opp_hole + flop + turn + river + opp_auction
            if eval7.evaluate(my_hand) >= eval7.evaluate(opp_hand_auction):
                my_wins += 1


    return my_wins/num_sims


hello = eval7.Deck()
hello.shuffle()
drw = hello.deal(7)
my_hole = drw[0:2]
flop = drw[2:5]
auction_card = []
turn = [drw[6]]
print(my_hole)
print(flop)
print(auction_card)
print(turn)

print(simulate_rest_of_game_post_turn(my_hole, flop, auction_card, turn))


def simulate_rest_of_game_post_river(my_hole, flop, auction_card, turn, river, num_sims):
    revealed_cards = my_hole + flop + auction_card + turn + river
    my_wins = 0

    if auction_card:
        for _ in range(num_sims):
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)

            deck.shuffle()
            draw = deck.deal(2)

            opp_hole = draw[0:2]

            my_hand_auction = my_hole + flop + auction_card + turn + river
            opp_hand = opp_hole + flop + turn + river
            if eval7.evaluate(my_hand_auction) >= eval7.evaluate(opp_hand):
                my_wins += 1

    else:
        for _ in range(num_sims):
            deck = eval7.Deck()
            for card in revealed_cards:
                deck.cards.remove(card)

            deck.shuffle()
            draw = deck.deal(3)

            opp_hole = draw[0:2]
            opp_auction = [draw[2]]

            my_hand = my_hole + flop + turn + river
            opp_hand_auction = opp_hole + flop + turn + river + opp_auction
            if eval7.evaluate(my_hand) >= eval7.evaluate(opp_hand_auction):
                my_wins += 1


    return my_wins/num_sims


