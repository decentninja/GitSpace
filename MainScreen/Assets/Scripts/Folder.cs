﻿using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;

public class Folder : MonoBehaviour {

    public GameObject parent;
    public Dictionary<string, GameObject> children = new Dictionary<string, GameObject>();
    public SpringJoint spring;
    public Rigidbody rb;
    public int size;
    public int lastModifiedDate;
    public Text text;
    public float extraglow = 0;
    public float glowdiminish = 0.5f;
    public float minimumglow = 0.2f;
    public float maxglow = 200;
    string mail = "";

    void Start () {
	spring.connectedBody = parent.GetComponent<Rigidbody>();
	text.text = name;
    }

    void Update() {
	if(extraglow > 0) {
	    extraglow -= Time.deltaTime * glowdiminish;
	}
	EmailToColor();
    }

    public void showtext(bool yes) {
	text.enabled = yes;
    }

    public void Changed(string user) {
	mail = user;
	extraglow = 1;
    }

    public Color EmailToColor()
    {
        int mod = 100;
        float h = Mathf.Abs((float)mail.GetHashCode()) % 100;
        h = h / 100;
        float s = Mathf.Abs((float)mail.GetHashCode()) % 50;
        s = s / 100;
        float v = s;
        Color c = Color.HSVToRGB(h, s, v);
	float g = Mathf.Max(minimumglow, extraglow) * maxglow;
	return new Color(c.r * g, c.g * g, c.b * g);
    }
}
