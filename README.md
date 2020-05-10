# Slimes
Simulation d'évolution d'une population de slimes

# Introduction
J'ai été inspiré par le travail de Primer [Chîne Youtube Primer](https://www.youtube.com/channel/UCKzJFdi57J53Vr_BkTfN3uQ), qui simule des phénomènes (comme la loi de l'offre et de la demande, l'optimisation de productivité, la croissance d'une population, etc.) à travers la modélisation de créatures évoluant sur un plateau de jeu.

**Problématique :** Est-il possible de simuler l'évolution (au sens Darwinien du terme) d'une population , en reprenant le même cadre (ie. des créatures sur un plateau limité)?

# Principe 
Mettre sur un terrain de jeu des créatudes, les "*Slimes*" ainsi que des sources ponctuelles de nourriture. Les *slimes* ont la capacité de se déplacer, de voir la nourriture, de se nourrire quand une source de nourriture est assez proche, de voir leur congénères, de les attaquer ainsi que de se reproduire.

Chaque *slime* a des gènes, déterminant ses caractères, comme sa vitesse, force, taille, beauté, etc. Ces caractères ont bien sûr une incidence sur leur relation au monde. Par exemple leur vitesse leur permet d'accéder à la nourriture plus ou moins vite que les autres, au coût d'une plus ou moins grande dépense d'énergie.

Lors de la reproduction, les créatures mélangent aléatoirement leur génome et le génome résultant est ensuite soumis à des mutations, aléatoires, selon des hyperparamètres fixés.

# Implémentation
J'ai commencé par implémenter cette simulation en Python, donc sans interface graphique complexe. Les slimes jouent tour par tour (cf. plus loin), dans un ordre randomisé à la fin de chaque tour, pour ne pas induire de biais favorable perturbateur. Python oblige, on ne peut pas voir en direct les slimes évoluer, mais j'ai msi en place une interface "statistique". C'est-à-dire que l'on voit en permanence les graphes de répartition des différents caractères dans les génomes des slimes. On peut donc à tout instant se donner une idée de la tendance de l'évolution, ie. quels caractères sont favorisés et lesquels ne le sont pas.

Dans une première version, pour simplifier, le terrain de jeu est une grille discrète, les slimes sont placés dans une matrice. Bien sûr, ceci est très peu réaliste, donc j'ai changé cela pour avoir un terrain de jeu continu dans la deuxième version.

Ensuite, dans une volonté d'améliorer les performances et l'équilibre de la simulation, en permettant à tous les slimes d'agir en même temps, j'ai utilisé le module **Threading** de Python, en assignant chaque *slime* à un thread. Le résultat était cependant assez décevant, avec des performances plus mauvaises qu'avant. J'ai donc abandonné cette idée et j'en suis resté là pour mon implémentation en Python.

Je me suis alors interessé au moteur de jeu **Unity**, qui permet de contrôler, et de visualiser, facilement des objects en 3D (les fichiers *.cs* sont les fichiers en C# que j'ai écrits pour Unity).
