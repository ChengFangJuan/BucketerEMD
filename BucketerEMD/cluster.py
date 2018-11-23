import numpy
from pyemd import emd
import random
import math
import BucketerEMD.settings as settings

userArgs = None

class Clustering():

    def __init__(self, street = None):
        self.street = street
        self.DataPoints = self.get_data_set()
        self.file = open(self.open_file(), 'w')
        self.get_centroids()

    def get_data_set(self):
        dataPoints = []
        if self.street == "river":
            file_name = "river_data.csv"
            self.cluster_state_count = 1
            self.cluster_count = settings.river_cluster_count
        elif self.street == "turn":
            file_name = "turn_data.csv"
            self.cluster_state_count = settings.river_cluster_count
            self.cluster_count = settings.turn_cluster_count
        else:
            file_name = "flop_data.csv"
            self.cluster_state_count = settings.turn_cluster_count
            self.cluster_count = settings.flop_cluster_count

        with open(file_name) as file:
            for line in file:
                string_line = line.split(",")
                dataPoint = []
                for i in range(self.cluster_state_count):
                    line_ = float(string_line[i])
                    dataPoint.append(line_)
                dataPoints.append(dataPoint)
        return dataPoints

    def open_file(self):
        if self.street == "river":
            file_name = "river_cluster.csv"
        elif self.street == "turn":
            file_name = "turn_cluster.csv"
        else:
            file_name = "flop_cluster.csv"
        return file_name

    def get_centroids(self):
        if self.street == "turn":
            self.centroids_river = self._get_centroids_street('river')
        elif self.street == 'flop':
            self.centroids_river = self._get_centroids_street('river')
            self.centroids_turn = self._get_centroids_street('turn')

    def _get_centroids_street(self, street_type):
        centroids = []
        file_name = ""
        if street_type == "river":
            file_name = "river_cluster.csv"
            self.state_count = 1
        elif street_type == "turn":
            file_name = "turn_cluster.csv"
            self.state_count = settings.river_cluster_count
        elif street_type == "flop":
            file_name = "flop_cluster.csv"
            self.state_count = settings.turn_cluster_count
        else:
            print("The file name is None")

        with open(file_name) as file:
            for line in file:
                string_line = line.split(",")
                centroid = []
                for i in range(self.state_count):
                    line_ = float(string_line[i])
                    centroid.append(line_)
                centroids.append(centroid)

        return centroids

    def computer_distance_matrix(self):

        if self.street == 'turn':
            matrix = numpy.zeros([settings.river_cluster_count, settings.river_cluster_count])
            for i in range(settings.river_cluster_count):
                for j in range(settings.river_cluster_count):
                    matrix[i][j] = math.pow(self.centroids_river[i][0]-self.centroids_river[j][0],2)
        elif self.street == 'flop':
            matrix = numpy.zeros([settings.turn_cluster_count, settings.turn_cluster_count])
            matrix_turn = numpy.zeros([settings.river_cluster_count, settings.river_cluster_count])
            for i in range(settings.river_cluster_count):
                for j in range(settings.river_cluster_count):
                    matrix_turn[i][j] = math.pow(self.centroids_river[i][0]-self.centroids_river[j][0],2)
            for i in range(settings.turn_cluster_count):
                for j in range(settings.turn_cluster_count):
                    matrix[i][j] = emd(numpy.array(self.centroids_turn[i]),numpy.array(self.centroids_turn[j]), matrix_turn)
        else:
            pass
            matrix = numpy.array([[0,1/3.0,2/3.0],[1/3.0,0,1/3.0],[2/3.0,1/3.0,0]])
        return matrix


    def points_best_cluster(self, centroids, dataPoint):
        closestCentroid = None
        leastDistance = None
        # matrix = numpy.array([[0,1/3.0,2/3.0],[1/3.0,0,1/3.0],[2/3.0,1/3.0,0]])
        matrix = self.computer_distance_matrix()
        for i in range(len(centroids)):
            if self.street == "river":
                distance = math.pow(dataPoint[0] - centroids[i][0], 2)
            else:
                distance = emd(numpy.array(dataPoint),numpy.array(centroids[i]),matrix)
            #print(distance)
            if (leastDistance == None or distance < leastDistance ):
                closestCentroid = i
                leastDistance = distance

        return closestCentroid

    def new_centroid(self, cluster):
        if self.street == "river":
            temp_out = []
            for i in range(len(cluster)):
                temp_out.append(cluster[i][0])
            out = sum(temp_out) / len(temp_out)
        else:
            out = numpy.mean(cluster, axis = 0)
            out = out.tolist()

        return out

    def configure_clusters(self, centroids, dataPoints):
        clusters = []
        for i in range(len(centroids)):
            cluster = []
            clusters.append(cluster)

        for i in range(len(dataPoints)):
            idealCluster = self.points_best_cluster(centroids, dataPoints[i])
            clusters[idealCluster].append(dataPoints[i])
        max = 0
        max_index = 0
        blank = []
        for i in range(len(clusters)):
            if len(clusters[i]) > max:
                max = len(clusters[i])
                max_index = i
            if len(clusters[i]) == 0:
                blank.append(i)
        for i in range(len(blank)):
            clusters[blank[i]].append(clusters[max_index].pop())
        return clusters

    def get_cluster_RSS(self, cluster, centroid):
        sumRSS = 0
        # matrix = numpy.array([[0, 1 / 3.0, 2 / 3.0], [1 / 3.0, 0, 1 / 3.0], [2 / 3.0, 1 / 3.0, 0]])
        matrix = self.computer_distance_matrix()
        for i in range(len(cluster)):
            if self.street == 'river':
                sumRSS += math.pow(cluster[i][0] - centroid[0], 2)
            else:
                sumRSS += pow(abs(emd(numpy.array(cluster[i]), numpy.array(centroid),matrix)), 2)

        return sumRSS

    def solve(self):

        random.shuffle(self.DataPoints)
        centroids = self.DataPoints[0:self.cluster_count]
        print(centroids)
        clusters = self.configure_clusters(centroids, self.DataPoints)

        allRSS = []
        notDone = True
        lastRSS = 0
        while (notDone):
            # Find Residual Sum of Squares of the clusters
            clustersRSS = []
            for i in range(len(clusters)):
                clustersRSS.append(self.get_cluster_RSS(clusters[i], centroids[i]) / len(self.DataPoints))
            currentRSS = sum(clustersRSS)
            allRSS.append(currentRSS)
            print("RSS:", currentRSS)
            # See if the kmean algorithm has converged
            if (currentRSS == lastRSS):
                notDone = False
            else:
                lastRSS = currentRSS

            # Update each of the centroids to the new mean location
            for i in range(len(centroids)):
                if self.street == 'river':
                    centroids[i][0] = self.new_centroid(clusters[i])
                else:
                    centroids[i] = self.new_centroid(clusters[i])

            # Reconfigure the clusters to the new centroids
            clusters = self.configure_clusters(centroids, self.DataPoints)
        #print(centroids)
        for mean in centroids:
            out_string = ''
            for i in range(self.cluster_state_count):
                if i == self.cluster_state_count -1:
                    out_string = out_string + str(mean[i])
                else:
                    out_string = out_string + str(mean[i]) + ','
            self.file.write(out_string + '\n')

if __name__ == '__main__':
    cluster = Clustering(street= 'flop')
    cluster.solve()
