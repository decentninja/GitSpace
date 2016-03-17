using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Collections;

public class Options {
	public string host;
}

public class Settings : MonoBehaviour {

	public InputField hostfield;
	public Options options;
	public GameObject chooser;

	void Start () {
		DontDestroyOnLoad(transform.gameObject);
		hostfield.Select();
	}
	
	void Update () {
		if(Input.GetKeyDown(KeyCode.Return)) {
			Connect();
		}
		if(Input.GetKeyDown(KeyCode.Escape)) {
			Application.Quit();
		}
	}

	public void Connect() {
		options = new Options();
		if(hostfield.text.Length != 0) {
			options.host = hostfield.text;
		} else {
			options.host = "127.0.0.1";
		}
		chooser.SetActive(false);
		SceneManager.LoadScene("Mainscreen");
	}
}
