#!/usr/bin/env python3
"""
Job Applier - Generates tailored resumes using Mistral API.
Uses user's real resume data and working system instructions.

Usage:
    python applier.py                          # Use default job description
    python applier.py --job-desc "your job"    # Custom job description
    python applier.py --file job.txt           # Read job description from file
"""
import sys
import argparse
from pathlib import Path

import openai
import yaml


def load_secrets():
    """Load API keys from secrets.yaml and backup .env."""
    secrets_path = Path(__file__).parent.parent / "external" / "rasjobauto" / "data_folder" / "secrets.yaml"
    with open(secrets_path) as f:
        secrets = yaml.safe_load(f)
    
    # Also check backup .env for Mistral key
    env_path = Path("/home/rastinder/Desktop/backup/resume generater/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith("MISTRAL_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    if "clients" not in secrets:
                        secrets["clients"] = {}
                    if "mistral" not in secrets["clients"]:
                        secrets["clients"]["mistral"] = {}
                    secrets["clients"]["mistral"]["llm_api_key"] = key
                    break
    
    return secrets


def load_user_data():
    """Load user's real resume data from backup."""
    data_dir = Path(__file__).parent.parent / "08-shared" / "data_folder"
    
    instructions = ""
    instructions_path = data_dir / "systeminstructions.txt"
    if instructions_path.exists():
        instructions = instructions_path.read_text(encoding="utf-8")
    
    rag_data = ""
    rag_path = data_dir / "comprehensive_rag_data.md"
    if rag_path.exists():
        rag_data = rag_path.read_text(encoding="utf-8")[:8000]
    
    return {
        "system_instructions": instructions,
        "rag_data": rag_data,
    }


def generate_resume(job_description: str, user_data: dict, secrets: dict) -> str:
    """Generate tailored resume using Mistral API."""
    
    mistral_config = secrets.get("clients", {}).get("mistral", {})
    api_key = mistral_config.get("llm_api_key", "")
    api_url = mistral_config.get("llm_api_url", "https://api.mistral.ai/v1")
    model = mistral_config.get("llm_model", "mistral-large-latest")
    
    if not api_key:
        raise ValueError("No Mistral API key found. Check secrets.yaml or .env")
    
    client = openai.OpenAI(api_key=api_key, base_url=api_url)
    
    system_content = f"""{user_data['system_instructions']}

TODAY'S DATE: May 19, 2026

CRITICAL CANDIDATE IDENTITY (NEVER CHANGE):
Name: Rastinder Singh Brar
Address: 61 Bonistel Crescent, Brampton, ON L7A 3G9
Email: rastinder@gmail.com | Phone: 437-322-9241
LinkedIn: linkedin.com/in/rastinder-brar-53741777 | GitHub: github.com/rastinder

BACKGROUND DATA:
---
{user_data['rag_data'][:6000]}
---

FORMAT RULES:
1. First 3 lines: Name, Address, Contact (exactly as shown)
2. ALL CAPS section headers
3. Use • for bullets, | for separators
4. NO brackets [like this], NO markdown ```
5. Results-driven tone, emphasize scale and impact
"""

    user_content = f"""Craft a premium tailored resume for this job:

{job_description}

Generate complete resume with:
1. Name & Contact
2. PROFESSIONAL SUMMARY
3. CORE SKILLS (categorized)
4. PROFESSIONAL EXPERIENCE
5. EDUCATION
6. CERTIFICATIONS
7. PROJECT HIGHLIGHTS
8. LANGUAGES
"""

    print(f"   🤖 Calling Mistral API ({model})...")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        max_tokens=4000,
    )
    
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Generate tailored resume")
    parser.add_argument("--job-desc", "-j", help="Job description text")
    parser.add_argument("--file", "-f", help="Read job description from file")
    parser.add_argument("--out", "-o", help="Output file path")
    args = parser.parse_args()
    
    print("=" * 60)
    print("JOB APPLIER - Tailored Resume Generator")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading config and user data...")
    secrets = load_secrets()
    user_data = load_user_data()
    print(f"   ✅ API keys loaded")
    print(f"   ✅ System instructions: {len(user_data['system_instructions'])} chars")
    print(f"   ✅ Background data: {len(user_data['rag_data'])} chars")
    
    # Get job description
    if args.file:
        job_description = Path(args.file).read_text(encoding="utf-8")
    elif args.job_desc:
        job_description = args.job_desc
    else:
        job_description = """Software Engineer - Python & Automation
Location: Remote / Toronto, Canada

Requirements:
- 3+ years Python development
- Experience with Selenium/Playwright
- Cloud platforms (AWS/GCP/Azure)
- AI/ML API integrations
- Docker, Kubernetes, CI/CD

Responsibilities:
- Develop automation frameworks
- Build web scraping pipelines
- Integrate AI/ML models
"""
    
    print(f"\n📋 Job Description: {job_description[:100]}...")
    
    # Generate resume
    print("\n🚀 Generating tailored resume...")
    try:
        resume = generate_resume(job_description, user_data, secrets)
        
        print("\n" + "=" * 60)
        print("GENERATED RESUME:")
        print("=" * 60)
        print(resume)
        print("=" * 60)
        
        # Save
        out_path = Path(args.out) if args.out else Path(__file__).parent / "generated_resume.txt"
        out_path.write_text(resume, encoding="utf-8")
        print(f"\n💾 Saved to: {out_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
