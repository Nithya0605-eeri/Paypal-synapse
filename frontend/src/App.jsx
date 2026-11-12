import { useState } from "react";
import PaymentConfirmation from "./PaymentConfirmation";
import {
  Activity, BrainCircuit, Boxes, CreditCard,
  LayoutDashboard, Package, RefreshCw,
  ShieldCheck, TrendingUp, Workflow
} from "lucide-react";

const navigation = [
  { name: "Overview", icon: LayoutDashboard },
  { name: "Inventory", icon: Package },
  { name: "Demand Forecast", icon: TrendingUp },
  { name: "Digital Twin", icon: Activity },
  { name: "Procurement", icon: Boxes },
  { name: "AI Agents", icon: BrainCircuit },
  { name: "PayPal Payments", icon: CreditCard },
];
import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, LineChart, Line, Legend
} from "recharts";
export default function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [productId, setProductId] = useState("1");
  const [approvalId, setApprovalId] = useState("2");
  const [budget, setBudget] = useState("1000");
const [demandMultiplier, setDemandMultiplier] = useState("1.5");
const [days, setDays] = useState("7");
  const [apiKey, setApiKey] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function callAPI(path, method = "GET") {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`/api${path}`, {
        method,
        headers: {
          ...(apiKey ? { "X-Merchant-API-Key": apiKey } : {}),
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Request failed: ${response.status}`
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const actions = {
    Overview: [
      ["Check API Health", "/health", "GET"],
    ],
    Inventory: [
      ["Load Products", "/products", "GET"],
    ],
    "Demand Forecast": [
      ["Predict Demand", `/forecast/${productId}`, "GET"],
    ],
    "Digital Twin": [
  [
    "Run Simulation",
    `/simulate/${productId}?demand_multiplier=${encodeURIComponent(demandMultiplier)}&days=${encodeURIComponent(days)}`,
    "GET",
  ],
],
Procurement: [
  [
    "Optimize Procurement",
    `/optimize/${productId}?budget=${encodeURIComponent(budget)}&demand_multiplier=${encodeURIComponent(demandMultiplier)}&days=${encodeURIComponent(days)}`,
    "GET",
  ],
],
"AI Agents": [
  [
    "Run Agent Workflow",
    `/agents/run/${productId}?budget=${encodeURIComponent(budget)}&demand_multiplier=${encodeURIComponent(demandMultiplier)}&days=${encodeURIComponent(days)}`,
    "GET",
  ],
],
    "PayPal Payments": [
  [
    "Check Checkout Status",
    `/approvals/${approvalId}/checkout-status`,
    "GET"
  ],
  [
    "Approve Procurement",
    `/approvals/${approvalId}/approve`,
    "POST"
  ],
  [
    "Reject Procurement",
    `/approvals/${approvalId}/reject`,
    "POST"
  ],
  [
    "Reserve Checkout",
    `/approvals/${approvalId}/reserve-checkout`,
    "POST"
  ],
  [
    "Create PayPal Sandbox Order",
    `/approvals/${approvalId}/checkout`,
    "POST"
  ],
],
  };

  return (
    <div className="min-h-screen bg-[#080e1c] text-slate-100 md:flex">
      <aside className="w-full border-b border-slate-800 bg-[#0d1629] p-6 md:min-h-screen md:w-72 md:border-b-0 md:border-r">
        <div className="mb-10 flex items-center gap-3">
          <div className="rounded-xl bg-blue-600 p-3">
            <Workflow size={26} />
          </div>
          <div>
            <h1 className="text-xl font-bold">Synapse</h1>
            <p className="text-xs text-slate-400">
              AI Commerce Digital Twin
            </p>
          </div>
        </div>

        <nav className="space-y-2">
          {navigation.map(({ name, icon: Icon }) => (
            <button
              key={name}
              onClick={() => {
                setActivePage(name);
                setResult(null);
                setError("");
              }}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left transition ${
                activePage === name
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Icon size={19} />
              {name}
            </button>
          ))}
        </nav>

        <div className="mt-12 rounded-xl border border-slate-700 bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-sm text-emerald-400">
            <ShieldCheck size={17} />
            Human-approved payments
          </div>
          <p className="mt-2 text-xs text-slate-400">
            PayPal Sandbox environment. Checkout creation is
            separate from merchant approval.
          </p>
        </div>
      </aside>

      <main className="flex-1 p-6 md:p-10">
        <header className="mb-10 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-2 text-sm font-medium text-blue-400">
              PAYPAL SYNAPSE
            </p>
            <h2 className="text-3xl font-bold">{activePage}</h2>
            <p className="mt-2 text-slate-400">
              Intelligent commerce orchestration platform
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300">
            <Activity size={16} className="text-emerald-400" />
            Sandbox workspace
          </div>
        </header>

        <div className="mb-8 grid gap-4 md:grid-cols-3">
          {[
            ["AI Forecasting", "XGBoost", TrendingUp],
            ["Agent Orchestration", "LangGraph", BrainCircuit],
            ["Payment Infrastructure", "PayPal Sandbox", CreditCard],
          ].map(([label, value, Icon]) => (
            <div
              key={label}
              className="rounded-2xl border border-slate-800 bg-[#111c31] p-6"
            >
              <Icon className="mb-4 text-blue-400" size={24} />
              <p className="text-sm text-slate-400">{label}</p>
              <h3 className="mt-2 text-xl font-semibold">{value}</h3>
            </div>
          ))}
        </div>

        <section className="rounded-2xl border border-slate-800 bg-[#111c31] p-6">
          <div className="mb-6 flex items-center gap-3">
            <Boxes className="text-blue-400" />
            <h3 className="text-xl font-semibold">
              {activePage} Controls
            </h3>
          </div>

          <div className="mb-6 grid gap-4 md:grid-cols-3">
            <label className="text-sm text-slate-400">
              Product ID
              <input
                type="number"
                min="1"
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white"
              />
            </label>

            <label className="text-sm text-slate-400">
              Approval ID
              <input
                type="number"
                min="1"
                value={approvalId}
                onChange={(e) => setApprovalId(e.target.value)}
                className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white"
              />
            </label>

            <label className="text-sm text-slate-400">
              Merchant API Key
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter merchant key"
                autoComplete="off"
                className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white"
              />
            </label>
          </div>
{["Digital Twin", "Procurement", "AI Agents"].includes(activePage) && (
  <div className="mb-6 grid gap-4 md:grid-cols-3">
    <label className="text-sm text-slate-400">
      Procurement Budget (USD)
      <input
        type="number"
        min="1"
        value={budget}
        onChange={(e) => setBudget(e.target.value)}
        className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white"
      />
    </label>

    <label className="text-sm text-slate-400">
      Demand Multiplier
      <input
        type="number"
        min="0.1"
        step="0.1"
        value={demandMultiplier}
        onChange={(e) => setDemandMultiplier(e.target.value)}
        className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white"
      />
    </label>

    <label className="text-sm text-slate-400">
      Simulation Days
      <input
        type="number"
        min="1"
        max="365"
        value={days}
        onChange={(e) => setDays(e.target.value)}
        className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white"
      />
    </label>
  </div>
)}

         <div className="flex flex-wrap gap-3">
            {(actions[activePage] || []).map(
              ([label, path, method]) => (
                <button
                  key={label}
                  disabled={loading}
                  onClick={() => {
                    if (
                      method === "POST" &&
                      !window.confirm(
                        `Confirm action: ${label}?`
                      )
                    ) {
                      return;
                    }
                    callAPI(path, method);
                  }}
                  className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium text-white hover:bg-blue-500 disabled:opacity-50"
                >
                  <RefreshCw size={16} />
                  {label}
                </button>
              )
            )}
          </div>
        </section>
{activePage === "PayPal Payments" && (
  <PaymentConfirmation
    key={`${approvalId}-${apiKey}`}
    approvalId={approvalId}
    apiKey={apiKey}
    onResult={(data) => {
      setResult(data);
      setError("");
    }}
    onError={(message) => setError(message)}
  />
)}
        <section className="mt-6 rounded-2xl border border-slate-800 bg-[#111c31] p-6">
          <h3 className="mb-4 text-lg font-semibold">AI Output</h3>

          {loading && (
            <p className="text-blue-400">Processing request...</p>
          )}

          {error && (
            <p role="alert" className="rounded-lg bg-red-950 p-4 text-red-300">
              {error}
            </p>
          )}

          {!loading && !error && !result && (
            <p className="text-slate-400">
              Select an action to retrieve live backend results.
            </p>
          )}
{result &&
  activePage === "Digital Twin" &&
  typeof result.current_stock === "number" &&
  typeof result.projected_total_demand === "number" && (
    <div className="mb-6 rounded-xl border border-slate-700 bg-slate-950 p-5">
      <h4 className="mb-2 text-lg font-semibold">
        Inventory vs Projected Demand
      </h4>

      <p className="mb-5 text-sm text-slate-400">
        {result.simulation_days}-day scenario at{" "}
        {result.demand_multiplier}× demand
      </p>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={[
              {
                name: "Current Stock",
                units: result.current_stock,
                color: "#38bdf8",
              },
              {
                name: "Projected Demand",
                units: result.projected_total_demand,
                color: "#a78bfa",
              },
              {
                name: "Shortage",
                units: result.projected_shortage,
                color: "#fb7185",
              },
            ]}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="units" radius={[6, 6, 0, 0]}>
              {[
                "#38bdf8",
                "#a78bfa",
                "#fb7185",
              ].map((color, index) => (
                <Cell key={index} fill={color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {result.stockout_risk && (
        <p className="mt-4 rounded-lg border border-red-800 bg-red-950 p-3 text-sm text-red-300">
          Stockout warning: projected demand exceeds available inventory.
        </p>
      )}
    </div>
  )}
  {result && activePage === "Demand Forecast" && (
  <div className="mb-6 rounded-xl border border-slate-700 bg-slate-950 p-5">
    <h4 className="mb-3 text-lg font-semibold">
      AI Demand Forecast
    </h4>

    <p className="mb-4 text-sm text-slate-400">
      Prediction results from the machine learning backend.
    </p>

    {(() => {
      const forecast = Array.isArray(result.forecast)
        ? result.forecast
        : Array.isArray(result.predictions)
          ? result.predictions
          : null;

      if (!forecast || forecast.length === 0) {
        return (
          <p className="text-slate-400">
            Forecast received. Detailed prediction values
            are shown below.
          </p>
        );
      }

      const data = forecast
        .map((item, index) => ({
          day: item.day ?? index + 1,
          demand: Number(
            item.predicted_demand ??
            item.demand ??
            item.prediction ??
            item
          ),
        }))
        .filter((item) => Number.isFinite(item.demand));

      if (!data.length) {
        return <p className="text-slate-400">No chartable forecast series returned.</p>;
      }

      return (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="demand"
                stroke="#38bdf8"
                strokeWidth={3}
                dot={{ r: 4 }}
                name="Predicted Demand"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    })()}
  </div>
)}
{result &&
  activePage === "Demand Forecast" &&
  typeof result.predicted_units === "number" && (
    <div className="mb-6 rounded-xl border border-blue-800 bg-slate-950 p-6">
      <p className="text-sm font-medium text-blue-400">
        XGBoost Next-Day Demand Prediction
      </p>

      <div className="mt-4 flex flex-wrap items-end gap-3">
        <span className="text-5xl font-bold text-white">
          {result.predicted_units.toFixed(2)}
        </span>
        <span className="pb-1 text-slate-400">
          predicted units
        </span>
      </div>

      <div className="mt-5 h-4 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400"
          style={{
            width: `${Math.min(
              100,
              Math.max(0, result.predicted_units)
            )}%`,
          }}
        />
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-3">
        <div>
          <p className="text-xs text-slate-400">Forecast Date</p>
          <p className="font-medium">{result.forecast_date}</p>
        </div>

        <div>
          <p className="text-xs text-slate-400">ML Model</p>
          <p className="font-medium">{result.model}</p>
        </div>

        <div>
          <p className="text-xs text-slate-400">Data Source</p>
          <p className="font-medium">{result.data_source}</p>
        </div>
      </div>
    </div>
  )}

  {result &&
  activePage === "Procurement" &&
  result.optimization && (
    <div className="mb-6 rounded-xl border border-slate-700 bg-slate-950 p-6">
      <h4 className="mb-5 text-xl font-semibold">
        AI Procurement Recommendation
      </h4>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">Purchase Quantity</p>
          <p className="mt-2 text-2xl font-bold text-cyan-400">
            {result.optimization.total_quantity ?? 0}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">Total Cost</p>
          <p className="mt-2 text-2xl font-bold text-white">
            ${Number(result.optimization.total_cost ?? 0).toFixed(2)}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">Unfulfilled Demand</p>
          <p className="mt-2 text-2xl font-bold text-rose-400">
            {result.optimization.unfulfilled_quantity ?? 0}
          </p>
        </div>
      </div>

      <h5 className="mb-3 font-semibold">Supplier Purchase Plan</h5>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-700 text-slate-400">
            <tr>
              <th className="p-3">Supplier</th>
              <th className="p-3">Quantity</th>
              <th className="p-3">Unit Cost</th>
              <th className="p-3">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {(result.optimization.purchase_plan ?? []).map(
              (item, index) => (
                <tr key={index} className="border-b border-slate-800">
                  <td className="p-3">{item.supplier_name}</td>
                  <td className="p-3">{item.quantity}</td>
                  <td className="p-3">${Number(item.unit_cost).toFixed(2)}</td>
                  <td className="p-3">${Number(item.subtotal).toFixed(2)}</td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-6">
        <div className="mb-2 flex justify-between text-sm">
          <span>Budget Utilization</span>
          <span>
            {result.optimization.budget > 0
              ? (
                  (result.optimization.total_cost /
                    result.optimization.budget) *
                  100
                ).toFixed(1)
              : "0.0"}%
          </span>
        </div>

        <div className="h-3 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-cyan-500"
            style={{
              width: `${
                result.optimization.budget > 0
                  ? Math.min(
                      100,
                      (result.optimization.total_cost /
                        result.optimization.budget) *
                        100
                    )
                  : 0
              }%`,
            }}
          />
        </div>
      </div>

      <p className="mt-5 text-sm text-amber-300">
        Payment status: {result.payment_status ?? "not_initiated"}.
        Supplier purchases require a separate approval and checkout process.
      </p>
    </div>
  )}
  {result &&
  activePage === "AI Agents" &&
  result.forecast &&
  result.simulation &&
  result.optimization && (
    <div className="mb-6 rounded-xl border border-slate-700 bg-slate-950 p-6">
      <h4 className="mb-6 text-xl font-semibold">
        AI Agent Execution Workflow
      </h4>

      <div className="space-y-4">
        {[
          {
            title: "1. Demand Forecast",
            detail: `${result.forecast.predicted_units} predicted units`,
            status: "Forecast returned",
          },
          {
            title: "2. Digital Twin Simulation",
            detail: `${result.simulation.projected_total_demand} projected units of demand`,
            status: result.simulation.stockout_risk
              ? "Stockout risk detected"
              : "No stockout projected",
          },
          {
            title: "3. Procurement Optimization",
            detail: `${result.optimization.total_quantity} units recommended · $${Number(result.optimization.total_cost).toFixed(2)}`,
            status: result.optimization.status,
          },
          {
            title: "4. Merchant Approval",
            detail: "Human authorization required before payment",
            status: result.payment_status,
          },
        ].map((step, index) => (
          <div
            key={index}
            className="flex gap-4 rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-600 font-bold">
              {index + 1}
            </div>

            <div>
              <h5 className="font-semibold text-white">
                {step.title}
              </h5>
              <p className="mt-1 text-sm text-slate-300">
                {step.detail}
              </p>
              <p className="mt-2 text-xs text-cyan-400">
                {step.status}
              </p>
            </div>
          </div>
        ))}
      </div>

      <p className="mt-5 rounded-lg border border-amber-800 bg-amber-950 p-4 text-sm text-amber-300">
        AI recommendations do not automatically authorize or execute payments.
        Merchant approval is required before PayPal checkout.
      </p>
    </div>
  )}
  {result &&
  activePage === "PayPal Payments" &&
  result.checkout_status && (
    <div className="mb-6 rounded-xl border border-slate-700 bg-slate-950 p-6">
      <h4 className="mb-5 text-xl font-semibold text-white">
        PayPal Checkout Status
      </h4>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">Approval ID</p>
          <p className="mt-2 text-2xl font-bold">
            {result.approval_id}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">Checkout Status</p>
          <p className="mt-2 font-semibold text-cyan-400">
            {result.checkout_status.replaceAll("_", " ")}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">Payment State</p>
          <p className="mt-2 font-semibold text-amber-400">
            {result.payment_state.replaceAll("_", " ")}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900 p-4">
          <p className="text-sm text-slate-400">PayPal Order</p>
          <p className="mt-2 font-semibold">
            {result.paypal_order_exists
              ? "Order recorded"
              : "No order recorded locally"}
          </p>
        </div>
      </div>

      <div className="mt-5 rounded-lg border border-amber-800 bg-amber-950 p-4">
        <p className="font-semibold text-amber-300">
          Recovery Action
        </p>
        <p className="mt-2 text-sm text-amber-200">
          {result.recovery_action.replaceAll("_", " ")}
        </p>
        <p className="mt-2 text-xs text-slate-300">
          Request ID stored: {result.request_id_stored ? "Yes" : "No"}
        </p>
      </div>

      <p className="mt-5 text-sm text-slate-400">
        PayPal Sandbox checkout requires merchant authorization.
        An unconfirmed payment outcome must be reconciled before retrying.
      </p>
    </div>
  )}
  {activePage === "PayPal Payments" &&
  result?.approval_url &&
  (() => {
    try {
      const url = new URL(result.approval_url);

      if (
        url.protocol !== "https:" ||
        !["www.sandbox.paypal.com", "sandbox.paypal.com"].includes(url.hostname)
      ) {
        return null;
      }

      return (
        <div className="mb-4 rounded-xl border border-blue-500 bg-blue-950/40 p-5">
          <h3 className="text-lg font-semibold text-white">
            PayPal Sandbox Buyer Approval
          </h3>

          <p className="mt-2 text-sm text-slate-300">
            The PayPal order has been created. Buyer authorization
            is required before payment capture.
          </p>

          <a
            href={url.href}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block rounded-lg bg-blue-600 px-5 py-3 font-medium text-white hover:bg-blue-500"
          >
            Open PayPal Sandbox Approval
          </a>
        </div>
      );
    } catch {
      return null;
    }
  })()}
          {result && (
            <pre className="overflow-auto rounded-xl bg-slate-950 p-5 text-sm text-emerald-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </section>

        <footer className="mt-10 text-center text-xs text-slate-500">
          PayPal Synapse · AI-powered autonomous commerce digital twin
        </footer>
      </main>
    </div>
  );
}