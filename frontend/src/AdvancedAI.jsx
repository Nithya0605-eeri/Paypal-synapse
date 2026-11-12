import { useState } from "react";
const features = [
  ["Monte Carlo Simulation", "monte-carlo"], ["SHAP Explainability", "explain"],
  ["Supplier Graph Neural Network", "graph"], ["AI Procurement Risk", "risk"],
  ["ML Evaluation", "metrics"], ["LLM Agent Explanation", "agent-explain"]
];
export default function AdvancedAI() {
  const [productId,setProductId] = useState("1");
  const [question,setQuestion] = useState("What is the inventory risk?");
  const [output,setOutput] = useState(null);
  const [error,setError] = useState("");
  const [loading,setLoading] = useState(false);
  async function run(path, body) {
    setLoading(true);setError("");setOutput(null);
    try {
      const response = await fetch(`/api/advanced/${path}`, body ? {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)} : {});
      const result = await response.json();
      if (!response.ok) throw Error(typeof result.detail === "string" ? result.detail : "Request failed");
      setOutput(result);
    } catch(e) {setError(e.message);} finally {setLoading(false);}
  }
  return <section className="rounded-2xl border border-slate-700 bg-[#111c31] p-6 text-slate-100">
    <h3 className="text-2xl font-bold mb-2">Advanced AI Laboratory</h3>
    <p className="text-slate-400 mb-5">Experimental analytics. Recommendations never execute payments.</p>
    <label className="block mb-4">Product ID <input className="ml-3 rounded bg-slate-950 border border-slate-600 p-2" type="number" min="1" value={productId} onChange={e=>setProductId(e.target.value)}/></label>
    <div className="grid gap-3 sm:grid-cols-2">{features.map(([label,path])=><button key={path} disabled={loading} className="rounded-lg bg-blue-600 p-3 text-left hover:bg-blue-500 disabled:opacity-50" onClick={()=>run(path === "metrics" ? "metrics" : `${path}/${productId}`)}>{label}</button>)}</div>
    <div className="mt-6"><label className="block mb-2">Merchant AI Chatbot</label><textarea className="w-full rounded bg-slate-950 border border-slate-600 p-3" maxLength={500} value={question} onChange={e=>setQuestion(e.target.value)}/><button disabled={loading} className="mt-2 rounded bg-cyan-600 px-5 py-3 disabled:opacity-50" onClick={()=>run("chat",{product_id:Number(productId),question})}>Ask AI</button></div>
    {loading && <p className="mt-4">Processing...</p>}{error && <p role="alert" className="mt-4 text-red-300">{error}</p>}
    {output && <pre className="mt-5 overflow-auto rounded-lg bg-slate-950 p-4 text-sm text-emerald-300">{JSON.stringify(output,null,2)}</pre>}
  </section>;
}
