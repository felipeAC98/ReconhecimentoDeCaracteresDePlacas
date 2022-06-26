from matplotlib import pyplot as plt
import sys
import numpy as np
import cv2
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import sklearn.metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score #novidade
import argparse
import sys

def plotTesteParametrosKNN(caracteres,rotulos):
  x_train, x_test, y_train, y_test = train_test_split(caracteres, rotulos,
                                                      test_size=0.20, 
                                                    random_state=42)
  tr_acc = []
  k_set = range(3,11)

  for n_neighbors in k_set:
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    scores = cross_val_score(knn, x_train, y_train, cv=10)
    tr_acc.append(scores.mean())
    
  best_k = np.argmax(tr_acc)
  print("primeiro best"+str(k_set[best_k]))

  te_acc = []
  k_set = range(3,11)

  for n_neighbors in k_set:
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(x_train, y_train)
    y_pred = knn.predict(x_test)
    te_acc.append(sklearn.metrics.accuracy_score(y_test, y_pred)) 

  import matplotlib.pyplot as plt

  plt.plot(k_set,tr_acc, label='Treino')
  plt.plot(k_set,te_acc, label='Teste')
  plt.ylabel('Acurácia')
  plt.xlabel('k')
  plt.legend()

  plt.show()

def main():

  parser = argparse.ArgumentParser(description='args')
  parser.add_argument('--algoritmo')			#tipod e algoritmo para criar o modelo
  parser.add_argument('--testeKNN')			#tipod e algoritmo para criar o modelo
  parser.add_argument('--bagging')			#tipod e algoritmo para criar o modelo
  args = parser.parse_args()
  algoritmo="knn"
  if args.algoritmo != None:
    algoritmo=str(args.algoritmo)

  caracteres = np.loadtxt('caracteres.data',np.float32)
  rotulos = np.loadtxt('rotulos.data',np.float32)
  rotulos = rotulos.reshape((rotulos.size,1))

  if args.testeKNN != None:
    plotTesteParametrosKNN(caracteres,rotulos)

  #=========== KNN
  if algoritmo == "knn":
    clf = KNeighborsClassifier(n_neighbors=5)
    clf.fit(caracteres,rotulos.ravel()) 

  #=========== Arvore de decisao
  if algoritmo == "tree":
    clf = tree.DecisionTreeClassifier(criterion="gini")#
    clf = clf.fit(samples, responses)

  #=========== Bagging
  if args.bagging != None:
    from sklearn.ensemble import BaggingClassifier
    clf = BaggingClassifier(DecisionTreeClassifier(criterion='entropy'))#
    clf = clf.fit(samples, responses)

  #========== Salvando modelo
  filename = 'modelos/modeloKNN.sav'
  pickle.dump(clf, open(filename, 'wb'))

if __name__ == '__main__':
    sys.exit(main())