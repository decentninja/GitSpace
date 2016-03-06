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

	void Start () {
		spring.connectedBody = parent.GetComponent<Rigidbody>();
		text.text = name;
	}

	public void showtext(bool yes) {
		text.enabled = yes;
	}
	
}
