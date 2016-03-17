using UnityEngine;
using System.Collections;
using LitJson;
using System.Collections.Generic;


public class Repositories : MonoBehaviour {

    public Dictionary<string, Repository> repoDictionary = new Dictionary<string, Repository>();

    public GameObject repoPrefab;
    public SeeEverythingCamera secamera;
    public GameObject legend;
    int threshold = 10080;

    void Start() {
	resetCamera();
    }

    public void handle(JsonData data) {
        string type = (string) data["type"];
	string repoName = "";
	if(type != "command") {
	    repoName = (string) data["repo"];
	}
        switch (type) {
            case "command":
		// TODO Handle display label commands using displayLabels(bool)
		// TODO handle focus camera commands using focusCamera(reponame)
		// TODO handle see everything using resetCamera(void)
        string command = (string)data["command"];
                switch (command) {
                    case "repo focus":
                        repoName = (string)data["repo"];
                        focusCamera(repoName);
                        break;
                    case "reset camera":
                        resetCamera();
                        break;
                    case "labels":
                        bool labels = (bool)data["labels"];
                        if(labels)
                        {
                            displayLabels(true);
                        } else
                        {
                            displayLabels(false);
                        }
                        break;
                    case "activity threshold":
                        this.threshold = (int)data["threshold"]; //TODO det här kanske inte funkar (int alltså)
                        break;
                }
                break;
            case "delete":
		        dierepo(repoName);
                break;
            case "state":
		        dierepo(repoName);
                Repository newRepo = Instantiate(repoPrefab).GetComponent<Repository>();
                newRepo.transform.parent = transform;
                repoDictionary.Add(repoName, newRepo);
		        newRepo.CreateConstellation(data);
                break;
            case "update":
		        repoDictionary[repoName].cueUpdate(data);
                break;
            default:
                return;
        }
    }

    void Update()
    {
        ArrayList newMailList = new ArrayList();
        ArrayList newExtList = new ArrayList();
        foreach (Folder folder in Object.FindObjectsOfType<Folder>())
        {
            if (!newMailList.Contains(folder.mail))
            {
                newMailList.Add(folder.mail);
            }
            if (!newExtList.Contains(folder.ext))
            {
                newExtList.Add(folder.ext);
            }
        }

        legend.GetComponent<Legend>().updateLegend(filterList(newMailList), filterList(newExtList));
    }

    //Merges two lists and return the latter with new values if any
    private ArrayList mergeLists(ArrayList list1, ArrayList list2)
    {
        foreach(string test in list1)
        {
            if(!list2.Contains(test))
            {
                list2.Add(test);
            }
        }
        return list2;
    }

    private ArrayList filterList(ArrayList list)
    {
        ArrayList cleanList = new ArrayList();
        foreach(string text in list)
        {
            if(text.Equals("none") || text.Equals(""))
            {
                
            } else
            {
                cleanList.Add(text);
            }
        }
        return cleanList;
    }

    private void resetCamera() {
	secamera.target = transform;
	foreach(Repository repo in repoDictionary.Values) {
	    repo.Hidden = false;
	}
    }

    private void focusCamera(string repoName) {
	secamera.target = repoDictionary[repoName].transform;
	foreach(string name in repoDictionary.Keys) {
	    if(repoName == name) {
		repoDictionary[name].Hidden = false;
	    } else {
		repoDictionary[name].Hidden = true;
	    }
	}
    }

    private void dierepo(string repoName) {
	if (repoDictionary.ContainsKey(repoName))
	{
	    Destroy(repoDictionary[repoName].gameObject);
	    repoDictionary.Remove(repoName);
	}
    }

    void displayLabels(bool yes) {
	foreach(Folder folder in Object.FindObjectsOfType<Folder>()) {
	    folder.showtext(yes);
        legend.GetComponent<Legend>().showText(yes);
	}
    }
    public int getThreshold()
    {
        return threshold;
    }

}
