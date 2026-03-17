#!/bin/bash
# Guard hook: blocks kubectl write operations via SSH unless deployer auth token is present.
# Deployer places the token at /tmp/.deployer-auth before running, removes it after.

INPUT=$(cat)

# Fast exit: if input doesn't contain ssh, no kubectl/docker guard needed
case "$INPUT" in
  *ssh*) ;;
  *) echo '{}'; exit 0 ;;
esac

# Extract command from tool_input
CMD=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only guard SSH commands containing kubectl write operations
if echo "$CMD" | grep -qE 'ssh\s+\S+.*kubectl\s+(apply|delete|scale|rollout|create|patch|set|replace|edit|label|annotate|taint|drain|cordon|uncordon)'; then
  SECRET=$(cat "$HOME/.claude/.deployer-secret" 2>/dev/null)
  AUTH=$(cat /tmp/.deployer-auth 2>/dev/null)

  if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
    # Valid deployer auth — hard-block anything that could kill the workstation or its node.

    # Block kustomize apply on master/ namespace (contains workstation + all master infra)
    if echo "$CMD" | grep -qE 'kubectl\s+apply\s+-k\s+\S*master'; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Hard block: kubectl apply -k on master/ would restart the workstation pod you are running inside. This is never safe from inside the pod. Use `kubectl apply -f` for individual non-workstation manifests, or restart externally."}}'
      exit 0
    fi

    # Block applying workstation.yaml directly
    if echo "$CMD" | grep -qE 'kubectl\s+apply\s+-f\s+\S*workstation\.yaml'; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Hard block: applying workstation.yaml would restart the workstation pod you are running inside. Workstation restarts must be done externally."}}'
      exit 0
    fi

    # Block any write operation targeting the master namespace by name
    if echo "$CMD" | grep -qE 'kubectl\s+(delete|scale|rollout|patch|replace|set)\s.*(-n|--namespace)[= ]?master\b'; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Hard block: write operations in the master namespace can kill the workstation. Only read operations (get, describe, logs) are allowed from inside the pod."}}'
      exit 0
    fi
    if echo "$CMD" | grep -qE 'kubectl\s+(delete|scale|rollout|patch|replace|set)\s.*\bworkstation\b'; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Hard block: write operations targeting workstation resources are not safe from inside the pod."}}'
      exit 0
    fi

    # Block node operations (drain/cordon) — evicting the workstation node kills the pod
    if echo "$CMD" | grep -qE 'kubectl\s+(drain|cordon|uncordon)\b'; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Hard block: drain/cordon can evict the workstation pod. Node operations must be done externally."}}'
      exit 0
    fi

    echo '{}'
    exit 0
  else
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked: kubectl write operations require the deployer agent. Use /deployer:roll <project> <source> <target> instead."}}'
    exit 0
  fi
fi

# Also guard direct docker build/push via SSH
if echo "$CMD" | grep -qE 'ssh\s+\S+.*(docker\s+(build|push|tag|save)|k3s\s+ctr)'; then
  SECRET=$(cat "$HOME/.claude/.deployer-secret" 2>/dev/null)
  AUTH=$(cat /tmp/.deployer-auth 2>/dev/null)

  if [[ -n "$SECRET" && "$AUTH" == "$SECRET" ]]; then
    echo '{}'
    exit 0
  else
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked: image build/push requires the deployer agent. Use /deployer:roll <project> <source> <target> instead."}}'
    exit 0
  fi
fi

# Not a guarded command — allow
echo '{}'
exit 0
