using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System;

public class HUD : MonoBehaviour {

	public Text time;

	public void setTime(int unixtime) {
		DateTime datetime = new DateTime(1970, 1, 1);
		datetime = datetime.AddSeconds(unixtime);
		time.text = datetime.ToString("yyyy.MM.dd HH:mm");
	}
}
