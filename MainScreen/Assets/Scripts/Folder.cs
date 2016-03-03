using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class Folder : MonoBehaviour {

	public GameObject parent;
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
