﻿using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using LitJson;


public class Repository : MonoBehaviour {
    public GameObject folderPrefab;
    public SphereCollider collider;
    public Dictionary<string, GameObject> children = new Dictionary<string, GameObject>();
    public Canvas hudunder;
    public float folderStartSize = 0.5f;
    public float folderMaxSize = 2f;
    public GameObject rootStar;

    Queue<JsonData> queue = new Queue<JsonData>();
    float update_cooldown = 0;
    float update_time = 1;	// Time between updates in milliseconds

    void Update() {
	Bounds bounds = AndreasAwesomeHelperSuperLibrary.CalculateTotalBounds(transform);
	hudunder.transform.position = bounds.center + new Vector3(0, 0, bounds.extents.z);
	collider.center = bounds.center;
	collider.radius = bounds.extents.magnitude;

	update_cooldown -= Time.deltaTime;
	if(update_cooldown < 0 && queue.Count != 0) {
	    update_cooldown = update_time;
	    handleUpdate(queue.Dequeue());
	}
    }

    void setTime(JsonData data) {
	try {
	    GameObject gh = GameObject.Find("HUD");
	    if(gh != null) {
		gh.GetComponent<HUD>().setTime((int) data["timestamp"]);
	    }
	} catch(KeyNotFoundException) {}
    }

    void handleUpdate(JsonData data)
    {
        setTime(data);
        int numChanges = data["changes"].Count;
        for (int i = 0; i < numChanges; i++)
        {
            JsonData change = data["changes"][i];
            Folder changedFolder = children[(string)change["name"]].GetComponent<Folder>();
            recursiveUpdate(changedFolder, change);
        }
    }

    public void recursiveUpdate(Folder folder, JsonData data)
    {
        if ("update".Equals((string)data["action"]))
        {
            //folder.change(); //nån funktion som updaterar glow och sånt

            int numChanges = data["subfolder"].Count;
            for (int i = 0; i < numChanges; i++)
            {
                JsonData change = data["subfolder"][i];
                Folder changedFolder = children[(string)change["name"]].GetComponent<Folder>();
                recursiveUpdate(changedFolder, change);
            }
        }
        else if ("create".Equals((string)data["action"]))
        {
            createStar(folder.gameObject, data);

            int numChanges = data["subfolder"].Count;
            for (int i = 0; i < numChanges; i++)
            {
                JsonData change = data["subfolder"][i];
                Folder changedFolder = children[(string)change["name"]].GetComponent<Folder>();
                recursiveUpdate(changedFolder, change);
            }
        }
        else if ("delete".Equals((string)data["action"]))
        {
            //TODO
        }
    }

    public List<GameObject> getSubFolders(Folder folder, JsonData data)
    {
        int numChanges = data["subfolder"].Count;
        for (int i = 0; i < numChanges; i++)
        {
            JsonData change = data["subfolder"][i];
            Folder changedFolder = children[(string)change["name"]].GetComponent<Folder>();
            recursiveUpdate(changedFolder, change);
        }
        return null;
    }

    public void CreateConstellation(JsonData data)
    {
        setTime(data);
        hudunder.transform.Find("Title").GetComponent<Text>().text = (string)data["repo"];

        // rootstar code
        GameObject root = GameObject.Find("Root");
        GameObject rootObject = (GameObject)Instantiate(rootStar);
        rootObject.transform.parent = gameObject.transform;
        rootObject.transform.GetChild(0).GetComponent<MeshRenderer>().material.color = new Color(220, 220, 255);
        rootObject.transform.GetChild(0).transform.localScale = new Vector3(1.5f,1.5f,1.5f);

        int numSubFolders = data["state"].Count;
        for (int i = 0; i < numSubFolders; i++)
        {
            JsonData folder = data["state"][i];
            GameObject child = recursiveCreate(gameObject, folder);
            children.Add(child.name, child);
        }
        resizeallfolders();
    }

    public GameObject recursiveCreate(GameObject parent, JsonData folder)
    {
        // Add star.
        GameObject thisStar = createStar(parent, folder);
        Folder foldercomp = thisStar.GetComponent<Folder>();
        foldercomp.size = (int)folder["size"];

        // Calculate color using file extension.
        int numFileTypes = folder["filetypes"].Count;
        string[] fileExtension = new string[numFileTypes];
        float[] filePart = new float[numFileTypes];
        float partMax = 0;
        int index = -1;
        for (int i = 0; i < numFileTypes; i++)
        {
            fileExtension[i] = (string)folder["filetypes"][i]["extension"];
            filePart[i] = float.Parse(folder["filetypes"][i]["part"].ToString());
            if (filePart[i] > partMax)
            {
                partMax = filePart[i];
                index = i;
            }
        }
        if (index != -1) thisStar.transform.GetChild(0).GetComponent<MeshRenderer>().material.color = StringToColor(fileExtension[index]);

        // Recursively go down the file tree.
        int numSubFolders = folder["subfolder"].Count;
        for (int i = 0; i < numSubFolders; i++)
        {
            JsonData subfolder = folder["subfolder"][i];
            GameObject child = recursiveCreate(thisStar, subfolder);
            foldercomp.children.Add(child.name, child);
        }
        return thisStar;
    }

    private GameObject createStar(GameObject parent, JsonData data)
    {
        float angle = Random.Range(0, 2 * Mathf.PI);
        Vector3 pos = new Vector3(Mathf.Sin(angle), 0, Mathf.Cos(angle)) + parent.transform.position;
        GameObject star = (GameObject)Instantiate(folderPrefab, pos, Quaternion.identity);

        star.name = (string)data["name"];
        Folder foldercomp = star.GetComponent<Folder>();
        foldercomp.parent = parent;
        star.transform.parent = transform;

        return star;
    }

    private void resizeallfolders() {
	SortedList<int,List<Folder>> children = new SortedList<int,List<Folder>>();
	foreach(Transform t in transform) {
	    Folder folder = t.GetComponent<Folder>();
	    if(folder != null) {
		List<Folder> row;
		if(children.ContainsKey(folder.size)) {
		    row = children[folder.size];
		} else {
		    row = new List<Folder>();
		}
		row.Add(folder);
		children[folder.size] = row;
	    }
	}
	float step = (folderMaxSize - folderStartSize) / children.Count;
	float currentSize = folderStartSize;
	foreach(KeyValuePair<int, List<Folder>> kvp in children) {
	    foreach(Folder folder in kvp.Value) {
		folder.transform.GetChild(0).transform.localScale = Vector3.one * currentSize;
	    }
	    currentSize += step;
	}
    }
    
    public void cueUpdate(JsonData update) {
	queue.Enqueue(update);
    }

    private Color StringToColor(string s) {
        int mod = 255;
        float hash = Mathf.Abs((float)s.GetHashCode()) % (mod * 2);
        Color color;

        if (hash <= mod) //Gradient from red to white
        {
            color = Color.Lerp(Color.red, Color.white, hash / mod);
            return new Color(color.r * 255, color.g * 255, color.b * 255); //RGB values have to be in the interval 0 to 255 (rather than 0 to 1) for the glow to work
        }
        else if (hash <= mod * 2) //Gradient from white to blue
        {
            hash -= mod;
            color = Color.Lerp(Color.white, Color.blue, hash / mod);
            return new Color(color.r * 255, color.g * 255, color.b * 255);
        }
        else
        {
            Debug.Log("Color Error");
            return new Color(0, 0, 0);
        }
    }
}
