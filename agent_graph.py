from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolExecutor

# Define the State
class AgentState(TypedDict):
    job_search_criteria: Dict
    found_jobs: List[Dict]
    current_job: Dict
    application_status: str
    outreach_targets: List[Dict]
    logs: List[str]

# Define Nodes
def search_jobs(state: AgentState):
    print("--- Searching for Jobs ---")
    import asyncio
    from browser_manager import BrowserManager
    
    # We need to run async browser code in this sync node
    # For now, we instantiate a fresh manager or reuse one if global
    # Ideally, we inject the browser_manager, but for this prototype:
    
    async def run_search():
        bm = BrowserManager()
        # Criteria from state or default
        query = state.get("job_search_criteria", {}).get("query", "Software Engineer")
        location = state.get("job_search_criteria", {}).get("location", "United States")
        
        jobs = await bm.search_jobs(query, location)
        await bm.close()
        return jobs

    found_jobs = asyncio.run(run_search())
    return {"found_jobs": found_jobs}

def analyze_job(state: AgentState):
    print("--- Analyzing Job ---")
    from job_analyzer import create_job_analyzer
    
    analyzer = create_job_analyzer()
    found_jobs = state.get("found_jobs", [])
    
    if not found_jobs:
        print("No jobs to analyze")
        return {"current_job": None}
    
    # Analyze the first job (in real workflow, we'd loop through all)
    job = found_jobs[0]
    print(f"Analyzing: {job['title']} at {job['company']}")
    
    analysis = analyzer.analyze(job)
    
    # Add analysis to job data
    job["score"] = analysis["score"]
    job["analysis"] = analysis
    
    print(f"Score: {analysis['score']}/100")
    print(f"Reason: {analysis['reason']}")
    print(f"Should Apply: {analysis['should_apply']}")
    
    return {"current_job": job}

def apply_to_job(state: AgentState):
    print("--- Applying to Job ---")
    from form_filler import create_form_filler
    
    job = state.get("current_job")
    if not job:
        print("No job to apply to")
        return {"application_status": "no_job"}
    
    # Check if should apply based on score
    should_apply = job.get("analysis", {}).get("should_apply", False)
    if not should_apply:
        print(f"Skipping application (score too low: {job.get('score', 0)})")
        return {"application_status": "skipped_low_score"}
    
    print(f"Applying to: {job['title']} at {job['company']}")
    
    # Get browser from state
    browser = state.get("browser")
    if not browser:
        print("No browser instance available")
        return {"application_status": "error_no_browser"}
    
    async def apply():
        # Navigate to job
        success = await browser.navigate_to_job(job["url"])
        if not success:
            return "error_navigation"
        
        # Check for Easy Apply
        has_easy_apply = await browser.find_easy_apply_button()
        if not has_easy_apply:
            return "no_easy_apply"
        
        # Click Easy Apply
        clicked = await browser.click_easy_apply()
        if not clicked:
            return "error_click"
        
        # Detect form fields
        fields = await browser.detect_form_fields()
        if len(fields) > 10:
            print(f"Form too complex ({len(fields)} fields), skipping")
            return "skipped_complex_form"
        
        # Fill each field
        form_filler = create_form_filler()
        for field in fields:
            answer = form_filler.get_answer(field)
            if answer:
                await browser.fill_form_field(field, answer)
            else:
                print(f"  Skipped field (no answer): {field['label']}")
        
        # Submit
        submitted = await browser.submit_application()
        if submitted:
            return "submitted"
        else:
            return "error_submit"
    
    # Run async function
    import asyncio
    status = asyncio.run(apply())
    
    print(f"Application status: {status}")
    return {"application_status": status}

def networking(state: AgentState):
    print("--- Networking Step ---")
    return {"outreach_targets": []}

# Define Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("search", search_jobs)
workflow.add_node("analyze", analyze_job)
workflow.add_node("apply", apply_to_job)
workflow.add_node("network", networking)

# Set Entry Point
workflow.set_entry_point("search")

# Add Edges
workflow.add_edge("search", "analyze")
workflow.add_edge("analyze", "apply")
workflow.add_edge("apply", "network")
workflow.add_edge("network", END)

# Compile
app = workflow.compile()

if __name__ == "__main__":
    print("Graph Compiled Successfully.")
    # test run
    # app.invoke({"job_search_criteria": {}})
