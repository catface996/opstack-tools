"""Describe an RDS database instance."""

TOOL_DEFINITION = {
    "name": "aws_describe_rds",
    "display_name": "Describe RDS Instance",
    "description": "Get detailed information about an RDS database instance including endpoint, storage, and configuration.",
    "tags": ["aws", "rds", "database", "describe"],
    "input_schema": {
        "type": "object",
        "properties": {
            "region": {"type": "string"},
            "db_instance_identifier": {
                "type": "string",
                "description": "RDS instance identifier",
            },
            "aws_access_key_id": {"type": "string"},
            "aws_secret_access_key": {"type": "string"},
        },
        "required": ["region", "db_instance_identifier"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "db_instance_identifier": {"type": "string"},
                    "db_instance_class": {"type": "string"},
                    "engine": {"type": "string"},
                    "engine_version": {"type": "string"},
                    "status": {"type": "string"},
                    "endpoint": {"type": "object"},
                    "allocated_storage_gb": {"type": "integer"},
                    "storage_type": {"type": "string"},
                    "multi_az": {"type": "boolean"},
                    "availability_zone": {"type": "string"},
                    "vpc_id": {"type": "string"},
                    "publicly_accessible": {"type": "boolean"},
                    "backup_retention_days": {"type": "integer"},
                    "latest_restorable_time": {"type": "string"},
                    "tags": {"type": "object"},
                },
            },
        },
    },
}


def _get_boto_session(input_data: dict):
    """Get boto3 session with credentials from input or environment."""
    import boto3

    if input_data.get("aws_access_key_id") and input_data.get("aws_secret_access_key"):
        return boto3.Session(
            aws_access_key_id=input_data["aws_access_key_id"],
            aws_secret_access_key=input_data["aws_secret_access_key"],
            region_name=input_data.get("region"),
        )
    return boto3.Session(region_name=input_data.get("region"))


def main(input_data: dict) -> dict:
    """Describe an RDS instance.

    Args:
        input_data: Dictionary with region, db_instance_identifier, optional credentials

    Returns:
        Dictionary with success status and RDS details or error
    """
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "AWS_IMPORT_ERROR",
                "message": "boto3 package not installed",
            },
        }

    region = input_data.get("region")
    db_instance_identifier = input_data.get("db_instance_identifier")

    if not region or not db_instance_identifier:
        return {
            "success": False,
            "error": {
                "code": "AWS_INVALID_INPUT",
                "message": "region and db_instance_identifier are required",
            },
        }

    try:
        session = _get_boto_session(input_data)
        rds = session.client("rds")

        response = rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)

        if not response.get("DBInstances"):
            return {
                "success": False,
                "error": {
                    "code": "AWS_NOT_FOUND",
                    "message": f"RDS instance '{db_instance_identifier}' not found",
                },
            }

        instance = response["DBInstances"][0]

        # Extract tags
        tags = {}
        if instance.get("TagList"):
            for tag in instance["TagList"]:
                tags[tag["Key"]] = tag["Value"]

        # Get endpoint info
        endpoint = {}
        if instance.get("Endpoint"):
            endpoint = {
                "address": instance["Endpoint"].get("Address", ""),
                "port": instance["Endpoint"].get("Port", 0),
            }

        return {
            "success": True,
            "data": {
                "db_instance_identifier": instance["DBInstanceIdentifier"],
                "db_instance_class": instance["DBInstanceClass"],
                "engine": instance["Engine"],
                "engine_version": instance["EngineVersion"],
                "status": instance["DBInstanceStatus"],
                "endpoint": endpoint,
                "allocated_storage_gb": instance["AllocatedStorage"],
                "storage_type": instance.get("StorageType", ""),
                "multi_az": instance.get("MultiAZ", False),
                "availability_zone": instance.get("AvailabilityZone", ""),
                "vpc_id": instance.get("DBSubnetGroup", {}).get("VpcId", ""),
                "publicly_accessible": instance.get("PubliclyAccessible", False),
                "backup_retention_days": instance.get("BackupRetentionPeriod", 0),
                "latest_restorable_time": instance.get("LatestRestorableTime", "").isoformat() if instance.get("LatestRestorableTime") else "",
                "tags": tags,
            },
        }

    except NoCredentialsError:
        return {
            "success": False,
            "error": {
                "code": "AWS_AUTH_ERROR",
                "message": "No AWS credentials found",
            },
        }
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "DBInstanceNotFound":
            return {
                "success": False,
                "error": {
                    "code": "AWS_NOT_FOUND",
                    "message": f"RDS instance '{db_instance_identifier}' not found",
                },
            }
        return {
            "success": False,
            "error": {
                "code": "AWS_ERROR",
                "message": str(e),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "AWS_ERROR",
                "message": str(e),
            },
        }
