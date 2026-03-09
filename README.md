# ETL 2
### Parquet to XLSX Pipeline and Dashboard Deployment

Automated pipeline to fetch parquet files (transformed Typeform data) and transform them into a single `.xlsx` file usable for visualization.

## Overview

This project represents the second phase (ETL2) of the performance data workflow. 

1. **ETL1 (Daily at 07:00):** Extracts survey data collected through Typeform and loads it into SharePoint as `.parquet` files.
2. **ETL2 (Daily at 07:15 via GitHub Actions):** This project retrieves the `.parquet` files from SharePoint, transforms and combines them into a single structured Excel dataset, and serves the data to a secured Streamlit dashboard.

The dashboard enables employees to reflect on their performance using aggregated peer and client feedback while ensuring controlled data access.

### Key Objectives
- Fully automated data flow from SharePoint → ETL → Dashboard.
- Secure, authenticated access to sensitive performance data.
- Near real-time insights for internal use.

## Features
- **Automated ETL Pipeline:** Runs daily via GitHub Actions.
- **Data Transformation:** `create_and_upload_combined_df.py` processes multiple `.parquet` files into one large `.xlsx` file.
- **SharePoint Integration:** Managed through `sharepoint_client.py` using the Microsoft Graph API.
- **Secure Dashboard:** Deployed on Streamlit Cloud with personal authentication and scoped data visibility.
- **Modular Utilities:** Reusable helper functions stored in `utils.py`.

## Project Structure
```text
project-root/
│
├── src/
│   └── performance_dashboard/
│       │
│       ├── services/
│       │   ├── create_and_upload_combined_df.py # ETL 2 logic
│       │   └── sharepoint_client.py          # SharePoint integration
│       │
│       └── utils.py                          # General helpers
│
├── tests/                                    # Unit tests
│   └── test_app.py
│
├── .github/
│   └── workflows/                            # GitHub Actions orchestration
│
├── pyproject.toml                            # Dependencies + build config
├── uv.lock                                   # Locked dependency versions
├── runtime.txt                               # Runtime specification
└── README.md
```

# Usage

## Daily automation
The intended production setup runs ETL1 and ETL2 on a daily schedule.

Typical orchestration options:
GitHub Actions
Azure Functions / WebJobs
Cron-based VM job

Currently, GitHub Actions is used. This may change upon further development in the Azure environment.


## Installation

Clone the repository:

```bash
git clone <repo-url>
cd <repo-name>
```

Install dependencies:
```bash
uv sync
```

## Configuration
Create a .env file in the root folder, never commit!
```
TENANT_ID=
CLIENT_ID=
CLIENT_SECRET=
SHAREPOINT_SITE=
```
