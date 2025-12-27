"""
Test Phase 3: Job Analysis and Cover Letter Generation
"""
from agent_graph import app

print("=" * 60)
print("PHASE 3 TEST: Job Search + Analysis + Cover Letter")
print("=" * 60)

# Search for jobs
criteria = {
    "query": "Python Developer",
    "location": "Remote"
}

print(f"\n1. Searching for: {criteria['query']} in {criteria['location']}")
print("-" * 60)

result = app.invoke({"job_search_criteria": criteria})

# Display results
found_jobs = result.get('found_jobs', [])
current_job = result.get('current_job')

print(f"\n2. Found {len(found_jobs)} jobs")
print("-" * 60)

if current_job:
    print(f"\n3. Analyzed Job:")
    print(f"   Title: {current_job['title']}")
    print(f"   Company: {current_job['company']}")
    print(f"   Score: {current_job.get('score', 'N/A')}/100")
    print(f"   Reason: {current_job.get('analysis', {}).get('reason', 'N/A')}")
    print(f"   Should Apply: {current_job.get('analysis', {}).get('should_apply', 'N/A')}")
    
    # Generate cover letter
    print(f"\n4. Generating Cover Letter...")
    print("-" * 60)
    
    from cover_letter_generator import create_cover_letter_generator
    generator = create_cover_letter_generator()
    cover_letter = generator.generate(current_job)
    
    print(cover_letter)
    print("-" * 60)

print("\n✅ Phase 3 Test Complete!")
print("=" * 60)
