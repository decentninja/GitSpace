using UnityEngine;
using System.Collections;
using System;

public class RootStarControl : MonoBehaviour {

    public TimeManager tm;

	// Use this for initialization
	void Start () {
        tm = FindObjectOfType<TimeManager>();
	}
	
	// Update is called once per frame
	void Update () {
        DateTime currentTime = tm.currentDate;
        //hours 22 to and including 6 counts as night
        if(currentTime.Hour > 21 || currentTime.Hour < 7)
        {
            this.gameObject.transform.GetChild(0).gameObject.SetActive(false); //sun
            this.gameObject.transform.GetChild(1).gameObject.SetActive(true); //moon
        }
        else //daytime
        {
            this.gameObject.transform.GetChild(0).gameObject.SetActive(true);
            this.gameObject.transform.GetChild(1).gameObject.SetActive(false);
        }
    }
}
