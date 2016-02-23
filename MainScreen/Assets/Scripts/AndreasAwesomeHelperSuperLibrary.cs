using System.Collections;
using UnityEngine;


public class AndreasAwesomeHelperSuperLibrary {

	public static Bounds CalculateTotalBounds(Transform transform) {
		Bounds bounds = new Bounds(Vector3.zero, Vector3.zero);
		foreach(Transform folder in transform) {
			Collider c = folder.GetComponent<Collider>();
			if(c)
				bounds.Encapsulate(c.bounds);
		}
		return bounds;
	}
}
