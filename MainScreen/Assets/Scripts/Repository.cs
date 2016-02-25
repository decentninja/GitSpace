using UnityEngine;
using System.Collections;
using System.Collections.Generic;


public class Repository : MonoBehaviour {

	public SphereCollider collider;
	public Canvas hudunder;
	Queue<Message.Update> queue = new Queue<Message.Update>();

	void Update() {
		Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(transform);
		hudunder.transform.position = bounds.center + new Vector3(0, 0, bounds.extents.z);
		collider.center = bounds.center;
		collider.radius = bounds.extents.magnitude;
	}

}
