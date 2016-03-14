using UnityEngine;
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
    public Gradient edgecolor;
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
	Color c = edgecolor.Evaluate((1 + (float) mail.GetHashCode() / int.MaxValue) / 2);
	float g = Mathf.Max(minimumglow, extraglow) * maxglow;
	c = new Color(c.r * g, c.g * g, c.b * g);
	return c;
    }
}
