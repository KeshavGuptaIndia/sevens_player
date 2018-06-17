from sevens import *

hand = [Card("7C"), Card("8C"), Card("6H"), Card("KC")]
board = Board()
player = Player(board, hand)
while True:
    print("***********************************")
    print("1. Enter someone else's move:\n2. Play a card")
    inp = int(input())
    print("***********************************")
    try:
        if inp == 1:
            board.play_card(Card(input()))
        if inp == 2:
            card = player.play_card()
            if card is not None:
                print("I played:", card)
                board.play_card(card)
            else:
                print("I passed!")
            input()
        print(board)
        print("***********************************")
        print(player.dump_hand())
        print("***********************************")
    except:
        continue
