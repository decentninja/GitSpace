using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System;

public class HUD : MonoBehaviour {

	public Text time;

	public void setTime(int unixtime) { }

	void Update() {
		DateTime datetime = DateTime.Now;
		time.text = datetime.ToString("yyyy.MM.dd HH:mm");
	}
}
