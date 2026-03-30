# Platinum Tier Demo Flow (End-to-End)

This document describes the exact setup and execution flow to demonstrate the Platinum Tier architecture:

> **Scenario**: "An email arrives while the Local Machine is OFFLINE. The Cloud Agent drafts a reply, waits for Local Agent approval when it comes online, and then the Local Agent executes the transaction."

## 1. Prerequisites (Setup the Demo State)

To simulate this perfectly, ensure the following state before starting the demo:

**On the Local Machine:**
1. Git repository `AI_Employee_Vault_Sync` is cloned and properly configured.
2. The Vault is currently synchronized.
3. **Turn OFF the Local Agent.** (Ensure `local_agent.py` and `vault_sync.py` on the local machine are stopped).

**On the Cloud VM:**
1. The `cloud_orchestrator` and `vault_sync.py` are RUNNING via PM2.
2. The Cloud VM is actively monitoring the `Needs_Action` folders and your Email/Social accounts.

## 2. Triggering the Event (Local Machine is Offline)

Since the local machine is effectively "offline" to the system:

1. Send an email to the Gmail account connected to the `gmail_cloud_watcher.py`.
2. Alternatively, for a faster mock trigger, create a file named `test_trigger.md` in your cloud VM repository path:
   ```bash
   touch /opt/ai-employee/AI_Employee_Vault_Sync/Needs_Action/email/test_trigger.md
   ```

## 3. Cloud Agent Action (Observation)

On the Cloud VM, the `gmail_cloud_watcher.py` will detect the event:
1. It reads the email (or trigger file).
2. It claims the task by moving it (if applicable).
3. It generates a Draft Response using Claude API (statically mocked in our test script).
4. The Cloud Agent creates a file: `/Pending_Approval/email/DRAFT_EMAIL_<TIMESTAMP>.md`.
5. The `vault_sync.py` script running on the Cloud VM automatically commits and pushes this draft to the private GitHub repository.

*At this exact moment, the drafted response lives ONLY in the Cloud and the GitHub repository. It has NOT been sent.*

## 4. Local Machine Comes Online

1. On your Local Machine, simulate coming online by starting the Local Sync and Agent:
   ```bash
   python vault_sync.py
   python local_agent.py
   ```
2. The `vault_sync.py` script pulls the latest changes from GitHub.
3. The new draft file `DRAFT_EMAIL_<TIMESTAMP>.md` appears in your local `AI_Employee_Vault/Pending_Approval/email/` folder.

## 5. Human-in-the-Loop (HITL) Approval

You (the CEO/Human) review the pending actions using the local CLI tool:

1. View pending approvals:
   ```bash
   python approve.py --list
   ```
   *Output shows 1 pending email draft.*

2. Approve the specific draft:
   ```bash
   python approve.py --approve DRAFT_EMAIL_<TIMESTAMP>.md
   ```
3. The `approve.py` script moves the file from `/Pending_Approval/email/` to `/Approved/`.

## 6. Local Agent Execution

The `local_agent.py` polling the `/Approved/` folder detects the newly moved file:

1. It reads the file contents.
2. Because it runs locally, it has access to the *real* execution credentials (e.g., SMTP password, WhatsApp session).
3. It executes the sending via the Email MCP server.
4. It logs the exact action to `/Logs/YYYY-MM-DD.json`.
5. It moves the file from `/Approved/` to `/Done/`.
6. Finally, the Local Agent appends a success block to `/Updates/local_status.md` and updates the `Dashboard.md`.

## 7. Final State Synchronization

1. The Local `vault_sync.py` cycle runs again.
2. It commits the `Dashboard.md` updates, the new `/Logs/`, and the file movement to `/Done/`.
3. It pushes back to GitHub.
4. The Cloud VM syncs and knows the task is fully completed.

**Demo Complete.** This proves the Hybrid Cloud-Local architecture operates perfectly with a rigid isolation of concerns and zero-trust execution rights on the Cloud side.
