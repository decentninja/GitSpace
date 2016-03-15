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
        StartCoroutine("TCPClientRoutine");
    }

    void Update () {
        // Test Delete folder by pressing '1'. Removes Assets folder from the constellation.
        if (Input.GetKeyDown("1")) {
            ParseJSON("{ 'type': 'update', 'repo': 'decentninja/GitSpace', 'apiv': 1, 'direction': 'forward', 'forced': false, 'changes': [{ 'last modified date': 1230583, 'name': 'MainScreen', 'last modified by': 'test@test.com', 'action': 'update', 'non_master_branch': false, 'subfolder': [{ 'last modified date': 1230583, 'name': 'Assets', 'last modified by': 'test@test.com', 'action': 'delete', 'non_master_branch': false, 'subfolder': [], 'filetypes': [] }], 'filetypes': [] }] }");
        }
        // Test Create folder by pressing '2'. Adds a folder containing a folder to MainScreen.
        if (Input.GetKeyDown("2")) {
            ParseJSON("{'type': 'update','repo': 'decentninja/GitSpace','apiv': 1,'direction': 'forward','forced': false,'changes': [{'last modified date': 1230583,'name': 'MainScreen','last modified by': 'test@test.com','action': 'update','non_master_branch': false,'subfolder': [{'last modified date': 1230583,'name': 'TestFolder','last modified by': 'test@test.com','action': 'update','non_master_branch': false,'subfolder': [{'last modified date': 1230583,'name': 'TestFolder2','last modified by': 'test@test.com','action': 'update','non_master_branch': false,'subfolder': [],'filetypes': []}],'filetypes': []}],'filetypes': []}]}");
        }
        if (Input.GetKeyDown("3")) {
            ParseJSON("{'api version': 1,'type': 'delete','repo':'decentninja/GitSpace'}");
        }
        
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
	string name = "gitspace";
	Byte[] bytes = System.Text.Encoding.UTF8.GetBytes(name);
	stream.Write(bytes, 0, bytes.Length);
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
