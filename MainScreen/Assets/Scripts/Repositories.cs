using UnityEngine;
using System.Collections;
using System.Collections.Generic;


public class Repositories : MonoBehaviour {
    private Dictionary<string, Repository> repoDictonary = new Dictionary<string, Repository>();
    public GameObject repoPrefab;

	public void delete(Message.Delete data) {}

	public void update(Message.Update data) {}

	public void renew(Message.State data) {
        if (repoDictonary.ContainsKey(data.repo)) {
            repoDictonary.Remove(data.repo);
        }
        Repository newRepo = Instantiate(repoPrefab).GetComponent<Repository>();
        newRepo.transform.parent = transform;
        repoDictonary.Add(data.repo, newRepo);
        print(data.repo);
        foreach (Message.Folder folder in data.state) {
            newRepo.CreateConstellation(newRepo.gameObject, folder);
        }
    }

}
