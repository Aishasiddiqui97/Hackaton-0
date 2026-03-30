#!/bin/bash
# Ralph Wiggum Loop Convenience Script
# Usage: ./ralph_loop.sh "your task description"

TASK_DESC=$1
TIMESTAMP=$(date +%s)
VAULT_PATH="$HOME/AI_Employee_Vault"
PLAN_FILE="$VAULT_PATH/Plans/RALPH_TASK_$TIMESTAMP.md"

if [ -z "$TASK_DESC" ]; then
    echo "Usage: ./ralph_loop.sh \"task description\""
    exit 1
fi

# Create the plan file
cat <<EOF > "$PLAN_FILE"
# Ralph Task: $TASK_DESC
- [ ] $TASK_DESC
- [ ] Verify completion
EOF

echo "Created plan: $PLAN_FILE"

# Start Claude Code with the hook (Hypothetical CLI flag)
# In actual usage, the user would run claude with the hook configured.
# Here we simulate the logic:
MAX_ITER=15
ITER=0

while [ $ITER -lt $MAX_ITER ]; do
    echo "Iteration $((ITER+1)) starts..."
    # Replace the following command with the actual claude code command
    # claude-code "$TASK_DESC"
    
    # Run the hook manually to check
    python3 "$VAULT_PATH/.claude/hooks/stop_hook.py"
    if [ $? -eq 0 ]; then
        echo "TASK_COMPLETE"
        mv "$PLAN_FILE" "$VAULT_PATH/Done/"
        exit 0
    fi
    
    ITER=$((ITER+1))
    echo "Ralph says: I'm in a loop! (Waiting for completion...)"
    sleep 5
done

echo "Max iterations reached. Force exiting with error log."
echo "RALPH_LOOP_FAILURE: $TASK_DESC" >> "$VAULT_PATH/Logs/system_errors.log"
exit 1
