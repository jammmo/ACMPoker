from pokercards import handorder, Card, hands
from random import shuffle
from time import sleep
from string import ascii_uppercase
from random import randint

ranks = list(range(2, 15))
suits = ['D', 'S', 'C', 'H']

class Game:
    def __init__(self, numplayers, startingchips, bigblind):
        self.players = [Player(ascii_uppercase[num], None, startingchips, self) for num in range(numplayers)]
        self.activeplayers = set(self.players)
        self.blindsequence = self.players.copy()
        self.bigblind = bigblind
        self.smallblind = bigblind // 2
        self.board = []
        self.pot = 0
        self.minimum = 0
        self.rounds = 0

    def resetround(self):
        self.activeplayers = set(self.players)
        self.minimum = 0
        self.board = []
        for player in self.players:
            player.cards = []
            player.currentbet = 0
            player.hand = None
            player.allin = False
            player.folded = False

    def eliminate(self, player):
        self.players.remove(player)
        self.blindsequence.remove(player)
        self.activeplayers.discard(player)


class Player:
    def __init__(self, playerID, cards, chips, game):
        self.cards = cards or []
        self.chips = chips
        self.currentbet = 0
        self.hand = None
        self.allin = False
        self.folded = False
        self.playerID = playerID
        self.game = game
    
    def receivecard(self, item):
        self.cards.append(item)

    def bet(self, game):
        r = randint(1, 10)
        if r == 1:
            return "Fold"
        elif r == 2:
            return "Raise"
        else:
            return "Check"
    
    def updatebet(self, amount):
        added = amount - self.currentbet
        if added > self.chips:
            self.allin = True
            print('*** Player ' + self.playerID + "'s all in!")
            self.currentbet += self.chips
            self.game.pot += self.chips
            self.chips = 0
            self.game.activeplayers.remove(self)
        else:
            self.currentbet = amount
            self.chips -= added
            self.game.pot += added

    def __repr__(self):
        return 'Player ' + self.playerID


def betloop(G):
    x = 0
    while not all((player.currentbet == G.minimum) for player in G.activeplayers):
        player = G.blindsequence[x]
        if player in G.activeplayers:
            move = player.bet(G)
            if move == "Fold":
                player.folded = True
                G.activeplayers.remove(player)
                print('***', player, 'folds!')
            elif move == "Check":
                player.updatebet(G.minimum)
            elif move == "Raise":
                G.minimum += G.bigblind
                player.updatebet(G.minimum)
        x += 1
        if x == len(G.blindsequence):
            x = 0
        print("Bets:", end='\t\t')
        print(*[p.currentbet for p in G.players], sep='\t')


def gameround(G):
    #dealing
    G.rounds += 1
    print('Round', G.rounds)
    players = G.players
    deck = [Card(r, s) for r in ranks for s in suits]
    shuffle(deck)
    for _ in range(2):
        for player in G.players:
            player.receivecard(deck.pop())
    print("Players:", end='\t')
    print(*[player.playerID for player in G.players], sep='\t')
    print("Chips:", end='\t\t')
    print(*[x.chips for x in players], sep='\t')
    #blinds
    G.blindsequence[-2].updatebet(G.smallblind)
    G.blindsequence[-1].updatebet(G.bigblind)
    print("Blinds:", end='\t\t')
    print(*[p.currentbet for p in players], sep='\t')
    G.minimum = G.bigblind
    #preflop betting
    betloop(G)
    #flop
    for _ in range(3):
        G.board.append(deck.pop())
    betloop(G)
    #turn
    G.board.append(deck.pop())
    betloop(G)
    #river
    G.board.append(deck.pop())
    betloop(G)
    #comparing hands
    for player in players:
        player.hand = hands(player.cards + G.board)
    if any(x.allin for x in G.players):
        sidepots, playersperpot = allIn(G)
        for i in range(len(sidepots)):
            pot = sidepots[i]
            winninghand = min([x.hand[0] for x in playersperpot[i]], key=lambda x: handorder.index(x))
            possiblewinners = [x for x in playersperpot[i] if x.hand[0] == winninghand]
            if len(possiblewinners) == 1:
                winner = possiblewinners[0]
                print('*** Player', winner.playerID, 'wins a sidepot:', winner.hand[0] + ';', 'Sidepot:', pot, playersperpot[i])
                #winner takes sidepot
                winner.chips += pot
            else:
                possiblewinners.sort(key=lambda x: x.hand[1], reverse=True)
                winners = [x for x in possiblewinners if x.hand == possiblewinners[0].hand]
                if len(winners) == 1:
                    winner = winners[0]
                    print('*** Player', winner.playerID, 'wins a sidepot:', winner.hand[0] + ';', 'Sidepot:', pot, playersperpot[i])
                    #winner takes sidepot
                    winner.chips += pot
                else:
                    #multiple winners in one sidepot - split the sidepot!
                    amount = pot // len(winners)
                    amounts = [amount]*len(winners)
                    for x in range(pot % len(winners)):
                        amounts[x] += 1
                    for x in range(len(winners)):
                        winners[x].chips += amounts[x]
                        print("*** Player", winners[x].playerID, "wins part of sidepot:", winners[x].hand[0] + ';', 'Amount:', amounts[x], playersperpot[i])
    else:
        winninghand = min([x.hand[0] for x in G.activeplayers], key=lambda x: handorder.index(x))
        possiblewinners = [x for x in G.activeplayers if x.hand[0] == winninghand]
        if len(possiblewinners) == 1:
            winner = possiblewinners[0]
            print("*** Player", winner.playerID, "wins the round:", winner.hand[0])
            #winner takes pot
            winner.chips += G.pot
        else:
            possiblewinners.sort(key=lambda x: x.hand[1], reverse=True)
            winners = [x for x in possiblewinners if x.hand == possiblewinners[0].hand]
            if len(winners) == 1:
                winner = winners[0]
                print("*** Player", winner.playerID, "wins the round:", winner.hand[0])
                #winner takes pot
                winner.chips += G.pot
            else:
                #multiple winners - split pot
                amount = G.pot // len(winners)
                amounts = [amount]*len(winners)
                for x in range(G.pot % len(winners)):
                    amounts[x] += 1
                for x in range(len(winners)):
                    winners[x].chips += amounts[x]
                    print("*** Player", winners[x].playerID, "wins part of pot:", winners[x].hand[0] + ';', 'Amount:', amounts[x])
    G.pot = 0
    print("Chips:", end='\t\t')
    print(*[x.chips for x in players], sep='\t')
    print('_'*80)
    print()
    #reset game for next round
    for player in players:
        if player.chips == 0:
            G.eliminate(player)
    G.resetround()


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
