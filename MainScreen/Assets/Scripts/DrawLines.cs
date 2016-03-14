using UnityEngine;
using System.Collections;

public class DrawLines : MonoBehaviour {

	public Material mat;
	public Repositories repositories;
	public Color glow_target;

	Color originalmat;

	void Awake() {
		originalmat = mat.color;
	}

	void OnPostRender() {
		GL.PushMatrix();
		mat.SetPass(0);
		foreach(Repository child in repositories.repoDictionary.Values) {
			if(!child.Hidden) {
				foreach(Transform grandchild in child.transform) {
					Folder folder = grandchild.GetComponent<Folder>();
					if(folder != null) {
						mat.color = Color.Lerp(originalmat, glow_target, folder.extraglow);
						mat.SetPass(0);
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
