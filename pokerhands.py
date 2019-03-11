def hands(cards):   #takes a list of 7 cards
    d = {}
    for card in cards:
        if card.rank in d:
            d[card.rank][1] += 1
        else:
            d[card.rank] = (card.suit, 1) # (suit, count)
    counts = sorted([x[1] for x in d.values()], reversed=True)
    if counts[0] == 4:
        pass #Four of a kind
    elif counts[0] == 3 and counts[1] >= 2:
        pass #Full House
    elif counts[0] == 3:
        pass #Three of a Kind
    elif counts[0] == 2 and counts[0] == 2:
        pass #Two Pair
    elif counts[0] == 2:
        pass #One Pair
    x = 14
    consecutive = 0
    while x >= 2:
        if x in d:
            consecutive += 1
        else:
            consecutive = 0
        if consecutive == 5:
            break #Straight
        x -= 1
