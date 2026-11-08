"""Keep each diagram bundle together in the presentation/reference layout."""
from pathlib import Path
import os

DIAGRAM_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_FOLDERS = {
    "architecture-design": "main",
    "event-outbox-design": "main",
    "outbox-delivery-sequence": "main",
    "order-lifecycle": "main",
    "commerce-overview": "reference/business",
    "checkout-sequence": "reference/business",
    "start-payment-sequence": "reference/payment",
    "payment-webhook-sequence": "reference/payment",
    "refund-sequence": "reference/payment",
    "mongodb-document-model": "reference/data",
    "config-publication-sequence": "reference/data",
    "deployment-security": "reference/operations",
    "observability-design": "reference/operations",
    "recovery-design": "reference/operations",
    "repository-architecture": "reference/repository",
    "domain-model": "domain",
    "domain-identity-model": "domain",
    "domain-merchandising-model": "domain",
    "domain-commerce-model": "domain"
}


def artifact_dir(slug):
    return DIAGRAM_ROOT / ARTIFACT_FOLDERS[slug]


def artifact_path(slug, extension):
    return artifact_dir(slug) / (slug + extension)


def resource_link(slug, relative):
    return Path(os.path.relpath(DIAGRAM_ROOT / relative, artifact_dir(slug))).as_posix()
