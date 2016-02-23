using UnityEngine;
using System.Collections;

public class Folder : MonoBehaviour {

	public Folder parent;
	public LineRenderer line;
	public SpringJoint spring;
	public Rigidbody rb;
	float savedOffMinDistance;
	float savedOffMaxDistance;

	void Start () {
		if(parent) {
			spring.connectedBody = parent.rb;
			line.enabled = true;
		} else {
			rb.constraints |= RigidbodyConstraints.FreezePosition;
			savedOffMinDistance = spring.minDistance;
			savedOffMaxDistance = spring.maxDistance;
			spring.minDistance = 0;
			spring.maxDistance = 0;
		}
	}

	public void SetParent(Folder other) {
		line.enabled = true;
		rb.constraints = RigidbodyConstraints.FreezeRotation;
		parent = other;
		spring.connectedBody = parent.rb;
		spring.minDistance = savedOffMinDistance;
		spring.maxDistance = savedOffMaxDistance;
	}
	
	void Update () {
		if(parent) {
			line.SetPosition(0, transform.position);
			line.SetPosition(1, parent.transform.position);
		}
	}
}
