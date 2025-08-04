# MVP User Flow Document

## 1. Log in
User authenticates (MVP: Email/password modal).

## 2. Create Workflow
- User drags nodes (agent, email, Slack) onto canvas.
- Configures each with mini-form (API keys, messages, filters).

## 3. Save & Run
- Name and save the workflow.
- Hit “Run” – backend triggers agent execution via LangGraph runner.

## 4. Monitor & Debug
- UI shows running status in real-time panel.
- After execution, user inspects logs and results.

## 5. Human-in-the-loop
- Certain steps may require approval; user can accept, edit, or override actions.

## 6. Templates
- User can select prebuilt “Lead Qualification” workflow and customize variables.
