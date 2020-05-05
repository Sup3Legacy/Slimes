import numpy as np
import matplotlib.pyplot as plt
import usuelles
import random

plt.ion()

BREED_RATE = 0.75
COEFF_DIFFERENCE_BEAUTE = 0.5 # Coeff lié à la probabilité qu'un slime veuille mate avec un partenaire moins beau que lui, * la différence de beauté
COEFF_ABSORPTION = 2
COEFF_SPEED = 1
COEFF_FATIGUE = 1
COEFF_DEGAT = 1
COEFF_MUTATION = 0.5 #Coeff pour l'ampleur des mutations de l'agressivité et de la fuite

NOMBRE_BOUFFE = 10 #Quantité de bouffe par tas

FOODMAX_INIT = 100
SEERANGE_INIT = 2
EAT_AND_WALK = 0.1 # Proba de bouger même si de la nourriture a été trouvée
SPEED_INIT = 1
SIZE_INIT = 1
AGRESSIVITY_INIT = 0 #(Entre 0 et 1)
DEGAT_CONST = 1 #Dégât minimal causé
FLY_INIT = 0

class Food:
    def __init__(self, coords):
        self.amount = NOMBRE_BOUFFE
        self.X, self.Y = coords


    def __repr__(self):
        return "\033[1;33;40mF " + str(self.amount) + "\033[1;37;40m"

class Slime:
    def __init__(self, coords, args = []):
        if args == []:
            self.speed = SPEED_INIT
            self.size = SIZE_INIT
            self.foodMax = FOODMAX_INIT
            self.food = self.foodMax
            self.generation = 0
            self.X, self.Y = coords
            self.seeRange = SEERANGE_INIT
            self.age = 0
            self.gender = 'Male' if random.random() <= 0.5 else 'Female'
            self.beauty = 5
            self.agressivity = AGRESSIVITY_INIT
            self.flyrate = FLY_INIT
        else:
            self.speed, self.size, self.foodMax, self.seeRange, self.beauty, self.agressivity, self.flyrate = args
            self.gender = 'Male' if random.random() <= 0.5 else 'Female'
            self.X, self.Y = coords


    def __repr__(self):
        return "\033[1;32;40mS " + str(self.generation) + "\033[1;37;40m"

    def eat(self, target, distance):
        amount = min(target.amount, int((self.size ** 3) * COEFF_ABSORPTION))
        target.amount -= amount
        self.food += amount
        self.food = min(self.foodMax, self.food)

    def fatigue(self, amount):
        self.food -= amount

    def getBreededGenes(self):
        return [max(1, self.speed + np.random.randint(-5, 6)), max(1, self.size + np.random.randint(-1, 2)),
                max(1, self.foodMax + np.random.randint(-5, 6)), max(1, self.seeRange), min(10, max(0, self.beauty + np.random.randint(-2, 3))),
                min(1, max(0, self.agressivity + np.random.normal(0, COEFF_MUTATION))), min(1, max(0, self.flyrate + np.random.normal(0, COEFF_MUTATION)))]

    def attack(self, target, distance):
        amount = int(abs(self.size - target.size) * COEFF_DEGAT / distance)
        if amount != 0:
            amount += (abs(amount) // amount) * DEGAT_CONST
        amount *= COEFF_DEGAT
        target.food = usuelles.clipcoord(target.food - 2 * amount, target.foodMax)
        self.food = usuelles.clipcoord(self.food - amount, self.foodMax)

    def fly(self, target, size):
        if self.gender != target.gender:
            return False
        deltaX = target.X - self.X
        deltaY = target.Y - self.Y
        hyp = np.sqrt(deltaX ** 2 + deltaY ** 2)
        facteur = hyp * self.speed
        self.X = usuelles.clipcoord(self.X - facteur * deltaX, size)
        self.Y = usuelles.clipcoord(self.Y - facteur * deltaX, size)
        self.fatigue(self.size * self.speed)

class Terrain:
    def __init__(self, size, numberSlimes, numberFood):
        self.size = size
        self.numberSlimes = numberSlimes
        self.numberFood = numberFood
        self.slimes = [Slime(self.size * np.random.rand(2)) for _ in range(self.numberSlimes)]
        self.food = []
        self.population = [self.numberSlimes]

    def clear(self):
        self.slimes = []
        self.food = []

    def spawnFood(self):
        self.food = [Food(self.size * np.random.rand(2)) for _ in range(self.numberFood)]

    def clearFood(self):
        self.food = []

    def spawnSlime(self, coords, args):
        self.slimes.append(Slime(coords, args))

    def step(self):
        for i in reversed(range(len(self.slimes))):
            S = self.slimes[i]
            self.searchTarget(self.slimes[i])
            self.searchMate(self.slimes[i])
            if not self.searchFood(self.slimes[i]) or np.random.rand() < EAT_AND_WALK:
                self.searchPlace(self.slimes[i])
            self.slimes[i].age += 1

    def cleanSlimes(self):
        n = len(self.slimes)
        for i in reversed(range(0, n)):
            if self.slimes[i].food <= 0:
                self.slimes.pop(i)


    def distanceEntities(self, e1, e2):
        return np.sqrt((e1.X - e2.X) ** 2 + (e1.Y - e2.Y) ** 2)

    def searchFood(self, slime):
        possibles = []
        if slime.food >= slime.foodMax:
            slime.food = slime.foodMax
            return False
        for F in self.food:
            if self.distanceEntities(slime, F) <= slime.seeRange and F.amount > 0:
                possibles.append(F)
        if possibles != []:
            F = possibles[np.random.randint(0, len(possibles))]
            slime.eat(F, self.distanceEntities(slime, F))
            return True
        else:
            return False

    def searchPlace(self, slime):
        alpha = np.random.rand() * 2 *  np.pi
        distance = np.random.rand()
        X = usuelles.clipcoord(slime.X + distance * COEFF_SPEED * slime.speed * np.cos(alpha), self.size)
        Y = usuelles.clipcoord(slime.Y + distance * COEFF_SPEED * slime.speed * np.sin(alpha), self.size)
        slime.X, slime.Y = X, Y
        slime.fatigue((slime.speed ** 2) * (slime.size ** 3) * COEFF_FATIGUE * distance)
        return True

    def searchMate(self, slime):
        if slime.food < slime.foodMax * (3 / 4):
            return False
        possible = []
        for S in self.slimes:
            if self.distanceEntities(slime, S) <= min(slime.seeRange, S.seeRange) and S.food >= S.foodMax * (3 / 4) and slime.gender != S.gender:
                possible.append(S)
        if possible != []:
            possible = sorted(possible, key = lambda object : object.beauty)
            S = possible[len(possible) - 1] #On prend le plus beau partenaire potentiel!
            if np.random.rand() * abs(slime.beauty - S.beauty) <= COEFF_DIFFERENCE_BEAUTE:
                return self.mate(slime, S)
        return False

    def searchTarget(self, slime):
        possibles = []
        for S in self.slimes:
            dist = self.distanceEntities(slime, S)
            if dist <= min(slime.seeRange, S.seeRange) and dist > 0 and slime.gender == S.gender:
                possibles.append(S)
        if possibles != []:
            possibles = sorted(possibles, key = lambda slime : slime.size)
            faible = possibles[0]
            fort = possibles[len(possibles) - 1]
            if random.random() <= slime.agressivity:
                slime.attack(faible, self.distanceEntities(slime, faible))
            if random.random() <= slime.flyrate:
                slime.fly(fort, self.size)
        else:
            return False


    def mate(self, S1, S2):
        if np.random.rand() < BREED_RATE:
            genes1 = list(S1.getBreededGenes())
            genes2 = list(S2.getBreededGenes())
            genes = usuelles.tupleFact(usuelles.tupleAdd(genes1, genes2), 1/2)
            S = Slime(coords = np.random.rand(2) * self.size, args = genes)
            S.generation = max(S1.generation, S2.generation) + 1
            S.food = S.foodMax // 2
            S.age = 0
            S1.fatigue(S1.foodMax // 2)
            S2.fatigue(S2.foodMax // 2)
            self.slimes.append(S)
            return True
        return False

    def cycle(self, number, foodDecay = False):
        for i in range(number):
            random.shuffle(self.slimes)
            self.spawnFood()
            self.step()
            self.cleanSlimes()
            #print(T.plateau)
            self.clearFood()
            self.population.append(len(self.slimes))
            if i % 50 == 0:
                T.getTrucs()
                if foodDecay and i % 100 == 0:
                    self.numberFood = int(np.log(self.numberFood))

    def breed(self, slime):
        if slime.food >= slime.foodMax * (3/4) and np.random.rand() < BREED_RATE:
            genes = slime.getBreededGenes()
            S = Slime(coords = (slime.X, slime.Y), args = genes)
            S.generation = slime.generation + 1
            S.food = S.foodMax // 2
            S.age = 0
            slime.fatigue(slime.food // 2)
            self.slimes.append(S)
            return True
        else:
            return False

    def getTrucs(self):
        plt.clf()
        speed = []
        size = []
        foodMax = []
        seeRange = []
        generation = []
        age = []
        gender = []
        beauty = []
        agressivity = []
        flyrate = []
        saturation = []
        for S in self.slimes:
            speed.append(S.speed)
            size.append(S.size)
            foodMax.append(S.foodMax)
            seeRange.append(S.seeRange)
            generation.append(S.generation)
            age.append(S.age)
            gender.append(S.gender)
            beauty.append(S.beauty)
            agressivity.append(S.agressivity)
            flyrate.append(S.flyrate)
            saturation.append(S.food / S.foodMax)
        plt.subplot(3, 4, 1)
        plt.hist(speed)
        plt.title("speed")
        plt.subplot(3, 4, 2)
        plt.hist(size, color = 'lime')
        plt.title("size")
        plt.subplot(3, 4, 3)
        plt.hist(foodMax, color = 'darkorange')
        plt.title("FoodMax")
        plt.subplot(3, 4, 4)
        plt.hist(seeRange, color = 'blue')
        plt.title("seeRange")
        plt.subplot(3, 4, 5)
        plt.plot([i for i in range(len(self.population))], self.population, color = 'firebrick')
        plt.title("population")
        plt.subplot(3, 4, 6)
        plt.hist(generation, color = 'teal')
        plt.title("Génération")
        plt.subplot(3, 4, 7)
        plt.hist(age, color = 'peru')
        plt.title("Age")
        plt.subplot(3, 4, 8)
        plt.hist(gender, color = 'red')
        plt.title("Gender")
        plt.subplot(3, 4, 9)
        plt.xlim(0, 10)
        plt.hist(beauty, color = 'cyan')
        plt.title("Beauty")
        plt.subplot(3, 4, 10)
        plt.hist(agressivity, color = 'magenta')
        plt.xlim(0, 1)
        plt.title("Agressivity")
        plt.subplot(3, 4, 11)
        plt.hist(flyrate, color = 'gold')
        plt.xlim(0, 1)
        plt.title("Flyrate")
        plt.subplot(3, 4, 12)
        plt.hist(saturation, color = 'darkviolet')
        plt.xlim(0, 1)
        plt.title("Saturation")
        plt.show()
        plt.pause(0.5)




T = Terrain(10, 5, 5)
T.cycle(10000, foodDecay = False)
