"""List S3 buckets in AWS account."""

TOOL_DEFINITION = {
    "name": "aws_list_s3_buckets",
    "display_name": "List S3 Buckets",
    "description": "List all S3 buckets in the account with their creation dates and regions.",
    "tags": ["aws", "s3", "buckets", "list"],
    "input_schema": {
        "type": "object",
        "properties": {
            "aws_access_key_id": {"type": "string"},
            "aws_secret_access_key": {"type": "string"},
            "region": {
                "type": "string",
                "description": "Region for S3 client (buckets are global but client needs region)",
                "default": "us-east-1",
            },
        },
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "buckets": {"type": "array"},
                    "total_count": {"type": "integer"},
                },
            },
        },
    },
}


def _get_boto_session(input_data: dict):
    """Get boto3 session with credentials from input or environment."""
    import boto3

    region = input_data.get("region", "us-east-1")
    if input_data.get("aws_access_key_id") and input_data.get("aws_secret_access_key"):
        return boto3.Session(
            aws_access_key_id=input_data["aws_access_key_id"],
            aws_secret_access_key=input_data["aws_secret_access_key"],
            region_name=region,
        )
    return boto3.Session(region_name=region)


def main(input_data: dict) -> dict:
    """List S3 buckets.

    Args:
        input_data: Dictionary with optional credentials and region

    Returns:
        Dictionary with success status and bucket list or error
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

    try:
        session = _get_boto_session(input_data)
        s3 = session.client("s3")

        response = s3.list_buckets()

        buckets = []
        for bucket in response.get("Buckets", []):
            bucket_info = {
                "name": bucket["Name"],
                "creation_date": bucket["CreationDate"].isoformat(),
                "region": "unknown",
            }

            # Try to get bucket region
            try:
                location = s3.get_bucket_location(Bucket=bucket["Name"])
                bucket_region = location.get("LocationConstraint")
                # None means us-east-1
                bucket_info["region"] = bucket_region if bucket_region else "us-east-1"
            except Exception:
                pass

            buckets.append(bucket_info)

        return {
            "success": True,
            "data": {
                "buckets": buckets,
                "total_count": len(buckets),
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
        if error_code == "AccessDenied":
            return {
                "success": False,
                "error": {
                    "code": "AWS_ACCESS_DENIED",
                    "message": "Access denied. Check IAM permissions for s3:ListAllMyBuckets",
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
