import os
import json
import subprocess
import atexit
import time
import boto3
import pulumi
import pulumi_aws as aws
import pulumi_synced_folder as synced_folder

# Pulumi configuration settings
config = pulumi.Config()

# Set S3 bucket configuration settings
public_read = config.get_bool("public") or False
error_document = config.get("errorDoc") or "404.html"
index_document = config.get("indexDoc") or "index.html"

# Set path of static site content to deploy
path_hugo = config.get("hugoDir") or "hugo"
path_deploy = config.get("siteDir") or "public"

# Create an S3 bucket and configure it as a website.
bucket = aws.s3.Bucket(
    "next-level-iac",
    website=aws.s3.BucketWebsiteArgs(
        index_document=index_document,
        error_document=error_document
    ),
)

# Configure public ACL block on the new bucket
public_access_block = aws.s3.BucketPublicAccessBlock(
    "public-access-block",
    bucket=bucket.bucket,
    block_public_acls=False,
)

# Set ownership controls for the new bucket
ownership_controls = aws.s3.BucketOwnershipControls(
    "ownership-controls",
    bucket=bucket.bucket,
    rule=aws.s3.BucketOwnershipControlsRuleArgs(
        object_ownership="ObjectWriter",
    )
)

# Attach a bucket policy to make the contents publicly readable if configured to do so.
def create_bucket_policy(bucket_name):
    """
    Creates an S3 bucket policy that allows public read access to objects in the bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.

    Returns:
        pulumi.Output: The created S3 bucket policy resource.
    """
    # Create the S3 bucket policy resource
    bucket_policy = aws.s3.BucketPolicy(
        "hugo-bucket-policy",
        bucket=bucket_name,
        policy=bucket_name.apply(lambda name: json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{name}/*"]
            }]
        }))
    )
    return bucket_policy

# Log bucket name and set the bucket policy based on the public_read configuration.
bucket.bucket.apply(lambda name: pulumi.log.info(f"Bucket policy public read access: {name}:policy:{public_read}"))

# Check if the public_read variable is True
if public_read:
    # Create a bucket policy with public read access
    bucket_policy = create_bucket_policy(bucket.bucket)
    # Set the ACL to public-read
    acl = "public-read"
else:
    # Set the bucket policy to None
    bucket_policy = None
    # Set the ACL to private
    acl = "private"

# Sync directory hugo/public files into the bucket
upload = synced_folder.S3BucketFolder(
    "sync-static-site",
    bucket_name=bucket.bucket,
    path=path_deploy,
    # ACL: Set based on public_read configuration.
    acl=acl,
    opts=pulumi.ResourceOptions(
        depends_on=[
            bucket,
            ownership_controls,
            public_access_block
        ]
    ),
)

# Create a CloudFront CDN to distribute and cache the website.
cdn = aws.cloudfront.Distribution(
    "hugo-site-cdn",
    enabled=public_read,
    origins=[
        aws.cloudfront.DistributionOriginArgs(
            origin_id=bucket.arn,
            domain_name=bucket.website_endpoint,
            custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                origin_protocol_policy="http-only",
                http_port=80,
                https_port=443,
                origin_ssl_protocols=["TLSv1.2"],
            ),
        )
    ],
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        target_origin_id=bucket.arn,
        viewer_protocol_policy="redirect-to-https",
        allowed_methods=[
            "GET",
            "HEAD",
            "OPTIONS",
        ],
        cached_methods=[
            "GET",
            "HEAD",
            "OPTIONS",
        ],
        default_ttl=600,
        max_ttl=600,
        min_ttl=600,
        forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=True,
            cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="all",
            ),
        ),
    ),
    price_class="PriceClass_100",
    custom_error_responses=[
        aws.cloudfront.DistributionCustomErrorResponseArgs(
            error_code=404,
            response_code=404,
            response_page_path=f"/{error_document}",
        )
    ],
    restrictions=aws.cloudfront.DistributionRestrictionsArgs(
        geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none",
        ),
    ),
    viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True,
    ),
)

# Export the CDN URL and hostname for the website.
pulumi.export("bucket_name", bucket.bucket)
pulumi.export("bucketHostname", bucket.website_endpoint)
pulumi.export("cdnHostname", cdn.domain_name)
pulumi.export("bucketURL", pulumi.Output.concat("http://", bucket.website_endpoint))
pulumi.export("cdnURL", pulumi.Output.concat("https://", cdn.domain_name))
