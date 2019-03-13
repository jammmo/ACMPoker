from random import shuffle

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __lt__(self, other):
        return self.rank < other.rank

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __repr__(self):
        return str(self.rank) + '-' + self.suit

class Player:
    def __init__(self, cards, chips):
        self.cards = cards or []
        self.chips = chips
        self.currentbet = 0
        self.folded = False
    
    def append(self, item):
        self.cards.append(item)

    def bet(self, board):
        return "Check"
    
    def updatebet(self, amount):
        global pot
        added = amount - self.currentbet
        self.currentbet = amount
        self.chips -= added
        pot += added


handorder = ['Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight', 'Three of a Kind', 'Two Pair', 'One Pair', 'High Card']
ranks = list(range(2, 15))
suits = ['D', 'S', 'C', 'H']

pot = 0
minimum = 0
deck = [Card(r, s) for r in ranks for s in suits]
shuffle(deck)


def highestHand(cards):
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
    foundhands = {}
    for x in cards:
        for y in cards:
            copied = cards.copy()
            if x != y:
                copied.remove(x)
                copied.remove(y)
                newhand = highestHand(copied)
                if newhand in foundhands:
                    foundhands[newhand].append(cards)
                else:
                    foundhands[highestHand(copied)] = [cards]
    return foundhands

def game(numplayers, startingchips, bigblind):
    #dealing
    global minimum
    global pot
    board = []
    players = [Player(None, startingchips) for _ in range(numplayers)]
    for _ in range(2):
        for P in players:
            P.append(deck.pop())
    #blinds
    smallblind = bigblind // 2
    players[-2].updatebet(smallblind)
    players[-1].updatebet(bigblind)
    print([p.currentbet for p in players])
    minimum = bigblind
    #preflop betting
    betloop(players, bigblind, board)
    #flop
    for _ in range(3):
        board.append(deck.pop())
    #flop betting
    betloop(players, bigblind, board)
    #turn
    board.append(deck.pop())
    #turn betting
    betloop(players, bigblind, board)
    #river
    board.append(deck.pop())
    #river betting
    betloop(players, bigblind, board)
    #NEED TO ADD - comparing hands, winner takes pot

def betloop(players, bigblind, board):
    global minimum
    x = 0
    while not all((player.currentbet == minimum) for player in players):
        player = players[x]
        if player is not None:
            move = player.bet(board)
            if move == "Fold":
                players[x] = None
            elif move == "Check":
                player.updatebet(minimum)
            elif move == "Raise":
                minimum += bigblind
                player.updatebet(minimum)
        x += 1
        if x == len(players):
            x = 0
        print([(p.currentbet if p is not None else None) for p in players])

if __name__ == '__main__':
    # 4 players, each starting with 500 chips. Big blind is 50
    game(4, 500, 50)