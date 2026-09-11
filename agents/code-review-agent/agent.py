import os
import json
import time
import re

from dotenv import load_dotenv
from openai import OpenAI

from tools import list_files, read_file

load_dotenv()

MODEL = "poolside/laguna-xs-2.1"

MAX_STEPS = 20
FORCE_FINAL_AFTER = 14
MAX_FILE_READS = 12


# ============================================================
# MODEL
# ============================================================

def call_model(client, messages, tools=None, max_tokens=3000, temperature=0.1):
    for attempt in range(5):
        try:
            kwargs = {
                "model": MODEL,
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.9,
                "max_tokens": max_tokens,
            }

            if tools:
                kwargs["tools"] = tools

            return client.chat.completions.create(**kwargs)

        except Exception as e:
            if attempt == 4:
                raise

            wait_time = 2 ** attempt

            print(f"\nModel request failed: {e}")
            print(f"Retrying in {wait_time} seconds...")

            time.sleep(wait_time)


# ============================================================
# TOOLS
# ============================================================

def build_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": (
                    "List files available in the repository. "
                    "Use this once at the beginning."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": (
                    "Read one repository-relative source code or "
                    "configuration file."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        }
                    },
                    "required": ["path"],
                },
            },
        },
    ]


# ============================================================
# INVESTIGATOR PROMPT
# ============================================================

INVESTIGATOR_PROMPT = """
You are a senior DevOps and software engineer performing
an evidence-based repository investigation.

Your job is ONLY to inspect the repository.

Do NOT write the final review yet.

CORE RULE:

NEVER GUESS.

Only make observations that are supported by files you actually inspected.

Investigation priorities:

1. GitHub Actions / CI/CD
2. Dockerfiles
3. docker-compose
4. Backend
5. Frontend
6. package.json
7. security configuration
8. infrastructure configuration

Rules:

- Call list_files() exactly once.
- Never call list_files() again.
- Never read the same file twice.
- Prefer high-value files.
- Do not waste steps reading every source file.
- Stop investigating once enough evidence exists.
- Do not assume missing functionality is a vulnerability.
- Do not assume an absence is dangerous.
- Distinguish observations from security conclusions.

Important:

If you see:

app.use(cors());

You may say:

"CORS is configured with the default permissive configuration."

You may NOT automatically say:

"This causes CSRF."

"This allows data exfiltration."

"This allows authentication bypass."

unless repository evidence proves those claims.

For Docker:

Count the actual FROM instructions.

One FROM = single-stage.

Two or more FROM instructions = multi-stage.

For tests:

"No test files observed" is different from:

"the project has zero test coverage."

Only claim what the repository proves.

When enough evidence has been collected, stop.
"""


# ============================================================
# FINDING GENERATOR
# ============================================================

FINDING_PROMPT = """
You are a senior security, DevOps and software engineering reviewer.

You are given repository evidence collected by another investigator.

Generate candidate findings.

IMPORTANT:

Every finding MUST be supported by evidence contained in the
provided repository evidence.

Return ONLY valid JSON.

Schema:

{
  "findings": [
    {
      "id": "F1",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "category": "security|ci-cd|docker|infrastructure|correctness|testing|maintainability",
      "file": "repository/path",
      "claim": "What was actually observed",
      "evidence": "Exact short quote from the file",
      "impact": "Only the impact supported by the evidence",
      "recommendation": "Concrete recommendation",
      "confidence": "high|medium|low",
      "evidence_type": "direct|absence|inference"
    }
  ]
}

STRICT RULES:

1. evidence MUST be an exact quote from the supplied file.
2. Do not invent evidence.
3. Do not report generic best practices as vulnerabilities.
4. Missing tests are not CRITICAL.
5. Public health endpoints are not automatically vulnerabilities.
6. cors() is not automatically a CSRF vulnerability.
7. Missing HEALTHCHECK is normally an operational improvement.
8. Missing .dockerignore is normally hardening unless sensitive
   files are actually exposed by the build context.
9. Do not claim multi-stage Docker builds unless the Dockerfile
   actually contains multiple FROM instructions.
10. If evidence is weak, use INFO or LOW.
11. If a claim depends on assumptions about authentication,
    sessions, databases, users or deployment, mark it as inference
    or reject it.
12. Never claim RCE, CSRF, data exfiltration, authentication bypass,
    DoS or privilege escalation without concrete repository evidence.
"""


# ============================================================
# EVIDENCE VALIDATOR
# ============================================================

VALIDATOR_PROMPT = """
You are an evidence validator.

Your job is NOT to find new issues.

You receive:

1. Repository evidence
2. Candidate findings generated by another model

Validate every finding.

For each finding determine:

- Is the referenced file actually present?
- Is the evidence actually present in that file?
- Does the claim accurately describe the evidence?
- Is the impact justified?
- Is the severity justified?
- Is the finding based on an unsupported assumption?

Return ONLY valid JSON:

{
  "validated_findings": [
    {
      "id": "F1",
      "decision": "KEEP|DOWNGRADE|REJECT",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "reason": "Short explanation",
      "corrected_claim": "Corrected claim",
      "corrected_impact": "Corrected impact"
    }
  ]
}

IMPORTANT:

If evidence does not exist:

REJECT.

If the evidence exists but the claim overstates the impact:

DOWNGRADE.

Example:

Evidence:

app.use(cors());

Claim:

"CORS allows requests from any origin."

This is supported.

Claim:

"Attackers can steal authenticated user data through CSRF."

This is NOT automatically supported.

Therefore downgrade/reject the second claim.

Docker example:

If a Dockerfile contains:

FROM node:22-alpine

there is one stage.

Calling it multi-stage is incorrect.

Reject that claim.

If a Dockerfile contains:

FROM node:22-alpine AS builder
...
FROM nginx:alpine

then multi-stage is supported.
"""


# ============================================================
# REPORT GENERATOR
# ============================================================

REPORT_PROMPT = """
You are a senior DevOps engineer producing the final repository review.

Use ONLY the validated findings and repository evidence.

Do not invent additional findings.

Do not resurrect rejected findings.

Use this format:

# Code Review

## Executive Summary

Brief summary.

## Critical Issues

Only validated CRITICAL findings.

## High Issues

Only validated HIGH findings.

## Medium Issues

Only validated MEDIUM findings.

## Low / Informational

Only validated LOW and INFO findings.

## Security Review

Summarize confirmed security observations.

Clearly distinguish:

- confirmed issue
- hardening recommendation
- unverified concern

## CI/CD Review

Summarize CI/CD observations.

## Docker / Infrastructure Review

Summarize Docker and infrastructure observations.

## Positive Findings

Only mention things directly supported by the repository.

## Recommended Action Plan

Prioritize practical improvements.

IMPORTANT:

Never describe something as a vulnerability merely because
it is not implemented.

Never say a Dockerfile is multi-stage unless it actually has
multiple FROM statements.

Never claim authentication, authorization, CSRF, data exposure,
RCE, DoS or similar impact unless validated evidence supports it.
"""


# ============================================================
# HELPERS
# ============================================================

def normalize_text(text):
    """
    Normalize whitespace so evidence matching is less brittle.
    """
    return re.sub(r"\s+", " ", text).strip()


def evidence_exists(evidence, file_content):
    """
    Check whether the quoted evidence actually exists.
    """

    if not evidence:
        return False

    normalized_evidence = normalize_text(evidence)
    normalized_file = normalize_text(file_content)

    return normalized_evidence in normalized_file


def extract_json(text):
    """
    Robustly extract the first valid JSON object from an LLM response.

    Handles:
    - plain JSON
    - ```json fenced JSON
    - extra text before JSON
    - extra text after JSON
    - multiple JSON-looking blocks
    """

    if not text:
        raise ValueError("Model returned an empty response.")

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    text = re.sub(
        r"```(?:json)?",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = text.replace("```", "").strip()

    # --------------------------------------------------------
    # Find the first JSON object and decode it properly.
    #
    # json.JSONDecoder().raw_decode() is important here.
    # Unlike json.loads(), it can parse the first JSON object
    # even when additional text exists after it.
    # --------------------------------------------------------

    decoder = json.JSONDecoder()

    for index, character in enumerate(text):

        if character != "{":
            continue

        candidate = text[index:]

        try:
            data, consumed = decoder.raw_decode(candidate)

            return data

        except json.JSONDecodeError:
            continue

    raise ValueError(
        "Could not extract valid JSON from model response.\n"
        f"Model response:\n{text}"
    )


# ============================================================
# DETERMINISTIC VALIDATION
# ============================================================

def deterministic_validate(findings, evidence_store, file_inventory):
    """
    First validation layer.

    This does NOT replace the LLM validator.

    It catches obvious hallucinations before the second
    model gets involved.
    """

    validated = []

    for finding in findings:

        file_path = finding.get("file", "")
        evidence = finding.get("evidence", "")

        # ----------------------------------------------------
        # File existence
        # ----------------------------------------------------

        if file_path not in evidence_store:
            print(
                f"[VALIDATOR] REJECT {finding.get('id')}: "
                f"file was not inspected"
            )
            continue

        # ----------------------------------------------------
        # Evidence existence
        # ----------------------------------------------------

        file_content = evidence_store[file_path]

        if not evidence_exists(evidence, file_content):
            print(
                f"[VALIDATOR] REJECT {finding.get('id')}: "
                f"evidence not found in file"
            )
            continue

        # ----------------------------------------------------
        # Docker multi-stage guard
        # ----------------------------------------------------

        claim = finding.get("claim", "").lower()

        if "multi-stage" in claim or "multistage" in claim:

            from_count = len(
                re.findall(
                    r"(?m)^\s*FROM\s+",
                    file_content,
                )
            )

            if from_count < 2:
                print(
                    f"[VALIDATOR] REJECT {finding.get('id')}: "
                    f"Dockerfile is not multi-stage"
                )
                continue

        # ----------------------------------------------------
        # Dangerous unsupported security claims
        # ----------------------------------------------------

        dangerous_claims = [
            "csrf",
            "data exfiltration",
            "authentication bypass",
            "remote code execution",
            "rce",
            "privilege escalation",
        ]

        unsupported_security_claim = False

        for term in dangerous_claims:
            if term in claim:
                unsupported_security_claim = True
                break

        if unsupported_security_claim:

            relevant_security_evidence = any(
                keyword in file_content.lower()
                for keyword in [
                    "cookie",
                    "session",
                    "authorization",
                    "authenticate",
                    "jwt",
                    "token",
                    "password",
                    "database",
                    "user",
                ]
            )

            if not relevant_security_evidence:

                print(
                    f"[VALIDATOR] DOWNGRADE {finding.get('id')}: "
                    f"security impact not supported"
                )

                finding["severity"] = "LOW"

                finding["impact"] = (
                    "The inspected repository does not provide "
                    "enough evidence to establish the claimed "
                    "security exploit."
                )

        validated.append(finding)

    return validated


# ============================================================
# INVESTIGATION
# ============================================================

def investigate(client):

    tools = build_tools()

    messages = [
        {
            "role": "system",
            "content": INVESTIGATOR_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "Start investigating the repository. "
                "Use the available tools."
            ),
        },
    ]

    evidence_store = {}
    file_inventory = []

    inspected_files = set()
    list_files_used = False

    for step in range(1, MAX_STEPS + 1):

        print(f"\n===== INVESTIGATION STEP {step}/{MAX_STEPS} =====")

        # Force the model to stop after enough investigation.
        if step >= FORCE_FINAL_AFTER:
            print("\n===== INVESTIGATION COMPLETE =====")
            break

        response = call_model(
            client,
            messages,
            tools=tools,
            max_tokens=2000,
        )

        message = response.choices[0].message

        # ----------------------------------------------------
        # No tool call
        # ----------------------------------------------------

        if not message.tool_calls:

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                }
            )

            print("Model finished investigation.")
            break

        messages.append(message)

        # ----------------------------------------------------
        # Execute tools
        # ----------------------------------------------------

        for tool_call in message.tool_calls:

            name = tool_call.function.name

            try:
                args = json.loads(
                    tool_call.function.arguments or "{}"
                )
            except json.JSONDecodeError:
                args = {}

            # ================================================
            # list_files
            # ================================================

            if name == "list_files":

                if list_files_used:
                    result = (
                        "ERROR: list_files() has already been used. "
                        "Do not call it again."
                    )

                else:

                    list_files_used = True

                    result = list_files()

                    file_inventory = [
                        line.strip()
                        for line in result.splitlines()
                        if line.strip()
                    ]

                    print("\n[FILES]")
                    print(result)

            # ================================================
            # read_file
            # ================================================

            elif name == "read_file":

                path = args.get("path", "")

                if not path:
                    result = "ERROR: path is required."

                elif path in inspected_files:

                    result = (
                        "ERROR: This file was already inspected. "
                        "Choose another high-value file."
                    )

                elif len(inspected_files) >= MAX_FILE_READS:

                    result = (
                        "ERROR: investigation file-read budget "
                        "has been reached. Stop investigating."
                    )

                else:

                    inspected_files.add(path)

                    result = read_file(path)

                    evidence_store[path] = result

                    print(f"\n[READ] {path}")

            else:

                result = f"ERROR: Unknown tool {name}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

    return evidence_store, file_inventory


# ============================================================
# FINDING GENERATION
# ============================================================

def generate_findings(client, evidence_store, file_inventory):

    evidence_text = ""

    for path, content in evidence_store.items():

        evidence_text += (
            f"\n\n===== FILE: {path} =====\n"
            f"{content}\n"
        )

    prompt = (
        FINDING_PROMPT
        + "\n\nREPOSITORY FILE INVENTORY:\n"
        + json.dumps(file_inventory, indent=2)
        + "\n\nINSPECTED FILES:\n"
        + evidence_text
    )

    response = call_model(
        client,
        [
            {
                "role": "system",
                "content": FINDING_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=5000,
        temperature=0.0,
    )

    content = response.choices[0].message.content

    data = extract_json(content)

    return data.get("findings", [])


# ============================================================
# LLM EVIDENCE VALIDATION
# ============================================================

def validate_findings_with_llm(
    client,
    findings,
    evidence_store,
    file_inventory,
):

    evidence_text = ""

    for path, content in evidence_store.items():

        evidence_text += (
            f"\n\n===== FILE: {path} =====\n"
            f"{content}\n"
        )

    prompt = (
        VALIDATOR_PROMPT
        + "\n\nFILE INVENTORY:\n"
        + json.dumps(file_inventory, indent=2)
        + "\n\nREPOSITORY EVIDENCE:\n"
        + evidence_text
        + "\n\nCANDIDATE FINDINGS:\n"
        + json.dumps(findings, indent=2)
    )

    response = call_model(
        client,
        [
            {
                "role": "system",
                "content": VALIDATOR_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=4000,
        temperature=0.0,
    )

    content = response.choices[0].message.content
    
    print("\n===== VALIDATOR MODEL RESPONSE =====")
    print(content)
    print("===== END VALIDATOR RESPONSE =====\n")

    data = extract_json(content)

    return data.get("validated_findings", [])


# ============================================================
# FINAL REPORT
# ============================================================

def generate_report(
    client,
    findings,
    validated_findings,
    evidence_store,
):

    kept = []

    finding_map = {
        finding.get("id"): finding
        for finding in findings
    }

    for validation in validated_findings:

        decision = validation.get("decision")

        if decision not in ["KEEP", "DOWNGRADE"]:
            continue

        finding_id = validation.get("id")

        finding = finding_map.get(finding_id)

        if not finding:
            continue

        finding["severity"] = validation.get(
            "severity",
            finding.get("severity", "INFO"),
        )

        finding["claim"] = validation.get(
            "corrected_claim",
            finding.get("claim"),
        )

        finding["impact"] = validation.get(
            "corrected_impact",
            finding.get("impact"),
        )

        kept.append(finding)

    prompt = (
        REPORT_PROMPT
        + "\n\nVALIDATED FINDINGS:\n"
        + json.dumps(kept, indent=2)
        + "\n\nINSPECTED EVIDENCE:\n"
    )

    for path, content in evidence_store.items():

        prompt += (
            f"\n===== {path} =====\n"
            f"{content}\n"
        )

    response = call_model(
        client,
        [
            {
                "role": "system",
                "content": REPORT_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=5000,
        temperature=0.1,
    )

    return response.choices[0].message.content


# ============================================================
# MAIN
# ============================================================

def main():

    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not configured."
        )

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
    )

    print("\n==========================================")
    print(" AI CODE REVIEW AGENT")
    print("==========================================")

    # --------------------------------------------------------
    # PHASE 1
    # --------------------------------------------------------

    print("\n[PHASE 1] Repository Investigation")

    evidence_store, file_inventory = investigate(client)

    print(
        f"\nInspected {len(evidence_store)} files."
    )

    # --------------------------------------------------------
    # PHASE 2
    # --------------------------------------------------------

    print("\n[PHASE 2] Candidate Finding Generation")

    findings = generate_findings(
        client,
        evidence_store,
        file_inventory,
    )

    print(
        f"Generated {len(findings)} candidate findings."
    )

    # --------------------------------------------------------
    # PHASE 3A
    # --------------------------------------------------------

    print("\n[PHASE 3A] Deterministic Evidence Validation")

    deterministic_findings = deterministic_validate(
        findings,
        evidence_store,
        file_inventory,
    )

    print(
        f"{len(deterministic_findings)} findings "
        f"passed deterministic validation."
    )

    # --------------------------------------------------------
    # PHASE 3B
    # --------------------------------------------------------

    print("\n[PHASE 3B] LLM Evidence Validation")

    validated_findings = validate_findings_with_llm(
        client,
        deterministic_findings,
        evidence_store,
        file_inventory,
    )

    kept_count = sum(
        1
        for finding in validated_findings
        if finding.get("decision")
        in ["KEEP", "DOWNGRADE"]
    )

    print(
        f"{kept_count} findings survived validation."
    )

    # --------------------------------------------------------
    # PHASE 4
    # --------------------------------------------------------

    print("\n[PHASE 4] Final Report Generation")

    report = generate_report(
        client,
        deterministic_findings,
        validated_findings,
        evidence_store,
    )

    print("\n")
    print("=" * 60)
    print("FINAL CODE REVIEW")
    print("=" * 60)
    print(report)
    
    review_path = "review.md"

    with open(review_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReview written to {review_path}")


if __name__ == "__main__":
    main()
    
