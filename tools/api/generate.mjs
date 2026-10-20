// Intentionally bounded Python prototype; WebIDL2 owns parsing the IDL syntax.
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { parseArgs } from "node:util";
import { parse } from "webidl2";

function fail(message) {
  throw new Error(message);
}

function keysOnly(value, allowed, context) {
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) fail(`Unknown ${context} key: ${key}`);
  }
}

function identifier(value) {
  if (typeof value !== "string" || !/^[A-Za-z_]\w*$/.test(value)) {
    fail(`Invalid native identifier: ${value}`);
  }
  return value;
}

const pythonKeywords = new Set((
  "False None True and as assert async await break class continue def del elif else except " +
  "finally for from global if import in is lambda nonlocal not or pass raise return try " +
  "while with yield"
).split(" "));

function pythonIdentifier(value) {
  identifier(value);
  if (pythonKeywords.has(value)) fail(`Python keyword requires a binding override: ${value}`);
  return value;
}

function snakeCase(value) {
  return pythonIdentifier(value
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2").toLowerCase());
}

function qualifiedImport(value, alias) {
  const parts = value.split(".");
  parts.forEach(pythonIdentifier);
  if (parts.length < 2) fail(`Expected module.Type: ${value}`);
  const name = parts.pop();
  return `from ${parts.join(".")} import ${name} as ${alias}`;
}

async function generate(specPath, bindingPath) {
  const tree = parse(await readFile(specPath, "utf8"));
  const binding = JSON.parse(await readFile(bindingPath, "utf8"));
  keysOnly(binding, ["formatVersion", "interface", "target", "nativeTypes", "overrides"],
    "binding");
  if (binding.formatVersion !== 1) fail("Unsupported binding formatVersion");
  const definition = tree.find(item => item.type === "interface"
    && item.name === binding.interface);
  if (!definition) fail(`Missing interface ${binding.interface}`);
  const selected = definition.members.filter(item =>
    item.extAttrs.some(attribute => attribute.name === "StructuralPrototype"));
  if (!selected.length) fail("No StructuralPrototype members; refusing an empty check");

  const overrides = binding.overrides ?? {};
  for (const [name, override] of Object.entries(overrides)) {
    const member = definition.members.find(item => item.name === name);
    if (!member) fail(`Unknown overridden member: ${name}`);
    keysOnly(override, ["name", "parameters"], "override");
    for (const param of Object.keys(override.parameters ?? {})) {
      if (!member.arguments?.some(item => item.name === param)) {
        fail(`Unknown parameter: ${name}.${param}`);
      }
    }
  }

  const imports = new Set(["from typing import Protocol"]);
  function pythonType(type) {
    if (type.generic || type.union) fail("Prototype does not emit generics/unions");
    const primitives = {DOMString: "str", boolean: "bool", undefined: "None"};
    let name = primitives[type.idlType];
    if (!name) {
      const external = tree.find(item => item.name === type.idlType
        && item.extAttrs?.some(attribute => attribute.name === "External"));
      const native = binding.nativeTypes?.[type.idlType];
      if (!external || !native) fail(`Unmapped native type: ${type.idlType}`);
      name = `_${identifier(type.idlType)}`;
      imports.add(qualifiedImport(native, name));
    }
    return type.nullable ? `${name} | None` : name;
  }

  const surface = [];
  const protocol = [];
  const scaffold = [];
  const calls = [];
  const usedNames = new Set();
  for (const member of selected) {
    if (!["attribute", "operation"].includes(member.type)
        || !["", "static"].includes(member.special)
        || (member.type === "attribute" && member.special === "static")
        || member.extAttrs.some(attr => attr.name !== "StructuralPrototype"
          || attr.rhs || attr.arguments.length)) {
      fail(`Unsupported selected declaration: ${member.name ?? member.type}`);
    }
    const override = overrides[member.name] ?? {};
    const name = pythonIdentifier(override.name ?? snakeCase(member.name));
    if (usedNames.has(name)) fail(`Binding name collision: ${name}`);
    usedNames.add(name);
    const type = pythonType(member.idlType);
    const info = {name, kind: member.type, readonly: member.readonly ?? false,
      static: member.special === "static"};
    surface.push(info);
    if (member.type === "attribute") {
      protocol.push(`    @property\n    def ${name}(self) -> ${type}: ...`);
      scaffold.push(`    @property\n    def ${name}(self) -> ${type}:\n` +
        "        raise NotImplementedError");
      if (!member.readonly) {
        protocol.push(`    @${name}.setter\n    def ${name}(self, value: ${type}) -> None: ...`);
        scaffold.push(`    @${name}.setter\n    def ${name}(self, value: ${type}) -> None:\n` +
          "        raise NotImplementedError");
      }
    } else if (member.type === "operation") {
      info.parameters = [];
      const supplied = [];
      const required = [];
      const args = member.arguments.map(arg => {
        if (arg.variadic) fail("Prototype does not emit variadics");
        const argName = pythonIdentifier(override.parameters?.[arg.name] ?? snakeCase(arg.name));
        info.parameters.push({name: argName, optional: arg.optional});
        const argumentType = pythonType(arg.idlType);
        const callArgument = `${argName}=cast(${argumentType}, None)`;
        supplied.push(callArgument);
        if (!arg.optional) required.push(callArgument);
        let result = `${argName}: ${argumentType}`;
        if (arg.optional) {
          if (arg.default?.type !== "null") fail("Prototype supports only explicit null defaults");
          result += " = None";
        }
        return result;
      });
      if (!info.static) args.unshift("self");
      const decorator = info.static ? "    @staticmethod\n" : "";
      const signature = `${decorator}    def ${name}(${args.join(", ")}) -> ${type}`;
      protocol.push(`${signature}: ...`);
      scaffold.push(`${signature}:\n        raise NotImplementedError`);
      const receiver = info.static ? "Actual" : "value";
      calls.push(`    ${receiver}.${name}(${supplied.join(", ")})`);
      if (required.length !== supplied.length) {
        calls.push(`    ${receiver}.${name}(${required.join(", ")})`);
      }
    } else {
      fail(`Unsupported selected member kind: ${member.type}`);
    }
  }

  const header = "# Generated structural prototype. Do not edit; not a behavioral implementation.\n";
  const importText = [...imports].sort().join("\n");
  const preamble = `${header}from __future__ import annotations\n\n${importText}\n\n`;
  const actualImport = qualifiedImport(binding.target, "Actual");
  const targetName = binding.target.split(".").at(-1);
  const probe = [header, "from typing import cast", importText,
    "from contract import ExpectedAPI", actualImport,
    "\ndef check(value: Actual) -> ExpectedAPI:", "    return value",
    "\ndef check_calls(value: Actual) -> None:", calls.join("\n") || "    pass", "",
  ].join("\n");
  return {
    protocol: `${preamble}\nclass ExpectedAPI(Protocol):\n${protocol.join("\n\n")}\n`,
    scaffold: `${preamble}\nclass ${targetName}:\n${scaffold.join("\n\n")}\n`,
    probe,
    surface: {target: binding.target, members: surface, selected: selected.length,
      total: definition.members.length},
  };
}

async function main() {
  const {values} = parseArgs({options: {
    spec: {type: "string", default: "api/dicom4ortho.webidl"},
    bindings: {type: "string", default: "python/api-bindings.json"},
    output: {type: "string"},
    scaffold: {type: "string"},
  }});
  if (Boolean(values.output) === Boolean(values.scaffold)) {
    fail("Supply either --output DIRECTORY or --scaffold FILE");
  }
  const result = await generate(values.spec, values.bindings);
  if (values.scaffold) {
    // Exclusive creation protects human-written implementations, including symlinks.
    await writeFile(values.scaffold, result.scaffold, {flag: "wx"});
  } else {
    await mkdir(dirname(resolve(values.output)), {recursive: true});
    await mkdir(values.output); // No overwrite/update mode in this bootstrap prototype.
    await writeFile(join(values.output, "contract.py"), result.protocol);
    await writeFile(join(values.output, "probe.py"), result.probe);
    await writeFile(join(values.output, "surface.json"),
      JSON.stringify(result.surface, null, 2) + "\n");
  }
  console.log(`Structural prototype: ${result.surface.selected}/${result.surface.total} ` +
    "interface members; not full API conformance.");
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
