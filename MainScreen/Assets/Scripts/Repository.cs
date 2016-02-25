using UnityEngine;
using System.Collections;
using LitJson;


public class Repository : MonoBehaviour {
    public GameObject folderPrefab;
	public SphereCollider collider;
	public Canvas hudunder;
	//Queue<Message.Update> queue = new Queue<Message.Update>();

	void Update() {
		Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(transform);
		hudunder.transform.position = bounds.center + new Vector3(0, 0, bounds.extents.z);
		collider.center = bounds.center;
		collider.radius = bounds.extents.magnitude;
	}

    public void CreateConstellation(GameObject parent, JsonData folder) {
        float angle = Random.Range(0, 2 * Mathf.PI);
        Vector3 pos = new Vector3(Mathf.Sin(angle), 0, Mathf.Cos(angle)) + parent.transform.position;
        GameObject thisStar = (GameObject) Instantiate(folderPrefab, pos, Quaternion.identity);
        thisStar.GetComponent<Folder>().parent = parent;
        thisStar.transform.parent = transform;
        for (int i = 0; folder["subfolders"][i] != null; i++)
        {
            JsonData subfolder = folder["state"][i];
            CreateConstellation(thisStar, subfolder);
        }
    }
}
