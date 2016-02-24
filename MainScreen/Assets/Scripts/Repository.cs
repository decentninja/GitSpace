using UnityEngine;
using System.Collections;
using System.Collections.Generic;


public class Repository : MonoBehaviour {

	public SphereCollider collider;
	Queue<Message.Update> queue = new Queue<Message.Update>();

	void Update() {
		Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(transform);
		collider.center = bounds.center;
		collider.radius = bounds.extents.magnitude;
	}

}
