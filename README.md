# Pulumi Next Level - IaC Logic

> Based on the blog from [Christian Nunciato](https://github.com/cnunciato) [Next-level IaC: Drop those wrapper scripts and let your language do that for you](https://www.pulumi.com/blog/next-level-iac-pulumi-runtime-logic)

Exercise in building and deploying a website with Pulumi.

## Before you start

Launch a Github Codespace, or start this lab in VSCode with the Devcontainer extension installed.

## Steps:

1. Pulumi Login

```bash
pulumi login
```

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
