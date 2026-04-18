import { createAugurWorkflowHooks } from './augur.js'
import type { AgentWorkflowHooks, WorkflowContext } from './augur.js'

export type { AgentWorkflowHooks, WorkflowContext }

export function createAgentWorkflowHooks(context: WorkflowContext): AgentWorkflowHooks | undefined {
  if (context.agentContract.specialization === 'augur') {
    return createAugurWorkflowHooks(context)
  }
  return undefined
}
