# EcoSphere - Enterprise ESG Management Platform

EcoSphere is an Environmental, Social, and Governance (ESG) Management platform designed to replace manual spreadsheets by integrating sustainability data directly into daily corporate operations[cite: 1]. The system automates carbon tracking, monitors governance compliance, and structures data ready for employee gamification[cite: 1].

## 🚀 Features Implemented

### 1. Backend Engine & Data Models (Odoo Framework)
*   **`esg.emission.factor`**: Master database storing carbon values per activity unit[cite: 1].
*   **`esg.carbon.transaction`**: Automated transactional engine[cite: 1]. Uses Python (`@api.depends`) to instantly calculate total carbon footprints (`activity_amount` × `carbon_value`) without manual data entry[cite: 1].
*   **`esg.compliance.issue`**: Governance tracking system managing corporate compliance, resolving violations, and assigning owners to active due dates[cite: 1].

### 2. User Interface & Security
*   **Dynamic Odoo Views**: Complete list (tree) and form views designed for clear data entry and structural tracking[cite: 1].
*   **Unified Access Controls**: Configured `ir.model.access.csv` giving standard base users secure read, write, and create permissions across the network.

### 3. High-Fidelity Interactive Dashboard
*   A clean-tech dark-mode executive dashboard built to present high-level aggregated data.
*   Includes modular KPI cards tracking real-time carbon emissions, CSR status, active challenges, and overall compliance[cite: 1].

---

## 🛠️ Installation & Setup Instruction

### Prerequisites
*   Odoo 18.0 or compatible local environment.
*   PostgreSQL database backend.

### Module Installation Steps
1.  Clone this repository or copy the `ecosphere_esg` folder directly into your Odoo `addons` path.
2.  Restart your local Odoo server instance.
3.  Log into the Odoo web portal, navigate to **Settings**, and enable **Developer Mode**.
4.  Go to the **Apps** dashboard, click **Update Apps List** in the top menu bar, and confirm.
5.  Search for `EcoSphere ESG`, click **Install**, and the application will dynamically load into the root application switcher menu[cite: 1].
