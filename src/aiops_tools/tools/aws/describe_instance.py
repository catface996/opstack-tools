"""Describe an EC2 instance in detail."""

TOOL_DEFINITION = {
    "name": "aws_describe_instance",
    "display_name": "Describe EC2 Instance",
    "description": "Get detailed information about a specific EC2 instance including network configuration, security groups, and tags.",
    "tags": ["aws", "ec2", "instances", "describe"],
    "input_schema": {
        "type": "object",
        "properties": {
            "region": {"type": "string"},
            "instance_id": {
                "type": "string",
                "description": "EC2 instance ID (e.g., i-1234567890abcdef0)",
            },
            "aws_access_key_id": {"type": "string"},
            "aws_secret_access_key": {"type": "string"},
        },
        "required": ["region", "instance_id"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "instance_id": {"type": "string"},
                    "name": {"type": "string"},
                    "state": {"type": "string"},
                    "instance_type": {"type": "string"},
                    "ami_id": {"type": "string"},
                    "platform": {"type": "string"},
                    "architecture": {"type": "string"},
                    "vpc_id": {"type": "string"},
                    "subnet_id": {"type": "string"},
                    "private_ip": {"type": "string"},
                    "public_ip": {"type": "string"},
                    "private_dns": {"type": "string"},
                    "public_dns": {"type": "string"},
                    "availability_zone": {"type": "string"},
                    "launch_time": {"type": "string"},
                    "security_groups": {"type": "array"},
                    "tags": {"type": "object"},
                    "monitoring": {"type": "string"},
                    "ebs_optimized": {"type": "boolean"},
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
    """Describe an EC2 instance.

    Args:
        input_data: Dictionary with region, instance_id, optional credentials

    Returns:
        Dictionary with success status and instance details or error
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
    instance_id = input_data.get("instance_id")

    if not region or not instance_id:
        return {
            "success": False,
            "error": {
                "code": "AWS_INVALID_INPUT",
                "message": "region and instance_id are required",
            },
        }

    try:
        session = _get_boto_session(input_data)
        ec2 = session.client("ec2")

        response = ec2.describe_instances(InstanceIds=[instance_id])

        if not response["Reservations"] or not response["Reservations"][0]["Instances"]:
            return {
                "success": False,
                "error": {
                    "code": "AWS_NOT_FOUND",
                    "message": f"Instance '{instance_id}' not found",
                },
            }

        instance = response["Reservations"][0]["Instances"][0]

        # Extract tags as dict
        tags = {}
        name = ""
        if instance.get("Tags"):
            for tag in instance["Tags"]:
                tags[tag["Key"]] = tag["Value"]
                if tag["Key"] == "Name":
                    name = tag["Value"]

        # Extract security groups
        security_groups = [
            {"id": sg["GroupId"], "name": sg["GroupName"]}
            for sg in instance.get("SecurityGroups", [])
        ]

        return {
            "success": True,
            "data": {
                "instance_id": instance["InstanceId"],
                "name": name,
                "state": instance["State"]["Name"],
                "instance_type": instance["InstanceType"],
                "ami_id": instance.get("ImageId", ""),
                "platform": instance.get("Platform", "linux"),
                "architecture": instance.get("Architecture", ""),
                "vpc_id": instance.get("VpcId", ""),
                "subnet_id": instance.get("SubnetId", ""),
                "private_ip": instance.get("PrivateIpAddress", ""),
                "public_ip": instance.get("PublicIpAddress", ""),
                "private_dns": instance.get("PrivateDnsName", ""),
                "public_dns": instance.get("PublicDnsName", ""),
                "availability_zone": instance["Placement"]["AvailabilityZone"],
                "launch_time": instance["LaunchTime"].isoformat(),
                "security_groups": security_groups,
                "tags": tags,
                "monitoring": instance.get("Monitoring", {}).get("State", "disabled"),
                "ebs_optimized": instance.get("EbsOptimized", False),
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
        if error_code == "InvalidInstanceID.NotFound":
            return {
                "success": False,
                "error": {
                    "code": "AWS_NOT_FOUND",
                    "message": f"Instance '{instance_id}' not found",
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
