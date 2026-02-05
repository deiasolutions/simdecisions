# CapMetro Work Summary - Dave Eichler
## Operational Analyst III

---

## 1. Major Projects

### 1.1 PO Open Line Items Tool
- **Purpose**: Enable Requesters and Procurement Buyers to review ~4,000 open PO lines from Oracle and mark them for closure
- **Tech Stack**: SharePoint Lists, Access Database, Power BI dashboards, Oracle integration
- **Status Flow**: NULL → Reviewed → OK to Close → Procurement Reviewed → Closed in Oracle → ABSENT (closed)
- **Accomplishments**:
  - Built SharePoint-based review tool with monthly/weekly data refresh cycles
  - Created Power BI dashboard tracking status volumes, aging, reviewer activity
  - Developed data flow: Oracle Report → Access DB processing → SharePoint List → Power BI
  - Completed major PO review push: 105 POs reviewed, 85 approved for closure
  - Authored After Action Review and Activity Reports
  - Fixed automation issues and circular reference problems in Access/SharePoint integration

### 1.2 Strategic Plan 2030 Reporting Framework
- **Purpose**: Create implementation framework for SP2030 metrics reporting aligned to Critical Results
- **5 Workstreams**:
  1. Critical Results Reporting
  2. Action Tracking
  3. Metrics Onboarding
  4. Target Setting Process
  5. Non-DMA Data Roadmap
- **Deliverables**:
  - Dashboard Outline document
  - KPI scorecards with alert rules and performance thresholds
  - Critical Results Dashboard mockups (v2)
  - Project tracker (v1.11)
  - Implementation framework tied to 4 goal areas:
    - Customer → Reliable & Secure Service
    - Ridership
    - Fiscal Responsibility
    - Regional Significance

### 1.3 Bus Stop Asset Tracking Project
- **Purpose**: Bus stop lifecycle management and data accuracy
- **Key Elements**:
  - Hexagon confirmed as primary data source
  - FME used as data aggregator
  - Field audits capturing: Stop ID, location, amenities, ADA accessibility, ridership, maintenance, safety
  - Pilot: 100 stops with results review
  - Coordination with Dave Kubicek (FTA requirements)
  - Survey results analysis and reporting

### 1.4 Oracle Integration Projects
- **Sub-account and service location field changes** - Oracle development requiring testing/training/production rollout
- **Oracle import exception handling** - Built Python tools to parse rejection reports, extract interface keys, identify pattern matches
- **Requisition processing** - Tracked header, line, and distribution exceptions

---

## 2. Technical Skills Applied

### 2.1 Power BI
- Connected to multiple data sources: Snowflake (DWBI_PROD), SharePoint Lists, Access databases
- Built dashboards for:
  - Safety metrics (VW_CM_SAFETY_DASHBOARD - 249 visuals)
  - Ridership tracking (VW_DWH_FACT_STOPS_AGG)
  - Finance/expenses
  - Service operations (Fixed-Route, Rail, Access, Pickup)
- Created documentation: 95 report pages, 936 visuals, 68 tables mapped
- Power Query M transformations for status codes, date conversions, sorting

### 2.2 Snowflake
- Connected via SnowflakeExplorer class with SSO authentication
- Accessed DWBI_PROD database and schemas
- Used account: capmetro-dwbi
- Explored table structures and built queries

### 2.3 SharePoint/Access Integration
- Built linked tables between Access and SharePoint
- Developed SQL update queries for status management
- Created Power Automate flows for bulk data operations
- Handled multi-user concurrency and list size limitations (5000+ items)

### 2.4 Python Development
- Created Oracle import rejection analyzers (CSV output)
- Built Snowflake connection managers
- Developed batch Access database processors (tbl_history extraction)
- Data frame operations with column rationalization (union approach)

---

## 3. Organizational Context

### 3.1 Team Structure
- **Reports to**: Janene Niblock (Supervisor)
- **VP**: Ashley
- **Collaborators**: Mohamed (Procurement), Kevin (Finance), Lakshmi, Sharmila, Jess
- **Department**: OSP Team (Organizational Strategy & Performance)

### 3.2 Key Meetings/Activities
- Monthly/weekly PO review cycles with Procurement
- SP2030 Reporting Framework planning meetings
- Bus Stop project coordination with cross-functional stakeholders
- One-on-ones covering PMP process pilot, compliance training, project status

### 3.3 Professional Development
- PMP training application (demonstrating project management experience)
- Business Analysis training (BABOK, PMBOK standards)
- EPPM coordination requirements

---

## 4. Process Documentation Created

### 4.1 PO Line Items Process Flow
1. Oracle monthly report generated
2. Data merged with SharePoint tracking list
3. Requesters review items (Days 1-15)
4. Items marked "To Close" move to Procurement Inbox
5. Procurement reviews/closes in Oracle (Days 16-30)
6. Next month: items "Closed in Oracle" should drop off Oracle report
7. QA Exception flagging for items that reappear

### 4.2 Metrics Onboarding Tasks (w3.x series)
- w3.5: Reliability/security perception metrics
- w3.6: Security incident rates
- w3.7: Transit ridership per capita
- w3.8: Cost per passenger trip
- w3.9: Reserve funds vs designations
- w3.10: NPS metrics
- w3.11: Community perception & awareness

### 4.3 Target Setting Process (w4.x series)
- Baseline measurements establishment
- Annual review/adjustment process
- Peer practices research
- Methodology documentation
- FY2027 target-setting implementation

---

## 5. Current/Ongoing Challenges

### 5.1 AI Adoption Friction
- Tension between rapid AI implementation vision vs. organizational caution
- VP warning about appearing dismissive of supervisor's decisions
- Focus redirected to foundational project work before advanced technology

### 5.2 Technical Issues Resolved
- SharePoint circular reference errors in Access
- Oracle import exception patterns
- Power BI axis sorting and theme configuration
- Data ingestion workflow dependencies

### 5.3 End-of-Year Processes
- Compressed timelines (~3 weeks)
- Finance/AP invoice processing coordination
- PO line replacement timing

---

## 6. Dashboard/Report Inventory

| Report Area | Key Views/Tables |
|-------------|-----------------|
| Safety | VW_CM_SAFETY_DASHBOARD |
| Ridership | VW_DWH_FACT_STOPS_AGG |
| Date Dimensions | DWH_DIM_DATE |
| Finance | Expenses, Revenue views |
| Operations | OTP, Fixed-Route, Rail, Access, Pickup |
| PO Management | SharePoint-based tracking with history |

---

## 7. Performance Goals (FY Structure)

| Goal Area | Weight | Focus |
|-----------|--------|-------|
| Project Delivery | 35% | Tool optimization, SP2030 framework, dashboards |
| BI Support Quality | 35% | Timely deliverables, templates, strategic alignment |
| Skills Enhancement | 30% | Business Analysis training, methodology application |

---

*Document generated from conversation history search - January 2026*
