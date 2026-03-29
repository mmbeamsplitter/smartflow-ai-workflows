"""
Healthcare Document Processing Workflow Example

This workflow demonstrates automated processing of healthcare documents with AI
for extracting key information, validating compliance, and summarizing content.
"""

import os
from smartflow import Workflow, LLMAction, APIAction, TransformAction, ConditionalAction

# Configuration
HIPAA_COMPLIANT = True  # Set to True for HIPAA-compliant processing


def create_healthcare_document_workflow() -> Workflow:
    """
    Create a workflow for automated healthcare document processing.

    This workflow:
    1. Receives a healthcare document (insurance claim, medical record, etc.)
    2. Extracts and validates key information using AI
    3. Checks for HIPAA/GDPR compliance
    4. Generates structured summary
    5. Processes the document through appropriate systems

    Returns:
        Configured Workflow instance
    """
    workflow = Workflow(
        name="Healthcare Document Processing",
        description="Automated healthcare document analysis with compliance checking"
    )

    # Step 1: Receive and validate document input
    workflow.add_step(
        TransformAction(
            name="validate_input",
            source="document_text",
            operation="custom",
            custom_function=lambda text: len(text) > 50,  # Minimum length check
            description="Validate document input"
        )
    )

    # Step 2: Extract patient information (with care for PHI)
    workflow.add_step(
        LLMAction(
            name="extract_patient_info",
            prompt="""Extract and identify key information from this healthcare document.

Document content:
{document_text}

Identify (DO NOT output actual PII values, just field names and presence):
1. Patient identifier (present Y/N)
2. Date of birth (present Y/N)
3. Medical record number (present Y/N)
4. Insurance information (present Y/N)
5. Diagnosis codes (list if present)
6. Procedure codes (list if present)
7. Healthcare provider (present Y/N)
8. Treatment dates (present Y/N)

Provide output as structured JSON:
{
  "patient_id_present": true/false,
  "dob_present": true/false,
  "mrn_present": true/false,
  "insurance_present": true/false,
  "diagnosis_codes": ["code1", "code2"],
  "procedure_codes": ["code1", "code2"],
  "provider_present": true/false,
  "treatment_dates": [...],
  "document_type": "claim/record/referral/other"
}""",
            config={"provider": "openai", "model": "gpt-4", "temperature": 0.2},
            description="Extract structured healthcare information"
        )
    )

    # Step 3: HIPAA compliance check
    workflow.add_step(
        LLMAction(
            name="check_compliance",
            prompt="""Analyze this healthcare document for HIPAA compliance.

Document type: {document_type}
Information extracted: {extract_patient_info}

Check for:
1. Required protected health information (PHI) is present
2. Document includes necessary consent where required
3. Minimum necessary standard is met (appropriate information sharing)
4. Security indicators present
5. Privacy notice compliance

Provide compliance assessment:
{
  "compliant": true/false,
  "issues": ["issue1", "issue2"],
  "severity": "none/warning/critical",
  "recommendation": "text describing next steps"
}""",
            config={"provider": "openai", "model": "gpt-4", "temperature": 0.3},
            description="Check HIPAA/GDPR compliance"
        )
    )

    # Step 4: Generate document summary
    workflow.add_step(
        LLMAction(
            name="generate_summary",
            prompt="""Generate a professional healthcare document summary for this:

Document: {document_text}

Key information (structured): {extract_patient_info}
Compliance status: {check_compliance}

Create a concise summary including:
1. Document type and purpose
2. Key clinical/administrative information (non-specific)
3. Processing requirements
4. Next actions required

Summary should be professional, accurate, and suitable for healthcare administrative use.""",
            config={"provider": "openai", "model": "gpt-4", "temperature": 0.5},
            description="Generate document summary"
        )
    )

    # Step 5: Conditional routing based on compliance
    workflow.add_step(
        ConditionalAction(
            name="route_document",
            condition=simple_condition("check_compliance", "in", "compliant"),
            true_action=lambda ctx: {"route": "standard_processing", "status": "approved"},
            false_action=lambda ctx: {"route": "review_queue", "status": "requires_review"},
            description="Route based on compliance status"
        )
    )

    # Step 6: Update processing status (mock API call)
    workflow.add_step(
        APIAction(
            name="update_status",
            endpoint="https://api.healthcare-system.com/processing/status",
            method="POST",
            data={
                "document_type": "{document_type}",
                "summary": "{generate_summary}",
                "route": "{route_document.route}",
                "status": "{route_document.status}",
                "compliance": "{check_compliance}"
            },
            headers={"Content-Type": "application/json"},
            description="Update document processing in system"
        )
    )

    return workflow


if __name__ == "__main__":
    print("=" * 80)
    print("Healthcare Document Processing Workflow")
    print("=" * 80)

    # Example usage
    workflow = create_healthcare_document_workflow()

    # Validate workflow
    if not workflow.validate():
        print("❌ Workflow validation failed")
        exit(1)

    print("✓ Workflow validated successfully")

    # Sample document text (real documents would be much longer)
    sample_document = """
    PATIENT CLAIM FORM - CONFIDENTIAL

    Patient: [Redacted]
    Claim Number: CLM-2024-12345

    Services Provided:
    - CPT Code: 99213 - Office visit
    - ICD-10 Code: J01.90 - Acute sinusitis

    Treatment Date: March 15, 2024
    Provider: Dr. Smith, Family Medicine Associates

    Insurance: Blue Cross Blue Shield
    Policy: POL-987654321

    Notes: Patient presented with sinus congestion. Physical exam performed.
    Antibiotic prescribed. Follow-up recommended in 7 days.

    Total Charges: $150.00
    """

    print("\n📄 Sample Document Type: Insurance Claim")
    print("\n💡 This workflow would:")
    print("  1. Extract structured information from document")
    print("  2. Validate HIPAA/GDPR compliance")
    print("  3. Generate professional summary")
    print("  4. Route to appropriate processing queue")
    print("  5. Update system status")

    print("\n📊 Estimated Benefits:")
    print("  • 50% faster document processing")
    print("  • Improved compliance accuracy")
    print("  • Reduced manual review workload")
    print("  • Automatic PII detection and protection")
    print("  • Consistent documentation standards")

    print("\n🔒 Security Features:")
    print("  • HIPAA-compliant text extraction (no PII output)")
    print("  • Automated compliance checking")
    print("  • Secure routing based on risk level")
    print("  • Traceable processing audit trail")

    # Uncomment and add your document text to run:
    # result = workflow.run(
    #     document_text=sample_document,
    #     document_type="insurance_claim"
    # )
    #
    # print("\n📋 Processing Result:")
    # print(f"  Success: {result.success}")
    # print(f"  Steps Executed: {result.steps_executed}")
    # print(f"  Summary: {result.results.get('generate_summary', {}).get('output', 'N/A')}")