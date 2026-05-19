#!/usr/bin/env python3
"""
Job Applier using Mistral API (fast, reliable) + Google AI Studio for job applications.
Uses user's real resume data and working system instructions.
"""
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "04-resume-forge" / "resume_forge"))

import openai
import yaml


def load_secrets():
    """Load API keys from secrets.yaml and .env."""
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
                    if "mistral" not in secrets.get("clients", {}):
                        secrets["clients"] = secrets.get("clients", {})
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


def generate_resume_mistral(job_description: str, user_data: dict, secrets: dict):
    """Generate resume using Mistral API."""
    
    # Get Mistral config
    mistral_config = secrets.get("clients", {}).get("mistral", {})
    api_key = mistral_config.get("llm_api_key", "")
    api_url = mistral_config.get("llm_api_url", "https://api.mistral.ai/v1")
    model = mistral_config.get("llm_model", "mistral-large-latest")
    
    if not api_key:
        print("❌ No Mistral API key found in secrets.yaml")
        return None
    
    # Setup client
    client = openai.OpenAI(
        api_key=api_key,
        base_url=api_url,
    )
    
    system_content = f"""{user_data['system_instructions']}

TODAY'S DATE: May 19, 2026

CRITICAL CANDIDATE IDENTITY (NEVER CHANGE THIS):
Name: Rastinder Singh Brar
Address: 61 Bonistel Crescent, Brampton, ON L7A 3G9
Email: rastinder@gmail.com
Phone: 437-322-9241
LinkedIn: linkedin.com/in/rastinder-brar-53741777
GitHub: github.com/rastinder

CANDIDATE BACKGROUND DATA:
---
{user_data['rag_data'][:6000]}
---

STRICT FORMATTING RULES:
1. First line: Rastinder Singh Brar
2. Second line: 61 Bonistel Crescent, Brampton, ON L7A 3G9
3. Third line: 437-322-9241 | rastinder@gmail.com | github.com/rastinder | linkedin.com/in/rastinder-brar-53741777
4. ALL CAPS section headers
5. Use • for bullets, | for separators
6. NO brackets [like this], NO markdown ```
7. Results-driven tone, emphasize scale and impact
"""

    user_content = f"""Craft a premium-quality, tailored resume for this job description.

JOB DESCRIPTION:
{job_description}

Generate a complete resume with these sections:
1. Name & Contact Info
2. PROFESSIONAL SUMMARY
3. CORE SKILLS (categorized)
4. PROFESSIONAL EXPERIENCE
5. EDUCATION
6. CERTIFICATIONS
7. PROJECT HIGHLIGHTS
8. LANGUAGES
"""

    print(f"   🤖 Calling Mistral API ({model})...")
    
    try:
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
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None


def main():
    print("=" * 60)
    print("JOB APPLIER - Using Mistral API (Fast)")
    print("=" * 60)
    
    # Load secrets and user data
    print("\n📂 Loading config and user data...")
    secrets = load_secrets()
    user_data = load_user_data()
    print(f"   ✅ API keys loaded")
    print(f"   ✅ System instructions: {len(user_data['system_instructions'])} chars")
    print(f"   ✅ RAG data: {len(user_data['rag_data'])} chars")
    
    # Example job description
    job_description = """Software Engineer - Python & Automation
Location: Remote / Toronto, Canada

We are looking for a skilled Software Engineer with expertise in Python, 
web automation, and AI integrations.

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
    
    print("\n📋 Job Description:")
    print(f"   {job_description[:150]}...")
    
    # Generate resume
    print("\n🚀 Generating tailored resume...")
    resume = generate_resume_mistral(job_description, user_data, secrets)
    
    if resume:
        print("\n" + "=" * 60)
        print("GENERATED RESUME:")
        print("=" * 60)
        print(resume)
        print("=" * 60)
        
        # Save to file
        output_path = Path(__file__).parent / "generated_resume.txt"
        output_path.write_text(resume, encoding="utf-8")
        print(f"\n💾 Saved to: {output_path}")
    else:
        print("\n❌ Failed to generate resume")


if __name__ == "__main__":
    main()
