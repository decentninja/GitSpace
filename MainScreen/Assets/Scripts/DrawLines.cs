using UnityEngine;
using System.Collections;

public class DrawLines : MonoBehaviour {

	public Material mat;
	public Repositories repositories;

	void OnPostRender() {
		GL.PushMatrix();
		mat.SetPass(0);
		foreach(Transform child in repositories.transform) {
			foreach(Transform grandchild in child) {
				Folder folder = grandchild.GetComponent<Folder>();
				if(folder != null) {
					GL.Begin(GL.LINES);
					GL.Vertex(folder.transform.position);
					GL.Vertex(folder.parent.transform.position);
					GL.End();
				}
			}
		}
		GL.PopMatrix();
	}

}
