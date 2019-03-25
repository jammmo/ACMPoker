handorder = ['Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight', 'Three of a Kind', 'Two Pair', 'One Pair', 'High Card']

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return str(self.rank) + '-' + self.suit

def fiveHand(cards):
    assert(len(cards) == 5)
    suitset = set(x.suit for x in cards)
    rankset = set(x.rank for x in cards)
    ranklist = sorted([x.rank for x in cards], reverse=True)

    if len(suitset) == 1 and rankset == {14, 13, 12, 11, 10}:
        return 'Royal Flush', 14

    elif len(suitset) == 1 and any(rankset == set(range(x, x+5)) for x in range(2, 10)):
        return 'Straight Flush', ranklist[0]

    elif len(suitset) == 1 and rankset == {14, 2, 3, 4, 5}:   #case where ace is low
        return 'Straight Flush', 5

    elif len(rankset) == 2 and ranklist.count(cards[0].rank) in {1, 4}:
        return 'Four of a Kind', tuple([ranklist[1]] + [x for x in rankset if x != ranklist[1]])

    elif len(rankset) == 2 and ranklist.count(cards[0].rank) in {2, 3}:
        return 'Full House', tuple([ranklist[2]] + [x for x in rankset if x != ranklist[2]])

    elif len(suitset) == 1:
        return 'Flush', ranklist[0]

    elif any(rankset == set(range(x, x+5)) for x in range(2, 11)):
        return 'Straight', ranklist[0]

    elif rankset == {14, 2, 3, 4, 5}:   #case where ace is low
        return 'Straight', 5

    elif any([x.rank for x in cards].count(y) == 3 for y in rankset):
        return 'Three of a Kind', tuple([ranklist[2]] + sorted([x for x in ranklist if x != ranklist[2]], reverse=True))

    elif len(rankset) == 3:
        return 'Two Pair', tuple(sorted([ranklist[1], ranklist[3]], reverse=True) + [x for x in rankset if x != ranklist[1] and x != ranklist[3]])

    elif len(rankset) == 4:
        return 'One Pair', tuple([max(ranklist, key=ranklist.count)] + sorted([x for x in ranklist if x != max(ranklist, key=ranklist.count)], reverse=True))

    else:
        return 'High Card', tuple(sorted(ranklist, reverse=True))

def hands(cards):
    assert(len(cards) == 7)
    foundhands = set()
    for x in cards:
        for y in cards:
            copied = cards.copy()
            if x != y:
                copied.remove(x)
                copied.remove(y)
                foundhands.add(fiveHand(copied))
    return min(foundhands, key=lambda x: handorder.index(x[0]))
