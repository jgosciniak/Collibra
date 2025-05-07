# Collibra DQ Standalone Installation Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
  - [System Requirements](#system-requirements)
  - [Software Requirements](#software-requirements)
- [Installation Process](#installation-process)
  - [Step 1: Prepare the Server](#step-1-prepare-the-server)
  - [Step 2: Set Environment Variables](#step-2-set-environment-variables)
  - [Step 3: Run the Installation Script](#step-3-run-the-installation-script)
  - [Step 4: Verify Installation](#step-4-verify-installation)
  - [Step 5: Configure License Key](#step-5-configure-license-key)
- [Post-Installation Configuration](#post-installation-configuration)
  - [Agent Configuration](#agent-configuration)
  - [Connection Setup](#connection-setup)
  - [Test Job Execution](#test-job-execution)
  - [Important Configuration Files](#important-configuration-files)
  - [Database Driver Management](#database-driver-management)
  - [Log Monitoring and Troubleshooting](#log-monitoring-and-troubleshooting)
- [Troubleshooting](#troubleshooting)
  - [Permission Issues with PostgreSQL](#permission-issues-with-postgresql)
  - [Admin Login Issues](#admin-login-issues)
  - [Process Management Issues](#process-management-issues)
  - [Web Interface Access Issues](#web-interface-access-issues)
  - [License Configuration Issues](#license-configuration-issues)
  - [Creating a Complete System Backup](#creating-a-complete-system-backup)
- [Upgrading](#upgrading)
  - [Upgrading to Java 17 and Spark 3.5.3](#upgrading-to-java-17-and-spark-353)
- [Spark Configuration and Troubleshooting](#spark-configuration-and-troubleshooting)
  - [Common Spark Issues](#common-spark-issues)
  - [Spark Service Management](#spark-service-management)
  - [Fixing Spark in Collibra DQ](#fixing-spark-in-collibra-dq)
- [Working with the Local PostgreSQL Database](#working-with-the-local-postgresql-database)
  - [Connecting to PostgreSQL](#connecting-to-postgresql)
  - [Basic PostgreSQL Commands](#basic-postgresql-commands)
  - [Common Administrative Tasks](#common-administrative-tasks)
  - [Exiting PostgreSQL](#exiting-postgresql)
  - [Important Notes](#important-notes)
- [Additional Resources](#additional-resources)

## Overview

Collibra Data Quality & Observability (DQ) is a tool designed to monitor data quality and data pipeline reliability to help identify and remediate anomalies. It can be deployed in various environments including standalone installations, cloud platforms (AWS, GCP), and Kubernetes clusters.

This guide focuses on the standalone installation method, which is ideal for environments where large scale and high concurrency checks are not required. In this mode, Collibra DQ leverages a Spark Standalone pseudo-cluster where the master and workers run on the same server.

## Prerequisites

### System Requirements

For a standard standalone installation, the following hardware specifications are recommended:

- **Small Tier**: 16 Core CPU, 128GB RAM (e.g., AWS r5.4xlarge or Azure E16s v3)
- **Medium Tier**: 32 Core CPU, 256GB RAM (e.g., AWS r5.8xlarge or Azure E32s v3)
- **Large Tier**: 64 Core CPU, 512GB RAM (e.g., AWS r5.16xlarge or Azure E64s v3)

For storage:
- At least 50GB for the base installation
- Additional storage for logs and data processing

### Software Requirements

- **Operating System**: Red Hat Enterprise Linux (RHEL) 8 or 9
- **Java**: 
  - Current versions require Java 8 or 11
  - Important: In the 2025.02 version, Collibra DQ will require Java 17 and Spark 3.5.3
- **PostgreSQL**: Version 11 or newer (can be installed as part of the setup or use an existing instance)
- **Full sudo access** (required if including PostgreSQL in the installation)
- **ULIMIT settings** of 4096 or higher

## Installation Process

### Step 1: Prepare the Server

1. Set up a server with the required operating system (RHEL 8 or 9)
2. Access the server through SSH or console
3. Download the Collibra DQ installation package:
   ```bash
   # Replace with the actual link provided by Collibra
   curl -O <signed-link-to-full-package>
   ```
4. Extract the package:
   ```bash
   tar -xzf dq-full-package.tar.gz
   ```

### Step 2: Set Environment Variables

Set up the necessary environment variables for the installation:

```bash
# Base path where Collibra DQ will be installed (no trailing spaces)
export OWL_BASE=$(pwd)

# PostgreSQL username for DQ Web Application
export OWL_METASTORE_USER=postgres
# Or use a custom admin username:
# export OWL_METASTORE_USER=postgresadmin

# PostgreSQL password (use a complex password with minimum 18 characters)
# Example: should include upper, lower, numbers, and symbols
export OWL_METASTORE_PASS=YourComplexPassword123!@#

# Specify Spark version - select one of the options below:
# For Spark 3.4.1 (default)
export SPARK_PACKAGE=spark-3.4.1-bin-hadoop3.2.tgz
# For Spark 3.2.2
# export SPARK_PACKAGE=spark-3.2.2-bin-hadoop3.2.tgz
```

**Important**: Make sure to use a strong password that meets complexity requirements (minimum 18 characters, including uppercase letters, lowercase letters, numbers, and special symbols). Avoid using the dollar sign ($) in your PostgreSQL password as it's not supported.

### Step 3: Run the Installation Script

Run the setup script with the appropriate options:

```bash
# For installing PostgreSQL locally along with Collibra DQ
./setup.sh \
  -owlbase=$OWL_BASE \
  -user=$OWL_METASTORE_USER \
  -pgpassword=$OWL_METASTORE_PASS \
  -options=postgres,spark,owlweb,owlagent
```

If you want to use an existing PostgreSQL server:

```bash
# For using an existing PostgreSQL server
./setup.sh \
  -owlbase=$OWL_BASE \
  -user=$OWL_METASTORE_USER \
  -pgpassword=$OWL_METASTORE_PASS \
  -pghost=<postgres-host> \
  -pgport=<postgres-port> \
  -options=spark,owlweb,owlagent
```

During the installation:
- If prompted to install Java 8 or 11 because it's not present, accept the installation from the local package
- If prompted for PostgreSQL data location, either accept the default path or provide a custom path that has proper write permissions

**Note about PostgreSQL Authentication Warnings:**
You may see the following warning during installation:
```
initdb: warning: enabling "trust" authentication for local connections
You can change this by editing pg_hba.conf or using the option -A, or
--auth-local and --auth-host, the next time you run initdb.
```

This warning is informational and doesn't prevent the installation from completing successfully. It indicates that PostgreSQL is configured to trust local connections without password authentication. For most standalone installations, this default configuration is acceptable. If you need to change this for security reasons, you can edit the `pg_hba.conf` file after installation.

### Step 4: Verify Installation

After the installation completes, you should see output similar to:

```
installing owlweb
starting owlweb
starting owl-web
installing agent
not starting agent
install complete
please use owl owlmanage utility to configure license key and start owl-agent after owl-web successfully starts up
```

Verify the installation by:

1. Accessing the DQ Web interface at `http://<server-ip>:9000` using a web browser
2. Checking the Spark Cluster availability at `http://<server-ip>:8080`
3. Note the Spark Master URL (starting with `spark://...`) as it will be needed for Agent configuration

### Step 5: Configure License Key

Configure the license key to enable the DQ Agent:

```bash
cd $OWL_BASE/owl/bin
./owlmanage.sh setlic=<your-license-key>
./owlmanage.sh start=owlagent
```

Replace `<your-license-key>` with the valid license key provided by Collibra (found in the license provision email following "YOUR KEY IS =").

After setting the license key, you should see output confirming the license has been set, including information about the license expiration date. You can then start the agent using the `start=owlagent` command.

## Post-Installation Configuration

### Agent Configuration

1. Log in to DQ Web at `http://<server-ip>:9000`
2. Navigate to Admin Console
3. Click on the "Remote Agent" tile
4. Configure the agent with the following settings:
   - **Owl Base**: The location provided during installation followed by `/owl` (e.g., `/home/user/owl`)
   - **Spark Master**: The Spark Master URL noted in Step 4 (starts with `spark://...`)
   - **Deploy Mode**: Set to "Cluster"
   - **Default resources**: Configure the number of executors, memory per executor, number of cores, and driver memory according to your environment

### Connection Setup

1. In DQ Web, navigate to the Connections page (click the Connections tile)
2. Click on the PostgreSQL connection template
3. Configure the test connection with:
   - Host: localhost (or the PostgreSQL server address)
   - Port: 5432 (default PostgreSQL port)
   - Database: postgres
   - Username: The PostgreSQL user from the installation
   - Password: The PostgreSQL password from the installation
4. Click Save

### Test Job Execution

To verify that everything is working properly:

1. Navigate back to the Admin Console
2. Click the "Remote Agent" tile
3. On the left side, select the chain link icon next to the configured agent
4. Double-click the "metastore" connection from the left text area
5. Click "Update" to save the configuration
6. Click the compass icon in the navigation pane to access the Explorer page
7. Click on the "metastore" connection
8. Select the "public" schema
9. Select a table from the list
10. When the preview and scope tab appears, click "Build Model"
11. On the Profile page, click "Run"
12. On the Run page, click "Estimate Job"
13. Acknowledge the resource recommendations and click "Run"
14. Navigate to the Jobs page (click the clock icon)
15. Refresh the page to see the job progress until it reaches "Finished" status

### Important Configuration Files

Collibra DQ has several important configuration files that you may need to modify for optimal performance:

1. **owl-env.sh** (`$OWL_BASE/owl/config/owl-env.sh`)
   - Contains environment variables used by Collibra DQ
   - Key settings include:
     - Java options and memory allocation
     - Logging configuration
     - EXTRA_JVM_OPTIONS for Java compatibility
     - Temporary directory locations

2. **owl.properties** (`$OWL_BASE/owl/config/owl.properties`)
   - Primary configuration for the DQ Web application
   - Contains:
     - Database connection settings for the metastore
     - Web server configuration
     - Authentication settings
     - File upload limits

3. **agent.properties** (`$OWL_BASE/owl/config/agent.properties`)
   - Configuration for the DQ Agent
   - Includes:
     - Job processing parameters
     - Spark connection settings
     - Resource allocation defaults
     - Agent identification

4. **log4j2.properties** (`$OWL_BASE/owl/config/log4j2.properties`)
   - Controls logging behavior
   - Configure log levels, rotation policy, and format

When making changes to these files, always:
1. Stop the affected services first
2. Make a backup of the original file
3. Restart the services after changes
4. Check logs for any errors or warnings

### Database Driver Management

Collibra DQ requires specific JDBC drivers to connect to different database systems. These drivers are stored in the `$OWL_BASE/owl/drivers` directory, organized by database type.

To add or update database drivers:

1. Create a directory structure for your database type if it doesn't exist:
   ```bash
   mkdir -p $OWL_BASE/owl/drivers/<database_type>
   # Example: mkdir -p $OWL_BASE/owl/drivers/postgres
   ```

2. Copy the JDBC driver JAR files to the appropriate directory:
   ```bash
   cp /path/to/driver.jar $OWL_BASE/owl/drivers/<database_type>/
   ```

3. Restart the DQ Agent to load the new drivers:
   ```bash
   $OWL_BASE/owl/bin/owlmanage.sh restart=owlagent
   ```

Common database driver paths:
- PostgreSQL: `$OWL_BASE/owl/drivers/postgres/`
- Oracle: `$OWL_BASE/owl/drivers/oracle/`
- SQL Server: `$OWL_BASE/owl/drivers/mssql/`
- MySQL: `$OWL_BASE/owl/drivers/mysql/`

If you have a drivers.tar.gz file from Collibra, you can extract it directly:
```bash
tar -xvf drivers.tar.gz -C $OWL_BASE/owl/drivers/
```

### Log Monitoring and Troubleshooting

Monitoring logs is essential for diagnosing issues with Collibra DQ. The main log files are located in `$OWL_BASE/owl/log/`.

Key log files:
- `owl-web.log` - DQ Web application logs
- `owl-agent.log` - DQ Agent logs
- `postgresql-*.log` - PostgreSQL database logs (if installed locally)

Useful log monitoring commands:

```bash
# View the last 1000 lines of the web application log
tail -1000 $OWL_BASE/owl/log/owl-web.log

# Follow the agent log in real-time
tail -f $OWL_BASE/owl/log/owl-agent.log

# Search for errors in the agent log
tail -1000 $OWL_BASE/owl/log/owl-agent.log | grep -i error

# Monitor startup progress
tail -f $OWL_BASE/owl/log/owl-web.log

# View PostgreSQL logs (if installed locally)
tail -1000 $OWL_BASE/owl/postgres/data/log/postgresql-*.log
```

When diagnosing issues, look for:
- ERROR level messages that indicate serious problems
- WARN level messages that might point to configuration issues
- Exception stack traces that provide detailed error information
- Specific error codes or messages related to your database

Common issues and their log patterns:
- **Connection failures**: Look for "Connection refused" or "Cannot establish connection"
- **Authentication issues**: Search for "Authentication failed" or "Invalid credentials"
- **Resource limitations**: Watch for "Out of memory" or "Resource allocation failed"
- **Database errors**: Check for SQL exceptions or database-specific error codes

## Troubleshooting

### Permission Issues with PostgreSQL

If you encounter permission issues during PostgreSQL installation:

```bash
# Remove the problematic PostgreSQL data directory
sudo rm -rf $OWL_BASE/owl/postgres

# Set appropriate permissions
chmod -R 755 $OWL_BASE

# Reinstall just PostgreSQL
./setup.sh -owlbase=$OWL_BASE -user=$OWL_METASTORE_USER -pgpassword=$OWL_METASTORE_PASS -options=postgres
```

### Admin Login Issues

Sometimes the installation process may fail to properly create the admin user, resulting in an inability to log in after installation. Signs of this issue include:

- You can see the Spark welcome screen and the login page
- You cannot log in as 'admin' with any password
- In the owl-web.log, you might see messages like: "Query returned no results for user 'admin'" or "Authentication ERROR: admin"
- The postgres-init-error.log might show warnings about "trust" authentication

This issue is often caused by a password validation error during admin user creation. To fix this:

1. Connect to the PostgreSQL database:
   ```bash
   # Navigate to PostgreSQL bin directory
   cd $OWL_BASE/owl/postgres/bin
   
   # Connect to PostgreSQL
   ./psql -U postgres -d postgres
   ```

2. Create the admin user if it doesn't exist:
   ```sql
   INSERT INTO public.users (username, "password", email, enabled, password_reset_token, token_expiration, created, accountnonlocked, invalid_login_attempts) 
   VALUES('admin', '$2a$10$95kIfIHpB4rZBq8EA.wWn.e4HLsM6KmrgHB9st8bpgLcrYZ7kslSy', 'admin@admin.com', TRUE, NULL, NULL, '2024-06-17 15:03:50.074403+00', TRUE, 0);
   ```

3. If the admin user already exists, update the password:
   ```sql
   UPDATE public.users 
   SET "password" = '$2a$10$95kIfIHpB4rZBq8EA.wWn.e4HLsM6KmrgHB9st8bpgLcrYZ7kslSy', 
       accountnonlocked = 'TRUE', 
       invalid_login_attempts = 0 
   WHERE username = 'admin';
   ```

4. Add the admin role to the user:
   ```sql
   INSERT INTO public.authorities VALUES ('admin', 'ROLE_ADMIN');
   ```

5. Exit PostgreSQL:
   ```sql
   \q
   ```

After these steps, you should be able to log in with username `admin` and password `admin123`. Make sure to change this default password immediately after login.

### Process Management Issues

Sometimes DQ services may not stop properly using the standard commands. If you encounter this:

1. First, try the standard stop commands:
   ```bash
   $OWL_BASE/owl/bin/owlmanage.sh stop=owlweb
   $OWL_BASE/owl/bin/owlmanage.sh stop=owlagent
   ```

2. Check for running processes:
   ```bash
   ps -ef | grep owl
   ```

3. If processes are still running, you may need to force-stop them:
   ```bash
   # Replace PID with the actual process ID from the ps command
   kill -9 PID
   
   # Example:
   # kill -9 4632
   ```

4. For Spark services, use these commands:
   ```bash
   cd $OWL_BASE/owl/spark/sbin
   ./stop-worker.sh
   ./stop-master.sh
   ```

5. Check for any remaining processes after stopping:
   ```bash
   ps -ef | grep owl
   ps -ef | grep spark
   ```

### Web Interface Access Issues

If you cannot access the web interface after installation:
- Check that ports 9000 (DQ Web) and 8080 (Spark) are open in your firewall
- Ensure the DQ Web service is running: `$OWL_BASE/owl/bin/owlmanage.sh status=owlweb`
- If needed, restart the service: `$OWL_BASE/owl/bin/owlmanage.sh restart=owlweb`

### License Configuration Issues

If you encounter issues enabling the license option in the web interface:

1. Sign in to Collibra DQ
2. Go to Admin Console → Configuration → App Config
3. Set the `UX_REACT_ON` parameter to `TRUE`
4. Manage your license through the License option
5. After updating the license, set `UX_REACT_ON` back to `FALSE` to ensure proper functionality

### Creating a Complete System Backup

Before making significant changes to your Collibra DQ installation, create a full backup:

```bash
# Navigate to the parent directory of your installation
cd /path/to/parent/directory

# Create a compressed backup archive
tar -czf owldq_backup_$(date +%Y%m%d).tar.gz owldq/

# Verify the backup was created
ls -lh owldq_backup_*.tar.gz
```

This backup can be used to restore your installation if anything goes wrong during upgrades or configuration changes.

To restore from a backup:

```bash
# Stop all services
$OWL_BASE/owl/bin/owlmanage.sh stop

# Navigate to the parent directory
cd /path/to/parent/directory

# Remove the problematic installation (be careful with this command!)
rm -rf owldq

# Extract the backup
tar -xzf owldq_backup_YYYYMMDD.tar.gz

# Restart services
$OWL_BASE/owl/bin/owlmanage.sh start
```

## Upgrading

To upgrade Collibra DQ to a newer version:

1. Download the new package
2. Stop the current DQ services:
   ```bash
   $OWL_BASE/owl/bin/owlmanage.sh stop=owlweb
   $OWL_BASE/owl/bin/owlmanage.sh stop=owlagent
   ```
3. Back up the existing installation
4. Extract the new package and follow the installation steps with the same parameters as your original installation
5. Start the services:
   ```bash
   $OWL_BASE/owl/bin/owlmanage.sh start=owlweb
   $OWL_BASE/owl/bin/owlmanage.sh start=owlagent
   ```

Note: For Collibra DQ version 2025.02 and newer, you must upgrade to Java 17 and Spark 3.5.3.

### Upgrading to Java 17 and Spark 3.5.3

Starting with Collibra DQ version 2025.02, Java 17 and Spark 3.5.3 are required. Here's a detailed guide for upgrading:

1. Install Java 17:
   ```bash
   sudo dnf install java-17-openjdk-devel
   ```

2. Create a backup directory for your current JAR files:
   ```bash
   mkdir -p $OWL_BASE/owl/tempfiles
   ```

3. Move the old JAR files to the backup directory:
   ```bash
   # Replace the version numbers with your current version
   mv $OWL_BASE/owl/bin/dq-agent-*-SPARK*.jar $OWL_BASE/owl/tempfiles/
   mv $OWL_BASE/owl/bin/dq-core-*-SPARK*-jar-with-dependencies.jar $OWL_BASE/owl/tempfiles/
   mv $OWL_BASE/owl/bin/dq-webapp-*-SPARK*.jar $OWL_BASE/owl/tempfiles/
   ```

4. Copy the new JAR files to the bin directory:
   ```bash
   # Replace VERSION with your new version (e.g., 2025.03)
   mv dq-agent-VERSION-SPARK353-JDK17.jar $OWL_BASE/owl/bin/
   mv dq-core-VERSION-SPARK353-JDK17-jar-with-dependencies.jar $OWL_BASE/owl/bin/
   mv dq-webapp-VERSION-SPARK353-JDK17.jar $OWL_BASE/owl/bin/
   ```

5. Add required Java 17 JVM parameters to the environment:
   ```bash
   # Edit the owl-env.sh file
   nano $OWL_BASE/owl/config/owl-env.sh
   
   # Add or update the following line in the file
   export EXTRA_JVM_OPTIONS="--add-opens java.base/java.util=ALL-UNNAMED --add-opens java.base/java.net=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED --add-opens java.base/java.nio=ALL-UNNAMED --add-opens java.base/sun.util.calendar=ALL-UNNAMED"
   ```

6. Extract and update Spark:
   ```bash
   # Navigate to where your installation package is located
   cd /path/to/installation/package
   
   # Extract the Spark package
   tar -xvf spark-3.5.3-bin-hadoop3.tgz
   
   # Rename and move the directory
   mv spark-3.5.3-bin-hadoop3 spark
   
   # Backup the old Spark directory if needed
   mv $OWL_BASE/owl/spark $OWL_BASE/owl/spark_backup  # Optional
   
   # Move the new Spark to the installation directory
   mv spark $OWL_BASE/owl/
   ```

7. If you have extra Spark JARs (spark-extras):
   ```bash
   # Copy any extra JARs to the Spark jars directory
   cp spark-extras/* $OWL_BASE/owl/spark/jars/
   ```

8. Set optional Spark worker options for better cleanup:
   ```bash
   # Add to your environment or owl-env.sh
   export SPARK_WORKER_OPTS="${SPARK_WORKER_OPTS} -Dspark.worker.cleanup.enabled=true -Dspark.worker.cleanup.interval=1800 -Dspark.worker.cleanup.appDataTtl=3600"
   ```

9. Start Collibra DQ services:
   ```bash
   # Start Collibra Web
   $OWL_BASE/owl/bin/owlmanage.sh start=owlweb
   
   # Start Spark master and workers (if not managed by Collibra DQ)
   cd $OWL_BASE/owl/spark/sbin
   ./start-master.sh
   ./start-worker.sh spark://$(hostname -f):7077
   
   # Start Collibra Agent
   $OWL_BASE/owl/bin/owlmanage.sh start=owlagent
   ```

10. Verify the services are running properly:
    ```bash
    # Check logs for any errors
    tail -1000 $OWL_BASE/owl/log/owl-web.log
    tail -1000 $OWL_BASE/owl/log/owl-agent.log
    ```

11. If you encounter issues with Spark jobs not starting, verify:
    - The Spark master is running (`http://<server-ip>:8080`)
    - The worker is connected to the master
    - The hostname in the Spark master URL is correctly resolved (use FQDN if needed)
    
    ```bash
    # If necessary, restart the Spark worker with full hostname
    cd $OWL_BASE/owl/spark/sbin
    ./stop-worker.sh
    ./start-worker.sh spark://$(hostname -f):7077
    ```

These steps should help you successfully upgrade to Java 17 and Spark 3.5.3 for newer versions of Collibra DQ.

## Spark Configuration and Troubleshooting

Proper Spark configuration is critical for Collibra DQ to function correctly, especially for data quality job execution. This section covers common Spark configuration issues and how to resolve them.

### Common Spark Issues

1. **Jobs Stuck in "Pending" or "Submitted" Status**
   - This often indicates that Spark master and workers are not properly configured or running
   - Check if Spark master is running: `http://<server-ip>:8080`
   - Verify workers are connected to the master
   - Ensure the Spark master URL in the agent configuration is correct

2. **Hostname Resolution Problems**
   - Spark requires proper hostname resolution to function correctly
   - Use fully qualified domain names (FQDN) for Spark master URLs
   - Get your FQDN with: `hostname -f`
   - Update worker configuration with the correct master URL:
     ```bash
     ./start-worker.sh spark://<your-fqdn>:7077
     ```

3. **Insufficient Resources**
   - Spark jobs require adequate memory and CPU resources
   - Adjust executor memory and cores in the agent configuration
   - Increase executor memory if you see "Out of Memory" errors

### Spark Service Management

When Collibra DQ jobs aren't running properly, you may need to manually manage Spark services:

1. **Start Spark Master:**
   ```bash
   cd $OWL_BASE/owl/spark/sbin
   ./start-master.sh
   ```

2. **Start Spark Worker:**
   ```bash
   cd $OWL_BASE/owl/spark/sbin
   ./start-worker.sh spark://$(hostname -f):7077
   ```

3. **Stop Spark Services:**
   ```bash
   cd $OWL_BASE/owl/spark/sbin
   ./stop-worker.sh
   ./stop-master.sh
   ```

4. **Verify Spark Is Running:**
   - Check the Spark UI at `http://<server-ip>:8080`
   - Ensure at least one worker is connected
   - Verify available resources match your requirements

### Fixing Spark in Collibra DQ

If you need to reinstall or fix Spark configuration:

1. **Stop All Services:**
   ```bash
   $OWL_BASE/owl/bin/owlmanage.sh stop=owlweb
   $OWL_BASE/owl/bin/owlmanage.sh stop=owlagent
   cd $OWL_BASE/owl/spark/sbin
   ./stop-worker.sh
   ./stop-master.sh
   ```

2. **Replace Spark Installation:**
   ```bash
   # Backup current Spark if needed
   mv $OWL_BASE/owl/spark $OWL_BASE/owl/spark_backup
   
   # Extract new Spark package
   tar -xvf spark-3.5.3-bin-hadoop3.tgz
   mv spark-3.5.3-bin-hadoop3 spark
   mv spark $OWL_BASE/owl/
   ```

3. **Add Extra JARs if Needed:**
   ```bash
   # Copy any required extra JARs
   cp spark-extras/* $OWL_BASE/owl/spark/jars/
   ```

4. **Set Correct Permissions:**
   ```bash
   chmod -R 755 $OWL_BASE/owl/spark/bin
   chmod -R 755 $OWL_BASE/owl/spark/sbin
   ```

5. **Restart Services:**
   ```bash
   $OWL_BASE/owl/bin/owlmanage.sh start=owlweb
   
   cd $OWL_BASE/owl/spark/sbin
   ./start-master.sh
   ./start-worker.sh spark://$(hostname -f):7077
   
   $OWL_BASE/owl/bin/owlmanage.sh start=owlagent
   ```

6. **Monitor Logs for Success:**
   ```bash
   tail -f $OWL_BASE/owl/log/owl-agent.log
   ```

By following these steps, you should be able to resolve most Spark-related issues in your Collibra DQ installation.

## Working with the Local PostgreSQL Database

Collibra DQ uses PostgreSQL to store its metadata. Understanding how to interact with this database can be helpful for troubleshooting, configuration, and advanced customization. Below are instructions for common PostgreSQL operations in the context of Collibra DQ.

### Connecting to PostgreSQL

Connect to the PostgreSQL instance installed with Collibra DQ:

```bash
# Navigate to PostgreSQL bin directory
cd $OWL_BASE/owl/postgres/bin

# Connect using psql
./psql -U postgres -d postgres
```

If prompted for a password, enter the PostgreSQL password you defined during installation (the value of `OWL_METASTORE_PASS`).

Alternatively, you can connect using the standard `psql` command if it's in your PATH:

```bash
# Using the standard PostgreSQL client with environment variables
PGPASSWORD=$OWL_METASTORE_PASS psql -U postgres -h localhost -d postgres
```

### Basic PostgreSQL Commands

Once connected to PostgreSQL, you can use these common commands:

#### Database Operations

```sql
-- List all databases
\l

-- Connect to a specific database (usually 'postgres' for Collibra DQ)
\c postgres

-- Show current connection information
\conninfo
```

#### Table Operations

```sql
-- List all tables in the current database
\dt

-- Show the structure of a specific table
\d table_name

-- Example: Show the structure of the users table
\d public.users
```

#### Query Examples

```sql
-- View all users in the system
SELECT * FROM public.users;

-- Check user roles and permissions
SELECT * FROM public.authorities;

-- Count the number of DQ jobs
SELECT COUNT(*) FROM public.job;

-- Find the most recent DQ jobs
SELECT id, jobname, starttime, endtime, status 
FROM public.job 
ORDER BY starttime DESC 
LIMIT 10;
```

#### Modifying Data

```sql
-- Update a user's email
UPDATE public.users
SET email = 'new.email@example.com'
WHERE username = 'admin';

-- Reset a user's failed login attempts
UPDATE public.users
SET invalid_login_attempts = 0,
    accountnonlocked = TRUE
WHERE username = 'username_here';
```

### Common Administrative Tasks

#### Reset Admin Password

If you need to reset the admin password to the default:

```sql
UPDATE public.users 
SET password = '$2a$10$95kIfIHpB4rZBq8EA.wWn.e4HLsM6KmrgHB9st8bpgLcrYZ7kslSy',
    accountnonlocked = TRUE,
    invalid_login_attempts = 0 
WHERE username = 'admin';
```

This sets the password to `admin123` (the default).

#### Create a New User

```sql
-- First create the user entry
INSERT INTO public.users (
    username, password, email, enabled, 
    created, accountnonlocked, invalid_login_attempts
) 
VALUES (
    'newuser', 
    '$2a$10$95kIfIHpB4rZBq8EA.wWn.e4HLsM6KmrgHB9st8bpgLcrYZ7kslSy', 
    'newuser@example.com', 
    TRUE, 
    CURRENT_TIMESTAMP, 
    TRUE, 
    0
);

-- Then assign a role to the user
INSERT INTO public.authorities (username, authority) 
VALUES ('newuser', 'ROLE_USER');
```

#### Check Database Size and Growth

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('postgres')) AS database_size;

-- Check table sizes
SELECT 
    tablename AS table_name, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Exiting PostgreSQL

To exit the PostgreSQL interactive terminal:

```sql
-- Exit psql
\q
```

### Important Notes

1. Be extremely cautious when modifying the database directly. Incorrect changes can cause Collibra DQ to malfunction.
2. Always back up the database before making significant changes.
3. For production environments, consider documenting any manual changes made to the database.
4. The default database name used by Collibra DQ is `postgres`.

## Additional Resources

- Collibra Documentation Center: [https://productresources.collibra.com/docs/collibra/latest/](https://productresources.collibra.com/docs/collibra/latest/)
- Collibra Support: [https://support.collibra.com](https://support.collibra.com)
- PostgreSQL Documentation: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)