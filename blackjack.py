from random import shuffle

class Card:
    '''Instance of a single card, numeric rank 1-14, suited'''
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        face_cards = {1:'Ace', 11:'Jack', 12:'Queen', 13:'King'}
        face_card = face_cards.get(self.rank, str(self.rank))
        return "%s of %s" % (face_card, self.suit)


class Deck(object):
    '''Instance of a standard-ordered 52-card deck'''
    def __init__(self):
        self.suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
        self.cards = []
        self.build_deck()

    def __getitem__(self, index):
        return self.cards[index]

    def build_deck(self):
        """Create a list containing ordered playing cards."""
        for suit in self.suits:
            for rank in range(1,14):
                self.cards.append(Card(rank, suit))
                    

class Shoe(object):
    '''Instance of a shoe of decks, initialized shuffled'''
    def __init__(self, deck_count=6, shuffle_times=7):
        self.deck_count = deck_count
        self.shuffle_times = shuffle_times
        self.shoe = []
        self.fill_shoe()
        self.shuffle()

    def fill_shoe(self):
        """Build a list containing specified number of decks."""
        for deck in range(self.deck_count):
            self.shoe += Deck().cards

    def shuffle(self):
        """Shuffle the shoe list."""
        for i in range(self.shuffle_times):
            shuffle(self.shoe)

    def deal_card(self):
        """Returns card from shoe. Shoe is refilled if empty."""
        if len(self.shoe) == 0:
            self.fill_shoe()
            self.shuffle()
        self.dealt_card = self.shoe.pop(0)
        #self.shoe.append(self.dealt_card) # return card to back of shoe
        return self.dealt_card


class Hand(object):
    '''Hand object, handles scoring and available options'''
    def __init__(self, owner_id):
        self.id = owner_id
        self.reset()

    def __repr__(self):
        return str(self.hand)

    def __getitem__(self, index):
        return(self.hand[index])

    def length(self):
        return len(self.hand)

    def reset(self):
        self.hand = []
        self.bet = 0
        self.insurance = 0
        self.split_option = False
        self.double_option = False
        self.bust = False
        self.stand = False
        self.blackjack = False

    def score_card(self, card):
        """Score an individual card, noting aces."""
        if card.rank == 1:
            self.score += 11
            self.aces += 1
        elif card.rank > 10:
            self.score += 10
        else:
            self.score += card.rank

    def handle_aces(self):
        """Modifies the card value of aces as needed, updates self.score."""
        while self.aces > 0 and self.score > 21:
            self.score -= 10
            self.aces -= 1

    def check_options(self):
        """Checks for and sets blackjack and split_option flags."""
        if len(self.hand) == 2:
            if self.score == 21:
                self.blackjack = True
                self.stand = True
            if self.hand[0].rank == self.hand[1].rank:
                self.split_option = True

    def score_hand(self):
        """Determines the value of self.hand and options available."""
        self.score = 0
        self.aces = 0
        for card in self.hand:
            self.score_card(card)
        self.handle_aces()
        if self.score < 21:
            self.double_option = True
        if self.score > 21:
            self.busted()
        return(self.score)

    def hit(self, card):
        '''Add card to hand, returns updated score.'''
        self.hand.append(card)
        self.score = self.score_hand()
        return self.score

    def increase_bet(self, points):
        self.bet += points
        return self.bet

    def reset_bet(self):
        self.bet = 0

    def insurance_bet(self, points):
        self.insurance = self.bet*0.5
        return self.insurance

    def standed(self):
        self.stand = True
        return self.stand

    def busted(self):
        self.standed()
        self.bust = True
        return self.bust


class Dealer(object): # TODO: Player class should inherit from dealer
    '''Dealer player object, with attributes for tracking statistics. Dealer ID is set to 0.'''
    def __init__(self):
        self.wins = 0 # TODO: check if this is incremented
        self.busts = 0
        self.pushes = 0
        self.hand = Hand(owner_id=0) 

    def __repr__(self):
        return("Score: %s, Hand: %s\nBusts: %s, Pushes: %s\n" %(self.hand.score_hand(),
                                                                         self.hand,
                                                                         self.busts,
                                                                         self.pushes))
    def take_card(self, card):
        self.hand.hit(card)
        return self.hand


class Player(object):
    def __init__(self, player_id, human=False):
        self.id = player_id
        self.human = human
        self.balance = 0
        self.hand = Hand(self.id)
        self.wins = 0
        # TODO: implement increment of bust count when hand is scored >21
        self.busts = 0 # BUG: handled in Hand(), not updated in case of bust
               
    def __repr__(self):
        return("Score: %s, Hand: %s\nWins: %s, Busts: %s, Balance: %s\n" %(self.hand.score_hand(),
                                                                           self.hand,
                                                                           self.wins,
                                                                           self.busts,
                                                                           self.balance))

    def add_balance(self, points):
        self.balance += points
        return self.balance

    def dec_balance(self, points):
        self.balance -= points
        return self.balance

    def take_card(self, card):
        self.hand.hit(card)
        return self.hand

    def bet(self, points):
        self.balance -= points
        self.hand.increase_bet(points)
        return self.hand.bet


class Table(object):
    def __init__(self, num_decks=6, limit=400, debug=False):
        self.debug = debug
        self.num_decks = num_decks
        self.shoe = Shoe(self.num_decks)
        self.dealer = Dealer()
        self.players = {} # k,v = id,player
        self.limit = limit # table bet limit

    def add_player(self, player):
        self.players[player.id] = player

    def remove_player(self, player_id):
        self.players = {key: value for key, value in self.players.items()
                        if key is not player_id}
        
    def determine_winner(self, player_id):
        player = self.players[player_id]
        if not self.determine_blackjack(player):
            if not self.determine_push(player):
                if not player.hand.bust:
                    if self.dealer.hand.bust:
                        self.pay_win(player)
                        player.wins += 1
                    elif player.hand.score > self.dealer.hand.score:
                        self.pay_win(player)
                        player.wins += 1
        player.hand.reset_bet()

    def determine_blackjack(self, player): # TODO: Determine if blackjack requires a jack
        if player.hand.length() == 2:
            if player.hand.score == 21:
                # need to check for dealer blackjack before paying
                self.pay_blackjack(player)
                player.wins += 1
                return True
                
    def determine_push(self, player):
        if player.hand.score == self.dealer.hand.score:
            if not player.hand.bust:
                self.pay_push(player)
                self.dealer.pushes += 1
                return True

    def pay_win(self, player):
        if self.debug:
            print('paying win')
        player.add_balance(player.hand.bet*2)

    def pay_blackjack(self, player):
        if self.debug:
            print('paying blackjack')
        player.add_balance(player.hand.bet*1.5) # This doesn't seem right, blackjack pays less than any other win?
        
    def pay_push(self, player):
        if self.debug:
            print('paying push')
        player.add_balance(player.hand.bet)

    def pay_insurance(self, player):
        if self.debug:
            print('paying insurance')
        player.add_balance(player.hand.insurance*3)

    def change_shoe(self):
        if self.debug:
            print('changing shoe')
        self.shoe = Shoe(self.num_decks)
        return self.shoe

    def deal_players(self):
        if self.debug:
            print('dealing card to players')
        for player in self.players:
            self.players[player].take_card(self.shoe.deal_card())

    def deal_dealer(self):
        if self.debug:
            print('dealing card to dealer')
        self.dealer.take_card(self.shoe.deal_card())

            
