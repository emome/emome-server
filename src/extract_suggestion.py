from sys import argv
from sklearn.cluster import KMeans
import pickle
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

    pkl_file = open('model/suggestion_kmeans.pkl', 'rb')    
    clf = pickle.load(pkl_file)

    predicted_class = clf.predict(input_emotion)

    suggestion_clusters = []
    with open('data/suggestion_clusters.csv', 'rb') as csvfile:
        lines = csv.reader(csvfile)
        for line in lines:
            suggestion_clusters.append(line)

    random_suggestions = random.sample(suggestion_clusters[predicted_class], min(len(suggestion_clusters[predicted_class]), 10))

    return random_suggestions
