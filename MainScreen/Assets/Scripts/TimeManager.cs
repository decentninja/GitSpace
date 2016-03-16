using UnityEngine;
using System.Collections;
using System;

public class TimeManager : MonoBehaviour {
    public bool isRealtime = true;
    public DateTime currentDate;
	
	void Update () {
        if (isRealtime) {
            currentDate = DateTime.Now;
        }
	}

    public void setToRealtime() {
        isRealtime = true;
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
        dtDateTime = dtDateTime.AddSeconds(unixTimeStamp - 3600).ToLocalTime(); // -3600 to Adjust for timezone
        return dtDateTime;
    }
}
