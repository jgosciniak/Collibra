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
- [Troubleshooting](#troubleshooting)
  - [Permission Issues with PostgreSQL](#permission-issues-with-postgresql)
  - [Admin Login Issues](#admin-login-issues)
  - [Web Interface Access Issues](#web-interface-access-issues)
  - [License Configuration Issues](#license-configuration-issues)
- [Working with the Local PostgreSQL Database](#working-with-the-local-postgresql-database)
  - [Connecting to PostgreSQL](#connecting-to-postgresql)
  - [Basic PostgreSQL Commands](#basic-postgresql-commands)
  - [Common Administrative Tasks](#common-administrative-tasks)
  - [Exiting PostgreSQL](#exiting-postgresql)
  - [Important Notes](#important-notes)
- [Upgrading](#upgrading)
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

## Additional Resources

- Collibra Documentation Center: [https://productresources.collibra.com/docs/collibra/latest/](https://productresources.collibra.com/docs/collibra/latest/)
- Collibra Support: [https://support.collibra.com](https://support.collibra.com)
- PostgreSQL Documentation: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)