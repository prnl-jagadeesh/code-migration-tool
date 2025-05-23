import os
import openai # Updated import for v1.x.x
from openai import OpenAI # Explicitly import the client
import argparse
from dotenv import load_dotenv
import logging
import sys

# Global OpenAI client instance
client = None

def setup_logging():
    """Configures basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def load_env_and_setup_api_key():
    """Loads environment variables from .env and sets up the OpenAI API key."""
    global client
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("Error: OPENAI_API_KEY environment variable not set.")
        logging.error("Please create a .env file or set the environment variable directly.")
        sys.exit(1)
    
    try:
        client = OpenAI(api_key=api_key)
        # Test the API key with a simple call, e.g., listing models (optional, can incur cost/quota usage)
        # For this test, we'll assume the key is valid if client initializes.
        # client.models.list() 
        logging.info("OpenAI API client initialized successfully.")
    except openai.AuthenticationError as e:
        logging.error(f"OpenAI API Authentication Error: {e}. Check your API key.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")
        sys.exit(1)


def migrate_js_to_tsx(file_path):
    """
    Migrates a JavaScript React component file to TypeScript (TSX) using OpenAI API.
    """
    global client
    if client is None:
        logging.critical("Critical Error: OpenAI client not initialized before API call.")
        raise ValueError("OpenAI client not initialized.")

    with open(file_path, "r", encoding='utf-8') as f:
        js_code = f.read()

    prompt = (
        "Convert this React JavaScript component to TypeScript (.tsx). "
        "Add prop/state/event types. "
        "Return only the code. Do not include explanations or markdown.\n\n"
        f"{js_code}"
    )
    
    # Using the new API structure for chat completions
    response = client.chat.completions.create(
        model="gpt-4", # Model remains gpt-4
        messages=[
            {"role": "system", "content": "You are a code migration assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    # Accessing the response content according to the new structure
    return response.choices[0].message.content.strip()

def main():
    """
    Main function to handle command-line arguments and orchestrate the migration process.
    """
    setup_logging()

    parser = argparse.ArgumentParser(description="Migrate React JS components to TSX using OpenAI API.")
    parser.add_argument(
        "--input_dir", 
        default="extracted", 
        help="Directory containing JavaScript files to migrate. (default: 'extracted')"
    )
    parser.add_argument(
        "--output_dir", 
        default="migrated", 
        help="Directory to save migrated TSX files. (default: 'migrated')"
    )
    args = parser.parse_args()

    logging.info("Starting migration process...")
    load_env_and_setup_api_key() # This now initializes the global 'client'

    os.makedirs(args.output_dir, exist_ok=True)
    logging.info(f"Output directory '{args.output_dir}' ensured.")

    logging.info(f"Scanning '{args.input_dir}' for .js files...")
    
    try:
        js_files = [f for f in os.listdir(args.input_dir) if f.endswith(".js")]
    except FileNotFoundError:
        logging.error(f"Error: Input directory '{args.input_dir}' not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error listing files in input directory '{args.input_dir}': {e}")
        sys.exit(1)

    if not js_files:
        logging.info(f"No .js files found in '{args.input_dir}'. Nothing to migrate.")
        return

    logging.info(f"Found {len(js_files)} .js files to migrate.")
    
    successful_migrations = 0
    failed_migrations = 0

    for filename in js_files:
        input_file_path = os.path.join(args.input_dir, filename)
        output_filename = filename.replace(".js", ".tsx")
        output_file_path = os.path.join(args.output_dir, output_filename)

        logging.info(f"Migrating '{input_file_path}' to '{output_file_path}'...")
        try:
            tsx_code = migrate_js_to_tsx(input_file_path)
            
            if tsx_code.startswith("```tsx"):
                tsx_code = tsx_code[len("```tsx"):]
                if tsx_code.endswith("```"):
                    tsx_code = tsx_code[:-len("```")]
                tsx_code = tsx_code.strip()
            elif tsx_code.startswith("```typescript"):
                tsx_code = tsx_code[len("```typescript"):]
                if tsx_code.endswith("```"):
                    tsx_code = tsx_code[:-len("```")]
                tsx_code = tsx_code.strip()

            with open(output_file_path, "w", encoding='utf-8') as out_f:
                out_f.write(tsx_code)
            logging.info(f"✅ Successfully migrated '{output_filename}'")
            successful_migrations += 1
        # Updated error handling for OpenAI API v1.x.x
        except openai.APIError as e: # This is a base class for many API errors
            logging.error(f"❌ OpenAI API Error migrating '{filename}': {type(e).__name__} - {e}")
            failed_migrations += 1
        except Exception as e:
            logging.error(f"❌ An unexpected error occurred while migrating '{filename}': {type(e).__name__} - {e}")
            failed_migrations += 1
        # Continue to the next file even if an error occurs

    logging.info("Migration process complete.")
    logging.info(f"Summary: {successful_migrations} file(s) migrated successfully.")
    logging.info(f"         {failed_migrations} file(s) failed to migrate.")

if __name__ == "__main__":
    main()
