# 🛠️ Fault-Tolerant 2-Phase Commit (2PC) Protocol Implementation  

## 📌 Project Description  
This project implements a **fault-tolerant distributed 2-Phase Commit (2PC) protocol** to handle transactions across multiple nodes. The protocol ensures that a transaction is either **fully committed or fully aborted**, even in the presence of node failures.  

### 🔹 Key Features:  
✅ **Transaction Coordinator (TC)** – Manages the commit/abort process.  
✅ **Multiple Participant Nodes** – Emulated using separate processes.  
✅ **Fault Tolerance** – Handles random and controlled failures gracefully.  
✅ **Timeout Mechanism** – Ensures proper state transitions during failures.  
✅ **Logging & Recovery** – Logs all transactions for debugging and state recovery.  


## 📦 Requirements  
- **Programming Language:** Python 3.8 or higher  


## 🚀 How to Run  

1️⃣ **Clone the repository:**  
```bash
git clone https://github.com/yourusername/fault-tolerant-2pc.git
cd fault-tolerant-2pc
```

2️⃣ **Run the 2PC Simulation:**   
```bash
python 2pc.py
```

## 📊 Expected Output

### 📜 Logs:

 - State transitions (e.g., PREPARE, COMMIT, ABORT) of all nodes.
 - Recovery actions for failed nodes.
 - Logs are displayed in the terminal and saved in the root/user (Windows) folder for further analysis.

## 📬 Contact & Contribution
📌 Feel free to fork, contribute, or raise [issues](https://github.com/Akay06/Fault-Tolerant-2pc/issues)!  
⭐ If you like this project, don't forget to star the repository! 🌟
