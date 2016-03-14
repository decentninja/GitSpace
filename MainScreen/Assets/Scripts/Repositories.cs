using UnityEngine;
using System.Collections;
using LitJson;
using System.Collections.Generic;


public class Repositories : MonoBehaviour {

    public Dictionary<string, Repository> repoDictionary = new Dictionary<string, Repository>();

    public GameObject repoPrefab;
    public SeeEverythingCamera secamera;

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
                        string labels = (string)data["labels"];
                        if(labels.Equals("true"))
                        {
                            displayLabels(true);
                        } else if (labels.Equals("false"))
                        {
                            displayLabels(false);
                        } else {
                            Debug.Log("Error, label neither true nor false.");
                        }
                        break;
                    case "activity threshold":
                        int threshold = (int)data["threshold"]; //TODO det här kanske inte funkar (int alltså)
                        Debug.Log("Not implemented. Set activity threshold to: " + threshold);
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
	    Destroy(repoDictionary[repoName]);
	    repoDictionary.Remove(repoName);
	}
    }

    void displayLabels(bool yes) {
	foreach(Folder folder in Object.FindObjectsOfType<Folder>()) {
	    folder.showtext(yes);
	}
    }

}
