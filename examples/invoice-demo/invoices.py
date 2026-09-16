"""Synthetic local invoice service for evaluating the audit agent. No real data."""

INVOICES = {
    "inv-alice": {"owner": "alice", "amount": 125, "description": "Example invoice"},
    "inv-bob": {"owner": "bob", "amount": 75, "description": "Another example"},
}


def read_invoice(authenticated_user, invoice_id):
    """Return an invoice to its authenticated owner."""
    if not authenticated_user:
        raise PermissionError("Sign in first")
    return dict(INVOICES[invoice_id])
