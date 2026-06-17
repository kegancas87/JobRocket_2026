"""
PayFast Wallet Tokenization Service
Handles: Card setup (tokenization), ad hoc charges, auto top-up logic
"""

import os
import hashlib
import uuid
import logging
import urllib.parse
from datetime import datetime, timezone
import httpx

logger = logging.getLogger("payfast_wallet")

MERCHANT_ID = os.environ.get("PAYFAST_MERCHANT_ID")
MERCHANT_KEY = os.environ.get("PAYFAST_MERCHANT_KEY")
PASSPHRASE = os.environ.get("PAYFAST_PASSPHRASE")
IS_SANDBOX = os.environ.get("PAYFAST_SANDBOX", "False").lower() == "true"

PF_HOST = "sandbox.payfast.co.za" if IS_SANDBOX else "www.payfast.co.za"
PF_PROCESS_URL = f"https://{PF_HOST}/eng/process"
PF_API_BASE = "https://api.payfast.co.za"


def _generate_payment_signature(data: dict) -> str:
    """Generate MD5 signature for PayFast payment form (insertion order)."""
    pf_output = ""
    for key, val in data.items():
        if val is not None and val != "":
            pf_output += f"{key}={urllib.parse.quote_plus(str(val).strip())}&"
    pf_output = pf_output.rstrip("&")
    if PASSPHRASE:
        pf_output += f"&passphrase={urllib.parse.quote_plus(PASSPHRASE.strip())}"
    return hashlib.md5(pf_output.encode()).hexdigest()


def _generate_api_signature(params: dict) -> str:
    """Generate MD5 signature for PayFast API calls (alphabetical order)."""
    data = dict(params)
    if PASSPHRASE:
        data["passphrase"] = PASSPHRASE
    sorted_data = sorted(data.items())
    param_string = urllib.parse.urlencode(sorted_data)
    return hashlib.md5(param_string.encode()).hexdigest()


def generate_card_setup_data(user_id: str, user_email: str, user_first: str, user_last: str,
                              return_url: str, cancel_url: str, notify_url: str) -> dict:
    """
    Generate PayFast form data for tokenization card setup.
    subscription_type=2 means tokenization (ad hoc future charges).
    amount=0 means no initial charge — just save the card.
    """
    m_payment_id = f"wallet-setup-{user_id}-{uuid.uuid4().hex[:8]}"

    data = {
        "merchant_id": MERCHANT_ID,
        "merchant_key": MERCHANT_KEY,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": notify_url,
        "name_first": user_first,
        "name_last": user_last,
        "email_address": user_email,
        "m_payment_id": m_payment_id,
        "amount": "0.00",
        "item_name": "JobRocket Wallet - Save Card",
        "item_description": "Save your card for automatic wallet top-ups",
        "payment_method": "cc",
        "subscription_type": "2",
        "custom_str1": user_id,
        "custom_str2": "wallet_tokenization",
    }

    signature = _generate_payment_signature(data)
    data["signature"] = signature

    return {
        "form_data": data,
        "action_url": PF_PROCESS_URL,
        "m_payment_id": m_payment_id,
    }


async def charge_saved_card(token: str, amount_cents: int, item_name: str,
                             m_payment_id: str = None) -> dict:
    """
    Charge a saved card via PayFast ad hoc tokenization API.
    Amount must be in cents (ZAR). Minimum 500 cents (R5.00).
    """
    if amount_cents < 500:
        return {"success": False, "error": "Minimum charge is R5.00"}

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+02:00")
    if not m_payment_id:
        m_payment_id = f"wallet-topup-{uuid.uuid4().hex[:8]}"

    body = {
        "amount": amount_cents,
        "item_name": item_name,
        "m_payment_id": m_payment_id,
        "itn": "true",
    }

    header_params = {
        "merchant-id": MERCHANT_ID,
        "timestamp": timestamp,
        "version": "v1",
    }

    sig_data = {}
    sig_data.update({k: str(v) for k, v in body.items()})
    sig_data.update({k: str(v) for k, v in header_params.items()})
    signature = _generate_api_signature(sig_data)

    headers = {
        "merchant-id": MERCHANT_ID,
        "version": "v1",
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json",
    }

    url = f"{PF_API_BASE}/subscriptions/{token}/adhoc"
    if IS_SANDBOX:
        url += "?testing=true"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=body, headers=headers)
            result = resp.json()

        if resp.status_code == 200 and result.get("data", {}).get("response") is True:
            return {
                "success": True,
                "pf_payment_id": result["data"].get("pf_payment_id"),
                "message": result["data"].get("message", "Success"),
            }
        else:
            error_msg = result.get("data", {}).get("message", "Payment failed")
            logger.error(f"PayFast adhoc charge failed: {result}")
            return {"success": False, "error": error_msg}

    except Exception as e:
        logger.error(f"PayFast adhoc charge exception: {e}")
        return {"success": False, "error": str(e)}


async def process_auto_topup(db, user_id: str) -> dict:
    """
    Check if user needs auto top-up and process it.
    Called after each AI wallet deduction.
    Returns the top-up result or None if not needed.
    """
    user = await db.users.find_one({"id": user_id}, {
        "_id": 0, "wallet_balance": 1, "wallet_auto_topup": 1, "wallet_payfast_token": 1
    })
    if not user:
        return None

    settings = user.get("wallet_auto_topup", {})
    if not settings.get("enabled"):
        return None

    token = user.get("wallet_payfast_token")
    if not token:
        return None

    balance = user.get("wallet_balance", 0)
    threshold = settings.get("threshold", 0)
    topup_amount = settings.get("amount", 0)

    if balance >= threshold:
        return None

    if topup_amount < 5:
        return None

    amount_cents = int(topup_amount * 100)
    m_payment_id = f"auto-topup-{user_id[:8]}-{uuid.uuid4().hex[:8]}"

    result = await charge_saved_card(
        token=token,
        amount_cents=amount_cents,
        item_name=f"JobRocket Wallet Auto Top-Up R{topup_amount:.2f}",
        m_payment_id=m_payment_id,
    )

    if result.get("success"):
        new_doc = await db.users.find_one_and_update(
            {"id": user_id},
            {"$inc": {"wallet_balance": topup_amount}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            return_document=True,
            projection={"_id": 0, "wallet_balance": 1},
        )

        await db.ai_usage_log.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "auto_topup",
            "amount": topup_amount,
            "m_payment_id": m_payment_id,
            "pf_payment_id": result.get("pf_payment_id"),
            "created_at": datetime.now(timezone.utc),
        })

        new_balance = new_doc.get("wallet_balance", 0) if new_doc else 0
        logger.info(f"Auto top-up R{topup_amount:.2f} for user {user_id}. New balance: R{new_balance:.2f}")
        return {"success": True, "amount": topup_amount, "new_balance": new_balance}
    else:
        logger.warning(f"Auto top-up failed for user {user_id}: {result.get('error')}")
        await db.ai_usage_log.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": "auto_topup_failed",
            "amount": topup_amount,
            "error": result.get("error", "Unknown"),
            "created_at": datetime.now(timezone.utc),
        })
        return {"success": False, "error": result.get("error")}
