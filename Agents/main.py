import sys
from agent.graph import build_graph

def main():
    """
    Main entry point to run the Project Pigeon agent.
    """
    # 1. Setup the graph
    app = build_graph()
    
    # 2. Define the input state (Realistic example)
    # In a real app, this might come from a DB or API request.
    initial_state = {
        "lead_id": "lead_99",
        "linkedin_url": "https://www.linkedin.com/in/satyanadella",
        "approved": False
    }
    
    config = {"configurable": {"thread_id": "demo_thread_1"}}

    print(f"--- STARTING AGENT FOR: {initial_state['linkedin_url']} ---")

    # 3. Run the graph - It should pause at the interrupt
    # stream(..., stream_mode="values") yields the state at each step
    current_state = None
    for event in app.stream(initial_state, config=config):
        # event is a wrapper dict like {'research': {...}} or {'draft': {...}} depending on mode.
        # But app.stream defaults to yielding dicts of node updates.
        
        # We handle output printing
        for node_name, updates in event.items():
            print(f"\n--> Node '{node_name}' finished.")
            # If we just finished the draft node, show the draft
            if node_name == "draft":
                print("\n[DRAFT GENERATED]")
                print(f"Subject: {updates.get('email_subject')}")
                print(f"Body:    {updates.get('email_body')}")
                print("------------------------------------------------")

    # 4. Check status after run stops (it should stop before human_approval_interrupt)
    snapshot = app.get_state(config)
    
    if snapshot.next:
        print(f"\n[INTERRUPT DETECTED] Execution paused at: {snapshot.next}")
        
        # 5. Simulate Human Review
        user_input = input("Do you approve this draft? (yes/no): ").strip().lower()
        
        if user_input == "yes":
            print("\n>>> APPROVING LEAD...")
            
            # Update the state to approved=True
            # Note: We must update 'approved' SO THAT the check in 'human_approval_interrupt' passes.
            app.update_state(config, {"approved": True})
            
            # 6. Resume execution
            print(">>> RESUMING EXECUTION...")
            for event in app.stream(None, config=config):
                 for node_name, updates in event.items():
                    print(f"\n--> Node '{node_name}' finished.")
                    
            print("\n--- WORKFLOW COMPLETED ---")
            
        else:
            print("\n>>> DRAFT REJECTED. WORKFLOW TERMINATED.")
    else:
        print("\nWorkflow finished without interrupt (unexpected for this logic).")

if __name__ == "__main__":
    main()
