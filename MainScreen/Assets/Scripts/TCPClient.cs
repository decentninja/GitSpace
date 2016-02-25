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
