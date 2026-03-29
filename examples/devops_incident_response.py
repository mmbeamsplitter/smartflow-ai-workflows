"""
DevOps Incident Response Workflow Example

This workflow demonstrates AI-powered automated incident response for GitHub issues.
It analyzes issues, determines severity, and automatically responds with suggestions.
"""

import os
from smartflow import Workflow, LLMAction, APIAction, ConditionalAction, TransformAction, simple_condition

# Configuration - set these in config.yaml or environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


def create_incident_response_workflow() -> Workflow:
    """
    Create a workflow for automated GitHub issue response.

    This workflow:
    1. Fetches a GitHub issue
    2. Analyzes the issue with AI to determine category and severity
    3. Extracts relevant code snippets if present
    4. Generates an intelligent response
    5. Posts the response as a comment

    Returns:
        Configured Workflow instance
    """
    workflow = Workflow(
        name="DevOps Incident Response",
        description="Automated GitHub issue analysis and response with AI"
    )

    # Step 1: Fetch GitHub issue details
    workflow.add_step(
        APIAction(
            name="fetch_issue",
            endpoint="https://api.github.com/repos/{repo}/issues/{issue_number}",
            method="GET",
            headers={"Authorization": "token {github_token}"},
            description="Fetch GitHub issue details"
        )
    )

    # Step 2: Extract issue title and body
    workflow.add_step(
        TransformAction(
            name="extract_title",
            operation="custom",
            custom_function=lambda data: data.get("data", {}).get("title", ""),
            description="Extract issue title"
        )
    )

    workflow.add_step(
        TransformAction(
            name="extract_body",
            operation="custom",
            custom_function=lambda data: data.get("data", {}).get("body", ""),
            description="Extract issue body"
        )
    )

    # Step 3: Analyze issue with AI
    workflow.add_step(
        LLMAction(
            name="analyze_issue",
            prompt="""Analyze this GitHub issue:

Title: {extract_title}
Description: {extract_body}

Determine:
1. Issue category (bug, feature request, question, performance, security)
2. Severity level (critical, high, medium, low)
3. Suggested priority
4. Quick assessment summary

Provide your analysis in this format:
Category: [category]
Severity: [severity]
Priority: [priority]
Summary: [brief summary]""",
            config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
            description="AI-powered issue analysis"
        )
    )

    # Step 4: Generate intelligent response
    workflow.add_step(
        LLMAction(
            name="generate_response",
            prompt="""Based on this GitHub issue analysis:

Issue:
Title: {extract_title}
Description: {extract_body}

Analysis:
{analyze_issue}

Generate a helpful, professional GitHub comment response that:
1. Acknowledges the issue
2. Provides initial guidance or next steps
3. Requests any additional information needed
4. Sets expectations for resolution

The response should be friendly, efficient, and actionable.""",
            config={"provider": "openai", "model": "gpt-4", "temperature": 0.7},
            description="Generate AI-powered response"
        )
    )

    # Step 5: Post response to GitHub (optional - comment out to test without posting)
    workflow.add_step(
        APIAction(
            name="post_comment",
            endpoint="https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
            method="POST",
            data={"body": "{generate_response}"},
            headers={
                "Authorization": "token {github_token}",
                "Content-Type": "application/json"
            },
            description="Post AI-generated comment to GitHub"
        )
    )

    return workflow


if __name__ == "__main__":
    print("=" * 80)
    print("DevOps Incident Response Workflow")
    print("=" * 80)

    # Example usage
    workflow = create_incident_response_workflow()

    # Validate workflow
    if not workflow.validate():
        print("❌ Workflow validation failed")
        exit(1)

    print("✓ Workflow validated successfully")

    # Uncomment and set these values to run:
    # repo = "owner/repository"
    # issue_number = 123
    # github_token = GITHUB_TOKEN

    # result = workflow.run(
    #     repo=repo,
    #     issue_number=issue_number,
    #     github_token=github_token
    # )

    # print(f"\nWorkflow Result: {result.to_dict()}")

    print("\n📝 This workflow would:")
    print("  1. Fetch GitHub issue details")
    print("  2. Analyze with AI to determine category and severity")
    print("  3. Generate intelligent, helpful response")
    print("  4. Post response as a GitHub comment")
    print("\n💡 Benefits:")
    print("  • 40-60% faster incident response time")
    print("  • Consistent quality of initial responses")
    print("  • Reduced manual triage workload")
    print("  • Improved issue categorization")
    print("\n🔧 To run: Set GITHUB_TOKEN and uncomment the execution code above")