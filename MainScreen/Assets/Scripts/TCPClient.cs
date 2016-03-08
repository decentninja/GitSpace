using UnityEngine;
using System.Text;
using System.Collections;
using System.Net.Sockets;
using System.IO;
using LitJson;
using System;
using System.Collections.Generic;
using System.Net;
using System.Threading;


public class TCPClient : MonoBehaviour {

    public string ipaddress = "127.0.0.1";
    public int port = 5522;
    public Repositories repos;

    TcpListener server;
    NetworkStream stream;
    Thread thread;

    void Start () {
        //StartCoroutine("TCPClientRoutine");
	ParseJSON("{'type': 'state', 'state': [{'size': 370, 'name': 'MainScreen', 'subfolder': [{'size': 960, 'name': 'Assets', 'subfolder': [{'size': 1423, 'name': 'Editor', 'subfolder': [], 'filetypes': [{'part': 0.9578355586788475, 'extension': 'cs'}, {'part': 0.0421644413211525, 'extension': 'meta'}]}, {'size': 0, 'name': 'Materials', 'subfolder': [], 'filetypes': [{'part': 0, 'extension': ''}]}, {'size': 0, 'name': 'Scenes', 'subfolder': [], 'filetypes': [{'part': 0, 'extension': ''}]}, {'size': 0, 'name': 'Scripts', 'subfolder': [], 'filetypes': [{'part': 0, 'extension': ''}]}, {'size': 27748, 'name': 'UniMerge', 'subfolder': [{'size': 844, 'name': 'Demo', 'subfolder': [], 'filetypes': [{'part': 0.7559241706161137, 'extension': 'meta'}, {'part': 0.24407582938388625, 'extension': 'cs'}]}, {'size': 139805, 'name': 'Editor', 'subfolder': [], 'filetypes': [{'part': 0.9982833232001717, 'extension': 'cs'}, {'part': 0.0017166767998283324, 'extension': 'meta'}]}, {'size': 99070, 'name': 'Skin', 'subfolder': [], 'filetypes': [{'part': 0.2279802160088826, 'extension': 'png'}, {'part': 0.04166750782275159, 'extension': 'meta'}, {'part': 0.7303522761683658, 'extension': 'guiskin'}]}], 'filetypes': [{'part': 0.02515496612368459, 'extension': 'meta'}, {'part': 0.10227764163182933, 'extension': 'zip'}, {'part': 0.8725673922444861, 'extension': 'txt'}]}], 'filetypes': [{'part': 1.0, 'extension': 'meta'}]}, {'size': 27870, 'name': 'ProjectSettings', 'subfolder': [], 'filetypes': [{'part': 0.9981341944743451, 'extension': 'asset'}, {'part': 0.001865805525654826, 'extension': 'txt'}]}], 'filetypes': [{'part': 1.0, 'extension': ''}]}], 'repo': 'GitSpace', 'api version': 1, 'timestamp': 52341414}");
	ParseJSON("{'type': 'state', 'state': [{'size': 370, 'name': 'MainScreen', 'subfolder': [{'size': 960, 'name': 'Assets', 'subfolder': [{'size': 1423, 'name': 'Editor', 'subfolder': [], 'filetypes': [{'part': 0.9578355586788475, 'extension': 'cs'}, {'part': 0.0421644413211525, 'extension': 'meta'}]}, {'size': 0, 'name': 'Materials', 'subfolder': [], 'filetypes': [{'part': 0, 'extension': ''}]}, {'size': 0, 'name': 'Scenes', 'subfolder': [], 'filetypes': [{'part': 0, 'extension': ''}]}, {'size': 0, 'name': 'Scripts', 'subfolder': [], 'filetypes': [{'part': 0, 'extension': ''}]}, {'size': 27748, 'name': 'UniMerge', 'subfolder': [{'size': 844, 'name': 'Demo', 'subfolder': [], 'filetypes': [{'part': 0.7559241706161137, 'extension': 'meta'}, {'part': 0.24407582938388625, 'extension': 'cs'}]}, {'size': 139805, 'name': 'Editor', 'subfolder': [], 'filetypes': [{'part': 0.9982833232001717, 'extension': 'cs'}, {'part': 0.0017166767998283324, 'extension': 'meta'}]}, {'size': 99070, 'name': 'Skin', 'subfolder': [], 'filetypes': [{'part': 0.2279802160088826, 'extension': 'png'}, {'part': 0.04166750782275159, 'extension': 'meta'}, {'part': 0.7303522761683658, 'extension': 'guiskin'}]}], 'filetypes': [{'part': 0.02515496612368459, 'extension': 'meta'}, {'part': 0.10227764163182933, 'extension': 'zip'}, {'part': 0.8725673922444861, 'extension': 'txt'}]}], 'filetypes': [{'part': 1.0, 'extension': 'meta'}]}, {'size': 27870, 'name': 'ProjectSettings', 'subfolder': [], 'filetypes': [{'part': 0.9981341944743451, 'extension': 'asset'}, {'part': 0.001865805525654826, 'extension': 'txt'}]}], 'filetypes': [{'part': 1.0, 'extension': ''}]}], 'repo': 'Another GitSpace', 'api version': 1, 'timestamp': 52341414}");
    }

    private void ParseJSON(string json) {
        try {
	    JsonData parsed = JsonMapper.ToObject(json);
	    repos.handle(parsed);
        }
        catch (JsonException e) {
            Debug.LogError("Invalid JSON " + json);
        }
    }

    IEnumerator TCPClientRoutine() {
        TcpClient connection = new TcpClient(ipaddress, port);
        NetworkStream stream = connection.GetStream();
	StringBuilder json = new StringBuilder();
	while(true) {
	    if(stream.DataAvailable) {
		int c = stream.ReadByte();
		if(c == 2)
		    continue;
		if(c == 3) {
		    string done = json.ToString();
		    ParseJSON(done);
		    json.Length = 0;
		    yield return null;
		} else {
		    json.Append((char) c);
		}
	    } else {
		yield return null;
	    }
        }
    }

}
