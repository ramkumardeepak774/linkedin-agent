import sys
import asyncio
from config import Config
from database import init_db

def main():
    print("Welcome to LinkedIn Automation Agent")
    print("------------------------------------")
    
    # 1. Init Config & DB
    Config.ensure_dirs()
    db_session = init_db()
    print("System Initialized.")
    
    # TODO: Initialize LangGraph and Browser
    
    print("\nSelect Mode:")
    print("1. Job Search & Apply")
    print("2. Networking / Outreach")
    print("3. Analytics Dashboard (Streamlit)")
    
    try:
        choice = input("Enter choice (1-3): ")
        if choice == "1":
            print("Starting Job Search Agent...")
            from agent_graph import app
            # Define search criteria
            criteria = {
                "query": "Software Engineer", 
                "location": "Remote"
            }
            # Run the graph
            result = app.invoke({"job_search_criteria": criteria})
            print("\n--- Execution Complete ---")
            print(f"Jobs Found: {len(result['found_jobs'])}")
            for job in result['found_jobs']:
                print(f"- {job['title']} at {job['company']}")
            
        elif choice == "2":
            print("Starting Networking Agent... (Not implemented yet)")
        elif choice == "3":
            print("Run 'streamlit run dashboard.py' to view analytics.")
        else:
            print("Invalid choice.")
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
