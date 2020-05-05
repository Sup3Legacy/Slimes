using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class Slime : MonoBehaviour
{
    public Rigidbody rb;
    public Transform tf;
    GameObject constante;
    CONSTANTES constantes;
    public int Life = 100;
    //Genes
    public int maxLife = 100;
    public float height = 1f;
    public float speed = 1f;
    public float viewRange = 5f;
    public float beauty = 1f;
    public int gestationDelay = 10; //Nombre de tours avant naissance des enfants
    public double direction = -1;

    //Params
    public string gender = "male";
    public float forceIntensity = 100f;
    float lateralForce = 0f;
    float forwardForce = 0f;
    int sinceTick = 0;
    int sinceMate = 0; //Duree actuelle de gestation; ne concerne que female

    public Slime partner = null; //Référence du partenaire, pour avoir les gènes
    float[] mateGenes;
    float[] Genes;
    List<Slime> localSlimeList;
    List<Food> localFoodList;


    void Start() {
        Genes = new float[] {(float)maxLife, height, speed, viewRange, beauty, (float)gestationDelay};
        //Récupération des constantes de jeu
        constante = GameObject.Find("CONSTANTES");
        constantes = constante.GetComponent<CONSTANTES>();

        //Préparation des données locales
        Vector3 scale = new Vector3 (height, height, height);
        transform.localScale = scale;
        rb.mass = height * height * height;
        sinceTick = (int)(Random.Range(0, constantes.tickSpeed));
    }

    void OnEnable() { //Slime ajouté la la liste globale à la naissance
        CONSTANTES.slimeList.Add(this);
    }

    void OnDisable() {
        CONSTANTES.slimeList.Remove(this);
    }

    void Update () {
        if (sinceTick >= constantes.tickSpeed) { //Actions à chaque tick de jeu
            direction = -1;
            //Survie
            if (Life <= 0 | transform.position.y < -1f){ //Slime meurt si plus de vie
                CONSTANTES.slimeList.Remove(this);
                Destroy(gameObject);
            }

            //Reproduction
            if (partner != null){ //Si un autre slime a cherché à mate et critère de beauté
                if (partner.beauty/beauty >= Random.Range(0f, 2f)) {
                    Life = Life / 2;
                    partner.Life = partner.Life / 2;
                    if (gender == "female") {
                        mateGenes = new float[] {(float)partner.maxLife, partner.height, partner.speed, partner.viewRange, partner.beauty, (float)partner.gestationDelay};
                        partner.partner = null;
                        partner = null;
                    }
                    else {
                        partner.mateGenes = new float[] {(float)partner.maxLife, partner.height, partner.speed, partner.viewRange, partner.beauty, (float)partner.gestationDelay};
                        partner.partner = null;
                        partner = null;
                    }
                }
                else {
                    partner = null;
                }
            }

            if (mateGenes != null) { // Si on a un génome de partner
                if (sinceMate < gestationDelay) {
                    sinceMate += 1;
                }
                else {
                    float[] offspringGenome = mutateGenome(mixGenomes(Genes, mateGenes)); //Récupère le génome enfant, muté
                    GameObject.Find("Spawner").GetComponent<Spawner>().spawnOffspring(offspringGenome); //Spawn l'enfant
                    Debug.Log("Mated and reproduced !");
                    sinceMate = 0;
                    mateGenes = null;
                }
            }





            if (CONSTANTES.slimeList.Count > 0) { //Action si un slime dans le coin
                Slime nearestSlime = getNearestSlime(CONSTANTES.slimeList);
                if (Life >= maxLife / 2 & nearestSlime.gender != gender & (nearestSlime.transform.position - transform.position).magnitude <= viewRange) { //S'il est de genre opposé -> mate
                    tryMate(nearestSlime);
                }
                else { //Sinon -> Attack
                  if ((nearestSlime.transform.position - transform.position).magnitude <= viewRange) {
                      attack(getNearestSlime(CONSTANTES.slimeList), 10);
                }
              }
            }

            if (CONSTANTES.foodList.Count > 0) { //Recherche de nourriture
                Food nearestFood = getNearestFood(CONSTANTES.foodList);
                if ((nearestFood.transform.position - transform.position).magnitude <= viewRange) {
                    eat(nearestFood, 10);
                }
                else {
                    float deltaz = nearestFood.transform.position.z - transform.position.z;
                    float deltax = nearestFood.transform.position.x - transform.position.x;
                    direction = Mathf.Atan2(deltaz, deltax);
                }
            }

            //Perte d'énergie après le mouvement
            Life -= (int)(speed * (double)constantes.foodUsageMultiplier * height * height * height);

            //Direction, mouvement
            if (direction == -1 | (float) Life / (float) maxLife >= 0.5) { //Conditions pour ne pas avoir à focus la nourriture
                direction = Random.Range((float)0, (float)(2 * System.Math.PI));
            }
            //Rotation
            var angles = transform.rotation.eulerAngles;
            angles.z = (float)direction * (180f / (float)System.Math.PI);
            var rotation = Quaternion.Euler(angles);
            tf.rotation = rotation;
            //Forces
            forwardForce = (speed * (float)System.Math.Sin(direction) * constantes.movementForceMultiplier);
            lateralForce = (speed * (float)System.Math.Cos(direction) * constantes.movementForceMultiplier);
            //Debug.Log(string.Format("{0}, {1}, {2}", System.Math.Sin(direction), lateralForce, forwardForce));
            sinceTick = 0;
        }
        else {
            sinceTick += 1;
        }
    }






    void FixedUpdate () {
        //Application des forces calculées dans Update
        rb.AddForce(lateralForce * Time.deltaTime, 0, 0, ForceMode.VelocityChange);
        rb.AddForce(0, 0, forwardForce * Time.deltaTime, ForceMode.VelocityChange);
    }

    void attack(Slime autreSlime, int degats){
        Life -= constantes.minimalAttackHarm;
        autreSlime.Life -= constantes.minimalAttackHarm;
        Life -= constantes.attackHarmMultiplier * ((int)(autreSlime.height / height) - 1);
        autreSlime.Life += constantes.attackHarmMultiplier * ((int)(autreSlime.height / height) - 1);
    }

    void eat(Food food, int amount) {
        food.GetComponent<Food>().foodAmount -= amount;
        Life = Mathf.Min(maxLife, Life + amount);
    }

    Slime getNearestSlime(List<Slime> slimes) {
        // Détermination du slime le plus proche
        int length = slimes.Count;
        float minimum = 0f;
        int plusProcheSlime = 0;
        Slime autreSlime;
        for (int i = 0; i < length; i++){
            autreSlime = slimes[i];
            if (autreSlime != this & autreSlime != null) {
                float distance = (autreSlime.transform.position - transform.position).magnitude;
                if (distance < minimum | minimum == 0f) {
                    plusProcheSlime = i;
                    minimum = distance;
                  }
                }
            }
        return slimes[plusProcheSlime];
    }

    Food getNearestFood(List<Food> foods) {
        //Détermination de la nourriture la plus proche
        int length = foods.Count;
        float minimum = 0f;
        int plusProcheFood = 0;
        Food food;
        for (int i = 0; i < length; i++){
            food = foods[i];
            if (food != null) {
                float distance = (food.transform.position - transform.position).magnitude;
                if ((distance < minimum | minimum == 0f) & food.GetComponent<Food>().foodAmount > 0) {
                    plusProcheFood = i;
                    minimum = distance;
                }
            }
        }
        return foods[plusProcheFood];
    }

    void tryMate(Slime potentialMatePartner) { //Approche pour mate. La réussite dépend de la beauté, bien sûr.
        if (potentialMatePartner.beauty/beauty >= Random.Range(0f, 2f)) {
            potentialMatePartner.partner = this;
        }
    }

    //Utilitaires génétiques
    float[] mixGenomes(float[] G1, float[] G2){
        int L = G1.Length;
        float[] res = new float[L];
        for (int i = 0; i < L; i++) {
            res[i] = 0.5f * (G1[i] + G2[i]);
        }
        return res;
    }

    float[] mutateGenome(float[] genome) {
        int L = genome.Length;
        for (int i = 0; i < L; i++) {
            if (Random.Range(0f, 1f) <= constantes.MutationRate) {
                genome[i] = Mathf.Max(0f, genome[i] + GaussianExtended(0f, genome[i] * constantes.MutationEffectMultiplier));
            }
        }
        return genome;
    }

    public static float Gaussian() {
        float v1, v2, s;
        do {
            v1 = 2.0f * Random.Range(0f,1f) - 1.0f;
            v2 = 2.0f * Random.Range(0f,1f) - 1.0f;
            s = v1 * v1 + v2 * v2;
        } while (s >= 1.0f || s == 0f);

        s = Mathf.Sqrt((-2.0f * Mathf.Log(s)) / s);

        return v1 * s;
    }

    public static float GaussianExtended(float mean, float standard_deviation)
    {
        return mean + Gaussian() * standard_deviation;
    }

}
