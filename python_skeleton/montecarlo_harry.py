import eval7



deck = eval7.Deck()
for _ in range(1):
    deck.shuffle()
    game_cards = deck.deal(11)

    print(game_cards)
    # p1_hole = game_cards[0] game_cards[2]
    # p2_hole = game_cards[1] + game_cards[3]
    # comm = game_cards[4:10]
    # auction1 = game_cards[10]
    # auction2 = game_cards[11]

    # print(p1_hole)
    # print(p2_hole)
    # print(comm)
    # print(auction1)
    # print(auction2)