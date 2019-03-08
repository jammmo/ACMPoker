from random import shuffle

pot = 0
minimum = 0

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __repr__(self):
        return self.rank + '-' + self.suit

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

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = ['D', 'S', 'C', 'H']
deck = [Card(r, s) for r in ranks for s in suits]
shuffle(deck)

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