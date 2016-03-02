using UnityEngine;
using System.Collections;

public class Folder : MonoBehaviour {

	public GameObject parent;
	public SpringJoint spring;
	public Rigidbody rb;
	public int size;

	void Start () {
		spring.connectedBody = parent.GetComponent<Rigidbody>();
	}

}
