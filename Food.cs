using UnityEngine;

public class Food : MonoBehaviour
{
    public int foodAmount;
    GameObject constante;
    CONSTANTES constantes;
    void Start()
    {
        constante = GameObject.Find("CONSTANTES");
        constantes = constante.GetComponent<CONSTANTES>();
        foodAmount = constantes.foodAmountUnit;
    }

    void Update()
    {
        if (foodAmount <= 0) {
            CONSTANTES.foodList.Remove(this);
            Destroy(gameObject);
        }
    }

    void OnEnable() {
        CONSTANTES.foodList.Add(this);
    }

    void OnDisable() {
        CONSTANTES.foodList.Remove(this);
    }
}
