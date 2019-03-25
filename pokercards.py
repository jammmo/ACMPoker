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
    if len(suitset) == 1 and rankset == {14, 13, 12, 11, 10}:
        return 'Royal Flush'
    elif len(suitset) == 1 and any(rankset == set(range(x, x+5)) for x in range(2, 10)):
        return 'Straight Flush'
    elif len(suitset) == 1 and rankset == {14, 2, 3, 4, 5}:   #case where ace is low
        return 'Straight Flush'
    elif len(rankset) == 2 and [x.rank for x in cards].count(cards[0].rank) in {1, 4}:
        return 'Four of a Kind'
    elif len(rankset) == 2 and [x.rank for x in cards].count(cards[0].rank) in {2, 3}:
        return 'Full House'
    elif len(suitset) == 1:
        return 'Flush'
    elif any(rankset == set(range(x, x+5)) for x in range(2, 10)):
        return 'Straight'
    elif rankset == {14, 2, 3, 4, 5}:   #case where ace is low
        return 'Straight'
    elif any([x.rank for x in cards].count(y) == 3 for y in rankset):
        return 'Three of a Kind'
    elif len(rankset) == 3:
        return 'Two Pair'
    elif len(rankset) == 4:
        return 'One Pair'
    else:
        return 'High Card'

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
    return min(foundhands, key=lambda x: handorder.index(x))