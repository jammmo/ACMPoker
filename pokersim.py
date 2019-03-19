from random import shuffle
from time import sleep
from string import ascii_uppercase

handorder = ['Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House', 'Flush', 'Straight', 'Three of a Kind', 'Two Pair', 'One Pair', 'High Card']
ranks = list(range(2, 15))
suits = ['D', 'S', 'C', 'H']

pot = 0
minimum = 0


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
    def __init__(self, playerID, cards, chips):
        self.cards = cards or []
        self.chips = chips
        self.currentbet = 0
        self.folded = False
        self.hand = None
        self.playerID = playerID
    
    def receivecard(self, item):
        self.cards.append(item)

    def bet(self, board):
        return "Check"
    
    def updatebet(self, amount):
        global pot
        added = amount - self.currentbet
        self.currentbet = amount
        self.chips -= added
        pot += added


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


def betloop(players, bigblind, board):
    global minimum
    x = 0
    while not all((player.currentbet == minimum) for player in players):
        player = players[x]
        if player.folded == False:
            move = player.bet(board)
            if move == "Fold":
                players[x] = None
            elif move == "Check":
                player.updatebet(minimum)
            elif move == "Raise":
                minimum += bigblind
                player.updatebet(minimum)
            if player.chips <= 0:
                player.updatebet(player.currentbet + player.chips)
                players.remove(player)
        x += 1
        if x == len(players):
            x = 0
        print("bets:", [(player.currentbet if not player.folded else "N/A") for player in players])


def gameround(players, bigblind):
    #dealing
    global minimum
    global pot
    deck = [Card(r, s) for r in ranks for s in suits]
    shuffle(deck)
    for _ in range(2):
        for player in players:
            player.receivecard(deck.pop())
    board = []
    print("Players:", [player.playerID for player in players])
    #blinds
    smallblind = bigblind // 2
    players[-2].updatebet(smallblind)
    if players[-2].chips <= 0:
        players[-2].updatebet(players[-2].currentbet + players[-2].chips)
        players.remove(players[-2])
    players[-1].updatebet(bigblind)
    if players[-1].chips <= 0:
        players[-1].updatebet(players[-1].currentbet + players[-1].chips)
        players.remove(players[-1])
    print("bets:", [p.currentbet for p in players])
    minimum = bigblind
    #preflop betting
    betloop(players, bigblind, board)
    #flop
    for _ in range(3):
        board.append(deck.pop())
    betloop(players, bigblind, board)
    #turn
    board.append(deck.pop())
    betloop(players, bigblind, board)
    #river
    board.append(deck.pop())
    betloop(players, bigblind, board)
    #comparing hands
    for player in players:
        player.hand = hands(player.cards + board)
    winner = min(players, key=lambda x: handorder.index(x.hand))
    print("Player ", winner.playerID, ": ", winner.hand, sep='')
    #winner takes pot
    winner.chips += pot
    pot = 0
    minimum = 0
    print("chips:", [x.chips for x in players])
    print()
    for player in players:
        player.cards = []
        player.currentbet = 0
        player.folded = False
        player.hand = None
        
def sortplayerbets(players, left, right): #sorts the players from least to greatest in chips
    if right - left > 1:
        mid = partition(players, left, right)
        sortplayerbets(players, left, mid)
        sortplayerbets(players, mid + 1, right)

def partition(players, left, right):
    i, j, pivot = left, right - 2, right - 1
    while i < j:
        while players[i].chips < players[pivot].chips:
            i += 1
        while i < j and players[j].chips >= players[pivot].chips:
            j -= 1
        if i < j:
            players[i], players[j] = players[j], players[i]
    if players[pivot].chips <= players[i].chips:
        players[pivot], players[i] = players[i], players[pivot]
    return i
        

def AllIn(players): #returns list of pot amounts and list of each player per pot
    sidepots = []
    playersperpot = []
    sortplayerbets(players, 0, len(players))
    while len(players) > 1:
        if players[0].chips <= 0:
            players.remove(players[0])
        bet = players[0].chips
        pot = 0
        playing = []
        for player in players:
            pot += bet
            player.chips -= bet
            playing.append(player) #can change this to return playerID as well
        sidepots.append(pot)
        playersperpot.append(playing)
        playing = []
        players.remove(players[0])
    return sidepots, playersperpot

def startgame(numplayers, startingchips, bigblind):
    players = [Player(ascii_uppercase[num], None, startingchips) for num in range(numplayers)]
    while len(players) >= 2:
        gameround(players, bigblind)
        players.insert(0, players.pop())
        sleep(0.5)

if __name__ == '__main__':
    # 4 players, each starting with 500 chips. Big blind is 50
    startgame(4, 500, 50)
