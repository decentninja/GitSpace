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
	public Text text;
	public float extraglow = 0;
	public float glowdiminish = 0.5f;

	void Start () {
		spring.connectedBody = parent.GetComponent<Rigidbody>();
		text.text = name;
	}

	void Update() {
		if(extraglow > 0) {
			extraglow -= Time.deltaTime * glowdiminish;
		}
	}

	public void showtext(bool yes) {
		text.enabled = yes;
	}

	public void Changed() {
		extraglow = 1;
	}
}
