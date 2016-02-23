using UnityEngine;
using System.Collections;


public class Repository : MonoBehaviour {

	public SphereCollider collider;

	void Update() {
		Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(transform);
		collider.center = bounds.center;
		collider.radius = bounds.extents.magnitude;
	}

}
