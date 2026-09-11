# AI Code Review Agent

An AI-powered code review agent designed to automatically inspect a repository, identify potential issues, validate its findings using deterministic checks and an LLM-based validation layer, and generate a structured code review report.

The agent is currently integrated with **GitHub Actions** and can be executed automatically whenever code is pushed to the `main` branch.

---

## 1. Project Objective

The objective of this project is to combine traditional DevOps automation with AI-powered engineering workflows.

Instead of using AI only as a chatbot, this project demonstrates how an AI agent can participate in a software delivery pipeline.

The current workflow is:

```text
Developer
    |
    | git push
    v
GitHub Repository
    |
    v
GitHub Actions
    |
    +--------------------+
    |                    |
    v                    v
Traditional CI       AI Code Review
    |                    |
    |                    v
    |               Repository
    |               Investigation
    |                    |
    |                    v
    |               Candidate Findings
    |                    |
    |                    v
    |              Evidence Validation
    |                    |
    |                    v
    |               Final AI Review
    |                    |
    |                    v
    |               review.md
    |                    |
    |                    v
    |              GitHub Artifact
    |
    v
Build / Test / Release
```

The long-term goal is to evolve this into an autonomous AI-assisted software delivery platform.

---

# 2. What We Have Built

The project currently contains an AI Code Review Agent under:

```text
agents/
└── code-review-agent/
    ├── agent.py
    ├── tools.py
    ├── requirements.txt
    └── .env.example
```

The agent is capable of:

* Inspecting repository files
* Reading relevant source files
* Investigating the application architecture
* Generating potential findings
* Collecting evidence from the repository
* Validating findings deterministically
* Validating findings using an LLM
* Rejecting unsupported findings
* Generating a final review report
* Saving the report as `review.md`
* Running automatically through GitHub Actions
* Uploading the generated review as a GitHub Actions artifact

---

# 3. AI Code Review Architecture

The agent follows a multi-phase architecture instead of allowing the LLM to continuously inspect the repository without control.

```text
                 AI CODE REVIEW AGENT
                         |
                         v
              +---------------------+
              | Phase 1             |
              | Investigation       |
              +---------------------+
                         |
                         v
              +---------------------+
              | Phase 2             |
              | Candidate Findings  |
              +---------------------+
                         |
                         v
              +---------------------+
              | Phase 3A            |
              | Deterministic       |
              | Evidence Validation |
              +---------------------+
                         |
                         v
              +---------------------+
              | Phase 3B            |
              | LLM Validation      |
              +---------------------+
                         |
                         v
              +---------------------+
              | Phase 4             |
              | Final Report        |
              +---------------------+
                         |
                         v
                    review.md
```

This architecture was intentionally designed to reduce hallucinated findings and unsupported security claims.

---

# 4. Phase 1 — Repository Investigation

The first phase allows the agent to understand the repository.

The agent can:

* List repository files
* Read relevant files
* Inspect application configuration
* Inspect Dockerfiles
* Inspect CI/CD configuration
* Inspect backend and frontend implementation
* Collect evidence for later analysis

The investigation is controlled using limits such as:

```text
MAX_STEPS
FORCE_FINAL_AFTER
MAX_FILE_READS
```

These controls prevent the agent from getting stuck in an endless investigation loop.

Repeated operations such as repeatedly listing the same files or reading the same file are also controlled.

---

# 5. Phase 2 — Candidate Finding Generation

After investigating the repository, the agent generates potential findings.

Each finding follows a structured format:

```json
{
  "id": "F1",
  "severity": "HIGH",
  "category": "Security",
  "file": "backend/server.js",
  "claim": "What was actually observed",
  "evidence": "Exact short quote from the file",
  "impact": "Impact supported by the evidence",
  "recommendation": "Concrete recommendation",
  "confidence": "high",
  "evidence_type": "direct"
}
```

This is important because the agent is not simply asked:

> "Find problems in this repository."

Instead, every finding must contain:

* A specific file
* A specific claim
* Evidence
* Impact
* Recommendation
* Confidence
* Evidence type

This makes the output more auditable.

---

# 6. Phase 3A — Deterministic Evidence Validation

This is one of the most important parts of the architecture.

The system does not blindly trust the AI-generated findings.

The deterministic validation layer checks whether the finding is actually supported by the repository.

For example:

```text
AI Finding:

"backend/server.js contains X"

        |
        v

Does backend/server.js exist?
        |
        v
Was the file actually inspected?
        |
        v
Does the quoted evidence exist?
        |
        v
Does the technical claim match the file?
```

If the evidence cannot be found, the finding is rejected.

For example, during testing the system detected:

```text
[VALIDATOR] REJECT F6: evidence not found in file
```

This demonstrates that the validation layer can prevent unsupported findings from reaching the final report.

---

# 7. Phase 3B — LLM Evidence Validation

After deterministic validation, the remaining findings are passed through a second LLM validation layer.

The validator evaluates:

* Whether the observation is correct
* Whether the inference is justified
* Whether the impact is supported
* Whether the severity is appropriate
* Whether the recommendation makes sense

The validator can also correct the wording of a finding.

For example:

```text
Original AI finding
        |
        v
LLM Validator
        |
        +---- KEEP
        |
        +---- CORRECT
        |
        +---- REJECT
```

This provides a second layer of reasoning before a finding becomes part of the final review.

---

# 8. Phase 4 — Final Report Generation

The final phase generates the human-readable review.

The final report is generated from validated findings rather than directly from the initial AI output.

The report can contain:

* Executive summary
* Findings
* Severity
* Evidence
* Impact
* Recommendations
* Positive observations
* Improvement suggestions

The report is written to:

```text
review.md
```

The generated file is intentionally treated as an artifact rather than source code.

Therefore:

```gitignore
review.md
```

is included in `.gitignore`.

---

# 9. GitHub Actions Integration

The AI agent is integrated into GitHub Actions through:

```text
.github/workflows/ai-code-review.yml
```

The current workflow is triggered by a push to `main`.

```yaml
on:
  push:
    branches:
      - main
```

The workflow performs:

```text
Checkout
   ↓
Setup Python
   ↓
Install dependencies
   ↓
Read NVIDIA API key from GitHub Secret
   ↓
Run agent.py
   ↓
Generate review.md
   ↓
Upload review.md as artifact
```

The NVIDIA API key is not stored inside the repository.

The workflow accesses it through:

```yaml
env:
  NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
```

This keeps the credential outside the source code.

---

# 10. Current Technology Stack

The current implementation uses:

### Application

* Node.js
* Express
* React
* Vite

### DevOps

* Docker
* Docker Compose
* Git
* GitHub
* GitHub Actions

### AI Automation

* Python
* LLM API
* NVIDIA API
* AI Code Review Agent
* Tool-based repository investigation

### CI/CD

The project already contains a traditional CI/CD workflow that handles activities such as:

* Dependency installation
* Lint/build operations
* Version-based release workflows
* Docker image building
* Docker image publishing

The AI workflow is intentionally separated from the traditional CI pipeline.

---

# 11. What We Have Achieved

The project has moved beyond a simple LLM prompt.

We now have an AI agent capable of participating in an automated engineering workflow.

The major achievements are:

### 1. Autonomous repository investigation

The agent can inspect repository files without requiring the developer to manually provide each file.

### 2. Controlled agent execution

The agent contains execution limits to prevent infinite loops and unnecessary repository exploration.

### 3. Evidence-based findings

The agent is required to provide evidence for findings instead of producing unsupported recommendations.

### 4. Deterministic validation

Repository evidence is checked programmatically before findings are accepted.

### 5. LLM validation

A second AI validation layer reviews the generated findings.

### 6. Structured final output

The result is converted into a human-readable Markdown report.

### 7. CI integration

The agent can run automatically from GitHub Actions.

### 8. Secure credential handling

The NVIDIA API key is supplied through GitHub Actions Secrets instead of being committed to Git.

### 9. Artifact generation

The final review is saved as:

```text
review.md
```

and uploaded to GitHub Actions as an artifact.

---

# 12. Current Limitations

Although the current system works, it is still an early version of an AI engineering agent.

Important limitations include:

### 1. Push-based execution

The current workflow runs when code is pushed to `main`.

It does not yet understand pull requests.

Future implementation:

```text
Pull Request
     ↓
AI Review
     ↓
Review Comment
```

---

### 2. No automatic PR comments yet

The review is currently stored as an artifact.

The next improvement is to automatically publish:

```text
review.md
```

as a GitHub Pull Request comment.

---

### 3. Limited testing intelligence

The agent currently focuses primarily on repository inspection.

It should eventually be able to:

```text
Analyze code
     ↓
Identify risk
     ↓
Generate tests
     ↓
Run tests
     ↓
Analyze failures
     ↓
Suggest fixes
```

---

### 4. No automatic remediation

The current agent identifies issues but does not modify the repository.

A future version should be capable of:

```text
Finding
   ↓
Generate Fix
   ↓
Modify Code
   ↓
Run Tests
   ↓
Review Again
```

---

### 5. Limited security analysis

The current deterministic layer prevents some unsupported security claims, but it is not a complete security scanner.

It should eventually integrate tools such as:

* SAST
* Dependency scanning
* Secret scanning
* Container scanning
* IaC scanning
* DAST

The AI should then combine these results with its own analysis.

---

### 6. Provider dependency

The current implementation depends on an external LLM provider.

Temporary provider errors such as:

```text
503 ResourceExhausted
Worker local total request limit reached
```

can occur.

Retry handling has already been introduced, but production usage would require stronger reliability controls.

---

# 13. Improvements We Should Make

The next engineering improvements should focus on reliability, security, and automation.

## Priority 1 — Pull Request Integration

Change the workflow from:

```text
Push → AI Review
```

to:

```text
Pull Request → AI Review
```

This makes the agent useful during the actual software development lifecycle.

---

## Priority 2 — Automatic PR Comments

After generating `review.md`:

```text
review.md
    ↓
GitHub API
    ↓
Pull Request Comment
```

The developer should see the review directly inside GitHub.

---

## Priority 3 — Review Only Changed Files

Instead of analyzing the entire repository every time:

```text
PR
 ↓
git diff
 ↓
Changed files
 ↓
AI review
```

This will:

* Reduce token usage
* Reduce execution time
* Reduce API cost
* Improve review relevance

---

## Priority 4 — Add Automated Testing

The agent should execute:

```text
npm test
npm run lint
npm run build
```

or the appropriate repository commands.

The results should become evidence for the AI reviewer.

---

## Priority 5 — Add Security Scanners

Integrate deterministic security tools before the AI review.

Example:

```text
Repository
    |
    +---- SAST
    |
    +---- Dependency Scanner
    |
    +---- Secret Scanner
    |
    +---- Container Scanner
    |
    +---- IaC Scanner
    |
    v
AI Aggregator
    |
    v
Final Review
```

The AI becomes the reasoning and aggregation layer rather than the only security mechanism.

---

## Priority 6 — Confidence-Based Reviews

Every finding should have a confidence level:

```text
HIGH
MEDIUM
LOW
```

Low-confidence findings should either be excluded or clearly marked for human review.

---

## Priority 7 — Cost and Token Control

Introduce:

* File prioritization
* Diff-based analysis
* Token limits
* Caching
* Model selection
* Request batching
* Maximum review budget

This will make the agent more practical for production use.

---

# 14. Future Vision

The long-term objective is to evolve the current AI Code Review Agent into an **AI Software Engineering / DevOps Agent**.

The future architecture could look like:

```text
                    Developer
                        |
                        v
                     GitHub
                        |
                        v
                      Issue
                        |
                        v
                AI Coding Agent
                        |
                        v
                 Create Branch
                        |
                        v
                  Modify Code
                        |
                        v
                 Generate Tests
                        |
                        v
                  Run CI Tests
                        |
                 +------+------+
                 |             |
               PASS           FAIL
                 |             |
                 v             v
            AI Review      AI Debugging
                 |             |
                 +------+------+
                        |
                        v
                    Open PR
                        |
                        v
                 AI Code Review
                        |
                        v
                  Human Approval
                        |
                        v
                     CI/CD
                        |
                        v
                 Docker Build
                        |
                        v
                    Deploy
                        |
                        v
                  Monitoring
                        |
                        v
                 AI Operations
```

---

# 15. Future AI DevOps Capabilities

The system could eventually support:

### AI Coding Agent

Create and modify code based on issues or requirements.

### AI Testing Agent

Generate tests and execute them automatically.

### AI Code Review Agent

Review code and identify bugs, security problems, and engineering risks.

### AI Security Agent

Correlate SAST, dependency, container, secret, and IaC security findings.

### AI Infrastructure Agent

Analyze Terraform, Kubernetes, Docker, and cloud infrastructure.

### AI Deployment Agent

Deploy applications through controlled CI/CD workflows.

### AI Incident Agent

Analyze:

* Logs
* Metrics
* Traces
* Kubernetes events
* Application errors

and provide incident diagnosis.

### AI Remediation Agent

Generate and validate fixes for known operational problems.

---

# 16. Production-Level Architecture

A more mature implementation could eventually use multiple specialized agents:

```text
                    AI DevOps Platform
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
    Coding Agent      Review Agent      Security Agent
          |                |                |
          +----------------+----------------+
                           |
                           v
                    Testing Agent
                           |
                           v
                  Infrastructure Agent
                           |
                           v
                    Deployment Agent
                           |
                           v
                   Observability Agent
                           |
                           v
                   Incident Agent
```

A central orchestration layer could coordinate these agents.

---

# 17. Important Engineering Principle

The most important lesson from this project is:

> AI should not be treated as the source of truth.

The current architecture intentionally combines:

```text
LLM reasoning
+
Deterministic validation
+
Repository evidence
+
CI/CD results
+
Human approval
```

This is significantly safer than allowing an LLM to independently make production decisions.

The ideal architecture is:

```text
AI proposes
      ↓
Tools verify
      ↓
CI validates
      ↓
Human approves
      ↓
Automation executes
```

---

# 18. Current Status

### Completed

* [x] AI repository investigation
* [x] Controlled agent execution
* [x] Candidate finding generation
* [x] Evidence collection
* [x] Deterministic evidence validation
* [x] LLM evidence validation
* [x] Structured findings
* [x] Final review generation
* [x] `review.md` generation
* [x] GitHub Actions integration
* [x] NVIDIA API key through GitHub Secrets
* [x] GitHub Actions artifact upload
* [x] Traditional CI/CD pipeline
* [x] Docker-based application deployment workflow

### Next

* [ ] Pull Request-based review
* [ ] Automatic PR comments
* [ ] Changed-file/diff-based review
* [ ] Automated test execution
* [ ] Security scanner integration
* [ ] AI-generated remediation
* [ ] Automatic fix validation
* [ ] AI-generated Pull Requests
* [ ] Human approval gates
* [ ] Deployment automation
* [ ] AI-powered monitoring and incident response

---

# 19. Interview Value

This project demonstrates more than knowledge of LLM APIs.

It demonstrates practical experience with:

* DevOps automation
* CI/CD
* GitHub Actions
* Docker
* Python automation
* Cloud/API credential management
* Agent orchestration
* Tool-based AI workflows
* Evidence-based AI reasoning
* Automated validation
* Software delivery automation
* Security-aware AI design

The key interview message is:

> "I built an AI-assisted DevOps workflow where an agent investigates the repository, generates evidence-backed findings, validates those findings through deterministic checks and a second LLM validation layer, produces a review artifact, and executes automatically through GitHub Actions. The next step is to connect this workflow directly to pull requests and eventually evolve it into an autonomous coding, testing, review, and deployment system."

---

# 20. Conclusion

The current AI Code Review Agent is the foundation for a larger AI-driven DevOps platform.

It has progressed from:

```text
Simple LLM Prompt
```

to:

```text
Controlled AI Agent
        +
Repository Tools
        +
Evidence Collection
        +
Deterministic Validation
        +
LLM Validation
        +
CI/CD Integration
        +
Artifact Generation
```

The future goal is to build a system where AI can participate throughout the software delivery lifecycle while deterministic tooling, CI/CD controls, security checks, and human approval remain responsible for validating and controlling execution.

```

This is the documentation I'd keep **alongside the agent**, while `review.md` remains the **generated output of each run**. The README tells the interviewer *what you built and why*; `review.md` demonstrates *what the agent actually found*.
```
