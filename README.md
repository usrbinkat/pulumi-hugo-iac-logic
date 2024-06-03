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

2. Login to AWS

```bash
# for me I use aws sso login cli command
aws sso login
```

### Create a new Hugo site

3. Create a new hugo project following the [official quickstart](https://gohugo.io/getting-started/quick-start/)

```bash
hugo new site site && cd site
```

4. Add a theme to the site

```bash
# Add the Ananke theme
git clone https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke && rm -rf themes/ananke/.git

# Copy the example site content
cp -r themes/ananke/exampleSite/* .
```

5. Add the theme to the site configuration

```bash
echo 'theme = "ananke"' >> hugo.toml
```

6. Test the site locally

```bash
hugo server
```

7. Build the site

```bash
hugo --cleanDestinationDir --destination site/deploy/
```

### Pulumi Project

```bash
mkdir pulumi && pulumi new static-website-aws-python \
      --name next-level-iac \
      --description "deploy a static hugo site to aws s3" \
      --generate-only \
      --dir . --force
```

```bash
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
pulumi stack select --create nextleveliac
```

Then, run `pulumi up`
