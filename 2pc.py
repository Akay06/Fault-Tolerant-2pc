import multiprocessing
import time
import random
import os
import json

# Global constants for timeouts
TIMEOUT = 5
FAILURE_DELAY = 10

def write_to_disk(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def read_from_disk(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return None

# Function for the Transaction Coordinator
def transaction_coordinator(participants, failure_scenario):
    print("[TC] Transaction Coordinator started.")
    transaction_log = {"status": "", "committed_nodes": []}
    
    saved_log = read_from_disk('transaction_log.json')
    if saved_log:
        transaction_log = saved_log
        print("[TC] Resumed from previous transaction log.")

    try:
        # Simulate failure for Part 1
        if failure_scenario == 1:
            print("[TC] Simulating failure before sending 'prepare' message.")
            time.sleep(FAILURE_DELAY)
        
        # Phase 1: Prepare Phase
        print("[TC] Sending 'prepare' message to participants...")
        for p in participants:
            p.send(("prepare", None))
        transaction_log['status'] = 'prepare'
        write_to_disk('transaction_log.json', transaction_log)

        responses = []
        for p in participants:
            if p.poll(TIMEOUT):
                responses.append(p.recv())
            else:
                print("[TC] Timeout waiting for participant response.")
                responses.append("no")

        # Check responses
        if "no" in responses:
            print("[TC] Abort due to 'no' response.")
            for p in participants:
                p.send(("abort", None))
            transaction_log['status'] = 'abort'
            write_to_disk('transaction_log.json', transaction_log)
            return

        # Phase 2: Commit Phase
        print("[TC] All participants agree. Sending 'commit' message...")
        transaction_log['status'] = 'commit'
        write_to_disk('transaction_log.json', transaction_log)
        for i, p in enumerate(participants):
            if failure_scenario == 3 and i == 1:
                print("[TC] Simulating failure after sending one 'commit' message.")
                time.sleep(FAILURE_DELAY)
                break
            p.send(("commit", None))
            transaction_log['committed_nodes'].append(i)
            write_to_disk('transaction_log.json', transaction_log)

        # Recovery for Part 3
        if failure_scenario == 3:
            print("[TC] Reading transaction log...")
            transaction_log = read_from_disk('transaction_log.json')
            if transaction_log["status"] == "commit":
                print("[TC] Resuming commit phase.")
                committed_nodes = set(transaction_log["committed_nodes"])
                for i, p in enumerate(participants):
                    if i not in committed_nodes:
                        p.send(("commit", None))
                        transaction_log['committed_nodes'].append(i)
                        write_to_disk('transaction_log.json', transaction_log)
            return
        
        # Recovery for Part 4
        while True:
            for i, p in enumerate(participants):
                if p.poll(TIMEOUT):
                    message, _ = p.recv()
                    if message == "recover":
                        print(f"[TC] Received recovery request from Node-{i}.")
                        outcome = transaction_log["status"]
                        p.send((outcome, None))
                        print(f"[TC] Sent '{outcome}' message to Node-{i}.")
    finally:
        print("[TC] Transaction Coordinator shutting down.")

# Function for Participants
def participant(node_id, connection, failure_scenario):
    print(f"[Node-{node_id}] Participant started.")
    transaction_log = {}
    
    saved_log = read_from_disk(f'node_{node_id}_log.json')
    if saved_log:
        transaction_log = saved_log
        print(f"[Node-{node_id}] Resumed from previous transaction log.")

    while True:
        if connection.poll(TIMEOUT):
            message, _ = connection.recv()

            if message == "prepare":
                print(f"[Node-{node_id}] Received 'prepare' message.")
                if failure_scenario == 1 and transaction_log["status"] == "abort":
                    print(f"[Node-{node_id}] Already abort. Responding 'no'.")
                    connection.send("no")
                    break
                elif failure_scenario == 2 and node_id == 0:
                    print(f"[Node-{node_id}] Simulating failure by responding 'no'.")
                    connection.send("no")
                elif failure_scenario == 4 and node_id == 1:
                    print(f"[Node-{node_id}] Simulating failure after replying 'yes'.")
                    connection.send("yes")
                    time.sleep(FAILURE_DELAY)
                else:
                    connection.send("yes")                
                
                transaction_log['status'] = 'prepare'
                write_to_disk(f'node_{node_id}_log.json', transaction_log)
                
            elif message == "commit":
                print(f"[Node-{node_id}] Committing transaction.")
                transaction_log['status'] = 'commit'
                write_to_disk(f'node_{node_id}_log.json', transaction_log)
                break

            elif message == "abort":
                print(f"[Node-{node_id}] Aborting transaction.")
                transaction_log['status'] = 'abort'
                write_to_disk(f'node_{node_id}_log.json', transaction_log)
                break
            
            if failure_scenario == 4 and node_id == 1 and transaction_log.get("status") == "prepare":
                print(f"[Node-{node_id}] Recovering from failure...")
                connection.send(("recover", None))
                if connection.poll(TIMEOUT):
                    outcome, _ = connection.recv()
                    print(f"[Node-{node_id}] Received '{outcome}' message.")
                    transaction_log["status"] = outcome
                    write_to_disk(f'node_{node_id}_log.json', transaction_log)
                    if outcome == "commit":
                        print(f"[Node-{node_id}] Committing transaction.")
                    elif outcome == "abort":
                        print(f"[Node-{node_id}] Aborting transaction.")
                    break
        else:
            print(f"[Node-{node_id}] Timeout waiting for message.")
            transaction_log['status'] = 'abort'
            write_to_disk(f'node_{node_id}_log.json', transaction_log)

    print(f"[Node-{node_id}] Final state: {transaction_log['status']}")
    print(f"[Node-{node_id}] Shutting down.")

# Main function to simulate the 2PC protocol
def main(failure_scenario):
    # Create pipes for communication
    parent_conns = []
    child_conns = []
    for _ in range(2):  # Two participants
        parent_conn, child_conn = multiprocessing.Pipe()
        parent_conns.append(parent_conn)
        child_conns.append(child_conn)

    # Create processes
    coordinator_process = multiprocessing.Process(target=transaction_coordinator, args=(parent_conns, failure_scenario))
    participant_processes = [
        multiprocessing.Process(target=participant, args=(i, conn, failure_scenario))
        for i, conn in enumerate(child_conns)
    ]

    # Start processes
    coordinator_process.start()
    for p in participant_processes:
        p.start()

    # Wait for processes to finish
    coordinator_process.join()
    for p in participant_processes:
        p.join()

    print("[Main] Simulation complete.")

# Run the simulation
if __name__ == "__main__":
    print("Choose a failure scenario to test (1-4):")
    print("1: Coordinator fails before sending 'prepare'")
    print("2: Coordinator aborts due to 'no'")
    print("3: Coordinator fails after sending some 'commit'")
    print("4: Participant fails after 'yes'")
    scenario = int(input("Enter scenario number: "))
    main(scenario)