"""One shared contract for model responses and deterministic validation."""


def obj(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


TEXT = {"type": "string"}


def choices(*values):
    return {"type": "string", "enum": list(values)}


def array(items):
    return {"type": "array", "items": items}


GATES = ("reachability", "impact", "reproduction", "existing_protections", "control_case", "scope")
GATE = obj({"result": choices("PASS", "FAIL", "UNRESOLVED"), "evidence": TEXT})
PROOF = obj({"artifact": TEXT, "command": TEXT, "exit_code": {"type": "integer"},
             "observation": TEXT, "control_observation": TEXT})
FINDING = obj({
    "id": TEXT, "title": TEXT, "status": choices("confirmed", "unverified", "dismissed"),
    "severity": choices("critical", "high", "medium", "low", "informational"),
    "file": TEXT, "line": {"type": "integer"}, "source_excerpt": TEXT,
    "preconditions": TEXT, "expected": TEXT, "actual": TEXT, "impact": TEXT,
    "reproduction_steps": array(TEXT), "proof": PROOF,
    "falsification": TEXT, "fix": TEXT, "regression_test": TEXT,
    "next_action": TEXT, "gates": obj({name: GATE for name in GATES}),
})
RESPONSE = obj({
    "summary": TEXT, "done": {"type": "boolean"},
    "coverage": array(obj({"surface": TEXT, "file": TEXT,
                           "status": choices("reviewed", "tested", "blocked", "unreviewed"),
                           "details": TEXT})),
    "findings": array(FINDING), "blockers": array(TEXT), "next_steps": array(TEXT),
})


def validate(value, schema=RESPONSE, path="response"):
    """Validate the intentionally small JSON Schema subset used above, without dependencies."""
    kind = schema["type"]
    expected = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}[kind]
    if type(value) is not expected:
        raise ValueError(f"{path}: expected {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: invalid value {value!r}")
    if kind == "object":
        keys = set(schema["properties"])
        if set(value) != keys:
            raise ValueError(f"{path}: missing {sorted(keys - set(value))}; unexpected {sorted(set(value) - keys)}")
        for key, child in schema["properties"].items():
            validate(value[key], child, f"{path}.{key}")
    elif kind == "array":
        for i, item in enumerate(value):
            validate(item, schema["items"], f"{path}[{i}]")
