using UnityEngine;
using UnityEngine.UI;
using System;
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

    // timespan given from the controlpanel to show glow, in seconds
    public int timeInterval;
    int minPower = 0;

    bool hidden = false;
    Queue<JsonData> queue = new Queue<JsonData>();
    float update_cooldown = 0;
    float update_time = 1;	// Time between updates in milliseconds
    Coroutine hiddenanimation;

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
        int numChanges = data["changes"].Count;
        for (int i = 0; i < numChanges; i++)
        {
            JsonData change = data["changes"][i];
            recursiveUpdate(null, (string)change["name"], change);
        }
        resizeallfolders();
    }

    public void recursiveUpdate(Folder parent, string foldername, JsonData data)
    {
        Dictionary<string, GameObject> currentChildren;
        GameObject parentGameObject;
        if (parent == null)
        {
            currentChildren = children;
            parentGameObject = gameObject;
        }
        else
        {
            currentChildren = parent.children;
            parentGameObject = parent.gameObject;
        }
        if ("update".Equals((string)data["action"]))
        {
            if (currentChildren.ContainsKey((string)data["name"]))
            {
                parent.children[foldername].GetComponent<Folder>().Changed((string) data["user"]);
                //set sizes of stars based on update date
                parent.children[foldername].GetComponent<Folder>().size = setFolderSize(data);

                int numChanges = data["subfolder"].Count;
                for (int i = 0; i < numChanges; i++)
                {
                    JsonData change = data["subfolder"][i];
                    Folder newparent = currentChildren[foldername].GetComponent<Folder>();
                    recursiveUpdate(newparent, (string)change["name"], change);
                }
            }
            else
            {
                GameObject star = createStar(parentGameObject, data);
                currentChildren.Add(star.name, star);
                star.GetComponent<Folder>().Changed((string) data["user"]);
                //set sizes of stars based on update date
                star.GetComponent<Folder>().size = setFolderSize(data);

                int numChanges = data["subfolder"].Count;
                for (int i = 0; i < numChanges; i++)
                {
                    JsonData change = data["subfolder"][i];
                    Folder newparent = currentChildren[star.name].GetComponent<Folder>();
                    recursiveUpdate(newparent, star.name, change);
                }
            }
        }
        else if ("delete".Equals((string)data["action"]))
        {
            Folder f = currentChildren[foldername].GetComponent<Folder>();
            List<GameObject> rmList = getSubFolders(f, null);
            foreach (GameObject g in rmList)
            {
                Destroy(g);
            }
            Destroy(currentChildren[foldername]);
            currentChildren.Remove(foldername);
        }
        return;
    }

    public List<GameObject> getSubFolders(Folder folder, List<GameObject> list)
    {
        if (list == null) list = new List<GameObject>();
        
        foreach (GameObject g in folder.children.Values)
        {
            list.Add(g);
            list = getSubFolders(g.GetComponent<Folder>(), list);
        }
        return list;
    }

    public void CreateConstellation(JsonData data)
    {
        hudunder.transform.Find("Title").GetComponent<Text>().text = (string)data["repo"];

        // rootstar code
        // may only find one root when multiple projects are shown
        GameObject root = GameObject.Find("Root");
        GameObject rootObject = (GameObject)Instantiate(rootStar);
        rootObject.transform.parent = gameObject.transform;
        rootObject.transform.GetChild(0).GetComponent<MeshRenderer>().material.color = new Color(220, 220, 255);
        rootObject.transform.GetChild(0).transform.localScale = new Vector3(1.5f,1.5f,1.5f);

        int numSubFolders = data["state"].Count;
        for (int i = 0; i < numSubFolders; i++)
        {
            JsonData folder = data["state"][i];
            try
            {
                GameObject child = recursiveCreate(gameObject, folder);
                children.Add(child.name, child);
            }
            catch (ArgumentException e) {
		Debug.LogError(e);
	    }
        }
        resizeallfolders();
    }

    public GameObject recursiveCreate(GameObject parent, JsonData folder)
    {
        // Add star.
        GameObject thisStar = createStar(parent, folder);
        Folder foldercomp = thisStar.GetComponent<Folder>();
        foldercomp.Changed((string) folder["last modified by"]);
        //foldercomp.size = ((int) folder["last modified date"]) / Datetime.Now().Second;
        //Debug.Log(foldercomp.size);
        //set sizes of stars based on update date
        foldercomp.size = setFolderSize(folder);


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
        if (index != -1)
        {
            thisStar.transform.GetChild(0).GetComponent<MeshRenderer>().material.color = StringToColor(fileExtension[index]);
        } else
        {
            thisStar.transform.GetChild(0).GetComponent<MeshRenderer>().material.color = new Color(255, 255, 255);
        }

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
        //random can be both unityenginge and system.random
        float angle = UnityEngine.Random.Range(0, 2 * Mathf.PI);
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

    public bool Hidden {
	get { return hidden; }
	set { 
	    hidden = value;
	    if(hiddenanimation != null) {
		StopCoroutine(hiddenanimation);
	    }
	    hiddenanimation = StartCoroutine(animatehidden(!value));
	}
    }

    IEnumerator animatehidden(bool to) {
	foreach(Canvas thing in GetComponentsInChildren<Canvas>()) {
	    thing.enabled = to;
	}
	foreach(MeshRenderer thing in GetComponentsInChildren<MeshRenderer>()) {
	    if(thing.enabled != to) {
		thing.enabled = to;
		yield return new WaitForSeconds(3f);
	    }
	}
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

    private Color EmailToColor(string mail)
    {
        int mod = 100;
        float h = Mathf.Abs((float)mail.GetHashCode()) % 100;
        h = h / 100;
        float s = Mathf.Abs((float)mail.GetHashCode()) % 50;
        s = (s / 100) + 0.5f;
        float v = s;

        Color color = Color.HSVToRGB(h, s, v);
        return new Color(color.r* 255, color.g* 255, color.b* 255);
    }

    /* Ändra så att det blir olika nivårer av returns, färre antal nivåer ger större skillnad i localscale när resizeallfolders kallad då man splittar sizerangen på antal nivåer*/
    public int setFolderSize(JsonData folder)
    {
        Repositories sn = FindObjectOfType<Repositories>();
        //threshold is minutes in repository.cs
        timeInterval = 60 * sn.getThreshold();
        JsonData moddate = folder["last modified date"];
        int lastmoddate = int.Parse(moddate.ToString());
        if (lastmoddate == 0 || (ConvertToUnixTimestamp(DateTime.Now) - lastmoddate) > timeInterval)
        {
            return minPower;
        }
        else
        {
            double passedtime = ConvertToUnixTimestamp(DateTime.Now) - lastmoddate;
            double rounded = 1 - (passedtime / timeInterval);
            return (int)(rounded*10);
        }
    }
    public int ConvertToUnixTimestamp(DateTime date)
    {
        DateTime origin = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc);
        TimeSpan diff = date.ToUniversalTime() - origin;
        return (int)Math.Floor(diff.TotalSeconds);
    }
}
