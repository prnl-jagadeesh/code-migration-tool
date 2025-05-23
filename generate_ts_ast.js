// Using absolute path for require as it was more reliable
const { factory, createSourceFile, ScriptTarget, ScriptKind, SyntaxKind } = require('/app/node_modules/typescript');

const fs = require('fs');

const filePath = process.argv[2];
if (!filePath) {
  console.error('Usage: node generate_ts_ast.js <file_path>');
  process.exit(1);
}

const sourceCode = fs.readFileSync(filePath, 'utf8');
// Pass undefined for setParentNodes so parent isn't set, reducing circularity issues early
const sourceFile = createSourceFile(filePath, sourceCode, ScriptTarget.Latest, false, ScriptKind.TSX);


// Custom replacer function to handle circular references and filter nodes
const getCircularReplacer = () => {
  const seen = new WeakSet();
  return (key, value) => {
    // Remove most metadata properties to simplify and avoid circularity
    if (key === 'parent' || key === 'pos' || key === 'end' || key === 'modifierFlagsCache' || key === 'transformFlags') {
      return; // Always remove these
    }
    // Conditionally remove 'flags' unless it's on a VariableDeclarationList (kind 252)
    // or a FunctionDeclaration (kind 253) or ClassDeclaration (kind 254) where it might indicate export/default/async etc.
    // For VariableDeclarationList, flags indicate const/let/var.
    // For functions/classes, flags can indicate async, export, default etc.
    // We need to be careful; Esprima has its own 'async', 'generator' boolean fields.
    // Let's preserve flags on VariableDeclarationList for now.
    // The Python side will need to interpret these flags.
    if (key === 'flags') {
        // 'this' refers to the object being stringified.
        // We don't have direct access to the parent node here to check its kind easily.
        // This means the Python side will have to deal with 'flags' if they are present,
        // or we remove them more broadly here and reconstruct semantic meaning (e.g. async) in Python.
        // For now, let's keep the original logic of removing flags generally,
        // as the Python side is not yet equipped to use TS flags for Esprima properties.
        // The problem analysis showed VariableDeclarationList flags are needed.
        // This replacer is tricky for conditional removal based on parent node type.
        // A better approach is to let Python handle flags removal/interpretation.
        // So, for now, let's stick to removing flags that Python doesn't explicitly use.
        // The Python side's PROPERTIES_TO_REMOVE already lists 'flags'.
      return; // Continue removing flags generally via JS replacer. Python handles its own.
    }

    if (typeof value === 'object' && value !== null) {
      if (seen.has(value)) {
        return '[Circular]'; // Replace circular references
      }
      seen.add(value);
    }
    return value;
  };
};

// Output the raw AST; Python will handle cleaning and normalization.
console.log(JSON.stringify(sourceFile, getCircularReplacer(), 2));
