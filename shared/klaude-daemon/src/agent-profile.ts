import type { AgentProfile, RequestMessage } from './types.js'

const DEFAULT_REFLECTION_PROMPT = [
  'Based on the completed task, return strict JSON only with exactly these keys:',
  '{"project":"...","general":"..."}',
  'project: lessons specific to the current project/repo/context.',
  'general: lessons that transfer to any project.',
  'Use strings only. If there is no strong lesson for a key, return an empty string.',
].join('\n')

export function loadAgentProfile(agentName: string): AgentProfile {
  if (agentName === 'augur') {
    return {
      promptPrefix: 'You are Augur. Favor design-level reasoning and architecture trade-offs.',
      defaultReflectionPrompt: [
        'Return strict JSON with exactly {"project":"...","general":"..."}.',
        'For project, focus on design decisions, bundle strategy, and architecture-specific lessons.',
        'For general, focus on transferable architecture and review lessons.',
      ].join('\n'),
      supportedAgentParams: ['bundle_mode'],
    }
  }

  return {
    defaultReflectionPrompt: DEFAULT_REFLECTION_PROMPT,
    supportedAgentParams: [],
  }
}

export function buildPromptFromProfile(profile: AgentProfile, message: RequestMessage): string {
  const workingDirSuffix = message.working_dir
    ? `\n\nWorking directory hint: focus your work in \`${message.working_dir}\`. Start there unless the task clearly requires files outside it.`
    : ''

  if (!profile.promptPrefix) {
    return `${message.prompt}${workingDirSuffix}`
  }
  return `${profile.promptPrefix}\n\n${message.prompt}${workingDirSuffix}`
}

export function resolveReflectionPrompt(profile: AgentProfile, message: RequestMessage): string {
  return message.reflection_prompt ?? profile.defaultReflectionPrompt ?? DEFAULT_REFLECTION_PROMPT
}
