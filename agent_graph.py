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
    # TODO: Call LLM to analyze
    return {"current_job": state["found_jobs"][0]}

def apply_to_job(state: AgentState):
    print("--- Applying to Job ---")
    # TODO: Call Browser Manager to apply
    return {"application_status": "submitted"}

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
