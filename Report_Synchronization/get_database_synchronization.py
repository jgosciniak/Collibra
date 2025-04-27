#!/usr/bin/env python3
"""
Collibra Database Synchronization Schedule Retrieval Tool

This script retrieves schedule configuration for database jobs from Collibra using
the GraphQL API and parses cron expressions into human-readable format.

It requires authentication via a JSESSIONID cookie and CSRF token which must be
obtained from a browser session.
"""

import requests
import json
import csv
import datetime
import argparse
from typing import List, Dict, Any, Optional, Union


class CollibraScheduleConfig:
    """Class to interact with Collibra GraphQL API for schedule configuration"""

    def __init__(self, collibra_url: str, session_id: str, csrf_token: str):
        """
        Initialize with authentication details
        
        Args:
            collibra_url: Collibra instance URL (without protocol)
            session_id: JSESSIONID cookie value
            csrf_token: CSRF token value
        """
        self.collibra_url = collibra_url.replace("https://", "").replace("http://", "")
        self.session_id = session_id
        self.csrf_token = csrf_token
        self.session = requests.Session()
        
        # Set up cookies and headers
        self.session.cookies.set("JSESSIONID", session_id, domain=self.collibra_url, path="/")
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "x-csrf-token": csrf_token,
            "accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=UTF-8"
        })

    def get_schedule_config(self, asset_id: str, job_group: str = "INGESTION") -> Dict[str, Any]:
        """
        Retrieve schedule configuration for a database asset
        
        Args:
            asset_id: Collibra asset ID
            job_group: Job group name (default: INGESTION)
            
        Returns:
            Dictionary containing the API response
        """
        # Prepare the asset ID (add Asset: prefix if not present)
        original_asset_id = asset_id
        if not asset_id.startswith("Asset:"):
            asset_id = f"Asset:{asset_id}"
        
        # GraphQL query
        graphql_query = """
        query ScheduleConfig($assetId: ID!, $jobGroup: DatabaseJobGroups!) {
          api {
            databaseScheduleConfiguration(assetId: $assetId, jobGroupName: $jobGroup) {
              id
              cronExpression
              cronJson
              cronTimeZone
              lastRunTimeStamp
              nextRunDateLongValue
            }
          }
        }
        """
        
        # Build the request body
        body = {
            "query": graphql_query,
            "variables": {
                "assetId": asset_id,
                "jobGroup": job_group
            }
        }
        
        try:
            # Make the request
            response = self.session.post(
                f"https://{self.collibra_url}/graphql",
                json=body
            )
            response.raise_for_status()
            
            # Parse response
            json_response = response.json()
            
            # Add assetId to the response for tracking
            result = {
                "data": json_response.get("data", {}),
                "assetId": original_asset_id
            }
            
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"Error querying Collibra API: {e}")
            return None


class CronParser:
    """Class to parse cron expressions into human-readable format"""
    
    @staticmethod
    def parse_cron_config(json_string: str) -> Dict[str, Any]:
        """
        Parse cron configuration from JSON string
        
        Args:
            json_string: JSON string containing cron configuration
            
        Returns:
            Dictionary with parsed cron information
        """
        try:
            json_object = json.loads(json_string) if isinstance(json_string, str) else json_string
            config = json_object.get("data", {}).get("api", {}).get("databaseScheduleConfiguration", {})
            asset_id = json_object.get("assetId", "")
            
            if not config:
                print("Database schedule configuration not found in JSON")
                return None
            
            # Extract cron information
            cron_expression = config.get("cronExpression", "")
            cron_time_zone = config.get("cronTimeZone", "")
            
            # Parse the nested cronJson string
            cron_json = None
            try:
                cron_json_str = config.get("cronJson", "")
                if isinstance(cron_json_str, str):
                    cron_json_str = cron_json_str.replace('\\"', '"').strip('"')
                    cron_json = json.loads(cron_json_str)
            except json.JSONDecodeError as e:
                print(f"Could not parse cronJson: {e}")
            
            # Parse the cron expression components
            readable_schedule = "Invalid cron format"
            day_name = "Unknown"
            
            cron_parts = cron_expression.split()
            if len(cron_parts) >= 6:
                seconds = cron_parts[0]
                minutes = cron_parts[1]
                hours = cron_parts[2]
                day_of_month = cron_parts[3]
                month = cron_parts[4]
                day_of_week = cron_parts[5]
                
                # Get the day of week name (using Quartz scheduler convention)
                days_of_week = ["", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                try:
                    day_index = int(day_of_week)
                    if 1 <= day_index <= 7:
                        day_name = days_of_week[day_index]
                    else:
                        day_name = f"Unknown day ({day_of_week})"
                except ValueError:
                    day_name = f"Unknown day ({day_of_week})"
                
                # Create a human-readable schedule
                readable_time = f"{hours}:00:00"
                readable_schedule = f"Every {day_name} at {readable_time} {cron_time_zone}"
            
            # Convert NextRunDateLongValue to datetime
            next_run_date_time = None
            if config.get("nextRunDateLongValue"):
                try:
                    next_run_utc = datetime.datetime.utcfromtimestamp(config.get("nextRunDateLongValue") / 1000)
                    next_run_date_time = next_run_utc.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
                except (ValueError, TypeError) as e:
                    print(f"Could not convert next run timestamp: {e}")
            
            # Create result object with assetId
            result = {
                "Id": config.get("id", ""),
                "AssetId": asset_id,
                "CronExpression": cron_expression,
                "Timezone": cron_time_zone,
                "DayOfWeek": day_name,
                "Hour": hours if 'hours' in locals() else "",
                "Frequency": cron_json.get("preset") if cron_json and "preset" in cron_json else "unknown",
                "ReadableSchedule": readable_schedule,
                "LastRunTimestamp": config.get("lastRunTimeStamp", ""),
                "NextRunTimestamp": config.get("nextRunDateLongValue", ""),
                "NextRunDateTime": next_run_date_time
            }
            
            return result
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
        except Exception as e:
            print(f"Error parsing cron config: {e}")
            return None


def main():
    """Main function to run the script"""
    
    parser = argparse.ArgumentParser(description="Retrieve database synchronization schedules from Collibra")
    parser.add_argument("--url", required=True, help="Collibra URL (e.g., your-instance.collibra.com)")
    parser.add_argument("--session-id", required=True, help="JSESSIONID cookie value")
    parser.add_argument("--csrf-token", required=True, help="CSRF token value")
    parser.add_argument("--asset-ids", required=True, nargs='+', help="One or more asset IDs to query")
    parser.add_argument("--output", default="output.csv", help="Output CSV file name (default: output.csv)")
    parser.add_argument("--job-group", default="INGESTION", help="Job group name (default: INGESTION)")
    
    args = parser.parse_args()
    
    # Initialize the Collibra client
    client = CollibraScheduleConfig(args.url, args.session_id, args.csrf_token)
    
    # Process each asset ID
    results = []
    for asset_id in args.asset_ids:
        print(f"Processing asset ID: {asset_id}")
        json_response = client.get_schedule_config(asset_id, args.job_group)
        if json_response:
            parsed = CronParser.parse_cron_config(json_response)
            if parsed:
                results.append(parsed)
                print(f"  Schedule: {parsed['ReadableSchedule']}")
                print(f"  Next run: {parsed['NextRunDateTime']}")
                print("")
    
    # Write results to CSV
    if results:
        # Get all fields from the first result
        fieldnames = results[0].keys()
        
        with open(args.output, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        
        print(f"Results written to {args.output}")
    else:
        print("No results to output")


if __name__ == "__main__":
    main()
