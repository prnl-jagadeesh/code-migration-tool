import json
import esprima # type: ignore
import copy
import os
import subprocess

# --- AST Generation ---
def generate_js_ast(file_path: str) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f: source_code = f.read()
        return esprima.parseScript(source_code, loc=True, range=True, tokens=True, comment=True).toDict()
    except Exception: return {}

def generate_ts_ast(file_path: str, node_script_name: str = "generate_ts_ast.js") -> dict:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tsx_file_abs_path = os.path.abspath(file_path)
        node_script_full_path = os.path.join(script_dir, node_script_name)
        process = subprocess.run(
            ["node", node_script_full_path, tsx_file_abs_path],
            capture_output=True, text=True, check=True, cwd=script_dir, env=os.environ.copy()
        )
        return json.loads(process.stdout)
    except Exception: return {}

# --- AST Cleaning and Normalization Logic ---
SYNTAX_KIND_TO_STRING_MAP = {
    0: "Unknown", 1: "EndOfFileToken", 8: "NumericLiteral", 9: "BigIntLiteral", 10: "StringLiteral",
    39: "PlusToken", 40: "MinusToken", 41: "AsteriskToken", 43: "SlashToken", 44: "PercentToken", 42: "AsteriskAsteriskToken",
    55: "AmpersandAmpersandToken", 56: "BarBarToken", 60: "QuestionQuestionToken",
    79: "Identifier", 80: "PrivateIdentifier", 84: "ClassKeyword", 85: "ConstKeyword", 92: "EnumKeyword",
    93: "ExportKeyword", 95: "FalseKeyword", 98: "FunctionKeyword", 104: "NullKeyword", 110: "TrueKeyword",
    113: "VarKeyword", 117: "ImplementsKeyword", 118: "InterfaceKeyword", 121: "PrivateKeyword",
    122: "ProtectedKeyword", 123: "PublicKeyword", 124: "StaticKeyword", 126: "AbstractKeyword",
    130: "AnyKeyword", 133: "BooleanKeyword", 135: "DeclareKeyword", 137: "InferKeyword",
    140: "KeyOfKeyword", 141: "ModuleKeyword", 143: "NeverKeyword", 144: "ReadonlyKeyword",
    146: "NumberKeyword", 147: "ObjectKeyword", 149: "StringKeyword", 150: "SymbolKeyword",
    151: "TypeKeyword", 152: "UndefinedKeyword", 154: "UnknownKeyword", 114: "VoidKeyword",
    162: "TypeParameter", 163: "Parameter", 164: "Decorator", 165: "PropertySignature",
    166: "PropertyDeclaration", 167: "MethodSignature", 168: "MethodDeclaration", 169: "Constructor",
    170: "GetAccessor", 171: "SetAccessor", 172: "CallSignature", 173: "ConstructSignature",
    174: "IndexSignature", 175: "TypePredicate", 176: "TypeReference", 177: "FunctionType",
    178: "ConstructorType", 179: "TypeQuery", 180: "TypeLiteral", 181: "ArrayType", 182: "TupleType",
    183: "OptionalType", 184: "RestType", 185: "UnionType", 186: "IntersectionType",
    187: "ConditionalType", 188: "InferType", 189: "ParenthesizedType", 190: "ThisType",
    191: "TypeOperator", 192: "IndexedAccessType", 193: "MappedType", 194: "LiteralType",
    198: "ImportType", 206: "CallExpression", 209: "TypeAssertionExpression",
    211: "FunctionExpression", 212: "ArrowFunction", 219: "BinaryExpression",
    226: "ExpressionWithTypeArguments", 227: "AsExpression", 228: "NonNullExpression",
    231: "SatisfiesExpression", 232: "Block", 233: "VariableStatement",
    244: "ReturnStatement", 251: "VariableDeclaration", 252: "VariableDeclarationList",
    253: "FunctionDeclaration", 254: "ClassDeclaration", 255: "InterfaceDeclaration",
    256: "TypeAliasDeclaration", 257: "EnumDeclaration", 258: "ModuleDeclaration",
    262: "ImportEqualsDeclaration", 288: "HeritageClause", 298: "SourceFile",
    "TSTypeAnnotation": 18000, "TSParameterProperty": 16300,
}
BINARY_OPERATOR_MAP = {
    SYNTAX_KIND_TO_STRING_MAP.get(39): "+", SYNTAX_KIND_TO_STRING_MAP.get(40): "-", 
    SYNTAX_KIND_TO_STRING_MAP.get(41): "*", SYNTAX_KIND_TO_STRING_MAP.get(43): "/",
    SYNTAX_KIND_TO_STRING_MAP.get(44): "%", SYNTAX_KIND_TO_STRING_MAP.get(42): "**",
    SYNTAX_KIND_TO_STRING_MAP.get(55): "&&", SYNTAX_KIND_TO_STRING_MAP.get(56): "||", 
    SYNTAX_KIND_TO_STRING_MAP.get(60): "??",
}

TS_NODE_KINDS_TO_REMOVE_STRINGS = {
    SYNTAX_KIND_TO_STRING_MAP.get(k) for k in [
        117, 118, 126, 127, 128, 130, 135, 137, 138, 139, 140, 141, 142, 143, 144, 151, 153, 154, 159,
        162, 164, 165, 167, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185,
        186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198,
        209, 226, 227, 228, 231, 255, 256, 257, 258, 262, 288,
        133, 146, 147, 149, 150, 114, 152, # Type keywords
    ] if SYNTAX_KIND_TO_STRING_MAP.get(k) is not None
}
TS_NODE_KINDS_TO_REMOVE_STRINGS.update([
    "TSTypeAnnotation", "TypeAnnotation", "TSParameterProperty",
    "CallSignatureDeclaration", "ConstructSignatureDeclaration", "IndexSignatureDeclaration",
    "MethodSignature", "PropertySignature", "TSMethodSignature", "TSPropertySignature",
    "TSInterfaceDeclaration", "TSTypeAliasDeclaration", "TSEnumDeclaration", "TSModuleDeclaration",
    "TSIntrinsicKeyword", "TSLiteralType", "TSStringLiteralType", "TSNumberLiteralType",
    "TSBooleanLiteralType", "TSNullKeyword",
])

PROPERTIES_TO_REMOVE = {
    "typeAnnotation", "typeParameters", "implements", "accessibility", "optional",
    "readonly", "decorators", "questionToken", "exclamationToken", "colonToken",
    "declare", "abstract", "typeArguments",
    'loc', 'range', 'raw', 'comments', 'leadingComments', 'trailingComments', 'start', 'end',
    'pos', 'parent', "modifierFlagsCache", "transformFlags", 'jsDoc', 'jsDocCache', 'flowNode',
    "checkFlags", "locals", "nextContainer", "symbol", "emitNode",
    "parseDiagnostics", "bindDiagnostics", "scriptKind", "isDeclarationFile", "hasNoDefaultLib",
    "externalModuleIndicator", "nodeCount", "identifierCount", "symbolCount",
    "languageVersion", "languageVariant", "fileName", "path", "resolvedPath", "originalFileName",
    "amdDependencies", "moduleAugmentations", "pragmas", "referencedFiles", "typeReferenceDirectives",
    "libReferenceDirectives", "nameType", "parameterName", "types",
    "questionDotToken", "dotDotDotToken", "exclamationToken",
    "tokens", "sourceType", "directive", "hasExtendedUnicodeEscape", "jsDocParsingMode", "endOfFileToken",
}
TS_MODIFIER_KINDS_TO_REMOVE_NUMERIC = { 121, 122, 123, 144, 135, 126, 159 }

def _create_normalized_shell(original_node, is_ts_node):
    """
    Creates an Esprima-like shell from an original TS node or copies an Esprima node.
    Children are initially shallow copied from original_node and cleaned later.
    """
    shell = {}
    node_kind_numeric = original_node.get("kind") if is_ts_node else None
    
    # Determine Esprima type and basic structure
    esprima_type = None
    if is_ts_node:
        if node_kind_numeric == 79: esprima_type = 'Identifier'
        elif node_kind_numeric in [8, 10, 95, 104, 110]: esprima_type = 'Literal'
        elif node_kind_numeric == 253: esprima_type = "FunctionDeclaration"
        elif node_kind_numeric == 211: esprima_type = "FunctionExpression"
        elif node_kind_numeric == 212: esprima_type = "ArrowFunctionExpression"
        elif node_kind_numeric == 233: esprima_type = "VariableDeclaration"
        elif node_kind_numeric == 251: esprima_type = "VariableDeclarator"
        elif node_kind_numeric == 206: esprima_type = "CallExpression"
        elif node_kind_numeric == 219: esprima_type = "BinaryExpression"
        elif node_kind_numeric == 244: esprima_type = "ReturnStatement"
        elif node_kind_numeric == 232: esprima_type = "BlockStatement"
        elif node_kind_numeric == 163: # Parameter -> Becomes its name Identifier directly
            return _remove_ts_types_from_ast_recursive(original_node.get('name'), False, original_node.get('name'), True)
        elif node_kind_numeric == 298: esprima_type = "Program"
        else: # For unmapped TS nodes, copy essential fields if they exist
            shell['kind_original_ts'] = node_kind_numeric 
            # Copy other potentially relevant fields if not handled by PROPERTIES_TO_REMOVE
            for k,v in original_node.items():
                if k not in ['kind', 'pos', 'end', 'flags', 'parent', 'modifiers'] and k not in PROPERTIES_TO_REMOVE:
                    shell[k] = v # Shallow copy children for now
            return shell # Return as is, further recursion will clean children
    else: # Esprima node
        esprima_type = original_node.get("type")
        shell = copy.deepcopy(original_node) # Copy Esprima node, then clean its children
        return shell


    if esprima_type: shell['type'] = esprima_type
    else: # If no type determined (e.g. unhandled TS node), return a basic copy for child processing
        shell.update({k:v for k,v in original_node.items() if k not in ['kind', 'pos', 'end', 'flags', 'parent']})
        return shell


    # Populate shell with fields needed for Esprima structure, taking children from original_node
    # These children will be recursively cleaned later.
    if esprima_type == 'Identifier':
        shell['name'] = original_node.get('escapedText')
    elif esprima_type == 'Literal':
        if node_kind_numeric == 10: shell['value'] = original_node.get('text', '')
        elif node_kind_numeric == 8:
            val_text = original_node.get('text', '0')
            try: shell['value'] = int(val_text) if '.' not in val_text and 'e' not in val_text.lower() else float(val_text)
            except ValueError: shell['value'] = val_text
        elif node_kind_numeric == 104: shell['value'] = None
        elif node_kind_numeric == 110: shell['value'] = True
        elif node_kind_numeric == 95:  shell['value'] = False
    elif esprima_type in ["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]:
        shell['id'] = original_node.get('name') # This is an Identifier node
        shell['params'] = original_node.get('parameters', [])
        shell['body'] = original_node.get('body')
        original_flags = original_node.get('flags', 0)
        shell['async'] = bool(original_flags & 256)
        shell['generator'] = bool(original_flags & 512)
        shell['expression'] = (esprima_type == "ArrowFunctionExpression" and original_node.get('body', {}).get('kind') != 232)
    elif esprima_type == "VariableDeclaration": # From TS VariableStatement
        original_decl_list = original_node.get('declarationList', {})
        list_flags = original_decl_list.get('flags', 0)
        if list_flags & 2: shell['kind'] = 'const'
        elif list_flags & 1: shell['kind'] = 'let'
        else: shell['kind'] = 'var'
        shell['declarations'] = original_decl_list.get('declarations', [])
    elif esprima_type == "VariableDeclarator": # From TS VariableDeclaration
        shell['id'] = original_node.get('name')
        if 'initializer' in original_node: shell['init'] = original_node['initializer']
    elif esprima_type == "CallExpression":
        shell['callee'] = original_node.get('expression')
        shell['arguments'] = original_node.get('arguments', [])
    elif esprima_type == "BinaryExpression":
        shell['left'] = original_node.get('left')
        shell['right'] = original_node.get('right')
        op_kind_numeric = original_node.get('operatorToken', {}).get('kind')
        op_kind_str = SYNTAX_KIND_TO_STRING_MAP.get(op_kind_numeric)
        shell['operator'] = BINARY_OPERATOR_MAP.get(op_kind_str, f"OP_KIND:{op_kind_numeric}")
    elif esprima_type == "ReturnStatement":
        shell['argument'] = original_node.get('expression') if 'expression' in original_node else None
    elif esprima_type == "BlockStatement":
        shell['body'] = original_node.get('statements', [])
    elif esprima_type == "Program": # From TS SourceFile
        shell['body'] = original_node.get('statements', [])

    return shell

def _remove_ts_types_from_ast_recursive(node, is_top_level=False, original_node_for_shell=None, is_already_shell=False):
    if isinstance(node, list):
        return [item for item in (_remove_ts_types_from_ast_recursive(elem, False, elem) for elem in node) if item is not None]
    if not isinstance(node, dict): return node

    current_original_node = original_node_for_shell if original_node_for_shell is not None else node
    
    # If this node itself is a type to be removed (based on its original kind/type)
    node_kind_numeric = current_original_node.get('kind')
    is_ts_node = node_kind_numeric is not None
    node_kind_str = SYNTAX_KIND_TO_STRING_MAP.get(node_kind_numeric) if is_ts_node else None
    if node_kind_str and node_kind_str in TS_NODE_KINDS_TO_REMOVE_STRINGS: return None
    
    node_type_val = current_original_node.get('type') # Esprima type
    if isinstance(node_type_val, str) and node_type_val in TS_NODE_KINDS_TO_REMOVE_STRINGS: return None
    if node_type_val == "ExpressionStatement" and current_original_node.get("directive"): return None


    # Create a normalized shell if not already provided (i.e., not a recursive call on a shell's child)
    # Pass is_ts_node to guide shell creation
    processed_node = _create_normalized_shell(current_original_node, is_ts_node) if not is_already_shell else node
    
    if not isinstance(processed_node, dict): # If shell creation returned a final value (e.g. Parameter -> Identifier)
        return processed_node

    final_dict = {}
    # Set 'type' first from shell if it exists
    if 'type' in processed_node: final_dict['type'] = processed_node['type']


    # Handle modifiers for TS nodes based on original_node's modifiers
    if is_ts_node and 'modifiers' in current_original_node and isinstance(current_original_node['modifiers'], list):
        new_mods = [mod for mod_node in current_original_node['modifiers'] 
                    if isinstance(mod_node, dict) and mod_node.get('kind') not in TS_MODIFIER_KINDS_TO_REMOVE_NUMERIC 
                    and (mod := _remove_ts_types_from_ast_recursive(mod_node, False, mod_node)) is not None]
        if new_mods: final_dict['modifiers'] = new_mods
    
    # Iterate over keys in the normalized shell to process its children
    for key, value_from_shell in processed_node.items():
        if key == 'type' or key == 'modifiers' and 'modifiers' in final_dict : continue 
        if key in PROPERTIES_TO_REMOVE: continue
        
        # Contextual property handling (mostly for metadata on original TS nodes)
        # These checks should be on current_original_node not node_kind_numeric from shell
        original_kind_for_key_check = current_original_node.get('kind')
        if key == 'flags' and original_kind_for_key_check != 252 : continue 
        if key == 'id' and original_kind_for_key_check == 298 and value_from_shell == 0 : continue 
        
        # Recursively clean the children obtained from the shell
        cleaned_child = _remove_ts_types_from_ast_recursive(value_from_shell, False, value_from_shell, True) # Pass child as its own original_node_for_shell
        
        if cleaned_child is not None:
            if isinstance(cleaned_child, list) and not cleaned_child and \
               key not in ['params', 'arguments', 'body', 'members', 'elements', 'declarations', 'properties', 'statements']:
                continue
            final_dict[key] = cleaned_child
            
    # Ensure essential Esprima structures exist
    if final_dict.get("type") == "Program": final_dict.setdefault('body', [])
    if final_dict.get("type") in ["FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression"]:
        final_dict.setdefault('params', [])
        final_dict.setdefault('body', {"type": "BlockStatement", "body": []})
        if final_dict["type"] == "FunctionDeclaration" and "id" not in final_dict : final_dict["id"] = None
    if final_dict.get("type") == "VariableDeclaration": final_dict.setdefault('declarations', [])
    if final_dict.get("type") == "BlockStatement": final_dict.setdefault('body', [])


    # Final check: if dict is empty AND it was originally a TS type, remove.
    is_orig_ts_specific = (node_kind_str and node_kind_str in TS_NODE_KINDS_TO_REMOVE_STRINGS) or \
                           (isinstance(node_type_val, str) and node_type_val in TS_NODE_KINDS_TO_REMOVE_STRINGS)
    if not final_dict and is_orig_ts_specific: return None
    # If it became empty but wasn't a TS type (e.g. empty object literal from JS), keep it.
    if not final_dict and not current_original_node and not is_top_level: return {}


    return final_dict if final_dict or not is_orig_ts_specific else None


def compare_asts(js_ast: dict, ts_ast: dict) -> bool:
    if not js_ast and not ts_ast: return True
    if not js_ast or not ts_ast: return False

    js_ast_cleaned = _remove_ts_types_from_ast_recursive(copy.deepcopy(js_ast), True)
    if js_ast_cleaned is None: js_ast_cleaned = {"type": "Program", "body": []} 
    
    ts_ast_cleaned = _remove_ts_types_from_ast_recursive(copy.deepcopy(ts_ast), True)
    if ts_ast_cleaned is None: ts_ast_cleaned = {"type": "Program", "body": []}
    
    is_js_empty = not js_ast_cleaned.get("body") and js_ast_cleaned.get("type") == "Program"
    is_ts_empty = not ts_ast_cleaned.get("body") and ts_ast_cleaned.get("type") == "Program"

    if is_js_empty and is_ts_empty: return True
    if is_js_empty != is_ts_empty: return False
        
    try:
        js_ast_str = json.dumps(js_ast_cleaned, sort_keys=True)
        ts_ast_str = json.dumps(ts_ast_cleaned, sort_keys=True)
    except Exception as e:
        print(f"Error during AST canonicalization or JSON dump: {e}")
        return False
    
    if js_ast_str == ts_ast_str:
        return True
    else:
        is_test_match_case = False
        try:
            if isinstance(js_ast_cleaned.get("body"), list) and len(js_ast_cleaned["body"]) > 0:
                first_js_stmt = js_ast_cleaned["body"][0]
                if isinstance(first_js_stmt, dict) and first_js_stmt.get("type") == "FunctionDeclaration":
                    if first_js_stmt.get("id", {}).get("name") == "greet": is_test_match_case = True
        except Exception: pass 
        
        if is_test_match_case: # Only print for the "test_match" case
            print("ASTs differ. Canonical JSONs for 'test_match' case:")
            print("JS AST (cleaned for test_match.js):\n", json.dumps(js_ast_cleaned, sort_keys=True, indent=2))
            print("TS AST (cleaned for test_match.tsx):\n", json.dumps(ts_ast_cleaned, sort_keys=True, indent=2))
        return False

if __name__ == "__main__":
    with open("test_match.js", "w") as f: f.write("function greet(name) { return \"Hello, \" + name; }\nconst x = greet(\"World\");")
    with open("test_match.tsx", "w") as f: f.write("function greet(name: string): string { return \"Hello, \" + name; }\nconst x: string = greet(\"World\");")
    with open("test_structural_diff.js", "w") as f: f.write("function greet(name) { console.log(\"Hi\"); return \"Hello, \" + name; }")
    with open("test_structural_diff.tsx", "w") as f: f.write("function greet(name: string): string { return \"Hello, \" + name; }")

    print("\n--- Testing AST Comparison Logic ---")

    js_match_ast = generate_js_ast('test_match.js')
    ts_match_ast = generate_ts_ast('test_match.tsx')

    if js_match_ast and isinstance(js_match_ast, dict) and ts_match_ast and isinstance(ts_match_ast, dict):
        print("Comparing 'test_match.js' and 'test_match.tsx':")
        result_match = compare_asts(js_match_ast, ts_match_ast)
        print(f"    Should Match -> Result: {result_match}")
    else:
        print("Could not generate ASTs for 'test_match' pair. JS AST valid:", bool(js_match_ast), "TS AST valid:", bool(ts_match_ast))

    js_struct_ast = generate_js_ast('test_structural_diff.js')
    ts_struct_ast = generate_ts_ast('test_structural_diff.tsx')

    if js_struct_ast and isinstance(js_struct_ast, dict) and ts_struct_ast and isinstance(ts_struct_ast, dict):
        print("Comparing 'test_structural_diff.js' and 'test_structural_diff.tsx':")
        result_struct_diff = compare_asts(js_struct_ast, ts_struct_ast)
        print(f"    Should NOT Match -> Result: {not result_struct_diff}")
    else:
        print("Could not generate ASTs for 'test_structural_diff' pair. JS AST valid:", bool(js_struct_ast), "TS AST valid:", bool(ts_struct_ast))
    
    files_to_clean = [
        "test_match.js", "test_match.tsx", "test_structural_diff.js", "test_structural_diff.tsx",
        "js_match_cleaned_debug.json", "ts_match_cleaned_debug.json"
    ]
    for f_path in files_to_clean:
        if os.path.exists(f_path):
            try: os.remove(f_path)
            except OSError as e: print(f"Error removing file {f_path}: {e}")
