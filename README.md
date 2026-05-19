# Job Applier

Simplified job application system using Mistral API for fast, reliable resume generation.

## Features

- **Fast resume generation** — Uses Mistral API (not browser automation)
- **Real user data** — Loads from backup resume data
- **Working system instructions** — Proven resume formatting
- **CLI interface** — Easy to use with custom job descriptions

## Setup

1. Ensure `secrets.yaml` has valid Mistral API key, or place `.env` with:
   ```
   MISTRAL_API_KEY=your_key_here
   ```

2. User resume data is auto-loaded from `08-shared/data_folder/`:
   - `systeminstructions.txt` — Resume formatting rules
   - `comprehensive_rag_data.md` — Background data

## Usage

```bash
# Default job description
python applier.py

# Custom job description
python applier.py --job-desc "Python Developer with Django experience"

# From file
python applier.py --file job_description.txt

# Save to specific file
python applier.py --job-desc "..." --out my_resume.txt
```

## Output

Generated resume is saved to `generated_resume.txt` by default.
