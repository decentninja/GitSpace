using UnityEngine;
using System.Collections;
using System;

public class TimeManager : MonoBehaviour {
    private bool isRealtime = true;
    private DateTime currentDate;
	
	void Update () {
        if (isRealtime) {
            currentDate = DateTime.Now;
        }
	}

    public void setToRealtime() {
        isRealtime = true;
    }

    public bool isRealTime() {
        return isRealtime;
    }

    public DateTime getCurrentDate() {
        return currentDate;
    }

    public void setCurrentDate(int unixtime) {
        isRealtime = false;
        currentDate = UnixTimeStampToDateTime(unixtime);
    }

    public DateTime UnixTimeStampToDateTime(double unixTimeStamp)
    {
        DateTime dtDateTime = new DateTime(1970, 1, 1, 0, 0, 0, 0, System.DateTimeKind.Utc);
        dtDateTime = dtDateTime.AddSeconds(unixTimeStamp).ToLocalTime();
        return dtDateTime;
    }
}
