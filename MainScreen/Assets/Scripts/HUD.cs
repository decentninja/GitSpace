using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System;

public class HUD : MonoBehaviour {

	public Text time;
    public bool isRealtime = true;
    private TimeManager tm;

    void Start() {
        tm = FindObjectOfType<TimeManager>();
    }

	void Update() {
		time.text = tm.getCurrentDate().ToString("yyyy.MM.dd HH:mm");
	}
}
