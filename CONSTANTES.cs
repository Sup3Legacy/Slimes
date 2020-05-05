using System.Collections;
using System.Collections.Generic;
﻿using UnityEngine;

public class CONSTANTES : MonoBehaviour
{
    public float MutationRate = 0.5f;
    public float MutationEffectMultiplier = 1f;
    public int maxFood = 10;
    public int foodAmountUnit = 50;
    public int foodUsageMultiplier = 5;
    public int tickSpeed = 20; // Nombre de tics entre chaque action
    public float movementForceMultiplier = 10f;
    public int foodTickSpeed = 600; //Nombre de ticks avtn le respawn de nourriture
    public static List<Slime> slimeList = new List<Slime>();
    public static List<Food> foodList = new List<Food>();
    public int minimalAttackHarm = 1;
    public int attackHarmMultiplier = 5;

    void Update() {
        //Debug.Log(string.Format("{0}, {1}", slimeList.Count, foodList.Count));
    }
}
