using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System;

public class HUD : MonoBehaviour {

	public Text time;

	void Start() {
		setTime(0);
	}

	public void setTime(int unixtime) {
		DateTime datetime = new DateTime(1970, 1, 1);
		datetime.AddMilliseconds(unixtime);
		time.text = datetime.ToString("yyyy.mm.dd HH:MM");
	}
}
