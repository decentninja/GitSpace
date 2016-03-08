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
	foreach(string name in repoDictionary.Keys) {
	    if(repoName == name) {
		secamera.target = repoDictionary[name].transform;
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
