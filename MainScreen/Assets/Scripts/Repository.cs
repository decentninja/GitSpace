using UnityEngine;
using System.Collections;
using LitJson;


public class Repository : MonoBehaviour {
    public GameObject folderPrefab;
	public SphereCollider collider;
    public float folderScaling = 0.1f;
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

        // Star Size mapped to folder size (logarithmic scale)
        thisStar.transform.GetChild(0).transform.localScale = Vector3.one * Mathf.Log((int) folder["size"]) * folderScaling;
        // Set the folder name as gameObject name.
        thisStar.name = (string) folder["name"];

        thisStar.GetComponent<Folder>().parent = parent;
        thisStar.transform.parent = transform;
        int numSubFolders = folder["subfolder"].Count;
        for (int i = 0; i < numSubFolders; i++)
        {
            JsonData subfolder = folder["subfolder"][i];
            CreateConstellation(thisStar, subfolder);
        }
    }
}
