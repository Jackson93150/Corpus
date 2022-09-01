import textdistance
import pandas as pd
import math
import re
from collections import Counter
import Levenshtein as levenshtein
from fuzzywuzzy import fuzz

df = pd.read_csv("data.csv")
Jeu = df.Jeu
Paragraphe = df.Paragraphe
lim = []
WORD = re.compile(r"\w+")
double_index = []
name = []

with open("dictionnaires/lexique_corpus_sans_doublons.txt", "r") as tf:
    lines = tf.read().splitlines()

for line in lines:
    line = line.replace(" ","+")
    name.append(line)

name.pop(10)

def compteur(n): # compteur pour connaitre le nombre de paragraphe pour chaque jeu
    nb = 0
    for i in range(len(Jeu)):
        if Jeu[i] == n:
            nb+=1
    return nb-1

def limite(): # accumulation du nombre de paragraphe pour chaque (qui sera utile pour plus tard pour fixer des limites)
    x = 0
    for i in range(10):
        lim.append(x)
        x+=compteur(i)

limite()

#print(lim)

def hamming_similarity(x,n):
    doublons = []
    for i in range(n):
        for j in range(n):
            if j > i:
                if textdistance.hamming.normalized_similarity(Paragraphe[x+i], Paragraphe[x+j])>=0.95:
                    doublons.append(Paragraphe[x+j])
                    double_index.append(x+j)
    return doublons

#print(hamming_similarity(lim[9],compteur(9)))

all_doublons = []

def do_hamming():
    for i in range(10):
        all_doublons.append(hamming_similarity(lim[i],compteur(i)))

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

def cosine(x,n):
    doublons = []
    for i in range(n):
        for j in range(n):
            if j > i:
                if get_cosine(text_to_vector(Paragraphe[x+i]), text_to_vector(Paragraphe[x+j]))>=0.95:
                    doublons.append(Paragraphe[x+j])
                    double_index.append(x+j)
    return doublons

def do_cosine():
    for i in range(10):
        all_doublons.append(cosine(lim[i],compteur(i)))

def lev(x,n):
    doublons = []
    for i in range(n):
        for j in range(n):
            if j > i:
                if levenshtein.ratio(Paragraphe[x+i],Paragraphe[x+j])>=0.95:
                    doublons.append(Paragraphe[x+j])
                    double_index.append(x+j)
    return doublons

def do_lev():
    for i in range(10):
        all_doublons.append(lev(lim[i],compteur(i)))

def fuzzy(x,n):
    doublons = []
    for i in range(n):
        for j in range(n):
            if j > i:
                if (fuzz.ratio(Paragraphe[x+i],Paragraphe[x+j])/100)>=0.95:
                    doublons.append(Paragraphe[x+j])
                    double_index.append(x+j)
    return doublons

def do_fuzzy():
    for i in range(10):
        all_doublons.append(fuzzy(lim[i],compteur(i)))

double_index_res = []

def start():
    print("Quelle méthode voulez vous utilissez 1:Hamming  2:Cosine  3:Levenshtein  4:Fuzzy ") # on va executer un des 4 algo avec l'input choisie
    num = int(input())
    while num > 4 or num <= 0:
        print("Je n'ai pas compris quelle méthode voulez vous utilissez 1:Hamming  2:Cosine  3:Levenshtein  4:Fuzzy ")
        num = int(input())
    if num == 1:
        do_hamming()
    if num == 2:
        do_cosine()
    if num == 3:
        do_lev()
    if num == 4:
        do_fuzzy()

    double_index.sort() #On recompte le nombre de doublons en enlevant les fois ou il réaparaissent plusieurs fois
    for element in double_index:
        if element not in double_index_res:
            double_index_res.append(element)
    
    cpt = 0
    end = double_index_res[-1]
    for j in range(10):# on va ecrire dans des fichier texte le corpus de chaque jeu en enlevant les doublons
        fichier = open("corpus/corpus_"+name[j]+".txt", "w")
        for i in range(len(Paragraphe)):
            if Jeu[i] == j:
                if i == double_index_res[cpt]:
                    if i != end:
                        cpt+=1
                else:
                    fichier.write(Paragraphe[i]+"\n")
        fichier.close()
    
start()