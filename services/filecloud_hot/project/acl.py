import json

class fileACL:
    def __init__(self) -> None:
        pass

    def get_acl(self, source_system):
        acl = { 
            "read": "[all]",
            "write": f"[{source_system}]",
            "delete": f"[{source_system}]"
            }
        return json.dumps(acl)
