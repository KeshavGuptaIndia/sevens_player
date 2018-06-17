VALUE_TO_INT = {"A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
                     "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}
INT_TO_VALUE = {1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7",
                     8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K"}
SUITES = ["Spades", "Hearts", "Clubs", "Diamonds"]
SUITE_TO_UNICODE = {"Spades": u'\u2660', "Hearts": u'\u2665', "Clubs": u'\u2663', "Diamonds": u'\u2666'}
SHORTHAND_TO_SUITE = {"S": "Spades", "H": "Hearts", "C": "Clubs", "D": "Diamonds"}

class InvalidCardError(ValueError):
    pass

class Card:
    def __init__(self, crd):
        # crd is a two character string:
        # crd[1] = "S", "H", "C", "D"
        # crd[0] = "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"
        self.crd = crd
        self.suite = SHORTHAND_TO_SUITE[crd[-1]]
        self.value = crd[0:-1]

    def __str__(self):
        return "{0} of {1}".format(self.value, self.suite)

    def get_int(self):
        return VALUE_TO_INT[self.value]

    def get_value(self):
        return self.value

    def get_suite(self):
        return self.suite

    def get_parent(self):
        if self.get_int() == 7:
            return None
        elif self.get_int() > 7:
            return Card(str(INT_TO_VALUE[self.get_int()-1])+self.suite[0])
        elif self.get_int() < 7:
            return Card(str(INT_TO_VALUE[self.get_int()+1])+self.suite[0])

    def get_branch(self):
        branch = []
        card = self
        while card.get_distance() != 0:
            card = card.get_parent()
            branch.append(card)
        return branch

    def __hash__(self):
        return hash(self.crd)

    def __eq__(self, other):
        return self.crd == other.crd

    def get_distance(self):
        return abs(self.get_int() - 7)


class Board:
    def __init__(self):
        self.board = {"Spades": [None, None],
                      "Hearts": [None, None],
                      "Clubs": [None, None],
                      "Diamonds": [None, None]}
        self.empty = True

    def play_card(self, card):
        if self.empty:
            if card == Card("7H"):
                self.board["Hearts"] = [7,7]
                self.empty = False
            else:
                raise InvalidCardError
        else:
            if self.board[card.get_suite()] == [None, None]:
                if card.get_int() == 7:
                    self.board[card.get_suite()] = [7, 7]
                else:
                    raise InvalidCardError
            else:
                if card.get_int() == self.board[card.get_suite()][0] - 1:
                    self.board[card.get_suite()][0] -= 1
                elif card.get_int() == self.board[card.get_suite()][1] + 1:
                    self.board[card.get_suite()][1] += 1
                else:
                    raise InvalidCardError

    def is_clear(self, card):
        if self.empty:
            if card == Card("7H"):
                return True
            else:
                return False
        else:
            if self.board[card.get_suite()] == [None, None]:
                if card.get_int() == 7:
                    return True
                else:
                    return False
            else:
                if card.get_int() == self.board[card.get_suite()][0] - 1:
                    return True
                elif card.get_int() == self.board[card.get_suite()][1] + 1:
                    return True
                else:
                    return False

    def __str__(self):
        board_str = "Game Board Situation:\n"
        for i in range(1, 14):
            for suite in SUITES:
                if self.board[suite] != [None, None]:
                    if i >= self.board[suite][0] and i <= self.board[suite][1]:
                        board_str += "  " + INT_TO_VALUE[i] + SUITE_TO_UNICODE[suite] + "\t"
                    else:
                        board_str += "\t"
                else:
                    board_str += "\t"
            board_str += "\n"
        return board_str

class Player:
    def __init__(self, board, hand):
        # hand is a list of cards in hand
        self.board = board
        self.unclear_cards = set()
        self.pri_clear_cards = set()
        self.sec_clear_cards = set()
        for card in hand:
            if self.board.is_clear(card):
                self.pri_clear_cards.add(card)
            else:
                self.unclear_cards.add(card)
        self.update_clarity()

    def update_clarity(self):
        unclear_cards_remove = set()
        sec_clear_cards_remove = set()
        for card in self.unclear_cards:
            if self.board.is_clear(card):
                self.pri_clear_cards.add(card)
                unclear_cards_remove.add(card)
        self.unclear_cards -= unclear_cards_remove
        for card in self.sec_clear_cards:
            if self.board.is_clear(card):
                self.pri_clear_cards.add(card)
                sec_clear_cards_remove.add(card)
        self.sec_clear_cards -= sec_clear_cards_remove
        changes_made = True
        while changes_made:
            changes_made = False
            unclear_cards_remove = set()
            for card in self.unclear_cards:
                if card.get_parent() in self.pri_clear_cards or card.get_parent() in self.sec_clear_cards:
                    self.sec_clear_cards.add(card)
                    unclear_cards_remove.add(card)
                    changes_made = True
            self.unclear_cards -= unclear_cards_remove

    def play_card(self, difficulty = 2):
        # difficulty modes:
        # 0: random card from cleared cards
        # 1: some thought put into playing
        # 2: most thought put into playing
        self.update_clarity()
        if len(self.unclear_cards) == 0:
            print(str(len(self.pri_clear_cards)+len(self.sec_clear_cards)) + " cards, all clear!")
        if len(self.pri_clear_cards) == 0:
            return None
        else:
            if difficulty == 0:
                for card in self.pri_clear_cards:
                    self.pri_clear_cards.remove(card)
                    return card
            elif difficulty == 1:
                card = max(self.pri_clear_cards, key = lambda t: t.get_distance())
                self.pri_clear_cards.remove(card)
                return card
            elif difficulty == 2:
                hold_cards = set(list(self.pri_clear_cards)[:])
                play_cards = set()
                for card in self.unclear_cards:
                    branch = set(card.get_branch())
                    play_cards |= branch & hold_cards
                    hold_cards -= branch
                if len(play_cards):
                    card = max(play_cards, key = lambda t: t.get_distance())
                    self.pri_clear_cards.remove(card)
                    return card
                elif len(hold_cards):
                    card = max(hold_cards, key = lambda t: t.get_distance())
                    self.pri_clear_cards.remove(card)
                    return card

    def dump_hand(self):
        self.update_clarity()
        return "Cards in Hand:\nPrimary Clear Cards: " + str([str(card) for card in self.pri_clear_cards]) +\
                "\nSecondary Clear Cards: " + str([str(card) for card in self.sec_clear_cards]) +\
                "\nUnclear Cards: " + str([str(card) for card in self.unclear_cards])

if __name__ == "__main__":
    print("Enter cards in player hand in the format 7H, JD, 8S, AC, etc (Q to end):")
    hand = []
    while True:
        try:
            inp = input()
            if inp == "Q":
                break
            else:
                card = Card(inp)
                print(card)
                hand.append(card)
        except:
            continue
    board = Board()
    player = Player(board, hand)
    while True:
        print("***********************************************")
        print(board)
        print("***********************************************")
        print(player.dump_hand())
        print("***********************************************")
        print("Enter choice:\n 1. Enter someone else's move\n 2. Play a card\n 3. Exit")
        i = int(input())
        print("***********************************************")
        try:
            if i == 1:
                try:
                    board.play_card(Card(input()))
                except InvalidCardError:
                    print("Invalid Card!")
                    input()
            elif i == 2:
                card = player.play_card()
                if card is not None:
                    print("I played:", card)
                    board.play_card(card)
                else:
                    print("I pass!")
                input()
            elif i == 3:
                break
        except e:
            print(e)
        print("***********************************************")
