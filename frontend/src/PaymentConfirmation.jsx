import { useState } from "react";
import { CreditCard, ShieldCheck, AlertTriangle } from "lucide-react";

export default function PaymentConfirmation({
  approvalId,
  apiKey,
  onResult,
  onError,
}) {
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState("");

  async function reviewPayment() {
    setBusy(true);
    setConfirmed(false);
    setReview(null);
    setError("");

    try {
      if (!apiKey.trim()) {
        throw new Error("Enter your merchant API key.");
      }

      const response = await fetch(
        `/api/approvals/${encodeURIComponent(approvalId)}/checkout-status`,
        {
          headers: { "X-Merchant-API-Key": apiKey },
          cache: "no-store",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to retrieve payment status.");
      }

      setReview(data);
    } catch (err) {
      setError(err.message);
      onError?.(err.message);
    } finally {
      setBusy(false);
    }
  }

  const eligible =
    review?.checkout_status === "paypal_order_created" &&
    review?.payment_state === "order_created" &&
    review?.paypal_order_exists === true;

  async function confirmCapture() {
    if (!confirmed || !eligible || busy) return;

    if (!window.confirm(
      "Confirm this PayPal Sandbox capture? This may capture a Sandbox payment."
    )) return;

    setBusy(true);
    setConfirmed(false);
    setError("");

    try {
      const response = await fetch(
        `/api/approvals/${encodeURIComponent(approvalId)}/capture`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Merchant-API-Key": apiKey,
          },
          body: JSON.stringify({ human_confirmed: true }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Capture could not be confirmed."
        );
      }

      setReview(null);
      onResult?.(data);
    } catch (err) {
      setReview(null);
      setError(
        `${err.message} Do not retry automatically. Reconcile the payment first.`
      );
      onError?.(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mt-6 rounded-2xl border border-blue-800 bg-slate-950 p-6">
      <div className="mb-4 flex items-center gap-3">
        <CreditCard className="text-blue-400" />
        <h3 className="text-xl font-semibold">PayPal Sandbox Capture</h3>
      </div>

      <div className="mb-5 flex gap-3 rounded-xl border border-amber-800 bg-amber-950/40 p-4">
        <AlertTriangle className="shrink-0 text-amber-400" size={20} />
        <p className="text-sm text-amber-200">
          Payment capture requires merchant authorization.
          AI recommendations do not authorize payments.
          Verify the approved amount and PayPal order before capture.
        </p>
      </div>

      <button
        type="button"
        onClick={reviewPayment}
        disabled={busy}
        className="rounded-lg bg-slate-700 px-5 py-3 font-medium text-white hover:bg-slate-600 disabled:opacity-50"
      >
        {busy ? "Processing..." : "Review Payment Status"}
      </button>

      {review && (
        <div className="mt-5 rounded-xl border border-slate-700 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">Approval ID</p>
          <p className="font-semibold">{review.approval_id}</p>

          <p className="mt-3 text-sm text-slate-400">Checkout Status</p>
          <p className="font-semibold">
            {review.checkout_status?.replaceAll("_", " ")}
          </p>

          <p className="mt-3 text-sm text-slate-400">Payment State</p>
          <p className="font-semibold text-cyan-400">
            {review.payment_state?.replaceAll("_", " ")}
          </p>

          {!eligible && (
            <p className="mt-4 text-sm text-amber-300">
              Capture is not available for the current checkout status.
            </p>
          )}

          {eligible && (
            <>
              <p className="mt-4 text-sm text-amber-300">
                This preliminary status does not verify the buyer's
                approval or the final payment amount.
              </p>

              <label className="mt-5 flex items-start gap-3 text-sm">
                <input
                  type="checkbox"
                  checked={confirmed}
                  onChange={(e) => setConfirmed(e.target.checked)}
                  className="mt-1"
                />
                I am the authorized merchant and explicitly confirm
                this Sandbox payment capture.
              </label>

              <button
                type="button"
                onClick={confirmCapture}
                disabled={!confirmed || busy}
                className="mt-5 flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white disabled:opacity-40"
              >
                <ShieldCheck size={18} />
                {busy ? "Processing..." : "Confirm Sandbox Capture"}
              </button>
            </>
          )}
        </div>
      )}

      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-950 p-4 text-sm text-red-300">
          {error}
        </p>
      )}
    </div>
  );
}