using UnityEngine;
using System.Collections;

public class SeeEverythingCamera : MonoBehaviour {

	public Transform target;
	public float margin = 1;
	Camera camera;

	void Start() {
		camera = GetComponent<Camera>();
	}

	void Update () {
		Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(target);
		float height = bounds.size.z;
		Vector3 pos = bounds.center;
		pos.y = -height * 0.5f / Mathf.Tan(camera.fieldOfView * 0.5f * Mathf.Deg2Rad);
		pos.y *= margin;
		transform.position = pos;
	}
}
