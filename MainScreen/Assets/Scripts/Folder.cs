using UnityEngine;
using System.Collections;

public class Folder : MonoBehaviour {

	public GameObject parent;
	public LineRenderer line;
	public SpringJoint spring;
	public Rigidbody rb;
	public int size;

	void Start () {
		spring.connectedBody = parent.GetComponent<Rigidbody>();
	}

	void Update () {
		line.SetPosition(0, transform.position);
		line.SetPosition(1, parent.transform.position);
	}
}
