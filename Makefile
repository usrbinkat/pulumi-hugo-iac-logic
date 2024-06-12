# Define variables
HUGO_SOURCE = hugo
HUGO_DESTINATION = public
PULUMI_STACK = webdev

# Define default target
.PHONY: all
all: build_hugo deploy_infrastructure sync_s3 invalidate_cache

# Target to build the Hugo site
.PHONY: build_hugo
build_hugo:
	hugo --source $(HUGO_SOURCE) --destination $(HUGO_DESTINATION) --cleanDestinationDir

# Target to deploy infrastructure with Pulumi
.PHONY: deploy_infrastructure
deploy_infrastructure:
	pulumi login
	pulumi stack select --create $(PULUMI_STACK)
	pulumi up --skip-preview --continue-on-error --refresh=true

# Target to sync Hugo public directory with S3
.PHONY: sync_s3
sync_s3:
	aws s3 sync ./$(HUGO_DESTINATION) s3://$$(pulumi stack output bucket_name)

# Target to invalidate CloudFront cache
.PHONY: invalidate_cache
invalidate_cache:
	aws cloudfront create-invalidation --distribution-id $$(pulumi stack output distribution_id) --paths "/*"

# Clean up build artifacts
.PHONY: clean
clean:
	rm -rf $(HUGO_DESTINATION)
