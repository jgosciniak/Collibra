 function Get-CollibraScheduleConfig {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$CollibraUrl,
        
        [Parameter(Mandatory = $true)]
        [string]$AssetId,
        
        [Parameter(Mandatory = $true)]
        [string]$JobGroup,
        
        [Parameter(Mandatory = $true)]
        [string]$SessionId,
        
        [Parameter(Mandatory = $true)]
        [string]$CsrfToken,
        
        [Parameter(Mandatory = $false)]
        [switch]$ParseResult
    )
    
    # Create a session with just the required cookie
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    
    # Ensure the URL doesn't have protocol prefix
    $baseUrl = $CollibraUrl -replace "^https?://", ""
    
    # Add the session cookie
    $session.Cookies.Add((New-Object System.Net.Cookie("JSESSIONID", $SessionId, "/", $baseUrl)))
    
    # Prepare the asset ID (add Asset: prefix if not present)
    $originalAssetId = $AssetId
    if (-not $AssetId.StartsWith("Asset:")) {
        $AssetId = "Asset:$AssetId"
    }
    
    # GraphQL query
    $graphQLQuery = @"
query ScheduleConfig(`$assetId: ID!, `$jobGroup: DatabaseJobGroups!) {
  api {
    databaseScheduleConfiguration(assetId: `$assetId, jobGroupName: `$jobGroup) {
      id
      cronExpression
      cronJson
      cronTimeZone
      lastRunTimeStamp
      nextRunDateLongValue
    }
  }
}
"@
    
    # Build the request body
    $body = @{
        query = $graphQLQuery
        variables = @{
            assetId = $AssetId
            jobGroup = $JobGroup
        }
    } | ConvertTo-Json
    
    # Minimal required headers
    $headers = @{
        "x-csrf-token" = $CsrfToken
        "accept" = "application/json, text/plain, */*"
    }
    
    try {
        # Make the request
        $response = Invoke-WebRequest -UseBasicParsing -Uri "https://$baseUrl/graphql" `
            -Method "POST" `
            -WebSession $session `
            -Headers $headers `
            -ContentType "application/json; charset=UTF-8" `
            -Body $body
        
        # Add assetId to the response for tracking
        $jsonContent = $response.Content | ConvertFrom-Json
        
        # Create a custom PSObject that includes the original assetId
        $customResponse = [PSCustomObject]@{
            data = $jsonContent.data
            assetId = $originalAssetId
        } | ConvertTo-Json -Depth 10
        
        # Return parsed JSON if requested, otherwise raw content
        if ($ParseResult) {
            return $customResponse | ConvertFrom-Json
        } else {
            return $customResponse
        }
    }
    catch {
        Write-Error "Error querying Collibra API: $_"
        return $null
    }
}

# Function to parse the cron configuration into human-readable format
function Parse-CronConfig {
    param (
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [string]$JsonString
    )
    
    process {
        try {
            $jsonObject = $JsonString | ConvertFrom-Json
            $config = $jsonObject.data.api.databaseScheduleConfiguration
            $assetId = $jsonObject.assetId
            
            if (-not $config) {
                Write-Error "Database schedule configuration not found in JSON"
                return $null
            }
            
            # Extract cron information
            $cronExpression = $config.cronExpression
            $cronTimeZone = $config.cronTimeZone
            
            # Parse the nested cronJson string
            try {
                $cronJsonStr = $config.cronJson -replace '\\\"', '"'
                $cronJsonStr = $cronJsonStr.Trim('"')
                $cronJson = $cronJsonStr | ConvertFrom-Json
            }
            catch {
                Write-Warning "Could not parse cronJson: $_"
                $cronJson = $null
            }
            
            # Parse the cron expression components
            $cronParts = $cronExpression -split ' '
            if ($cronParts.Count -ge 6) {
                $seconds = $cronParts[0]
                $minutes = $cronParts[1]
                $hours = $cronParts[2]
                $dayOfMonth = $cronParts[3]
                $month = $cronParts[4]
                $dayOfWeek = $cronParts[5]
                
                # Get the day of week name (using Quartz scheduler convention)
                $daysOfWeek = @("", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
                $dayIndex = [int]$dayOfWeek
                if ($dayIndex -ge 1 -and $dayIndex -le 7) {
                    $dayName = $daysOfWeek[$dayIndex]
                }
                else {
                    $dayName = "Unknown day ($dayOfWeek)"
                }
                
                # Create a human-readable schedule
                $readableTime = "$hours`:00:00"
                $readableSchedule = "Every $dayName at $readableTime $cronTimeZone"
            }
            else {
                Write-Warning "Invalid cron expression format: $cronExpression"
                $readableSchedule = "Invalid cron format"
                $dayName = "Unknown"
            }
            
            # Convert NextRunDateLongValue to datetime
            $nextRunDateTime = $null
            if ($config.nextRunDateLongValue) {
                try {
                    $nextRunUtc = [datetime]::new(1970, 1, 1, 0, 0, 0, [DateTimeKind]::Utc).AddMilliseconds($config.nextRunDateLongValue)
                    $nextRunDateTime = $nextRunUtc.ToString("yyyy-MM-dd HH:mm:ss") + " UTC"
                }
                catch {
                    Write-Warning "Could not convert next run timestamp: $_"
                }
            }
            
            # Create result object with assetId
            $result = [PSCustomObject]@{
                Id = $config.id
                AssetId = $assetId
                CronExpression = $cronExpression
                Timezone = $cronTimeZone
                DayOfWeek = $dayName
                Hour = $hours
                Frequency = if ($cronJson.preset) { $cronJson.preset } else { "unknown" }
                ReadableSchedule = $readableSchedule
                LastRunTimestamp = $config.lastRunTimeStamp
                NextRunTimestamp = $config.nextRunDateLongValue
                NextRunDateTime = $nextRunDateTime
            }
            
            return $result
        }
        catch {
            Write-Error "Failed to parse JSON: $_"
            return $null
        }
    }
}

$collibraUrl = "your-instance.collibra.com" # Replace with your organization address
$sessionId = "your-session-id-here" # Replace with your JSESSIONID cookie value
$csrfToken = "your-csrf-token-here" # Replace with your x-csrf-token value

# Process multiple assets
$assetIds = @(
    "00000000-0000-0000-0000-000000000001", # Replace with your database asset type asset ID
    "00000000-0000-0000-0000-000000000002"  # Replace with another database asset type asset ID
)

$results = @()
foreach ($asset in $assetIds) {
    $json = Get-CollibraScheduleConfig -CollibraUrl $collibraUrl -AssetId $asset -JobGroup "INGESTION" -SessionId $sessionId -CsrfToken $csrfToken
    $parsed = $json | Parse-CronConfig
    $results += $parsed
}


$results | Format-Table Id, AssetId, ReadableSchedule, NextRunDateTime
$results | Export-Csv -Path ".\output.csv" -NoTypeInformation # Replace with your desired output path

