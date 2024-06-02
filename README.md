# Pulumi Next Level - IaC Logic

> Based on the blog from [Christian Nunciato](https://github.com/cnunciato) [Next-level IaC: Drop those wrapper scripts and let your language do that for you](https://www.pulumi.com/blog/next-level-iac-pulumi-runtime-logic)

Exercise in building and deploying a website with Pulumi.

## Before you start

Launch a Github Codespace, or start this lab in VSCode with the Devcontainer extension installed.

## Steps:

### Pulumi Setup

1. Pulumi Login

```bash
pulumi login
```

### Create a new Hugo site

2. Create a new hugo project following the [official quickstart](https://gohugo.io/getting-started/quick-start/)

```bash
hugo new site site && cd site
```

3. Add a theme to the site

```bash
# Add the Ananke theme
git clone https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke && rm -rf themes/ananke/.git

# Copy the example site content
cp -r themes/ananke/exampleSite/* .
```

4. Add the theme to the site configuration

```bash
echo 'theme = "ananke"' >> hugo.toml
```

5. Test the site locally

```bash
hugo server
```

6. Build the site

```bash
hugo --cleanDestinationDir --destination site/deploy/
```

### Pulumi Project

```bash
mkdir pulumi
pulumi new static-website-aws-python \
      --name next-level-iac \
      --description "deploy a static hugo site to aws s3" \
      --generate-only \
      --dir ./pulumi
```

```bash
pulumi stack select --create webdev
```

Login to AWS

```bash
# for me I use aws sso login cli command
aws sso login
```

Created project 'next-level-iac'


Your new project is ready to go!

To perform an initial deployment, run the following commands:

   1. cd pulumi
   2. python3 -m venv venv
   3. source venv/bin/activate
   4. python -m pip install --upgrade pip setuptools wheel
   5. python -m pip install -r requirements.txt
   6. pulumi stack init

Then, run `pulumi up`
