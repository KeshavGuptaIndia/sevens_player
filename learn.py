from sevens import *
from time import sleep
import numpy as np

win_alpha = 1.0
lose_alpha = 0.0
wins_fos = 0
points_fos = 0
training_trials = 200
max_iterations = 10000

possible_parent_child_pairs = []
for i in range(2, 8):
    for j in range(1,i):
        possible_parent_child_pairs.append((i,j))
for i in range(7, 13):
    for j in range(i+1, 14):
        possible_parent_child_pairs.append((i,j))
num_pairs = len(possible_parent_child_pairs)
pair_lookup_indexes = {possible_parent_child_pairs[idx]: idx for idx in range(len(possible_parent_child_pairs))}
hold_card_weights = np.array([0.0 for _ in range(14)])
play_card_weights = np.array([0.0 for _ in possible_parent_child_pairs])

def whc(card):
    return hold_card_weights[card.get_int()]

def wpc(card):
    # weight of hold card
    i = card.get_int()
    j = card.child.get_int()
    return play_card_weights[pair_lookup_indexes[(i,j)]]

deck = []
for v in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]:
    for s in ["S", "H", "C", "D"]:
        deck.append(Card(v+s))

try:
    best_wins = 0
    best_points = float('inf')
    itr = 0
    while itr < max_iterations:
        hold_cards_delta = np.random.random(14)
        play_cards_delta = np.random.random(num_pairs)
        hold_card_weights += hold_cards_delta*win_alpha
        play_card_weights += play_cards_delta*win_alpha
        wins = 0
        points = 0
        for i in range(training_trials):
            np.random.shuffle(deck)

            board = Board()

            # the first three are bots with fixed strategy
            p1 = Player(board, deck[0:13])
            p2 = Player(board, deck[13:26])
            p3 = Player(board, deck[26:39])
            # p4 is the bot under training
            p4 = Player(board, deck[39:52])

            while True:
                try:
                    p1.play_card(difficulty = 0)
                    p2.play_card(difficulty = 0)
                    p3.play_card(difficulty = 0)
                except GameOverException:
                    points += p4.value()
                    break
                try:
                    p4.play_card(difficulty = 3, get_weight_hold_card = whc, get_weight_play_card = wpc)
                except GameOverException:
                    wins += 1
                    break
        if wins > best_wins + training_trials*wins_fos:# and points < best_points - training_trials*points_fo:
            # success!
            best_wins = wins
            best_points = points
            result = "*************Passed, best_wins = " + str(best_wins)
        else:
            # not too good or bad, try other random nudges
            hold_card_weights -= hold_cards_delta*win_alpha
            play_card_weights -= play_cards_delta*win_alpha
            result = "No Change, wins = " + str(wins)
        print("Completed learning iteration {0}. Result: {1}".format(str(itr), result))
        itr += 1
except KeyboardInterrupt:
    pass
print("hold_card_weights:\n", hold_card_weights)
print("play_card_weights:\n", play_card_weights)
print("wins:", best_wins)
print("points:", best_points)
