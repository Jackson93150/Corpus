from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
from concurrent.futures import ThreadPoolExecutor
import csv

matrix = []
name = []

with open("dictionnaires/lexique_corpus_sans_doublons.txt", "r") as tf: #on met le nom de tous les jeux
    lines = tf.read().splitlines()

for line in lines:
    line = line.replace(" ","+")
    name.append(line)

name.pop(10)

for i in range(10): # on recupere tous les liens à l'aide des nom de jeux (parcourir les dossier)
    linkurl = []
    with open("fichiers/corpus/"+name[i]+"/lien_source_google.txt", "r") as tf:
        lines = tf.read().splitlines()
    
    for line in lines:
        linkurl.append(line)

    matrix.append(linkurl)

doublon = []
urlsansdoublon = []
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
for x in range(10): # on regard si il y'a des doublons de lien et on les separe dans deux liste
    text = matrix[x]

    vectorizer = CountVectorizer()
    vectorizer.fit(text)
    vectors = vectorizer.transform(text).toarray()
    cos_sim = cosine_similarity(vectors)
    #print(cos_sim)

    rst = []
    for i in range(8):
        for j in range(8):
            comp = (cos_sim[i][i])
            if i < j:
                if cos_sim[i][j] == comp:
                    rst.append(text[i])
                    text.pop(i)

    #print(rst)
    #print(text)
    doublon.append(rst)
    urlsansdoublon.append(text)

#print(doublon)
#print(urlsansdoublon[0])
paragraphe = []
compt = 0

with open("data.csv", "w" , newline='') as new_file:
    writer = csv.writer(new_file)
    writer.writerow(["Paragraphe", "Jeu"])

def fetch(url):
    page = requests.get(url)
    return page.text

pool = ThreadPoolExecutor(max_workers=100)
for i in range(10): #on recupere tous les paragraphes de toutes les balises <p> et on les met dans un fichier csv avec l'index du jeu a quelle il appartient
    texte = []
    for page in pool.map(fetch, urlsansdoublon[i]):#on utilise du multithreading pour traiter toutes les requests
        soup = BeautifulSoup(page,'html.parser')
        for p in soup.select('p'):
                rs = p.get_text(strip=True)
                if(len(rs)>45):
                    texte.append(rs)
                    with open("data.csv", "a" , newline='') as new_file:
                        writer = csv.writer(new_file)
                        writer.writerow([rs,i])
    #paragraphe.append(texte)

#for i in range(len(paragraphe[3])):
    #print(paragraphe[3][i])
