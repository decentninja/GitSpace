using UnityEngine;
using System.Collections;
using LitJson;
using System.Collections.Generic;


public class Repositories : MonoBehaviour {

    private Dictionary<string, Repository> repoDictonary = new Dictionary<string, Repository>();

    public GameObject repoPrefab;

	public void handle(JsonData data) {
        string type = (string) data["type"];
	string repoName;
        switch (type) {
            case "command":

                break;
            case "delete":
                repoName = (string) data["repo"];
		dierepo(repoName);
                break;
            case "state":
                repoName = (string) data["repo"];
		dierepo(repoName);
                Repository newRepo = Instantiate(repoPrefab).GetComponent<Repository>();
                newRepo.transform.parent = transform;
                repoDictonary.Add(repoName, newRepo);
                int numSubFolders = data["state"].Count;
                for (int i = 0; i < numSubFolders; i++) {
                    JsonData folder = data["state"][i];
                    newRepo.CreateConstellation(newRepo.gameObject, folder);
                }
                break;
            case "update":

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
