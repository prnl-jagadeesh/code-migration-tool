# React.js to TypeScript Migration Tools

## Overview

These tools provide a semi-automated workflow to assist in migrating React JavaScript components to TypeScript. The process involves two main steps:

1.  **Component Extraction**: A `jscodeshift` script (`extractComponents.js`) is used to extract React functional components and associated helper functions from a larger JavaScript file into individual component files.
2.  **AI-Powered Conversion**: A Python script (`run_migration.py`) takes these extracted JavaScript component files and uses an AI model via the OpenAI API (specifically GPT-4) to convert them into TypeScript (`.tsx`) files, adding type annotations for props, state, and events where possible.

After migration, users are advised to manually review the generated TypeScript code and use their own external AST (Abstract Syntax Tree) diffing tools or other verification methods to compare the original JavaScript components with the generated TypeScript components to ensure migration accuracy and make any necessary refinements.

## Setup

### Environment Variables

To use the AI-powered conversion script (`run_migration.py`), you need to set up an OpenAI API key.

1.  Create a file named `.env` in the root directory of this project.
2.  Add your OpenAI API key to the `.env` file as follows:
    ```
    OPENAI_API_KEY=your_actual_api_key_here
    ```
    Replace `your_actual_api_key_here` with your actual OpenAI API key.

### Dependencies

#### For `extractComponents.js` (Component Extraction)

*   **Node.js and npm:** Ensure you have Node.js (which includes npm) installed. You can download it from [nodejs.org](https://nodejs.org/).
*   **`jscodeshift`:** This is the codemod toolkit used to run the `extractComponents.js` script.
    *   Install it globally:
        ```bash
        npm install -g jscodeshift
        ```
    *   Or, install it as a local project dependency:
        ```bash
        npm install jscodeshift
        ```
        (If installed locally, you'll typically run it via `npx jscodeshift ...` or by adding it to your `package.json` scripts).
*   **Other Dependencies:** The `extractComponents.js` script itself does not have explicit external npm package dependencies beyond what `jscodeshift` provides for its execution environment. It uses standard JavaScript/Node.js modules like `fs` and `path`.

#### For `run_migration.py` (AI Conversion to TypeScript)

*   **Python:** Ensure Python 3.x is installed. You can download it from [python.org](https://www.python.org/).
*   **Python Packages:** Install the required Python packages using pip and the provided `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file includes:
    ```
    openai
    python-dotenv
    ```

## Migration Process

### Step 1: Extract Components

The `extractComponents.js` script is designed to be run with `jscodeshift`. It processes a JavaScript file containing multiple React components and extracts each top-level functional component and any directly associated helper functions or constants into separate files within the `extracted/` directory.

**Usage:**

```bash
jscodeshift -t extractComponents.js path/to/your/react/sourcefile.js
```

*   Replace `path/to/your/react/sourcefile.js` with the actual path to the JavaScript file you want to process.
*   The script will create individual `.js` files for each extracted component (e.g., `MyComponent.js`, `AnotherComponent.js`) inside the `extracted/` directory (this directory will be created if it doesn't exist).

For example, if your components are in `src/OldComponents.js`:
```bash
jscodeshift -t extractComponents.js src/OldComponents.js
```
This will populate the `extracted/` directory with files like `extracted/MyComponent.js`.

### Step 2: Convert to TypeScript

The `run_migration.py` script takes the JavaScript files from an input directory (by default, `extracted/`), converts them to TypeScript using the OpenAI API, and saves them to an output directory (by default, `migrated/`).

**Usage:**

```bash
python run_migration.py [--input_dir path/to/js/files] [--output_dir path/to/save/tsx/files]
```

*   `--input_dir`: (Optional) Specifies the directory containing the JavaScript files to be migrated. Defaults to `extracted/`.
*   `--output_dir`: (Optional) Specifies the directory where the migrated `.tsx` files will be saved. Defaults to `migrated/`. This directory will be created if it doesn't exist.

**Default Usage (after running Step 1):**

```bash
python run_migration.py
```
This will:
1.  Look for `.js` files in the `extracted/` directory.
2.  For each file, call the OpenAI API to convert its content to TypeScript/TSX.
3.  Save the converted code as a `.tsx` file in the `migrated/` directory (e.g., `extracted/MyComponent.js` becomes `migrated/MyComponent.tsx`).
4.  Log progress and any errors to the console.

## AST Comparison

After the migration process, particularly after the AI-powered conversion (Step 2), it is highly recommended to verify the accuracy of the generated TypeScript code.

While this toolkit provides `ast_utils.py` which contains functions for generating and comparing Abstract Syntax Trees (ASTs) for JavaScript and TypeScript, direct AST comparison for complex code can be challenging due to structural differences between parsers (Esprima for JS, TypeScript compiler for TS) and the nuances of type information.

Users are advised to:
1.  **Manually review** the generated `.tsx` files for correctness, completeness of type annotations, and any potential issues introduced during the AI conversion.
2.  **Use external AST diffing tools** or custom scripts leveraging `ast_utils.py` if deeper structural comparison is desired. This can help identify subtle changes beyond simple text diffs.
3.  **Run type checking and tests** on the migrated TypeScript code to ensure it behaves as expected and is type-safe.

The `ast_utils.py` script primarily serves as a utility that can be extended for more sophisticated local analysis or as a building block for custom verification workflows. Its `compare_asts` function attempts to normalize and compare ASTs but may require further refinement for robust, automated equivalence checking. The script also includes test files (`test_match.js`, `test_match.tsx`, etc.) that demonstrate its comparison capabilities and limitations.
