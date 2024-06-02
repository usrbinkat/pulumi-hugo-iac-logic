import os
import json
import pulumi
import pulumi_aws as aws
import pulumi_synced_folder as synced_folder
import subprocess

# Constants for default values
DEFAULT_BUILD_DIR = "hugo"
DEFAULT_INDEX_DOC = "index.html"
DEFAULT_ERROR_DOC = "404.html"

# Get current working directory
cwd = os.getcwd()

# Import the program's configuration settings.
config = pulumi.Config()
public_read = config.get_bool("public") or False
path_build = config.get("buildDir") or os.path.join(cwd, DEFAULT_BUILD_DIR)
path_deploy = config.get("deployDir") or os.path.join(path_build, "public")
index_document = config.get("indexDoc") or DEFAULT_INDEX_DOC
error_document = config.get("errorDoc") or DEFAULT_ERROR_DOC

# Log the configuration settings.
artifacts = {
    "buildDir": path_build,
    "deployDir": path_deploy,
    "indexDoc": index_document,
    "errorDoc": error_document
}
pulumi.log.info(f"Configuration settings: {artifacts}")
pulumi.export("artifacts", artifacts)

# Build the website using hugo via a subprocess command.
def hugo_build_website():
    if not pulumi.runtime.is_dry_run():
        pulumi.log.info("Building the website using Hugo CLI.")
        subprocess.run(
            ["hugo", "--source", path_build],
            stdout=subprocess.PIPE,
            cwd=path_build,
            check=True,
            shell=True,
        )
    else:
        pulumi.log.warn("Skipping Hugo build because this is a dry-run.")

hugo_build_website()

# Create an S3 bucket and configure it as a website.
bucket = aws.s3.Bucket(
    "next-level-iac",
    website=aws.s3.BucketWebsiteArgs(
        index_document=index_document,
        error_document=error_document
    ),
)
pulumi.export("bucket_name", bucket.bucket)

# Attach a bucket policy to make the contents publicly readable if configured to do so.
def create_bucket_policy(bucket_name):
    return aws.s3.BucketPolicy(
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

if public_read:
    pulumi.log.info(f"Setting bucket policy for public read access: {bucket.bucket}")
    bucket_policy = create_bucket_policy(bucket.bucket)

# Determine ACL based on publicRead configuration
acl = "public-read" if public_read else "private"

# Sync the website files into the bucket
upload = synced_folder.S3BucketFolder(
    "static",
    bucket_name=bucket.bucket,
    path=path_deploy,
    acl=acl
)

# Export the website URL
url = pulumi.Output.concat("http://", bucket.website_endpoint)
pulumi.export("website_url", url)

# Set ownership controls for the new bucket
ownership_controls = aws.s3.BucketOwnershipControls(
    "ownership-controls",
    bucket=bucket.bucket,
    rule=aws.s3.BucketOwnershipControlsRuleArgs(
        object_ownership="ObjectWriter",
    )
)

# Configure public ACL block on the new bucket
public_access_block = aws.s3.BucketPublicAccessBlock(
    "public-access-block",
    bucket=bucket.bucket,
    block_public_acls=False,
)

# Use a synced folder to manage the files of the website.
bucket_folder = synced_folder.S3BucketFolder(
    "bucket-folder",
    acl=acl,
    bucket_name=bucket.bucket,
    path=path_deploy,
    opts=pulumi.ResourceOptions(depends_on=[
        ownership_controls,
        public_access_block
    ])
)

# Create a CloudFront CDN to distribute and cache the website.
cdn = aws.cloudfront.Distribution(
    "cdn",
    enabled=True,
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
pulumi.export("originURL", pulumi.Output.concat("http://", bucket.website_endpoint))
pulumi.export("originHostname", bucket.website_endpoint)
pulumi.export("cdnURL", pulumi.Output.concat("https://", cdn.domain_name))
pulumi.export("cdnHostname", cdn.domain_name)
