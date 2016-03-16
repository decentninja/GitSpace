using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System;

public class HUD : MonoBehaviour {

	public Text time;
    public bool isRealtime = true;

	public void setTime(int unixtime) {
        isRealtime = false;
        DateTime datetime = UnixTimeStampToDateTime(unixtime);
        time.text = datetime.ToString("yyyy.MM.dd HH:mm");
    }

    public void setToRealTime() {
        isRealtime = true;
    }

	void Update() {
        if (isRealtime) {
		    DateTime datetime = DateTime.Now;
		    time.text = datetime.ToString("yyyy.MM.dd HH:mm");
        }
	}

    public static DateTime UnixTimeStampToDateTime(double unixTimeStamp)
    {
        // Unix timestamp is seconds past epoch
        DateTime dtDateTime = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
        dtDateTime = dtDateTime.AddSeconds(unixTimeStamp - 3600).ToLocalTime(); // -3600 to Adjust for timezone
        return dtDateTime;
    }
}
