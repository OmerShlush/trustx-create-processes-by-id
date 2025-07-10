# Environment Configuration

This project requires certain environment variables to function properly. These variables should be stored securely in a `.env` file or set as system environment variables.

## Required Environment Variables

| Variable Name   | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `BASE_URL`       | The base URL of the API endpoint you are connecting to. Example: `https://TENANT.env.trustx.com` |
| `API_KEY`        | Your private API key used for authentication. **Do not share or commit this value.** |
| `IDS`            | A comma-separated list of numeric IDs to process. Example: `12345678,87654321` |
| `PD_NAME`        | Name of the process definition. |
| `PD_VER`         | Version of the process. Example: `10` |
| `COUNTRY_CODE`   | Two-letter ISO country code. Example: `IL` |

---

## How to Set Environment Variables

### Option 1: Using a `.env` File (Recommended for Local Development)

Create a `.env` file in the root directory of your project with the following content:

```env
BASE_URL=https://TENANT.env.trustx.com
API_KEY=your-secret-api-key
IDS=12345678,87654321
PD_NAME=your_process_name
PD_VER=10
COUNTRY_CODE=IL
```

### Option 2: Using a system environment variables

You can also export these variables directly in your shell:

```Linux/MacOS:
export BASE_URL=https://TENANT.env.trustx.com
export API_KEY=your-secret-api-key
export IDS=12345678,87654321
export PD_NAME=your_process_name
export PD_VER=10
export COUNTRY_CODE=IL
```

```Windows (CMD):
set BASE_URL=https://TENANT.env.trustx.com
set API_KEY=your-secret-api-key
set IDS=12345678,87654321
set PD_NAME=your_process_name
set PD_VER=10
set COUNTRY_CODE=IL
```