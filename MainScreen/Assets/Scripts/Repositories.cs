using UnityEngine;
using System.Collections;
using LitJson;
using System.Collections.Generic;


public class Repositories : MonoBehaviour {

    private Dictionary<string, Repository> repoDictonary = new Dictionary<string, Repository>();
    public GameObject repoPrefab;

	public void handle(JsonData data) {
        string type = (string) data["type"];
        switch (type) {
            case "command":

                break;
            case "delete":

                break;
            case "state":
                string repoName = (string)data["repo"];
                if (repoDictonary.ContainsKey(repoName))
                {
                    repoDictonary.Remove(repoName);
                }
                Repository newRepo = Instantiate(repoPrefab).GetComponent<Repository>();
                newRepo.transform.parent = transform;
                repoDictonary.Add(repoName, newRepo);
                for (int i = 0; data["state"][i] != null; i++) {
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

}
