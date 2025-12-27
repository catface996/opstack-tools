"""List objects in an S3 bucket."""

TOOL_DEFINITION = {
    "name": "aws_list_s3_objects",
    "display_name": "List S3 Objects",
    "description": "List objects in an S3 bucket with optional prefix filtering. Returns object keys, sizes, and last modified dates.",
    "tags": ["aws", "s3", "objects", "list"],
    "input_schema": {
        "type": "object",
        "properties": {
            "bucket": {
                "type": "string",
                "description": "S3 bucket name",
            },
            "prefix": {
                "type": "string",
                "description": "Filter objects by prefix (e.g., 'logs/2024/')",
            },
            "aws_access_key_id": {"type": "string"},
            "aws_secret_access_key": {"type": "string"},
            "region": {"type": "string"},
            "max_keys": {
                "type": "integer",
                "description": "Maximum number of objects to return",
                "default": 1000,
            },
        },
        "required": ["bucket"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "bucket": {"type": "string"},
                    "prefix": {"type": "string"},
                    "objects": {"type": "array"},
                    "total_count": {"type": "integer"},
                    "truncated": {"type": "boolean"},
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
    """List objects in an S3 bucket.

    Args:
        input_data: Dictionary with bucket, optional prefix, credentials

    Returns:
        Dictionary with success status and object list or error
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

    bucket = input_data.get("bucket")
    if not bucket:
        return {
            "success": False,
            "error": {
                "code": "AWS_INVALID_INPUT",
                "message": "bucket is required",
            },
        }

    prefix = input_data.get("prefix", "")
    max_keys = input_data.get("max_keys", 1000)

    try:
        session = _get_boto_session(input_data)
        s3 = session.client("s3")

        params = {
            "Bucket": bucket,
            "MaxKeys": max_keys,
        }
        if prefix:
            params["Prefix"] = prefix

        response = s3.list_objects_v2(**params)

        objects = []
        for obj in response.get("Contents", []):
            objects.append({
                "key": obj["Key"],
                "size_bytes": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
                "storage_class": obj.get("StorageClass", "STANDARD"),
            })

        return {
            "success": True,
            "data": {
                "bucket": bucket,
                "prefix": prefix,
                "objects": objects,
                "total_count": len(objects),
                "truncated": response.get("IsTruncated", False),
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
        if error_code == "NoSuchBucket":
            return {
                "success": False,
                "error": {
                    "code": "AWS_NOT_FOUND",
                    "message": f"Bucket '{bucket}' not found",
                },
            }
        elif error_code == "AccessDenied":
            return {
                "success": False,
                "error": {
                    "code": "AWS_ACCESS_DENIED",
                    "message": f"Access denied to bucket '{bucket}'",
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
