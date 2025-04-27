# Python Script Usage Guide

I've created a Python version of the PowerShell script that retrieves database synchronization schedules from Collibra. Here's how to use it:

## Features

The Python script maintains all functionality from the original PowerShell script:
- Makes GraphQL API requests to Collibra to retrieve schedule configuration
- Parses cron expressions into human-readable format
- Supports multiple database assets
- Outputs results to both console and CSV

## Requirements

- Python 3.6+
- `requests` library (install via `pip install requests`)

## Key Improvements

The Python version includes several improvements:
1. **Command-line arguments** for easier configuration without editing the script
2. **Better error handling** with more detailed error messages
3. **More extensive type hints** for better code quality
4. **Modular code structure** with separate classes for API interaction and cron parsing
5. **Proper documentation** with docstrings and comments

## Usage

```bash
python get_database_synchronization.py --url your-instance.collibra.com \
                                      --session-id your-session-id \
                                      --csrf-token your-csrf-token \
                                      --asset-ids id1 id2 id3 \
                                      --output results.csv
```

### Required Arguments

- `--url`: Your Collibra instance URL (e.g., "your-instance.collibra.com")
- `--session-id`: The JSESSIONID cookie value (see the Database_Synchronization_Guide.md for instructions)
- `--csrf-token`: The CSRF token value (see the Database_Synchronization_Guide.md for instructions)
- `--asset-ids`: One or more database asset IDs to query (space-separated)

### Optional Arguments

- `--output`: Name of the output CSV file (default: output.csv)
- `--job-group`: Job group name to query (default: INGESTION)

## Example

```bash
python get_database_synchronization.py \
    --url your-instance.collibra.com \
    --session-id a1b2c3d4-5678-90ab-cdef-ghijklmnopqr \
    --csrf-token abcdef123456789 \
    --asset-ids 00000000-0000-0000-0000-000000000001 00000000-0000-0000-0000-000000000002 \
    --output database_schedules.csv
```

## Output

The script will display the schedule and next run time for each asset in the console and write detailed information to the CSV file:
- Id: The schedule configuration ID
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

## Using with API Tool

If you're using the Collibra REST API tool to get your authentication tokens:

1. Get the CSRF token as shown in the documentation (using the `/auth/sessions/current?include=csrfToken` endpoint)
2. Get the JSESSIONID from your browser's developer tools (Application tab → Cookies)
3. Run the script with those values

## Security Notes

The script requires authentication tokens that provide access to your Collibra environment. Consider:
- Not hardcoding credentials in the script
- Using environment variables to pass sensitive information
- Not sharing the configured script with unauthorized users
