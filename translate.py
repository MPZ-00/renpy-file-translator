#!/usr/bin/env python3

import os
import re
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------
# Load environment variables (DEEPL_API_KEY) from .env
# -----------------------------------------------------
load_dotenv()
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
DEEPL_API_URL = 'https://api.deepl.com/v2/translate'  # Deepl Pro API Endpoint

# -----------------------------------------------------
# Known mappings from spelled-out language to BCP-47
# (Add or update as needed)
# -----------------------------------------------------
LANGUAGE_MAP = {
    "german": "DE",
    "spanish": "ES",
    "english": "EN",
    "french": "FR",
    "italian": "IT",
    "polish": "PL",
    # ... add others as desired
}

def translate_text(text: str, target_lang: str, formality: str = "default") -> str:
    """
    Translates a given text string using the Deepl API.
    :param text: The text to translate.
    :param target_lang: The BCP-47 code (e.g. "DE", "PL") that Deepl expects.
    :param formality: "default", "more", or "less".
    :return: The translated text.
    """
    if not DEEPL_API_KEY:
        raise ValueError("DEEPL_API_KEY not found. Make sure it's set in .env")

    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang
    }

    # If the user wants to force formality, pass it; otherwise default to Deepl’s own default
    if formality.lower() in ["more", "less"]:
        params["formality"] = formality.lower()

    try:
        response = requests.post(DEEPL_API_URL, data=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        # Extract translated text (Deepl can return multiple translations if text was split)
        return data["translations"][0]["text"]
    except requests.exceptions.RequestException as e:
        print(f"Error while contacting Deepl API: {e}")
        return text  # fallback – just return original text

def process_rpy_file(rpy_path: Path, target_lang: str, formality: str):
    """
    Reads an .rpy file line by line. Whenever it sees a pair:

        old "Some text"
        new ""

    it translates "Some text" and places the translation inside new "…".
    """
    # Regex to capture old "Text" lines
    old_pattern = re.compile(r'^\s*old\s+"(.*)"')
    # Regex to capture new "" lines
    new_pattern = re.compile(r'^\s*new\s+"(.*)"')

    lines = rpy_path.read_text(encoding="utf-8").splitlines()
    output_lines = []
    buffer_old_text = None

    for line in lines:
        # Check if the line contains an `old "..."` statement
        old_match = old_pattern.match(line)
        if old_match:
            # Save the text we want to translate for the next "new" line
            buffer_old_text = old_match.group(1)
            output_lines.append(line)  # keep the original line
            continue

        # Check if the line is a `new "..."` statement
        new_match = new_pattern.match(line)
        if new_match and buffer_old_text is not None:
            current_new_text = new_match.group(1)
            # If the new text is empty or we want to retranslate anyway, do so:
            if current_new_text.strip() == "":
                # Call Deepl translation
                translation = translate_text(buffer_old_text, target_lang, formality)
                # Build the updated line
                updated_line = re.sub(r'new\s+".*"', f'new "{translation}"', line)
                output_lines.append(updated_line)
            else:
                # There's already something inside new "...", skip or overwrite if you prefer
                output_lines.append(line)
            buffer_old_text = None  # reset
        else:
            # Normal line (or it doesn't match) – just append
            output_lines.append(line)

    # Write the updated text back
    rpy_path.write_text("\n".join(output_lines), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(
        description="Translate Ren'Py .rpy files using Deepl."
    )
    parser.add_argument(
        "language",
        nargs="?",
        default="german",
        help="Target language (BCP-47 code like 'DE' or spelled-out 'german'). Default is 'german'."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Translate all directories under ./game/tl/* instead of a single language folder."
    )
    parser.add_argument(
        "--formality",
        choices=["default", "more", "less"],
        default="default",
        help="Optional formality setting passed to Deepl."
    )

    args = parser.parse_args()

    # Determine the final BCP-47 code
    user_lang = args.language.lower()
    target_lang = LANGUAGE_MAP.get(user_lang, user_lang.upper())  
    # For example: "german" -> "DE"; if user gave "de", we just do "DE"

    # Decide which tl dirs to scan:
    base_tl_path = Path("game") / "tl"
    if args.all:
        # All language subdirs
        lang_dirs = [p for p in base_tl_path.iterdir() if p.is_dir()]
    else:
        # Just one subdir
        lang_dirs = [base_tl_path / user_lang]
        if not lang_dirs[0].exists():
            print(f"Directory {lang_dirs[0]} does not exist. Aborting.")
            return

    # For each language dir, process all .rpy files
    for lang_dir in lang_dirs:
        if not lang_dir.is_dir():
            continue
        print(f"Processing directory: {lang_dir}")
        for rpy_file in lang_dir.rglob("*.rpy"):
            print(f"  -> Translating: {rpy_file}")
            process_rpy_file(rpy_file, target_lang, args.formality)

if __name__ == "__main__":
    main()
