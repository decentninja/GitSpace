using UnityEngine;
using System.Collections;
using LitJson;
using System.Collections.Generic;


public class Repositories : MonoBehaviour {

    private Dictionary<string, Repository> repoDictonary = new Dictionary<string, Repository>();

    public GameObject repoPrefab;

    public void handle(JsonData data) {
        string type = (string) data["type"];
	string repoName = "";
	if(type != "command") {
	    repoName = (string) data["repo"];
	}
        switch (type) {
            case "command":
                break;
            case "delete":
		dierepo(repoName);
                break;
            case "state":
		dierepo(repoName);
                Repository newRepo = Instantiate(repoPrefab).GetComponent<Repository>();
                newRepo.transform.parent = transform;
                repoDictonary.Add(repoName, newRepo);
		newRepo.CreateConstellation(data);
                break;
            case "update":
		repoDictonary[repoName].cueUpdate(data);
                break;
            default:
                return;
        }

    }

    private void dierepo(string repoName) {
	if (repoDictonary.ContainsKey(repoName))
	{
	    Destroy(repoDictonary[repoName]);
	    repoDictonary.Remove(repoName);
	}
    }

}
