# Pulumi Next Level - IaC Logic

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

### Create a new Hugo static site from templates

3. Create a new hugo project following the [official quickstart](https://gohugo.io/getting-started/quick-start/)

```bash
hugo new site hugo
```

4. Add a theme to your new site

```bash
git clone https://github.com/theNewDynamic/gohugo-theme-ananke.git hugo/themes/ananke && rm -rf hugo/themes/ananke/.git

# Copy the example site content
cp -r hugo/themes/ananke/exampleSite/* ./hugo/
```

5. Add the theme to the site configuration

```bash
echo 'theme = "ananke"' >> hugo/hugo.toml
```

6. Test the site locally

```bash
cd hugo && hugo server
```

7. Build the site

```bash
hugo --source hugo --destination public --cleanDestinationDir
```

### Create or Select a Pulumi Stack

```bash
make
```

## Attribution
Based on the blog from [Christian Nunciato](https://github.com/cnunciato):
* [Next-level IaC: Drop those wrapper scripts and let your language do that for you](https://www.pulumi.com/blog/next-level-iac-pulumi-runtime-logic)
