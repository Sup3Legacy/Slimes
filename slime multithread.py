import numpy as np
import sys, threading
import matplotlib
import matplotlib.pyplot as plt
import usuelles
import random
import time

#matplotlib.use('Agg')

plt.ion()

BREED_RATE = 0.75
COEFF_DIFFERENCE_BEAUTE = 0.5 # Coeff lié à la probabilité qu'un slime veuille mate avec un partenaire moins beau que lui, * la différence de beauté
COEFF_ABSORPTION = 2
COEFF_SPEED = 1
COEFF_FATIGUE = 1
COEFF_DEGAT = 1
COEFF_MUTATION = 0.5 #Coeff pour l'ampleur des mutations de l'agressivité et de la fuite

NOMBRE_BOUFFE = 25 #Quantité de bouffe par tas

TICK_INTERVAL = 100 #ms
TICK_FOOD = 50 #Nouvelle nourriture tous les TICK_FOOD ticks
DELAY_SCREEN = 500

FOODMAX_INIT = 100
SEERANGE_INIT = 2
EAT_AND_WALK = 0.1 # Proba de bouger même si de la nourriture a été trouvée
SPEED_INIT = 1
SIZE_INIT = 1
AGRESSIVITY_INIT = 0 #(Entre 0 et 1)
DEGAT_CONST = 1 #Dégât minimal causé
FLY_INIT = 0

def distanceEntities(self, e1, e2):
    return np.sqrt((e1.X - e2.X) ** 2 + (e1.Y - e2.Y) ** 2)

class Food:
    def __init__(self, coords):
        self.amount = NOMBRE_BOUFFE
        self.X, self.Y = coords


    def __repr__(self):
        return "\033[1;33;40mF " + str(self.amount) + "\033[1;37;40m"

class FoodList:
    def __init__(self, nombre, size):
        self.foodItems = [Food(np.random.rand(2) * size) for _ in range(nombre)]
        self.size = size
        self.nombre = nombre

    def refill(self):
        self.foodItems = [Food(np.random.rand(2) * self.size) for _ in range(self.nombre)]

class Slime(threading.Thread):
    def run(self):
        currentTick = 0
        while self.food > 0:
            time.sleep(0.001)
            if self.population.tick > currentTick:
                self.searchTarget()
                self.searchMate()
                if not self.searchFood() or np.random.rand() < EAT_AND_WALK:
                    self.searchPlace()
                self.age += 1
                currentTick += 1


    def __init__(self, coords, pop, foodList, args = []):
        threading.Thread.__init__(self)
        self.population = pop
        self.foodList = foodList
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

    def getDistance(self, entity):
        return np.sqrt((self.X - entity.X) ** 2 + (self.Y - entity.Y) ** 2)

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

    def searchFood(self): #Bon
        possibles = []
        if self.food >= self.foodMax:
            self.food = self.foodMax
            return False
        for F in self.foodList.foodItems:
            if self.getDistance(F) <= self.seeRange and F.amount > 0:
                possibles.append(F)
        if possibles != []:
            F = possibles[np.random.randint(0, len(possibles))]
            self.eat(F, self.getDistance(F))
            return True
        else:
            return False

    def searchPlace(self): #Bon
        alpha = np.random.rand() * 2 *  np.pi
        distance = np.random.rand()
        X = usuelles.clipcoord(self.X + distance * COEFF_SPEED * self.speed * np.cos(alpha), self.population.size)
        Y = usuelles.clipcoord(self.Y + distance * COEFF_SPEED * self.speed * np.sin(alpha), self.population.size)
        self.X, self.Y = X, Y
        self.fatigue((self.speed ** 2) * (self.size ** 3) * COEFF_FATIGUE * distance)
        return True

    def searchMate(self): #Bon
        if self.food < self.foodMax * (3 / 4):
            return False
        possible = []
        for S in self.population.slimes:
            if self.getDistance(S) <= min(self.seeRange, S.seeRange) and S.food >= S.foodMax * (3 / 4) and self.gender != S.gender:
                possible.append(S)
        if possible != []:
            possible = sorted(possible, key = lambda object : object.beauty)
            S = possible[len(possible) - 1] #On prend le plus beau partenaire potentiel!
            if np.random.rand() * abs(self.beauty - S.beauty) <= COEFF_DIFFERENCE_BEAUTE:
                return self.mate(S)
        return False

    def searchTarget(self):
        possibles = []
        for S in self.population.slimes:
            dist = self.getDistance(S)
            if dist <= min(self.seeRange, S.seeRange) and dist > 0 and self.gender == S.gender:
                possibles.append(S)
        if possibles != []:
            possibles = sorted(possibles, key = lambda slime : slime.size)
            faible = possibles[0]
            fort = possibles[len(possibles) - 1]
            if random.random() <= self.agressivity:
                self.attack(faible, self.getDistance(faible))
            if random.random() <= self.flyrate:
                self.fly(fort, self.population.size)
        else:
            return False

    def mate(self, partner):
        if np.random.rand() < BREED_RATE:
            genes1 = list(self.getBreededGenes())
            genes2 = list(partner.getBreededGenes())
            genes = usuelles.tupleFact(usuelles.tupleAdd(genes1, genes2), 1/2)
            S = Slime(coords = np.random.rand(2) * self.size, pop = self.population, foodList = self.foodList, args = genes)
            S.generation = max(self.generation, partner.generation) + 1
            S.food = S.foodMax // 2
            S.age = 0
            self.fatigue(self.foodMax // 2)
            partner.fatigue(partner.foodMax // 2)
            self.population.slimes.append(S)
            return True
        return False

class Population:
    def __init__(self, nombre, foodList, size):
        self.tick = 0
        self.tickInterval = TICK_INTERVAL
        self.size = size
        self.foodList = foodList
        self.slimes = [Slime(self.size * np.random.rand(2), self, self.foodList) for i in range(nombre)]
        self.nombreSlimes = [nombre]
        self.foodTick = TICK_FOOD
        self.finished = False
        for S in self.slimes:
            S.start()

    def nextTick(self):
        self.tick += 1
        time.sleep(self.tickInterval / 1000)
        if self.tick % self.foodTick == 0:
            print('Ticked ' + str(self.tick) + " " + str(threading.active_count()))

    def cleanSlimes(self):
        n = len(self.slimes)
        for i in reversed(range(0, n)):
            S = self.slimes[i]
            if S.food <= 0:
                S.join()
                self.slimes.pop(i)

    def launch(self, number): # Fait ticker number fois
        for i in range(number):
            self.nextTick()
            if i % self.foodTick == 0:
                self.foodList.refill()
                self.nombreSlimes.append(len(self.slimes))
                self.cleanSlimes()
                self.getTrucs()
        self.finished = True
        for S in self.slimes:
            S.join()

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
        plt.plot([i for i in range(len(self.nombreSlimes))], self.nombreSlimes, color = 'firebrick')
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
        plt.pause(0.01)

class Terrain:

    def __init__(self, size, numberSlimes, numberFood):
        self.size = size
        self.numberSlimes = numberSlimes
        self.numberFood = numberFood
        self.food = FoodList(self.numberFood, size)
        self.population = Population(self.numberSlimes, self.food, self.size)

    """def clear(self):
        self.population.slimes = []
        self.food = FoodList(0, self.size)"""

    def spawnFood(self):
        self.food.refill()

    """def clearFood(self):
        self.food = FoodList(0, self.size)"""

    def spawnSlime(self, coords, args):
        self.population.slimes.append(Slime(coords, pop = self.pop, foodList = self.food, args = args))

    def step(self):
        return True
        for i in reversed(range(len(self.population.slimes))):
            S = self.population.slimes[i]
            self.searchTarget(S)
            self.searchMate(S)
            if not self.searchFood(S) or np.random.rand() < EAT_AND_WALK:
                self.searchPlace(S)
            S.age += 1

    def cycle(self, number):
        self.population.launch(number)

    def breed(self, slime):
        if slime.food >= slime.foodMax * (3/4) and np.random.rand() < BREED_RATE:
            genes = slime.getBreededGenes()
            S = Slime(coords = (slime.X, slime.Y), args = genes)
            S.generation = slime.generation + 1
            S.food = S.foodMax // 2
            S.age = 0
            slime.fatigue(slime.food // 2)
            self.population.slimes.append(S)
            return True
        else:
            return False






T = Terrain(10, 10, 20)
T.cycle(1000)
