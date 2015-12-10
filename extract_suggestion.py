from sys import argv
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn import preprocessing
import numpy as np
import csv
import random


'''
example usage: python extract_songs.py 3 2 4 5
'''

def extract_suggestion_ids(sad, frustrated, angry, anxious):
    input_emotion = [float(sad), float(frustrated), float(angry), float(anxious)]

    # input normalization
    input_emotion = preprocessing.normalize(np.array(input_emotion).reshape(1, -1))

    clf = joblib.load('suggestion_kmeans.pkl')
    predicted_class = clf.predict(input_emotion)
    #print predicted_class

    suggestion_clusters = []
    with open('suggestion_clusters.csv', 'rb') as csvfile:
        lines = csv.reader(csvfile)
        for line in lines:
            suggestion_clusters.append(line)

    #print len(song_clusters[predicted_class])
    random_suggestions = random.sample(suggestion_clusters[predicted_class], min(len(suggestion_clusters[predicted_class]), 10))
    #print random_songs

    return random_suggestions
