using UnityEngine;
using System.Collections;
using System.Collections.Generic;


public class Repository : MonoBehaviour {
    public GameObject folderPrefab;
	public SphereCollider collider;
	Queue<Message.Update> queue = new Queue<Message.Update>();

	void Update() {
		Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(transform);
		collider.center = bounds.center;
		collider.radius = bounds.extents.magnitude;
	}

    public void CreateConstellation(GameObject parent, Message.Folder folder) {
        float angle = Random.Range(0, 2 * Mathf.PI);
        Vector3 pos = new Vector3(Mathf.Sin(angle), 0, Mathf.Cos(angle)) + parent.transform.position;
        GameObject thisStar = (GameObject) Instantiate(folderPrefab, pos, Quaternion.identity);
        thisStar.transform.parent = transform;
        foreach (Message.Folder subfolder in folder.subfolder)
        {
            CreateConstellation(thisStar, subfolder);
        }
    }
}
