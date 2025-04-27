# Collibra Database Synchronization Schedule Documentation

## Overview

The `get_database_synchronization.ps1` PowerShell script allows you to retrieve and analyze database synchronization schedules from your Collibra environment. This tool helps you understand when database synchronization jobs are scheduled to run, when they last ran, and when they will run next.

## Prerequisites

- PowerShell version 5.1 or higher
- Access to a Collibra environment with proper permissions
- Web browser with developer tools access
- Database synchronization jobs configured in Collibra

## Authentication Requirements

The script requires two key authentication elements:
1. **JSESSIONID** - A session cookie that authenticates your session
2. **CSRF Token** - A security token that prevents cross-site request forgery attacks

Both of these elements must be obtained from your browser while logged into your Collibra instance.

## How to Obtain Authentication Elements

### Getting the CSRF Token

1. Log in to your Collibra instance in a web browser
2. Open the developer tools (F12 or right-click and select "Inspect")
3. Navigate to the "Network" tab
4. In the URL bar of your browser, make a request to the `/auth/sessions/current` endpoint:
   ```
   https://your-instance.collibra.com/rest/2.0/auth/sessions/current?include=csrfToken
   ```
5. In the Network tab, find this request and view the response
6. The response will contain the CSRF token value

Alternatively, you can use the REST API testing tool in Collibra:

1. Navigate to the REST API interface in your Collibra instance
2. Find the GET `/auth/sessions/current` endpoint
3. Add `csrfToken` to the "include" parameter
4. Execute the request
5. The response will contain your CSRF token

### Getting the JSESSIONID

1. While logged into your Collibra instance, open the browser developer tools (F12)
2. Navigate to the "Application" tab
3. In the left sidebar, expand "Storage" and click on "Cookies"
4. Find the cookie named "JSESSIONID" and copy its value

## Script Configuration

Before running the script, you need to update the following variables in the `get_database_synchronization.ps1` file:

```powershell
$collibraUrl = "your-instance.collibra.com" # Replace with your organization address
$sessionId = "your-session-id-here" # Replace with your JSESSIONID cookie value
$csrfToken = "your-csrf-token-here" # Replace with your x-csrf-token value

# Process multiple assets
$assetIds = @(
    "00000000-0000-0000-0000-000000000001", # Replace with your database asset type asset ID
    "00000000-0000-0000-0000-000000000002"  # Replace with another database asset type asset ID
)
```

## How to Find Database Asset IDs

To find the asset IDs of your database assets:

1. Navigate to your database asset in Collibra
2. The asset ID is typically visible in the URL when viewing the asset details
3. The format is typically a UUID: `00000000-0000-0000-0000-000000000000`

## Running the Script

1. Open PowerShell
2. Navigate to the directory containing the script
3. Run the script with:
   ```
   .\get_database_synchronization.ps1
   ```

## Script Output

The script provides two types of output:

1. **Console output**: A formatted table showing:
   - Asset ID
   - Schedule in human-readable format
   - Next run time

2. **CSV file**: A file named `output.csv` in the current directory containing detailed information:
   - ID: The schedule configuration ID
   - AssetId: The Collibra asset ID
   - CronExpression: The raw cron expression
   - Timezone: The timezone of the schedule
   - DayOfWeek: The day of the week when the job runs
   - Hour: The hour when the job runs
   - Frequency: The job frequency (if available)
   - ReadableSchedule: Human-readable schedule description
   - LastRunTimestamp: When the job last ran
   - NextRunTimestamp: The timestamp for the next run
   - NextRunDateTime: Human-readable next run time

## How the Script Works

The script contains two main functions:

1. **Get-CollibraScheduleConfig**: Makes a GraphQL API request to Collibra to retrieve the schedule configuration for a specific asset ID and job group.

2. **Parse-CronConfig**: Parses the cron expression returned by the API into a human-readable format.

For each asset ID in the `$assetIds` array, the script:
- Retrieves the schedule configuration using the GraphQL API
- Parses the cron expression into a human-readable format
- Adds the result to an array
- Displays the results in a table and exports them to a CSV file

## Troubleshooting

### Authentication Issues

- If you receive authentication errors, ensure your JSESSIONID and CSRF token are current
- These tokens expire after some time, so you may need to refresh them
- Make sure you're copying the entire token values without any extra spaces

### No Results Returned

- Verify that the asset IDs are correct
- Ensure the assets have database synchronization jobs configured
- Check that you have sufficient permissions to view the assets

### API Errors

- Check that the Collibra URL is correct
- Ensure your network can reach the Collibra instance
- Verify that the GraphQL API is enabled in your Collibra environment

## Security Considerations

- The script contains authentication tokens that provide access to your Collibra environment
- Do not share the configured script with unauthorized users
- Consider storing credentials securely rather than hardcoding them
- The session tokens expire after some time, providing some security against misuse

## Notes

- Session tokens typically expire after a period of inactivity
- The script focuses on the "INGESTION" job group, but could be modified for other job groups
- The cron expression parsing assumes the Quartz scheduler convention (1-7 for Sunday-Saturday)
