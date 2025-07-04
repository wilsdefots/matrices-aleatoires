# -*- coding: utf-8 -*-
"""TP_ete25_matrices_aleatoires.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1A3jfmFXuzGMHtEUyoHNi8TFfOnPvzJPO

## Matrices aléatoires.

Dans ce travail, on va entrainer un perceptron multi couche sur les données
de MNIST, puis, observer le comportement des matrices des poids, pour voir si les valeurs s'éloignent des bornes définies par le théorème de marchenko-Pastur
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.initializers import RandomNormal
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Flatten, Dense
from tensorflow.keras.datasets import  fashion_mnist
from tensorflow.keras.datasets import mnist

# On connecte au GPU pour accelérer les calculs
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(" GPU détecté :", gpus)
else:
    print("Pas de GPU détecté")
physical_devices = tf.config.list_physical_devices('GPU')

"""### Entrainement du Perceptron multi couche"""

#On charge les données du Fashion_mnist
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
#(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Dimensions des données
print("dimensions x_train :", x_train.shape)
print("dimensions y_train :", y_train.shape)
print("dimensions x_test :", x_test.shape)
print("dimensions y_test :", y_test.shape)

# On affiche ici les 40 premières images (4 lignes × 10 colonnes)
# Chaque image est accompagnée de son étiquette (nom de classe)
# L'affichage se fait en niveaux de gris ("binary") sans axes

#Code copié dans un projet du cours d'apprentissage machine
noms_classes = ["Chandail ", " Pantalon ", " Pull ", " Robe ", " Manteau ",
               " Sandale ", " Chemise ", " Soulier ", " Sac ", "Botte"]

#noms_classes = ["0" , "1", "2 ", " 3 ", " 4 ", " 5 ", " 6 ", " 7 ", " 8", " 9 "]
n_rows = 4
n_cols = 10
plt.figure(figsize=(n_cols * 1.2, n_rows * 1.2))
for row in range(n_rows):
    for col in range(n_cols):
        index = n_cols * row + col
        plt.subplot(n_rows, n_cols, index + 1)
        plt.imshow(x_train[index], cmap="binary", interpolation="nearest")
        plt.axis('off')
        plt.title(noms_classes[y_train[index]], fontsize=12)
plt.subplots_adjust(wspace=0.2, hspace=0.5)
plt.show()

# On va premièrement normaliser les pixel
x_train = x_train / 255
x_test = x_test / 255

# encodage des etiquettes (one hot encoder)
tf.random.set_seed(2025)
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)

# J'ajoute le bruit dans 10% des étiquettes
seed = tf.random.set_seed(2025)


# Architechture des couches
ecart_type = 0.0125
initial = RandomNormal(mean=0.0, stddev= ecart_type, seed = seed)

 # je veux forcer le modèle à démarer avec des matrices
#de poids choisies de façon aléatoire, et non les poids initiaux choisis automatiquement selon la stratégie par défaut de Keras
#reference  https://keras.io/api/layers/initializers/?

reseau = Sequential([
    Input(shape=(28, 28)),
    Flatten(),
    Dense(512, activation='relu', kernel_initializer=initial),
    Dense(256, activation='relu', kernel_initializer=initial),
    Dense(128, activation='relu', kernel_initializer=initial),
    Dense(10, activation='softmax', kernel_initializer=initial)
])



#Compilation
reseau.compile(
    optimizer='adam',
   # optimizer=tf.keras.optimizers.SGD(),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

"""Le prétraitement des données inclut la normalisation des pixels des images pour pouvoir faciliter la convergence du réseau. Les étiquettes sont encodées en one-hot pour correspondre à la sortie multinomiale du modèle.
L’architecture choisie est un perceptron multicouche (MLP) avec trois couches cachées successives, utilisant la fonction d’activation ReLU pour introduire la non-linéarité, et une couche de sortie softmax adaptée à la classification multiclasses.
Le modèle est compilé avec l’optimiseur Adam, reconnu pour son efficacité, et la fonction de perte categorical_crossentropy, adaptée aux problèmes de classification à plusieurs classes.
L’entraînement est effectué sur 20 époques, avec un batch size de 128, et la performance est évaluée sur un ensemble de test distinct pour vérifier la capacité de généralisation du modèle.
"""

# On sauvegarde les matrices des poids à chaque époque, et on construit au passage la courbe de précision.
# Pour la sauvegarde des matrices de poids, voici la référence
# https://stackoverflow.com/questions/61046870/how-to-save-weights-of-keras-model-for-each-epoch?
#J'ai juste adapté le code
poids_par_epoque = []
precision_entrainement = []
precision_validation = []
nbre_epoque = 15

for epoque in range(nbre_epoque):
    print(f" Epoque {epoque + 1} : ")
    historique = reseau.fit(x_train, y_train,
               epochs=1,
              batch_size=256,
               validation_data=(x_test, y_test),
               verbose=1)
    poids = [
        reseau.layers[1].get_weights()[0],

        # il s'agit ici de la vrai premiere couche ayant les matrices de poids (celle de 512).
        # En effet, la couche Input(shape=(28, 28))  convertit les images en 2D :  28 x 28 (Elle n'a pas de poids) et cen'est pas un layer
         #La couche  Flatten()  applatit les images (en 1D ) 28*28 = 784px ;
        #elle n'a pas non plus les poids. C'est le premier layer : Layer[0]

        reseau.layers[2].get_weights()[0],  #  couche Dense(256, activation='relu')
        reseau.layers[3].get_weights()[0],  #  couche Dense(128, activation='relu')
        reseau.layers[4].get_weights()[0]   # couche Dense(10, activation='softmax')
    ]
    poids_par_epoque.append(poids)
    precision_entrainement.append(historique.history['accuracy'][0])
    precision_validation.append(historique.history['val_accuracy'][0])

    historique_global = {
    'precision_ent': precision_entrainement,
    'precision_val': precision_validation
    }

# Évaluation finale
score = reseau.evaluate(x_test, y_test, verbose=0)
print(f"\n Précision finale sur le test : {score[1]:.4f}")

def construire_courbe_simple(historique):
    plt.figure(figsize=(20, 5))
    plt.plot(range(nbre_epoque), historique['precision_ent'], label='Précision entraînement')
    plt.plot(range(nbre_epoque), historique['precision_val'], label='Précision validation')

    plt.title('Courbes de précision')
    plt.xlabel('Époques')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True)
    plt.ylim(0.5, 1)
    plt.savefig("Courbe_precision.png")
    plt.show()


construire_courbe_simple(historique_global)



"""Le modèle présente une bonne capacité de généralisation, ce qui exclut tout risque significatif de surapprentissage."""

#on va maintenant calculer la densité de Marchenko pastur pour chacune des matrices de poids à chaque époque
#Rappels des differents paramètres connus
#premiere couche
q1 = 32/49
a1 = (1-np.sqrt(q1))**2
b1 = (1+np.sqrt(q1))**2

#deuxieme couche
q2 = 256/512
a2 = (1-np.sqrt(q2))**2
b2 = (1+np.sqrt(q2))**2

#troisieme couche
q3 = 128/256
a3 = (1-np.sqrt(q3))**2
b3 = (1+np.sqrt(q3))**2

#quatrieme couche
q4 = 10/128
a4 = (1-np.sqrt(q4))**2
b4 = (1+np.sqrt(q4))**2

a= [a1,a2,a3,a4]
b= [b1,b2,b3,b4]


def loi_marchenko_pastur(x, q=2, sigma = ecart_type):
  densite = 0
  a = sigma**2 * (1 - np.sqrt(q))**2
  b = sigma**2 * (1 + np.sqrt(q))**2
  if (x > a and x < b):
    densite = np.sqrt((b - x) * (x - a)) / (2 * np.pi * sigma**2 * x * q)
  return densite



#Les deux cellules qui suivent ont été inspirées d'une visualisation faite en apprentissage machiene
#j'ai juste adapté le code
def afficher_visualisation_comparative(W, couche= " ", epoque=0, ax = None):
    p, n = W.shape  # (p,n) = (nbr de ligne, nbr de colones)
    Y_n = np.dot(W, W.T)/n
    q = n/p
    sigma = np.std(W)
    a = (1-np.sqrt(q))**2 *sigma**2
    b = (1+np.sqrt(q))**2 *sigma**2

    # Calcul des valeurs propres
    valeurs_propres = np.linalg.eigvals(Y_n)

    # Tracé
    if ax is None:
        fig, ax = plt.subplots(figsize=(3, 2))
    sns.histplot(valeurs_propres,
                 stat="density", color="skyblue",
                 ax=ax,label="Spectre empirique")
    #On va calculer le pourcentage de valeurs propres qui sont dans l'intervalle (a,b)
    nb_vp_dans_intervalle = np.sum((valeurs_propres >= a) & (valeurs_propres <= b))
    pourcentage_valeurs_dans_intervalle = (nb_vp_dans_intervalle / len(valeurs_propres)) * 100
    #print(f"Pourcentage de valeurs propres dans l'intervalle ({a:.2e}, {b:.e}) : {pourcentage_valeurs_dans_intervalle:.2f}%")


    # Densité MP sur même intervalle
    intervalle = np.linspace(a,b, 30)
    densite_mp = [loi_marchenko_pastur(x, q=q,  sigma = sigma) for x in intervalle]
    ax.plot(intervalle, densite_mp, 'r--', lw=2)
    ax.axvline(x=a, color='blue',linestyle='--', linewidth = 1)
    ax.axvline(x=b, color='blue', linestyle='--', linewidth=1)

    ax.set_title(f"Époque : {epoque+1}, Couche {couche}, q= {q:.2f} \n"
                  f" taux des vp dans (a,b)=({a:.2e},{b:.2e}) : \n {pourcentage_valeurs_dans_intervalle:.2f}% ")

    ax.set_xlabel("Valeurs propres")
    ax.set_ylabel("Densités")
    ax.grid(True)
    ax.set_xlim(0, 1.5*b)
    ax.legend().remove()

# Le code suivant a été inspiré de stack overflow via le lien suivant :
# https://stackoverflow.com/questions/16150819/common-xlabel-ylabel-for-matplotlib-subplots?

fig, axes = plt.subplots(nrows= nbre_epoque, ncols=3, sharex=False, sharey=False, figsize=(20, 60))
#plt.tick_params(labelcolor='none', which='both', top=True, bottom=True, left=False, right=False)

for epoque in range(nbre_epoque):  # époques
    for couche in range(3):  # couches
    # On ne représente pas la quatrième couche par ce qu'elle n'a que 10 valeurs propres, le
    #théorème de Marchenko-Pastur a son sens quand les dimension tendent vers l'infini
        W = poids_par_epoque[epoque][couche]
        ax = axes[epoque, couche]
        afficher_visualisation_comparative(W, couche=f"{couche+1}", epoque=epoque, ax=ax)
        ax.grid(True)
        #on supprime la graduation horizontale
        #ax.set_xticks([])
        #ax.set_yticks([])

plt.tight_layout()
plt.savefig("spectres_par_epoque_et_couche.png")
plt.show()











