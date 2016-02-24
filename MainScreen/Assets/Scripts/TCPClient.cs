using UnityEngine;
using System.Collections;
using System.Net.Sockets;
using System.IO;
using LitJson;
using System;
using System.Collections.Generic;
using System.Net;
using System.Threading;

public class TCPClient : MonoBehaviour {

    public List<JsonData> updatedList;
    public bool stateChanged = false;

    string testLine = "{'api version': 1,'type': 'delete','repo': 'Linux'}" + "\n";
    public string ipaddress = "127.0.0.1";
    public int port = 21;
    TcpListener server;
    NetworkStream stream;
    StreamReader reader;
    StreamWriter writer;
    JsonData itemData;
    List<JsonData> itemDataList;

    Thread thread;
    bool mRunning = true;

	// Use this for initialization
	void Start () {

        itemDataList = new List<JsonData>();
        updatedList = new List<JsonData>();

        StartCoroutine("TCPClientRoutine");
        InvokeRepeating("Trigger", 5f, 1f);
        /*ThreadStart ts = new ThreadStart(ThreadMethod);
        thread = new Thread(ts);
        thread.Start();*/

        
    }

    private void ParseJSON(string line)
    {
        try
        {

            itemData = JsonMapper.ToObject(line);

            string type = itemData["type"].ToString();

            if (type == "state")
            {
                itemDataList.RemoveRange(0, itemDataList.Count - 1);
                itemDataList.Add(itemData);
                stateChanged = true;
            }
            else if (type == "command" || type == "delete" || type == "update")
            {
                itemDataList.Add(itemData);
                stateChanged = true;
            }
            else
            {
                Debug.Log("Wrong type");
            }

        }
        catch (Exception e)
        {
            Debug.Log("Invalid JSON");
            //Debug.LogException(e);
        }


    }

    IEnumerator TCPServerRoutine()
    {
        IPAddress ip = IPAddress.Parse(ipaddress);
        server = new TcpListener(ip, port);
        server.Start();
        yield return null;
    }

    IEnumerator TCPClientRoutine()
    {
        Debug.Log("Started Client Coroutine");
        TcpClient connection = new TcpClient(ipaddress, port);
        NetworkStream stream = connection.GetStream();
        StreamReader reader = new StreamReader(stream);
        StreamWriter writer = new StreamWriter(stream);
        
        
        while(true)
        {
            
            if (stream.DataAvailable)
            {
                
                string line = reader.ReadLine();
                //string line = testLine;
                if (line != null)
                {
                    ParseJSON(line);
                }
            }
            else
            {
                
            }
            

            yield return null;
        }
        
    }

    void ThreadMethod()
    {
        

        try
        {
            IPAddress ip = IPAddress.Parse(ipaddress);
            server = new TcpListener(ip, port);
            server.Start();
            print("Server Start");
            while (mRunning)
            {
                // check if new connections are pending, if not, be nice and sleep 100ms
                if (!server.Pending())
                {
                    Thread.Sleep(100);
                }
                else
                {

                    TcpClient client = server.AcceptTcpClient();
 
                    NetworkStream ns = client.GetStream();

                    StreamReader rd = new StreamReader(ns);

                    string msg = rd.ReadLine();
                    Debug.Log(msg);
                    ParseJSON(msg);
                    rd.Close();
                    client.Close();
                }
            }
        }
        catch (ThreadAbortException)
        {
            print("exception");
        }
        finally
        {
            mRunning = false;
            server.Stop();
        }

    }

    private void Trigger()
    {
        updatedList = itemDataList;
    }

    public List<JsonData> GetUpdatedList()
    {
        stateChanged = false;
        List<JsonData> tempList = updatedList;
        updatedList.RemoveRange(0, updatedList.Count - 1);
        return tempList;
    }

    // Update is called once per frame
    void Update () {


    }
}
