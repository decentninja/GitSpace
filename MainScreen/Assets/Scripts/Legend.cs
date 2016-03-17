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
    public Folder folder;
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
            texts.Remove(text);
            Destroy(text.gameObject);
        }

        foreach(string user in users)
        {
            Text newtext = Instantiate(text) as Text;
            newtext.text = user;
            newtext.fontSize = Screen.width / 80;
            newtext.color = fixColor(EmailToColor(user));
            newtext.transform.SetParent(userPanel.transform);
            texts.Add(newtext);
        }
        foreach(string extension in extensions)
        {
            Text newtext2 = Instantiate(text) as Text;
            newtext2.text = extension;
            newtext2.fontSize = Screen.width / 80;
            newtext2.color = fixColor(repo.StringToColor(extension));
            newtext2.transform.SetParent(extensionPanel.transform);
            texts.Add(newtext2);
        }
    }

    public void showText(bool yes)
    {
        userPanel.active = yes;
        extensionPanel.active = yes;
    }

    private Color fixColor(Color color)
    {
        Color newcolor = new Color(color.r / 255, color.g / 255, color.b / 255);
        return newcolor;
    }
    public Color EmailToColor(string mail)
    {
        Color c = folder.edgecolor.Evaluate((1 + (float)(mail).GetHashCode() / int.MaxValue) / 2);
        //float g = Mathf.Max(folder.minimumglow, folder.extraglow) * folder.maxglow;
        float g = 255;
        c = new Color(c.r * g, c.g * g, c.b * g);
        return c;
    }
}
