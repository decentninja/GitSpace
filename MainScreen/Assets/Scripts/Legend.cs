using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class Legend : MonoBehaviour {

    private ArrayList userList;
    private ArrayList extensionList;
    public Text text;
    public GameObject userPanel;
    public GameObject extensionPanel;
    public Repository repo;
    private ArrayList texts = new ArrayList();

    public void updateLegend(ArrayList users, ArrayList extensions)
    {
        userList = users;
        extensionList = extensions;
        Text[] delUserList = userPanel.GetComponentsInChildren<Text>();
        Text[] delExtList = extensionPanel.GetComponentsInChildren<Text>();
        Text[] sumList = new Text[delExtList.Length + delUserList.Length];
        delUserList.CopyTo(sumList, 0);
        delExtList.CopyTo(sumList, delUserList.Length);
        foreach(Text text in sumList)
        {
            Destroy(text.gameObject);
        }

        foreach(string user in users)
        {
            Text newtext = Instantiate(text) as Text;
            newtext.text = user;
            newtext.color = fixColor(repo.StringToColor(user));
            newtext.transform.SetParent(userPanel.transform);
            texts.Add(newtext);
        }
        foreach(string extension in extensions)
        {
            Text newtext2 = Instantiate(text) as Text;
            newtext2.text = extension;
            newtext2.color = fixColor(repo.StringToColor(extension));
            newtext2.transform.SetParent(extensionPanel.transform);
            texts.Add(newtext2);
        }
    }

    /*
    void Start()
    {
        Text newtext1 = Instantiate(text) as Text;
        newtext1.fontStyle = FontStyle.Bold;
        newtext1.fontSize = newtext1.fontSize + 4;
        newtext1.text = "Users";
        newtext1.color = Color.white;
        newtext1.transform.SetParent(userPanel.transform);

        Text newtext2 = Instantiate(text) as Text;
        newtext2.fontStyle = FontStyle.Bold;
        newtext2.fontSize = newtext2.fontSize + 4;
        newtext2.text = "Extensions";
        newtext2.color = Color.white;
        newtext2.transform.SetParent(extensionPanel.transform);
    }*/


    public void showText(bool yes)
    {
        foreach(Text text in texts)
        {
            text.enabled = yes;
        }
    }

    private Color fixColor(Color color)
    {
        Color newcolor = new Color(color.r / 255, color.g / 255, color.b / 255);
        return newcolor;
    }
}
