using System.Collections;
using UnityEngine;


namespace Message {

	public class Message {
		public string type;
		public string repo;
	}

	public class Delete : Message {}

	public class State : Message {
		public int timestamp;
		public Folder[] state;
	}

	public class Update : Message {
		public string name;
		public int size;
		public string direction;
		public Change[] changes;
		public bool forced;
	}

	public class Folder {
		public string name;
		public int size;
		public Folder[] subfolder;
		public Filetype[] filetypes;
	}

	public class Change {
		public string name;
		public int size;
		public string user;
		public bool non_master_branch;
		public Change[] subfolder;
		public Filetype[] filetypes;
	}

	public class Filetype {
		public string extension;
		public float part;
	}
}


public class GitSpaceJSON {

	public static Message.Message parse(string json) {
		Message.Message type = JsonUtility.FromJson<Message.Message>(json);
		if(type != null) {
			switch(type.type) {
				case "update":
					return JsonUtility.FromJson<Message.Update>(json);
				case "delete":
					return JsonUtility.FromJson<Message.Delete>(json);
				case "state":
					return JsonUtility.FromJson<Message.State>(json);
			}
		}
		return null;
	}
}
