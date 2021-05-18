# Contributing Guidelines

## Bug-fix/Feature process

* First of all, please create an issue if not exist already. This will help create the visibility among the team to discuss further.
* Always used the `dev`/`devel` branch to checkout from for a feature/bug-fix and then create PR against it.

## Git branching process

* `master`/`main` branch is only reserved for stable versions, so it should be only used for release purpose.
* Most bug fixes and features should be merged only onto `dev`. This will be implemented by opening PR reviews against this branch.

## Nextflow-specific process

Some specifications to make Nextflow pipelines structure standard across the organization.
 
* Tool/software dependency of a pipeline are handled by combination of conda and docker (`env.yml` + `Dockerfile`)
* Try to make the tool versions very specific in `env.yml` file. Ex - `samtools==1.12`
* Try to add test profiles for each of the features making into the pipeline and also make sure they are part of github-actions Continues-Integration (CI) test (`.github/ci.yml`)
* For test profiles it will be needing small datasets, as they quickly need to test in CI. If the dataset is less than few KB keep them under `testdata` in same repo as pipeline or move them to appropriate places in `s3://lifebit-featured-datasets/pipelines/`

## Release process

Checklist - 
* Version bump in all the places
  * In nextflow.config
  * In VERSION file
  * Change the tag for containers used (should be same with the VERSION file)
* Add release note to the changelog.md

NOTE: The docker container with VERSION will be automatically build and pushed to quay.io 
