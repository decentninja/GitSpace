using UnityEngine;
using System.Collections;
using LitJson;


public class Repository : MonoBehaviour {
    public GameObject folderPrefab;
	public SphereCollider collider;
    public float folderScaling = 0.0001f;
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
        //if (!"js".Equals((string)folder["name"]))
        //{
            // Set color according to file extension
            /*int numFileTypes = folder["filetypes"].Count;
            string[] fileExtension = new string[numFileTypes];
            float[] filePart = new float[numFileTypes];
            float partMax = 0;
            int index = -1;
            for (int i = 0; i < numFileTypes; i++)
            {
                fileExtension[i] = (string)folder["filetypes"][i]["extension"];
                filePart[i] = (float)folder["filetypes"][i]["part"];
                if (filePart[i] > partMax) {
                    partMax = filePart[i];
                    index = i;
                }
            }*/
            //if (index != -1) thisStar.transform.GetChild(0).GetComponent<MeshRenderer>().material.color = StringToColor(fileExtension[index]);

            // Star Size mapped to folder size (logarithmic scale)
            //float logvalue = Mathf.Log((int)folder["size"]);
            //thisStar.transform.GetChild(0).transform.localScale = Vector3.one * ((logvalue < 0) ? 0 : logvalue) * folderScaling;
            thisStar.transform.GetChild(0).transform.localScale = Vector3.one * (int) folder["size"] * folderScaling;
            // Set the folder name as gameObject name.
            thisStar.name = (string)folder["name"];

            thisStar.GetComponent<Folder>().parent = parent;
            thisStar.transform.parent = transform;
            int numSubFolders = folder["subfolder"].Count;
            for (int i = 0; i < numSubFolders; i++)
            {
                JsonData subfolder = folder["subfolder"][i];
                CreateConstellation(thisStar, subfolder);
            }
        //}
    }

    private Color StringToColor(string s) {
        int hash = s.GetHashCode();
        byte r = (byte)((hash >> 16) & 0xff);
        byte g = (byte)((hash >> 8) & 0xff);
        byte b = (byte)((hash) & 0xff);
        return new Color(r, g, b);
    }
}
