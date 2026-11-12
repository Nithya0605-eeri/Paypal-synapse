# PayPal Synapse

### AI-Powered Autonomous Commerce Digital Twin

**Predict Demand. Simulate Disruptions. Optimize Procurement. Execute Human-Approved Payments.**

Built for the **PayPal AI Hackathon 2026**.

PayPal Synapse is an AI-powered commerce intelligence platform designed to help merchants anticipate inventory shortages, evaluate supply-chain disruptions, optimize procurement decisions, and manage purchasing through human-approved PayPal Sandbox payment workflows.

Instead of reacting to inventory shortages after they occur, Synapse helps merchants make proactive, data-driven decisions.

---

## 1. Problem Statement

Modern merchants face several interconnected challenges:

- Unpredictable customer demand
- Inventory shortages and overstocking
- Supplier delays and supply-chain disruptions
- Inefficient procurement decisions
- Limited visibility into future business risks
- Disconnected inventory planning and payment workflows

Traditional inventory management systems primarily monitor historical and current stock levels.

PayPal Synapse explores a more proactive approach by combining machine learning, probabilistic simulation, optimization, and payment orchestration.

---

## 2. Our Solution

PayPal Synapse acts as a digital twin of merchant commerce operations.

A digital twin is a computational representation of a real-world system that can be used to analyze its behavior and explore alternative scenarios.

The platform connects demand intelligence, inventory risk analysis, supplier decisions, and procurement payments.

### Core Workflow

1. Analyze merchant sales and inventory information.
2. Forecast future product demand.
3. Simulate alternative business scenarios.
4. Identify potential inventory shortages.
5. Evaluate procurement requirements.
6. Generate purchasing recommendations.
7. Require human approval before payment execution.
8. Create a PayPal Sandbox order.
9. Complete the Sandbox checkout and capture workflow.
10. Track the resulting payment status.

The goal is to support merchants throughout the procurement decision lifecycle.

---

## 3. Key Features

### 3.1 AI-Powered Demand Forecasting

The forecasting module analyzes historical sales patterns to estimate future product demand.

Its purpose is to support:

- Inventory planning
- Demand trend analysis
- Shortage anticipation
- Purchasing decisions
- Forecast evaluation

The machine learning implementation is organized into model training, prediction, and backtesting components.

### 3.2 Commerce Digital Twin

The digital twin provides a computational environment for exploring how merchant operations may respond to changing conditions.

Example scenarios include:

- Increased customer demand
- Unexpected demand spikes
- Supplier delays
- Inventory shortages
- Changes in replenishment requirements

These simulations help evaluate possible outcomes before procurement decisions are made.

### 3.3 Probabilistic Simulation

Probabilistic simulation helps represent uncertainty in commerce operations.

Instead of relying exclusively on one expected outcome, merchants can explore multiple potential demand and inventory scenarios.

This supports risk-aware decision-making.

### 3.4 Procurement Optimization

The optimization module supports procurement planning by evaluating purchasing requirements and business constraints.

Its objectives include:

- Reducing avoidable stockouts
- Improving inventory availability
- Supporting cost-aware purchasing
- Evaluating replenishment needs
- Producing actionable procurement recommendations

### 3.5 AI Commerce Decision Support

PayPal Synapse connects forecasting, simulation, and procurement analysis into a unified decision-support workflow.

The platform is designed to assist merchants in understanding why a purchase may be necessary and what risks it may address.

### 3.6 Human-in-the-Loop Approval

Financial decisions require explicit human authorization.

Synapse separates automated recommendations from payment execution.

The workflow includes:

- Purchase proposal generation
- Human approval or rejection
- Approved purchase preparation
- PayPal Sandbox checkout
- Explicit payment confirmation
- Transaction status tracking

AI recommendations do not independently authorize financial transactions.

### 3.7 PayPal Sandbox Integration

The payment module integrates PayPal Sandbox APIs into the procurement workflow.

Supported capabilities include:

- PayPal order creation
- Checkout approval URLs
- Human-confirmed payment capture
- Payment status tracking
- Persistent PayPal order identifiers
- Idempotency support
- Checkout recovery guidance

The Sandbox integration enables testing with simulated transactions rather than live payments.

### 3.8 Interactive Dashboard

The React frontend provides a user interface for exploring commerce intelligence and operational workflows.

The project includes dashboard and advanced analytics components for presenting the platform's capabilities.

---

## 4. System Architecture

PayPal Synapse follows a modular architecture separating the frontend, application backend, intelligence components, persistence layer, and payment integration.

```text
                         MERCHANT
                            |
                            v
                     REACT DASHBOARD
                            |
                            v
                      FASTAPI BACKEND
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
      AI / ML           DIGITAL TWIN      PROCUREMENT
      ENGINE            SIMULATION        WORKFLOW
          |                 |                 |
          v                 v                 v
      DEMAND             SCENARIO          PURCHASE
      FORECAST           ANALYSIS          PROPOSAL
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    HUMAN APPROVAL
                            |
                            v
                    PAYPAL SANDBOX
                            |
                            v
                    PAYMENT CAPTURE
                            |
                            v
                      SQLITE DATABASE
```

The architecture separates predictive intelligence, procurement decision-making, and payment execution.

This separation helps ensure that automated recommendations do not bypass financial authorization requirements.

---

## 5. Technology Stack

### Frontend

- React
- JavaScript
- JSX
- HTML
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- REST APIs
- Pydantic

### Machine Learning and Data Science

- Python
- Pandas
- NumPy
- Scikit-learn
- Demand forecasting
- Feature engineering
- Model evaluation
- Backtesting

### Simulation and Optimization

- Probabilistic simulation
- Scenario analysis
- Inventory risk evaluation
- Procurement optimization

### Database

- SQLite
- SQLAlchemy

### Payment Integration

- PayPal REST APIs
- PayPal Sandbox
- PayPal Orders
- Payment capture
- Idempotency keys

### Development and Testing

- Git
- GitHub
- Visual Studio Code
- Pytest
- Python virtual environments

---

## 6. Machine Learning Pipeline

The machine learning pipeline supports demand prediction and forecast evaluation.

### Stage 1: Data Preparation

Historical sales information is prepared for forecasting.

This may include:

- Date processing
- Data cleaning
- Missing-value handling
- Sales aggregation
- Feature engineering

### Stage 2: Feature Engineering

Features may capture temporal patterns such as:

- Day of the week
- Weekend indicators
- Day of the year
- Historical sales behavior
- Lagged sales information

### Stage 3: Model Training

The training module builds predictive models from historical data.

### Stage 4: Demand Prediction

The prediction module generates estimates of future demand.

### Stage 5: Backtesting

Backtesting evaluates forecasting behavior using historical observations.

A key objective is avoiding data leakage by ensuring that predictions do not use information unavailable at prediction time.

### Stage 6: Procurement Decision Support

Forecast outputs can inform inventory analysis and procurement recommendations.

---

## 7. Digital Twin and Simulation

The digital twin is designed to explore the relationship between demand, inventory availability, and procurement decisions.

### Example Scenario

A merchant expects increased demand for a product.

The simulation workflow can explore:

1. Baseline expected demand.
2. Higher-than-expected demand.
3. Potential supplier disruption.
4. Inventory availability under each scenario.
5. Possible replenishment requirements.

This helps merchants compare potential outcomes rather than relying on a single forecast.

---

## 8. Procurement and Payment Workflow

The procurement workflow connects business intelligence to financial execution.

```text
DEMAND FORECAST
      |
      v
INVENTORY RISK ANALYSIS
      |
      v
PROCUREMENT RECOMMENDATION
      |
      v
PURCHASE APPROVAL REQUEST
      |
      v
HUMAN APPROVAL
      |
      v
PAYPAL ORDER CREATION
      |
      v
PAYPAL SANDBOX CHECKOUT
      |
      v
HUMAN PAYMENT CONFIRMATION
      |
      v
PAYMENT CAPTURE
      |
      v
TRANSACTION STATUS UPDATE
```

### Payment Safety

PayPal Synapse uses a human-in-the-loop model.

A purchase recommendation is not equivalent to payment authorization.

Payment execution requires the appropriate approval state and explicit confirmation.

---

## 9. PayPal Sandbox Integration

PayPal Sandbox provides a test environment for validating payment workflows.

The integration connects approved procurement requests with PayPal order creation and capture.

### Order Creation

After a purchase is approved, the backend can create a PayPal Sandbox order.

The response includes information such as:

- Approval ID
- PayPal order ID
- Order status
- Approval URL
- Purchase amount
- Payment status

### Checkout Approval

The merchant can open the PayPal Sandbox checkout URL and review the purchase.

### Payment Capture

After PayPal checkout approval, the backend provides a capture operation requiring explicit human confirmation.

Example request:

```json
{
  "human_confirmed": true
}
```

### Payment Status

The system exposes a checkout-status endpoint.

Example completed payment state:

```json
{
  "approval_id": 2,
  "checkout_status": "payment_completed",
  "payment_state": "captured",
  "paypal_order_exists": true,
  "request_id_stored": true,
  "recovery_action": "none"
}
```

### Idempotency and Recovery

The payment implementation includes persisted request identifiers to support idempotent order creation.

Checkout recovery logic distinguishes between situations such as:

- Checkout not yet initiated
- Checkout currently processing
- Existing PayPal order
- Completed payment
- Unknown payment outcome requiring reconciliation

This is important because payment requests must not be retried blindly when the outcome is uncertain.

---

## 10. API Documentation

The FastAPI backend provides interactive Swagger documentation.

Start the backend and open:

http://127.0.0.1:8000/docs

### Procurement Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/approvals/{approval_id}/approve` | Approve a purchase |
| POST | `/approvals/{approval_id}/reject` | Reject a purchase |
| POST | `/approvals/{approval_id}/reserve-checkout` | Reserve an approved checkout |
| POST | `/approvals/{approval_id}/checkout` | Create a checkout for an approved purchase |
| GET | `/approvals/{approval_id}/checkout-status` | Read checkout status |
| POST | `/approvals/{approval_id}/capture` | Capture an approved payment |

Some endpoints require a merchant API key.

The key is supplied through the `X-Merchant-API-Key` request header.

Do not expose API keys in public repositories, screenshots, or documentation.

---

## 11. Project Structure

The repository is organized into independent frontend, backend, machine learning, simulation, optimization, and payment modules.

```text
paypal-synapse/
|
|-- backend/
|   |
|   |-- app/
|   |   |
|   |   |-- advanced/
|   |   |   `-- sprint.py
|   |   |
|   |   |-- ml/
|   |   |   |-- predict.py
|   |   |   |-- train_model.py
|   |   |   `-- backtest.py
|   |   |
|   |   |-- optimization/
|   |   |
|   |   |-- payments/
|   |   |   |-- approval_service.py
|   |   |   |-- checkout_service.py
|   |   |   |-- paypal_client.py
|   |   |   `-- README.md
|   |   |
|   |   |-- simulation/
|   |   |
|   |   |-- auth.py
|   |   |-- database.py
|   |   |-- models.py
|   |   |-- seed.py
|   |   `-- main.py
|   |
|   |-- tests/
|   `-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- AdvancedAI.jsx
|   |   `-- SprintLab.jsx
|   |
|   `-- package.json
|
|-- models/
|   `-- backtest_report.json
|
|-- .gitignore
`-- README.md
```

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| Frontend | Interactive merchant dashboard |
| Backend | REST API and application services |
| ML | Demand forecasting and backtesting |
| Simulation | Commerce scenario exploration |
| Optimization | Procurement decision support |
| Advanced | Advanced analytics components |
| Payments | Purchase approval and PayPal integration |
| Database | Persistent application records |
| Tests | Automated backend verification |

---

## 12. Installation and Setup

### Prerequisites

Install:

- Python 3.11 or a compatible version
- Node.js
- npm
- Git

PayPal Sandbox credentials are required for payment integration.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Nithya0605-eeri/Paypal-synapse.git
cd Paypal-synapse
```

### Step 2: Set Up the Backend

```bash
cd backend

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Configure the backend using local environment variables.

The PayPal integration requires Sandbox credentials, including the appropriate client ID and client secret.

The merchant API authentication mechanism also requires its configured API key.

Keep all secrets outside version control.

Do not commit your `.env` file.

### Step 4: Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

### Step 5: Start the Frontend

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Open the local URL displayed by the frontend development server.

### Step 6: Test the Application

Run the backend test suite:

```bash
cd backend

source .venv/bin/activate

python -m pytest tests -q
```

---

## 13. Testing and Validation

Testing is important for both forecasting reliability and payment safety.

The backend uses Pytest for automated testing.

### Verified Test Result

During development, the backend test suite produced:

```text
36 passed, 6 warnings
```

The warnings were associated with deprecated Pandas date-related properties.

They did not prevent the tests from passing.

### Testing Areas

The automated test suite includes coverage related to:

- Forecasting functionality
- Advanced analytics
- Backtesting behavior
- Data leakage prevention
- Backend application behavior
- Payment security

### PayPal Sandbox Validation

A separate manual Sandbox test verified the procurement payment workflow.

The demonstrated sequence included:

1. Preparing an approved purchase.
2. Creating a PayPal Sandbox order.
3. Opening the PayPal checkout URL.
4. Approving the order in the Sandbox.
5. Checking the PayPal order status.
6. Capturing the approved payment.
7. Verifying the completed payment state.

The tested purchase amount was **$390.00 USD**.

The capture endpoint returned:

```json
{
  "approval_id": 2,
  "payment_status": "captured",
  "status": "payment_completed"
}
```

The checkout-status endpoint subsequently confirmed:

```json
{
  "approval_id": 2,
  "checkout_status": "payment_completed",
  "payment_state": "captured",
  "paypal_order_exists": true,
  "request_id_stored": true,
  "recovery_action": "none"
}
```

These results demonstrate a successful Sandbox payment capture workflow.

They do not represent a live financial transaction.

---

## 14. Demonstration Scenario

Consider a merchant whose product demand is expected to increase.

### Stage 1: Forecast

The machine learning engine estimates future product demand.

### Stage 2: Simulate

The digital twin explores alternative demand scenarios and potential disruptions.

### Stage 3: Evaluate

Risk analysis identifies possible inventory shortages.

### Stage 4: Optimize

The procurement engine supports evaluation of replenishment decisions.

### Stage 5: Recommend

The platform generates a purchasing recommendation.

### Stage 6: Approve

A human reviews the proposed purchase and decides whether to authorize it.

### Stage 7: Checkout

The backend creates a PayPal Sandbox order for the approved purchase.

### Stage 8: Capture

After checkout approval, payment capture is performed with explicit human confirmation.

### Stage 9: Verify

The system records and exposes the resulting payment state.

The demonstrated payment workflow reached:

```text
PAYMENT COMPLETED
PAYMENT STATE: CAPTURED
RECOVERY ACTION: NONE
```

---

## 15. Security and Responsible AI

PayPal Synapse is designed around the principle that AI should support financial decisions without independently controlling payment authorization.

### Human Authorization

AI-generated recommendations require human approval before financial execution.

### Credential Protection

Sensitive credentials should be stored using environment variables.

Secrets must not be committed to GitHub.

### Idempotency

Persisted PayPal request identifiers support safer handling of repeated order-creation requests.

### Transaction Recovery

Unknown payment outcomes require reconciliation rather than automatic repeated execution.

### Sandbox Isolation

Payment demonstrations use PayPal Sandbox rather than live payment accounts.

### Decision Transparency

Forecasting and simulation outputs are intended to inform merchant decisions, not replace human judgment.

---

## 16. Innovation and PayPal Relevance

PayPal Synapse explores how payment infrastructure can become part of a broader AI-assisted commerce workflow.

Rather than treating payments as an isolated final transaction, the project connects them to the decisions that precede a purchase.

### Key Innovations

**Predictive Commerce**

Demand forecasting helps anticipate future purchasing requirements.

**Digital Twin Intelligence**

Simulation supports exploration of alternative operational scenarios.

**Risk-Aware Procurement**

Procurement decisions can incorporate demand uncertainty and inventory risk.

**Human-Governed Automation**

AI supports recommendations while humans retain authority over payment execution.

**Integrated PayPal Checkout**

Approved purchasing workflows connect to PayPal Sandbox order creation and capture.

**Payment Reliability**

Idempotency and recovery-state tracking help reduce risks associated with uncertain checkout outcomes.

---

## 17. Future Enhancements

Potential future improvements include:

- Real-time inventory data ingestion
- Additional forecasting models
- Multi-product demand forecasting
- Supplier reliability scoring
- More advanced procurement optimization
- Automated scenario comparisons
- Enhanced visualization of simulation results
- Real-time payment status synchronization
- Improved transaction reconciliation
- Expanded automated testing
- Cloud deployment
- Merchant analytics and reporting
- Advanced AI agent orchestration

These enhancements represent future development opportunities rather than claims of currently verified functionality.

---

## 18. Project Impact

PayPal Synapse demonstrates how AI and payment infrastructure can work together to support better commerce decisions.

The platform explores opportunities to:

- Anticipate inventory shortages
- Improve procurement planning
- Evaluate operational uncertainty
- Reduce manual decision-making effort
- Connect purchasing recommendations to secure payment workflows
- Maintain human control over financial execution

The project combines predictive machine learning, digital twin simulation, procurement intelligence, backend engineering, and PayPal Sandbox integration.

---

## 19. Conclusion

PayPal Synapse presents a vision for more intelligent and proactive commerce operations.

By combining demand forecasting, probabilistic simulation, procurement decision support, and human-approved PayPal payment workflows, the platform connects business intelligence with financial execution.

The future of commerce is not just automated.

**It is predictive, adaptive, and human-governed.**

---

**Built for the PayPal AI Hackathon 2026.**