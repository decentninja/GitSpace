using UnityEngine;
using System.Collections;

public class DrawLines : MonoBehaviour {

	public Repositories repositories;
	public Material mat;
	public float lowest = 0.1f;

	void OnPostRender() {
		GL.PushMatrix();
		foreach(Repository child in repositories.repoDictionary.Values) {
			if(!child.Hidden) {
				foreach(Transform grandchild in child.transform) {
					Folder folder = grandchild.GetComponent<Folder>();
					if(folder != null) {
						mat.SetPass(0);
						mat.SetColor("_EmissionColor", folder.EmailToColor());
						Color c = mat.color;
						c.a = lowest + folder.extraglow;
						mat.color = c;
						GL.Begin(GL.LINES);
						GL.Vertex(folder.transform.position);
						GL.Vertex(folder.parent.transform.position);
						GL.End();
					}
				}
			}
		}
		GL.PopMatrix();
	}
}
