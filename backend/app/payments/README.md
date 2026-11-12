PayPal Synapse

AI-Powered Autonomous Commerce Digital Twin

Predict demand. Simulate disruptions. Optimize procurement. Execute human-approved payments.

PayPal Synapse is an AI-powered commerce intelligence platform designed to help merchants anticipate inventory shortages, evaluate supplier decisions, and manage procurement through intelligent AI agents and secure PayPal Sandbox payment workflows.

Instead of reacting to inventory shortages after they occur, Synapse helps merchants make proactive, data-driven purchasing decisions.

Built for the PayPal AI Hackathon 2026.

⸻

1. The Problem

Modern merchants face several interconnected challenges:

* Unpredictable customer demand
* Inventory shortages and excess stock
* Supplier delays and disruptions
* Inefficient procurement decisions
* Limited visibility into future inventory risks
* Manual purchasing and payment workflows

Traditional inventory systems primarily track what has already happened.

Merchants need systems that can predict what might happen next, simulate potential outcomes, and recommend intelligent actions before problems occur.

2. Our Solution

PayPal Synapse introduces an AI-powered autonomous commerce digital twin.

The platform combines machine learning, probabilistic simulations, supplier optimization, explainable AI, and agent-based orchestration to support intelligent procurement.

The system follows a decision-making pipeline:

Monitor → Forecast → Simulate → Evaluate Risk → Optimize → Recommend → Human Approval → PayPal Checkout → Payment Capture

AI handles analysis and recommendations, while merchants retain control over purchasing and payment authorization.

3. Key Features

AI Demand Forecasting

Synapse uses machine learning to estimate future product demand based on historical sales and time-dependent features.

Capabilities include:

* Product-level demand forecasting
* Historical sales analysis
* Calendar-based feature engineering
* Inventory shortage prediction
* Forecast-driven procurement recommendations

Commerce Digital Twin

The digital twin provides a simulated representation of merchant inventory and purchasing conditions.

Merchants can explore potential outcomes before making real procurement decisions.

Monte Carlo Simulation

Probabilistic simulations help evaluate uncertainty in future demand.

This allows merchants to understand potential inventory risks rather than relying exclusively on single-point predictions.

Supplier Comparison and Optimization

Synapse evaluates procurement alternatives and helps identify suitable purchasing decisions.

The optimization workflow connects inventory requirements with supplier recommendations.

Multi-Agent Commerce Orchestration

AI-driven workflows coordinate several decision-making functions:

* Demand analysis
* Inventory risk evaluation
* Supplier comparison
* Procurement optimization
* Purchase recommendations

The goal is to transform individual AI predictions into actionable commerce decisions.

Explainable AI

Synapse includes explanation endpoints that help users understand model predictions, inventory risks, and agent recommendations.

Advanced AI Capabilities

The platform includes backend capabilities for:

* Monte Carlo simulations
* Risk analysis
* Graph-based analysis
* AI explanations
* Agent explanations
* Conversational AI interactions
* Model evaluation metrics

Backtesting and Evaluation

Historical backtesting supports the evaluation of forecasting behavior and helps assess model performance on past data.

Human-in-the-Loop Procurement

Synapse is designed around responsible automation.

AI agents can generate recommendations, but purchasing decisions require explicit human approval.

PayPal Sandbox Integration

The platform integrates PayPal Sandbox APIs to support a controlled procurement payment workflow.

Implemented capabilities include:

* PayPal Sandbox authentication
* Purchase approval and rejection
* Procurement checkout preparation
* PayPal order creation
* Checkout status tracking
* Human-confirmed payment capture
* Payment outcome tracking
* Idempotency support
* Checkout recovery guidance

⸻

4. System Architecture

                  MERCHANT
                     |
                     v
              REACT DASHBOARD
                     |
                     v
               FASTAPI BACKEND
                     |
        +------------+------------+
        |            |            |
        v            v            v
   AI / ML       DIGITAL TWIN   PROCUREMENT
   ENGINE        SIMULATION     ENGINE
        |            |            |
        +------------+------------+
                     |
                     v
              AI AGENT WORKFLOW
                     |
                     v
             SUPPLIER OPTIMIZATION
                     |
                     v
              PURCHASE PROPOSAL
                     |
                     v
               HUMAN APPROVAL
                     |
                     v
              PAYPAL SANDBOX
                     |
                     v
             ORDER + CHECKOUT
                     |
                     v
              PAYMENT CAPTURE
                     |
                     v
                SQLITE DATABASE

The architecture separates predictive intelligence, procurement decision-making, and payment execution.

This separation helps keep automated recommendations independent from financial authorization.

⸻

5. Technology Stack

Layer	Technologies
Frontend	React, JavaScript, JSX
Backend	Python, FastAPI
API Documentation	OpenAPI, Swagger UI
Machine Learning	Python, pandas, scikit-learn
Simulations	Monte Carlo methods
Database	SQLite
ORM	SQLAlchemy
Payments	PayPal REST APIs, PayPal Sandbox
Authentication	Merchant API key authentication
Testing	pytest
Version Control	Git, GitHub

⸻

6. Machine Learning Pipeline

The forecasting workflow follows these stages:

Step 1 — Data Preparation

Historical sales records are prepared for model training.

Step 2 — Feature Engineering

Time-dependent features are generated to capture demand patterns.

Step 3 — Model Training

Machine learning models learn relationships between historical observations and future demand.

Step 4 — Demand Prediction

Trained models generate product-level demand forecasts.

Step 5 — Simulation

Probabilistic simulations explore potential variations in future outcomes.

Step 6 — Optimization

Forecasts and inventory conditions inform procurement recommendations.

Step 7 — Evaluation

Backtesting helps assess model behavior on historical observations.

⸻

7. PayPal Integration

PayPal Synapse connects AI-driven procurement recommendations with PayPal Sandbox checkout.

Payment Workflow

1. The AI workflow identifies a procurement opportunity.
2. The system generates a purchase recommendation.
3. The merchant reviews the proposed purchase.
4. The merchant approves or rejects the request.
5. Synapse prepares the approved checkout.
6. A PayPal Sandbox order is created.
7. The merchant completes the PayPal approval flow.
8. The backend captures the approved payment after explicit confirmation.
9. The payment result is recorded and made available through the checkout status API.

Demonstrated Sandbox Transaction

A PayPal Sandbox procurement transaction was successfully tested.

Field	Result
Environment	PayPal Sandbox
Approval ID	2
Transaction Amount	$390.00 USD
PayPal Order Status	APPROVED
Capture Status	Captured
Application Status	payment_completed
HTTP Response	200

This demonstrates an end-to-end integration from an approved procurement record to a successfully captured PayPal Sandbox payment.

Note: PayPal Sandbox transactions are simulated and do not represent real-money transfers.

Payment Safety

The payment workflow includes:

* Explicit human approval
* Merchant API key protection
* Server-side payment execution
* Persisted PayPal request identifiers
* Duplicate checkout prevention
* Payment status verification
* Recovery handling for uncertain checkout outcomes

The system is designed to avoid blindly repeating payment operations when their outcome is unknown.

⸻

8. API Endpoints

FastAPI automatically generates interactive API documentation.

After starting the backend, visit:

http://127.0.0.1:8000/docs

Core Commerce APIs

Method	Endpoint	Description
GET	/health	Backend health check
GET	/products	Retrieve products
GET	/forecast/{product_id}	Demand forecasting
GET	/simulate/{product_id}	Product demand simulation
GET	/optimize/{product_id}	Procurement optimization
GET	/suppliers/compare/{product_id}	Supplier comparison
GET	/agents/run/{product_id}	Commerce agent orchestration

Advanced AI APIs

Method	Endpoint	Description
GET	/advanced/monte-carlo/{product_id}	Monte Carlo analysis
GET	/advanced/explain/{product_id}	Prediction explanations
GET	/advanced/graph/{product_id}	Graph analysis
GET	/advanced/risk/{product_id}	Risk analysis
GET	/advanced/metrics	Model metrics
GET	/advanced/agent-explain/{product_id}	Agent explanations
POST	/advanced/chat	AI chat

Procurement and Payment APIs

Method	Endpoint	Description
POST	/approvals/{approval_id}/approve	Approve procurement
POST	/approvals/{approval_id}/reject	Reject procurement
POST	/approvals/{approval_id}/reserve-checkout	Reserve checkout
POST	/approvals/{approval_id}/checkout	Create PayPal checkout
GET	/approvals/{approval_id}/checkout-status	Retrieve checkout status
POST	/approvals/{approval_id}/capture	Capture approved payment

Hackathon Demonstration APIs

Method	Endpoint	Description
GET	/sprint/scenario/{product_id}	Scenario analysis
GET	/sprint/trace/{product_id}	Agent execution trace
GET	/sprint/checkout-audit/{approval_id}	Checkout audit
GET	/sprint/backtest-summary	Backtesting summary
GET	/sprint/copilot/{product_id}	AI copilot

⸻

9. Installation and Setup

Prerequisites

Install:

* Python 3.11 or later
* Node.js and npm
* Git
* PayPal Sandbox developer credentials

Clone the Repository

git clone https://github.com/Nithya0605-eeri/Paypal-Synapse.git
cd Paypal-Synapse

Backend Setup

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Environment Configuration

Configure the required environment variables locally.

Example:

PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
MERCHANT_API_KEY=your_local_merchant_api_key

Use the environment variable names expected by the backend configuration.

Never commit actual credentials, API keys, or secrets to GitHub.

Start the Backend

uvicorn app.main:app --reload --port 8000

Backend health endpoint:

http://127.0.0.1:8000/health

Interactive API documentation:

http://127.0.0.1:8000/docs

Frontend Setup

Open a second terminal:

cd frontend
npm install
npm run dev

Open the local URL displayed by the frontend development server.

⸻

10. Testing and Validation

The backend uses pytest for automated testing.

Run:

cd backend
source .venv/bin/activate
python -m pytest tests -q

Latest Recorded Test Results

Metric	Result
Passing Tests	36
Failing Tests	0
Warnings	6
Test Framework	pytest

The six recorded warnings concern deprecated pandas date/time attributes.

The passing test suite validates implemented backend functionality, including forecasting-related features, backtesting, and payment security behavior.

A separate PayPal Sandbox checkout and capture flow was also manually verified.

⸻

11. Project Structure

paypal-synapse/
|
|-- backend/
|   |-- app/
|   |   |-- advanced/
|   |   |-- ml/
|   |   |   |-- predict.py
|   |   |   |-- train_model.py
|   |   |   `-- backtest.py
|   |   |-- optimization/
|   |   |-- payments/
|   |   |   |-- approval_service.py
|   |   |   |-- checkout_service.py
|   |   |   `-- paypal_client.py
|   |   |-- simulation/
|   |   |-- auth.py
|   |   |-- database.py
|   |   |-- models.py
|   |   |-- seed.py
|   |   `-- main.py
|   |-- tests/
|   `-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- AdvancedAI.jsx
|   |   `-- SprintLab.jsx
|   `-- package.json
|
|-- models/
|   `-- backtest_report.json
|
|-- .gitignore
`-- README.md

⸻

12. Demonstration Scenario

Consider a merchant whose product demand is expected to increase.

Stage 1: Forecast

The forecasting engine estimates future demand.

Stage 2: Simulate

The digital twin explores alternative demand scenarios and potential disruptions.

Stage 3: Evaluate

Risk analysis identifies possible inventory shortages.

Stage 4: Optimize

The procurement engine evaluates supplier options and purchasing requirements.

Stage 5: Recommend

AI agents generate a procurement recommendation.

Stage 6: Approve

The merchant reviews and explicitly authorizes the proposed purchase.

Stage 7: Pay

Synapse creates a PayPal Sandbox checkout for the approved amount.

Stage 8: Verify

After buyer approval and authorized capture, the application records the payment outcome.

This scenario demonstrates how predictive AI can connect directly to an actionable commerce workflow while preserving human financial control.

⸻

13. What Makes Synapse Different?

From Reactive to Predictive Commerce

Rather than simply reporting inventory levels, Synapse forecasts potential shortages.

From Predictions to Decisions

Machine learning results are connected to supplier evaluation and procurement optimization.

From Isolated Models to Coordinated Agents

AI workflows bring forecasting, simulation, risk analysis, and purchasing recommendations together.

From Recommendations to Payments

PayPal Sandbox integration demonstrates how an approved procurement recommendation can become a payment workflow.

Human Control Over Financial Actions

The platform separates AI decision support from final purchase authorization.

Transparent and Testable Architecture

Explainability endpoints, backtesting, checkout status tracking, and automated tests make system behavior easier to inspect.

⸻

14. Future Improvements

Potential future extensions include:

* Real-time merchant inventory integrations
* Multi-merchant commerce support
* Advanced time-series forecasting models
* Dynamic supplier reliability scoring
* Reinforcement learning for procurement policies
* Automated anomaly detection
* Real-time payment event synchronization
* Cloud deployment and monitoring
* Production-grade authentication and authorization
* Expanded observability and model drift monitoring

⸻

15. Responsible AI and Security

PayPal Synapse is a prototype designed to demonstrate AI-assisted commerce.

Its guiding principles include:

* Human oversight of purchasing decisions
* Explicit payment confirmation
* Protection of credentials and API keys
* Separation of recommendations from financial execution
* Traceability of procurement actions
* Clear reporting of payment outcomes
* Safe handling of uncertain payment states

The application currently demonstrates payment integration through PayPal Sandbox and is not presented as a production-certified financial platform.

⸻

16. Hackathon Submission

Project: PayPal Synapse

Event: PayPal AI Hackathon 2026

Category: AI-Powered Commerce and Intelligent Automation

Core Technologies: Machine Learning, Agentic AI, Digital Twins, Probabilistic Simulation, FastAPI, React, and PayPal Sandbox

Project Objective: Build an intelligent commerce platform that predicts inventory needs, supports optimized procurement decisions, and connects human-approved purchasing workflows to PayPal.

⸻

17. Conclusion

PayPal Synapse demonstrates a vision for the future of intelligent commerce.

By combining predictive machine learning, probabilistic simulation, AI agent orchestration, supplier optimization, and PayPal payment infrastructure, the platform connects business intelligence with practical procurement execution.

The future of commerce is not just automated. It is predictive, intelligent, explainable, and human-controlled.

⸻

Built for the PayPal AI Hackathon 2026.