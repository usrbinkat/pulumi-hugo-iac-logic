import pulumi
import subprocess
import os
import boto3
config = pulumi.Config()

# Get current working directory
cwd = os.getcwd()
build_hugo = config.get_bool("build") or True
path_hugo = config.get("buildDir") or os.path.join(cwd, "hugo")
path_deploy = config.get("deployDir") or "public"
index_document = config.get("indexDoc") or "index.html"
error_document = config.get("errorDoc") or "404.html"

# Log the configuration settings.
artifacts = {
    "build": build_hugo,
    "buildDir": path_hugo,
    "deployDir": path_deploy,
    "indexDoc": index_document,
    "errorDoc": error_document
}
pulumi.log.info(f"Hugo build configuration: {artifacts}")
pulumi.export("artifacts", artifacts)

# Function to build hugo site via a subprocess command.
def hugo_build_website():
    if not pulumi.runtime.is_dry_run():
        pulumi.log.info("Building the website using Hugo CLI.")
        subprocess.run(
            ["hugo", "--source", path_hugo, "--destination", path_deploy],
            stdout=subprocess.PIPE,
            cwd=path_hugo,
            check=True,
            shell=True,
        )
    else:
        pulumi.log.warn("Skipping Hugo build because this is a dry-run.")

# Build the Hugo website if pulumi config `build` is set to true.
if build_hugo:
    hugo_build_website()

# Function to create an invalidation
def create_invalidation(id):
    # Don't bother invalidating unless it's an actual deployment.
    if pulumi.runtime.is_dry_run():
        print("This is a Pulumi preview, so skipping cache invalidation.")
        return

    client = boto3.client("cloudfront")
    result = client.create_invalidation(
        DistributionId=id,
        InvalidationBatch={
            "CallerReference": f"invalidation-{time.time()}",
            "Paths": {
                "Quantity": 1,
                "Items": ["/*"],
            },
        },
    )

    print(f"Cache invalidation for distribution {id}: {result['Invalidation']['Status']}.")

# Register the invalidation function to run at the end of the program
if public_read:
    cdn.id.apply(lambda id: atexit.register(lambda: create_invalidation(id)))
