import BucketerEMD.settings as settings

test = "flop"

if test == "river":
    file = open("river_cluster_result.txt", "r")
    cluster_count = settings.river_cluster_count
elif test == "turn":
    file = open("turn_cluster_result20.txt", "r")
    cluster_count = settings.turn_cluster_count
else:
    file = open("flop_cluster_result10.txt", "r")
    cluster_count = settings.flop_cluster_count


card_cluster_id = []
cluster_to_card = dict()
line = file.readline()
line = line[:-1]
id = line.split(":")[1]
card = line.split(":")[0]
card_cluster_id.append(int(id))
if id not in cluster_to_card:
    cluster_to_card[id] = []
cluster_to_card[id].append(card)
while line:
    line = file.readline()
    line = line[:-1]
    if line == "":
        break
    id = line.split(":")[1]
    card = line.split(":")[0]
    card_cluster_id.append(int(id))
    if id not in cluster_to_card:
        cluster_to_card[id] = []
    cluster_to_card[id].append(card)
file.close()

print(len(card_cluster_id))
for i in range(1,cluster_count+1):
    print("---- {0} th---:".format(i),card_cluster_id.count(i))