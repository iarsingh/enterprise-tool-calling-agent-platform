TOOLS = ["catalog.search", "policy.check", "cost.estimate"]
FORBIDDEN = ("apply", "delete", "destroy", "kubectl apply")


class InputError(ValueError):
    pass


def list_tools():
    return {"tools": TOOLS}


def call(name, arguments):
    if name not in TOOLS:
        raise InputError(f"unknown tool: {name}")
    blob = " ".join(str(v) for v in (arguments or {}).values()).lower() + " " + name
    if any(word in blob for word in FORBIDDEN):
        return {"ok": False, "reason": "apply and delete are refused", "applied": False}
    return {"ok": True, "tool": name, "echo": arguments or {}, "applied": False}
