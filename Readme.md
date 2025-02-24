# Deepl Ren’Py Translator

This is a small tool to automatically translate Ren’Py `.rpy` files using the [DeepL Pro API](https://www.deepl.com/pro).

---

## Features

- Scans `./game/tl/<language>` (or all languages in `./game/tl/*`) to find `.rpy` translation files.
- Looks for `old "Text"` / `new ""` pairs and automatically populates `new "<translation>"` lines.
- Uses Deepl’s optional formality level (`default`, `more`, `less`).

---

## Prerequisites

- **Python 3.7+** (Recommended, though older 3.x may work.)
- A **DeepL Pro API key** with sufficient translation quota.

---

## Installation

1. Clone or download this repository into your Ren’Py project folder (or wherever you prefer).
2. Ensure you have a `.env` file in the same directory as the script with your API key:
   ```
   DEEPL_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run `deepl_renpy_translator.py` with the desired arguments:

```bash
python deepl_renpy_translator.py [language] [options]
```

Where:

- `language` can be:
  - A BCP‐47 code like `de`, `pl`, `en`, etc.
  - A spelled‐out language like `german`, `spanish`, or `french` (this is mapped internally to BCP‐47).
  - Default is `german` if no argument is provided.

**Options**:

- `--all`  
  Translate *all* subfolders under `./game/tl/`. If omitted, only `./game/tl/<language>` is processed.

- `--formality {default, more, less}`  
  Controls formality for languages that support it. For example, `--formality more` can yield more formal translations. Defaults to `default`.

### Examples

1. **Translate all strings to German**  
   ```bash
   python deepl_renpy_translator.py german
   ```
   or
   ```bash
   python deepl_renpy_translator.py de
   ```

2. **Translate a single folder to Spanish, forcing informal style (`less`)**  
   ```bash
   python deepl_renpy_translator.py spanish --formality less
   ```

3. **Translate *all* subfolders under `./game/tl/` to formal German**  
   ```bash
   python deepl_renpy_translator.py german --all --formality more
   ```

---

## Notes

- The script identifies text that needs translation by finding lines of the form:

  ```renpy
  old "Text to translate"
  new ""
  ```
  It then replaces `new ""` with `new "DeepL result"`.  

- Any line that already has `new "Something"` won’t be overwritten by default. If you want to re‐translate lines that already have a translation, you can customize the code inside `process_rpy_file()`.
- Make sure your `.rpy` files are UTF‐8 encoded for best results.
- This tool modifies the `.rpy` files in place. Consider version control or backups before running.
