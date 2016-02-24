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
    public int port = 21;

    TcpListener server;
    NetworkStream stream;
    Queue<JsonData> changeQueue;
    Thread thread;

    void Start () {
        StartCoroutine("TCPClientRoutine");
    }

    private void ParseJSON(string json) {
        try {
	    JsonData parsed = JsonMapper.ToObject(json);
            string type = parsed["type"].ToString();
	    switch(type) {
		case "state":
		    changeQueue.Clear();
		    // TODO handle
		    break;
		case "update":
		    changeQueue.Enqueue(parsed);
		    break;
		default:
		    Debug.LogError("Unhandeled message type " + type);
		    break;
            }
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
		if(c == 1)
		    continue;
		if(c == 4) {
		    string done = json.ToString();
		    Debug.Log(done);
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
