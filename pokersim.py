from pokercards import handorder, Card, hands
from random import shuffle, randint
from time import sleep
from string import ascii_uppercase

ranks = list(range(2, 15))
suits = ['D', 'S', 'C', 'H']

class Game:
    def __init__(self, numplayers, startingchips, bigblind):
        self.players = [Player(ascii_uppercase[num], startingchips, self) for num in range(numplayers)]
        self.activeplayers = set(self.players)
        self.blindsequence = self.players.copy()
        self.bigblind = bigblind
        self.smallblind = bigblind // 2
        self.board = []
        self.bettinground = None
        self.pot = 0
        self.minimum = 0
        self.rounds = 0

    def resetround(self):
        self.activeplayers = set(self.players)
        self.pot = 0
        self.minimum = 0
        self.board = []
        self.bettinground = None
        for player in self.players:
            player.roundinit()

    def eliminate(self, player):
        self.players.remove(player)
        self.blindsequence.remove(player)
        self.activeplayers.discard(player)


class Player:
    def __init__(self, playerID, chips, game):
        self.chips = chips
        self.playerID = playerID
        self.game = game
        self.roundinit()

    def roundinit(self):
        self.cards = []
        self.currentbet = 0
        self.bethistory = []
        self.coefficients = None
        self.lastbet = 0
        self.hand = None
        self.allin = False
        self.folded = False
    
    def receivecard(self, item):
        self.cards.append(item)

    def bet(self, game, first):
        if self.coefficients is not None:
            c = {}
            coefficientnames = ('initial', 'preflop_before', 'preflop_after', 'flop_card1', 'flop_card2', 'flop_card3', 'flop_before', 'flop_after',
            'turn_card', 'turn_before', 'turn_after', 'river_card', 'river_before', 'river_after')
            for i in range(len(coefficientnames)):
                c[coefficientnames[i]] = self.coefficients[i]

            if game.bettinground == "preflop" and first:
                betamount = c['initial'] + (c['preflop_before'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1)))

            elif game.bettinground == "preflop":
                betamount = c['preflop_after'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1))

            elif game.bettinground == "flop" and first:
                betamount = (c['flop_card1'] * game.board[0].rank) + (c['flop_card2'] * game.board[1].rank) + (c['flop_card3'] * game.board[2].rank) + (c['flop_before'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1)))

            elif game.bettinground == "flop":
                betamount = c['flop_after'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1))

            elif game.bettinground == "turn" and first:
                betamount = (c['turn_card'] * game.board[3].rank) + (c['turn_before'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1)))

            elif game.bettinground == "turn":
                betamount = c['turn_after'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1))

            elif game.bettinground == "river" and first:
                betamount = (c['river_card'] * game.board[4].rank) + (c['river_before'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1)))

            elif game.bettinground == "river":
                betamount = c['river_after'] * (sum([game.players[x].lastbet for x in range(1, len(game.players))]) / (len(game.players) - 1))
            if betamount + self.currentbet < game.minimum:
                return "Fold"
            if betamount + self.currentbet < game.minimum + game.bigblind:
                return "Check"
            else:
                return (int(betamount)//game.bigblind)*game.bigblind
        else:
            r = randint(1, 10)
            if r == 1:
                return "Fold"
            elif r == 2:
                return "Raise"
            else:
                return "Check"
    
    def updatebet(self, amount):
        added = amount - self.currentbet
        assert(added >= 0)
        if added > self.chips:
            self.allin = True
            print('*** Player ' + self.playerID + "'s all in!")
            self.currentbet += self.chips
            self.lastbet = self.chips
            self.game.pot += self.chips
            self.chips = 0
            self.game.activeplayers.remove(self)
        else:
            self.currentbet = amount
            self.lastbet = added
            self.chips -= added
            self.game.pot += added

    def __repr__(self):
        return 'Player ' + self.playerID


def printbets(G):
    print("Bets:", end='\t\t')
    print(*[p.currentbet for p in G.players], sep='\t')

def printchips(G):
    print("Chips:", end='\t\t')
    print(*[p.chips for p in G.players], sep='\t')

def printplayers(G):
    print("Players:", end='\t')
    print(*[p.playerID for p in G.players], sep='\t')

def printblinds(G):
    print("Blinds:", end='\t\t')
    print(*[p.currentbet for p in G.players], sep='\t')


def betloop(G, bettinground):
    G.bettinground = bettinground
    x = 0
    once = True
    while len(G.activeplayers) >= 2 and (once or not all((player.currentbet == G.minimum) for player in G.activeplayers)):
        player = G.blindsequence[x]
        if player in G.activeplayers:
            move = player.bet(G, once)
            if move == "Fold":
                player.folded = True
                G.activeplayers.remove(player)
                print('***', player, 'folds!')
            elif move == "Check":
                player.updatebet(G.minimum)
            elif move == "Raise":
                player.updatebet(G.minimum + G.bigblind)
                G.minimum = max(G.minimum, player.currentbet)
            elif type(move) is not str:
                player.updatebet(player.currentbet + move)
                G.minimum = max(G.minimum, player.currentbet)
        x += 1
        if x == len(G.blindsequence):
            x = 0
            if once:
                once = False
        printbets(G)
    for p in G.players:
        p.bethistory.append(G.players[0].currentbet)


def gameround(G, reset=True):
    #dealing
    G.rounds += 1
    print('Round', G.rounds)
    deck = [Card(r, s) for r in ranks for s in suits]
    shuffle(deck)
    for _ in range(2):
        for player in G.players:
            player.receivecard(deck.pop())
    printplayers(G)
    printchips(G)
    #machine learning!!
    #G.players[0].coefficients = basic_14_output()
    if G.players[0].playerID == 'A':
        G.players[0].coefficients = (50,1,1,1,1,1,1,1,1,1,1,1,1,1)
    #blinds
    G.blindsequence[-2].updatebet(G.smallblind)
    G.blindsequence[-1].updatebet(G.bigblind)
    printblinds(G)
    G.minimum = G.bigblind
    #preflop betting
    betloop(G, "preflop")
    #flop
    for _ in range(3):
        G.board.append(deck.pop())
    betloop(G, "flop")
    #turn
    G.board.append(deck.pop())
    betloop(G, "turn")
    #river
    G.board.append(deck.pop())
    betloop(G, "river")
    #comparing hands
    determinewinner(G)
    printchips(G)
    print('_'*80, end='\n\n')
    #reset game for next round
    if reset:
        pcopy = G.players.copy()
        for player in pcopy:
            if player.chips == 0:
                G.eliminate(player)
        G.resetround()


def determinewinner(G):
    #comparing hands
    for player in G.players:
        player.hand = hands(player.cards + G.board)
    if any(x.allin for x in G.players):
        sidepots, playersperpot = allIn(G)
    else:
        sidepots = [G.pot]
        playersperpot = [[p for p in G.players if (p.folded is False)]]
    for i in range(len(sidepots)):
        pot = sidepots[i]
        winninghand = min([x.hand[0] for x in playersperpot[i]], key=lambda x: handorder.index(x))
        possiblewinners = [x for x in playersperpot[i] if x.hand[0] == winninghand]
        if len(possiblewinners) == 1:
            winner = possiblewinners[0]
            if len(sidepots) == 1:
                print("*** Player", winner.playerID, "wins the round:", winner.hand[0])
            else:
                print('*** Player', winner.playerID, 'wins a sidepot:', winner.hand[0] + ';', 'Sidepot:', pot, playersperpot[i])
            #winner takes pot / sidepot
            winner.chips += pot
        else:
            possiblewinners.sort(key=lambda x: x.hand[1], reverse=True)
            winners = [x for x in possiblewinners if x.hand == possiblewinners[0].hand]
            if len(winners) == 1:
                winner = winners[0]
                if len(sidepots) == 1:
                    print("*** Player", winner.playerID, "wins the round:", winner.hand[0])
                else:
                    print('*** Player', winner.playerID, 'wins a sidepot:', winner.hand[0] + ';', 'Sidepot:', pot, playersperpot[i])
                #winner takes pot / sidepot
                winner.chips += pot
            else:
                #multiple winners in one sidepot - split the sidepot!
                amount = pot // len(winners)
                amounts = [amount]*len(winners)
                for x in range(pot % len(winners)):
                    amounts[x] += 1
                for x in range(len(winners)):
                    winners[x].chips += amounts[x]
                    if len(sidepots) == 1:
                        print("*** Player", winners[x].playerID, "wins part of pot:", winners[x].hand[0] + ';', 'Amount:', amounts[x])
                    else:
                        print("*** Player", winners[x].playerID, "wins part of sidepot:", winners[x].hand[0] + ';', 'Amount:', amounts[x], playersperpot[i])


def allIn(G): #returns list of pot amounts and list of each player per pot
    sidepots = []
    playersperpot = []
    players = [[x, x.currentbet] for x in G.players if (x.folded is False)]
    players.sort(key=lambda x: x[1])
    while len(players) > 0:
        if players[0][1] == 0:
            players.remove(players[0])
        else:
            bet = players[0][1]
            pot = 0
            playing = []
            for player in players:
                pot += bet
                player[1] -= bet
                playing.append(player[0])
            sidepots.append(pot)
            playersperpot.append(playing)
            playing = []
            players.remove(players[0])
    return sidepots, playersperpot


def startgame(numplayers, startingchips, bigblind):
    G = Game(numplayers, startingchips, bigblind)
    while len(G.players) >= 2:
        gameround(G)
        G.blindsequence.insert(0, G.blindsequence.pop())
        #sleep(1)
    print('***', G.players[0], 'wins after', G.rounds, 'rounds!')


if __name__ == '__main__':
    # 4 players, each starting with 480 chips. Big blind is 50
    startgame(4, 480, 50)
