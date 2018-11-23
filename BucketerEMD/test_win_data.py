
test = "turn"
count = 4
interval = round(1/count, 2)

def read_data():
    if test == "river":
        file = open("river_win_rate.txt", "r")
    elif test == "turn":
        file = open("turn_win_rate.txt", "r")
    elif test == "preflop":
        file = open("preflop_win_rate.txt", "r")
    else:
        file = open("flop_win_rate.txt", "r")
    card_win_rate = []
    card_to_win = dict()
    line = file.readline()
    line = line[:-1]
    id = line.split(":")[1]
    card_win_rate.append(float(id))
    card_to_win[line.split(":")[0]] = float(id)
    while line:
        line = file.readline()
        line = line[:-1]
        if line == "":
            break
        id = line.split(":")[1]
        card_win_rate.append(float(id))
        card_to_win[line.split(":")[0]] = float(id)
    file.close()

    return card_to_win

def analysis_data():
    card_to_win = read_data()
    win_rate_card_dict = dict()
    for i in range(count):
        print('interval:', [round(i * interval, 2), round((i + 1) * interval, 2)])
        if i not in win_rate_card_dict:
            win_rate_card_dict[i] = []
        for key, value in card_to_win.items():
            if i == count -1 :
                if value >= i * interval and value <= (i+1) * interval:
                    win_rate_card_dict[i].append(key)
            else:
                if value >= i * interval and value < (i+1) * interval:
                    win_rate_card_dict[i].append(key)

    for win, card in win_rate_card_dict.items():
        print('--------------------')
        print('interval:', [round(win * interval, 2), round((win + 1) * interval, 2)])
        print('sample count:', len(card))
        print('sample rate:', round(len(card)/len(card_to_win), 2))


if __name__ == "__main__":
    analysis_data()
