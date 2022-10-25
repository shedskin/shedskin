#!/usr/bin/env python

# Adatron SVM with polynomial kernel
# placed in the public domain by Stavros Korokithakis

import sys
from math import exp

CYTOSOLIC = 0
EXTRACELLULAR = 1
NUCLEAR = 2
MITOCHONDRIAL = 3
BLIND = 4

D = 5.0

LENGTH = 50

PROTEINS = []

AMINOACIDS = "ACDEFGHIKLMNPQRSTVWY"

class Protein:
    def __init__(self, name, mass, isoelectric_point, size, sequence, type):
        self.name = name
        self.mass = mass
        self.isoelectric_point = isoelectric_point
        self.size = size
        self.sequence = sequence
        self.type = type
        self.extract_composition()

    def extract_composition(self):
        self.local_composition = dict(((x, 0.0) for x in AMINOACIDS))
        for counter in range(LENGTH):
            self.local_composition[self.sequence[counter]] += 1.0 / LENGTH
        self.global_composition = dict(((x, 0.0) for x in AMINOACIDS))
        for aminoacid in self.sequence:
            self.global_composition[aminoacid] += 1.0 / len(self.sequence)

    def create_vector(self):
        vector = []
        for key, value in sorted(self.local_composition.items()):
            vector.append(value)
        for key in sorted(self.global_composition.keys()):
            vector.append(value)
        return vector


def load_file(filename, type):
    global PROTEINS
    protfile = open(filename)
    for line in protfile:
        if line.startswith("name"):
            continue
        name, mass, isoelectric_point, size, sequence = line.strip().split("\t")
        protein = Protein(name, mass, isoelectric_point, size, sequence, type)
        PROTEINS.append(protein)
    protfile.close()


def create_tables():
    """Create the feature and label tables."""
    feature_table = []
    label_table = []

    for protein in PROTEINS:
        feature_table.append(protein.create_vector())

    for protein in PROTEINS:
        if protein.type == BLIND:
            continue
        labels = [-1] * 4
        # Invert the sign of the label our protein belongs to.
        labels[protein.type] *= -1
        label_table.append(labels)

    return feature_table, label_table


def create_kernel_table(feature_table):
    kernel_table = []
    for row in feature_table:
        kernel_row = []
        for candidate in feature_table:
            difference = 0.0
            for counter in range(len(row)):
                difference += (row[counter] - candidate[counter]) ** 2
            kernel_row.append(exp(-D*difference))
        kernel_table.append(kernel_row)
    return kernel_table


def train_adatron(kernel_table, label_table, h, c):
    tolerance = 0.5
    alphas = [([0.0] * len(kernel_table)) for _ in range(len(label_table[0]))]
    betas = [([0.0] * len(kernel_table)) for _ in range(len(label_table[0]))]
    bias = [0.0] * len(label_table[0])
    labelalphas = [0.0] * len(kernel_table)
    max_differences = [(0.0, 0)] * len(label_table[0])
    for iteration in range(10*len(kernel_table)):
        print("Starting iteration %s..." % iteration)
        if iteration == 20: # XXX shedskin test
            return alphas, bias
        for klass in range(len(label_table[0])):
            max_differences[klass] = (0.0, 0)
            for elem in range(len(kernel_table)):
                labelalphas[elem] = label_table[elem][klass] * alphas[klass][elem]
            for col_counter in range(len(kernel_table)):
                prediction = 0.0
                for row_counter in range(len(kernel_table)):
                    prediction += kernel_table[col_counter][row_counter] * \
                                 labelalphas[row_counter]
                g = 1.0 - ((prediction + bias[klass]) * label_table[col_counter][klass])
                betas[klass][col_counter] = min(max((alphas[klass][col_counter] + h * g), 0.0), c)
                difference = abs(alphas[klass][col_counter] - betas[klass][col_counter])
                if difference > max_differences[klass][0]:
                    max_differences[klass] = (difference, col_counter)

            if all([max_difference[0] < tolerance for max_difference in max_differences]):
                return alphas, bias
            else:
                alphas[klass][max_differences[klass][1]] = betas[klass][max_differences[klass][1]]
                element_sum = 0.0
                for element_counter in range(len(kernel_table)):
                    element_sum += label_table[element_counter][klass] * alphas[klass][element_counter] / 4
                bias[klass] = bias[klass] + element_sum

def calculate_error(alphas, bias, kernel_table, label_table):
    prediction = 0.0
    predictions = [([0.0] * len(kernel_table)) for _ in range(len(label_table[0]))]
    for klass in range(len(label_table[0])):
        for col_counter in range(len(kernel_table)):
            for row_counter in range(len(kernel_table)):
                prediction += kernel_table[col_counter][row_counter] * \
                              label_table[row_counter][klass] * alphas[klass][row_counter]
            predictions[klass][col_counter] = prediction + bias[klass]

    for col_counter in range(len(kernel_table)):
        current_predictions = []
        error = 0
        for row_counter in range(len(label_table[0])):
            current_predictions.append(predictions[row_counter][col_counter])

        predicted_class = current_predictions.index(max(current_predictions))

        if label_table[col_counter][predicted_class] < 0:
            error += 1

        return 1.0 * error / len(kernel_table)


def main():
    for filename, type in [("testdata/c.txt", CYTOSOLIC), ("testdata/e.txt", EXTRACELLULAR), ("testdata/n.txt", NUCLEAR), ("testdata/m.txt", MITOCHONDRIAL)]:#, ("b.txt", BLIND)]:
        load_file(filename, type)
    print("Creating feature tables...")
    feature_table, label_table = create_tables()
    #import pickle
    #print "Loading kernel table..."
    #kernel_file = file("kernel_table.txt")
    #kernel_table = pickle.load(kernel_file)
    #kernel_file.close()
    print("Creating kernel table...")
    kernel_table = create_kernel_table(feature_table)
    print("Training SVM...")
    alphas, bias = train_adatron(kernel_table, label_table, 1.0, 3.0)
    print(calculate_error(alphas, bias, kernel_table, label_table))


if __name__ == "__main__":
    main()

