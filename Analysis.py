#!/usr/bin/env python3
from __future__ import print_function

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.__version__

import os
import time
import sys
import math
import subprocess
from sklearn.tree import DecisionTreeClassifier, export_graphviz

class DataPoint:
    def __str__(self):
        return "< " + str(self.label) + ": " + str(self.features) + " >"
    def __init__(self, label, features):
        self.label = label # the classification label of this data point
        self.features = features


class TreeNode:
    is_leaf = True          # boolean variable to check if the node is a leaf
    feature_idx = None      # index that identifies the feature
    thresh_val = None       # threshold value that splits the node
    prediction = None       # prediction class (only valid for leaf nodes)
    left_child = None       # left TreeNode (all values < thresh_val)
    right_child = None      # right TreeNode (all values >= thresh_val)

    def printTree(self):    # for debugging purposes
        if self.is_leaf:
            print ('Leaf Node:      predicts ' + str(self.prediction))
        else:
            print ('Internal Node:  splits on feature '
                   + str(self.feature_idx) + ' with threshold ' + str(self.thresh_val))
            self.left_child.printTree()
            self.right_child.printTree()




year = int()

def get_data(file_name):
    d = []
    with open(file_name) as f:
        lines = f.readlines()
        for row in lines:
            ls = list(eval(row))
            data = DataPoint(label=ls[8], features=ls[:8])
            d.append(data)


    return d

def make_prediction(tree_root, data_point):
    if(tree_root.is_leaf) :
        return tree_root.prediction

    idx = tree_root.feature_idx
    thresh = tree_root.thresh_val
    if data_point.features[int(idx)] < thresh:
        return make_prediction(tree_root.left_child, data_point)

    return make_prediction(tree_root.right_child, data_point)

def split_dataset(data, feature_idx, threshold):
    left_split = []
    right_split = []
    for d in data :
        if d.features[feature_idx] < threshold:
            left_split.append(d)
        else:
            right_split.append(d)

    return (left_split, right_split)

def num_pos(data):
    positive = 0
    for d in data:
        if(d.label == 1):
            positive += 1

    return positive
def calc_entropy(data):
    entropy = 0.0
    positive = num_pos(data)
    total = len(data)
    pprop = positive / total
    nprop = (total - positive) / total
    if(nprop == 0 or pprop == 0):
        return 0

    return -((pprop) * math.log2(pprop) + (nprop) * math.log2(nprop))

def calc_best_threshold(data, feature_idx):
    best_gain = 0.0
    best_thresh = None
    data = sorted(data, key=lambda p: p.features[feature_idx])

    parent_entropy = calc_entropy(data)
    prev_split = data[0].features[feature_idx]

    for d in data:
        split = d.features[feature_idx]
        if(split != prev_split):
            left, right = split_dataset(data, feature_idx, (split + prev_split) / 2)
            left_gain  = (len(left)/len(data))  * calc_entropy(left)
            right_gain = (len(right)/len(data)) * calc_entropy(right)
            total_gain = parent_entropy - left_gain - right_gain
            if total_gain > best_gain:
                best_gain = total_gain
                best_thresh = split

    return (best_gain, best_thresh)

def identify_best_split(data):
    if len(data) < 2:
        return (None, None)
    best_feature = None
    best_thresh = None
    best_gain = 0
    for i in range(0, 8):
        gain, thresh = calc_best_threshold(data, i)
        if(gain > best_gain):
            best_gain = gain
            best_thresh = thresh
            best_feature = i

    return (best_feature, best_thresh)


def createLeafNode(data):
    n = TreeNode()
    n.isleaf = True
    p_count = num_pos(data)
    n.prediction = p_count / len(data)
    return n


def createDecisionTree(data, max_levels):
    if max_levels == 1 or num_pos(data) == len(data) or num_pos(data) == 0:
        return createLeafNode(data)
    start = time.time()
    feature, thresh = identify_best_split(data)
    end = time.time()

    if(thresh is None):
        return createLeafNode(data)
    t = TreeNode()
    t.thresh_val = thresh
    t.feature_idx = feature
    t.is_leaf = False
    left, right = split_dataset(data, feature, thresh)
    if(len(left) == 0 or len(right) == 0):
        return createLeafNode(data)

    t.left_child  = createDecisionTree(left , max_levels-1)
    t.right_child = createDecisionTree(right, max_levels-1)

    return t


def calcAccuracy(tree_root, data):
    correct = 0
    for d in data:
        percentage = make_prediction(tree_root, d)
        decision   = int(percentage * 2)
        if(decision == d.label):
            correct += 1



    return correct / len(data)

if __name__ == "__main__":
    year = sys.argv[1]
    dataset = get_data("Sits/" + year + "Sits.csv")

    s = len(dataset) /100
    for i in range(0,5):
        # partition data into train_set and test_set
        wall1 = int((s * i)/5)
        wall2 = int((s *(i+1))/5)
        wall3 = int(s)
        test_set = dataset[wall1 : wall2]
        train_set  = dataset[:wall1] + dataset[wall2:wall3]

        print ('Training set size:', len(train_set))
        print ('Test set size    :', len(test_set))

        # create the decision tree
        start = time.time()
        tree = createDecisionTree(train_set, 10)
        end = time.time()
        print ('Time taken:', end - start)

        # calculate the accuracy of the tree
        accuracy = calcAccuracy(tree, test_set)
        print ('The accuracy on the test set is ', str(accuracy * 100.0))
        #t.printTree()

    # i = 2
    # features = []
    # while(len(sys.argv) > i):
    #     features.append(sys.argv[i])
    #     i = i + 1
    # printTree(features)
