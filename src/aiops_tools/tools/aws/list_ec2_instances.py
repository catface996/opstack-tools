"""List EC2 instances in AWS."""

TOOL_DEFINITION = {
    "name": "aws_list_ec2_instances",
    "display_name": "List EC2 Instances",
    "description": "List EC2 instances in a region with their status, type, and key details. Supports filtering by instance state or tags.",
    "tags": ["aws", "ec2", "instances", "list"],
    "input_schema": {
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "description": "AWS region (e.g., us-east-1, eu-west-1)",
            },
            "aws_access_key_id": {
                "type": "string",
                "description": "AWS access key (optional, uses default credentials if not provided)",
            },
            "aws_secret_access_key": {
                "type": "string",
                "description": "AWS secret key",
            },
            "filters": {
                "type": "array",
                "description": "Filters to apply (e.g., instance-state-name, tag:Name)",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "values": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of instances to return",
                "default": 100,
            },
        },
        "required": ["region"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "region": {"type": "string"},
                    "instances": {"type": "array"},
                    "total_count": {"type": "integer"},
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


def _get_instance_name(instance) -> str:
    """Extract Name tag from instance."""
    if instance.get("Tags"):
        for tag in instance["Tags"]:
            if tag["Key"] == "Name":
                return tag["Value"]
    return ""


def main(input_data: dict) -> dict:
    """List EC2 instances.

    Args:
        input_data: Dictionary with region, optional credentials and filters

    Returns:
        Dictionary with success status and instance list or error
    """
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "AWS_IMPORT_ERROR",
                "message": "boto3 package not installed. Run: pip install boto3",
            },
        }

    region = input_data.get("region")
    if not region:
        return {
            "success": False,
            "error": {
                "code": "AWS_INVALID_INPUT",
                "message": "region is required",
            },
        }

    filters = input_data.get("filters", [])
    max_results = input_data.get("max_results", 100)

    try:
        session = _get_boto_session(input_data)
        ec2 = session.client("ec2")

        # Build API params
        params = {}
        if filters:
            params["Filters"] = [
                {"Name": f["name"], "Values": f["values"]}
                for f in filters
            ]

        # Describe instances
        instances = []
        paginator = ec2.get_paginator("describe_instances")

        for page in paginator.paginate(**params):
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append({
                        "instance_id": instance["InstanceId"],
                        "name": _get_instance_name(instance),
                        "state": instance["State"]["Name"],
                        "instance_type": instance["InstanceType"],
                        "private_ip": instance.get("PrivateIpAddress", ""),
                        "public_ip": instance.get("PublicIpAddress", ""),
                        "availability_zone": instance["Placement"]["AvailabilityZone"],
                        "launch_time": instance["LaunchTime"].isoformat(),
                    })

                    if len(instances) >= max_results:
                        break
                if len(instances) >= max_results:
                    break
            if len(instances) >= max_results:
                break

        return {
            "success": True,
            "data": {
                "region": region,
                "instances": instances,
                "total_count": len(instances),
            },
        }

    except NoCredentialsError:
        return {
            "success": False,
            "error": {
                "code": "AWS_AUTH_ERROR",
                "message": "No AWS credentials found. Provide aws_access_key_id and aws_secret_access_key or configure AWS credentials.",
            },
        }
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "AuthFailure":
            return {
                "success": False,
                "error": {
                    "code": "AWS_AUTH_ERROR",
                    "message": "Invalid AWS credentials",
                },
            }
        elif error_code == "AccessDenied":
            return {
                "success": False,
                "error": {
                    "code": "AWS_ACCESS_DENIED",
                    "message": "Access denied. Check IAM permissions for ec2:DescribeInstances",
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
