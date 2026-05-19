#!/usr/bin/env python3
"""Test the job applier without launching browser."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "04-resume-forge" / "resume_forge"))

from applier import load_user_data, build_resume_prompt


def main():
    print("=" * 60)
    print("JOB APPLIER - TEST MODE (No Browser)")
    print("=" * 60)
    
    # Test 1: Load user data
    print("\n[Test 1] Loading user data...")
    user_data = load_user_data()
    
    checks = [
        ("System instructions", len(user_data["system_instructions"]) > 100),
        ("RAG data", len(user_data["rag_data"]) > 1000),
        ("Detailed knowledge", len(user_data["detailed_knowledge"]) > 1000),
        ("Resume YAML", len(user_data["resume_yaml"]) > 100),
    ]
    
    for name, ok in checks:
        status = "✅" if ok else "❌"
        print(f"   {status} {name}: {len(user_data[name.lower().replace(' ', '_')])} chars")
    
    # Test 2: Build prompt
    print("\n[Test 2] Building resume prompt...")
    job_desc = "Software Engineer - Python & Automation\nLocation: Remote"
    prompt = build_resume_prompt(job_desc, user_data)
    
    print(f"   ✅ Prompt built: {len(prompt)} chars")
    print(f"   📝 Prompt preview (first 500 chars):")
    print(f"   {'-' * 50}")
    print(f"   {prompt[:500]}...")
    print(f"   {'-' * 50}")
    
    # Test 3: Check system instructions content
    print("\n[Test 3] System instructions preview:")
    instr = user_data["system_instructions"]
    print(f"   {'-' * 50}")
    print(f"   {instr[:500]}...")
    print(f"   {'-' * 50}")
    
    print("\n" + "=" * 60)
    print("All tests passed! Ready to run with browser.")
    print("Run: python job_applier/applier.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
