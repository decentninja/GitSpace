using UnityEngine;
using System.Text;
using System.Collections;
using System.Net.Sockets;
using System.IO;
using System;
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
        Message.Message message = GitSpaceJSON.parse(json);
        if(message == null) {
            Debug.LogError("Unable to parse json " + json);
            return;
        }
        switch(message.type) {
            case "update":
                repos.update((Message.Update) message);
                break;
            case "state":
                repos.renew((Message.State) message);
                break;
            case "delete":
                repos.delete((Message.Delete) message);
                break;
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
