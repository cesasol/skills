# Advanced Patterns — GitLab CI Reference

Container Registry management and Release pipeline patterns.
Read `_common.md` for shared patterns.

Source: <https://docs.gitlab.com/ci/yaml/>

## Container Registry

### Push with SHA + branch tags

```yaml
.registry-login: &registry-login
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"

push:latest:
  stage: deploy
  <<: *registry-login
  script:
    - docker pull "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
    - docker tag "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" "$CI_REGISTRY_IMAGE:latest"
    - docker push "$CI_REGISTRY_IMAGE:latest"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Cleanup old images

```yaml
cleanup:registry:
  stage: .post
  image: registry.gitlab.com/gitlab-org/cli:latest
  script:
    - glab api "projects/$CI_PROJECT_ID/registry/repositories" | jq '.[].id' | xargs -I{} glab api "projects/$CI_PROJECT_ID/registry/repositories/{}/tags" --method DELETE --field name_regex_delete='.*' --field keep_n=10
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## Release Pipelines

Source: <https://docs.gitlab.com/ci/yaml/#release>
Source: <https://docs.gitlab.com/ci/resource_groups/>

### GitLab Release job

```yaml
release:
  stage: deploy
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  needs: [build]
  script:
    - echo "Creating release $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    name: 'Release $CI_COMMIT_TAG'
    description: './CHANGELOG.md'
  rules:
    - if: $CI_COMMIT_TAG
```

For release operations via CLI (creating MRs, tagging, changelogs), use the `glab` skill.

## Deployment Environments

Source: <https://docs.gitlab.com/ci/environments/>

### Production (auto-deploy on main)

```yaml
deploy:production:
  stage: deploy
  needs: [build]
  environment:
    name: production
    url: https://your-app.example.com
  script:
    - ./deploy.sh production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: on_success
  resource_group: production  # serialize deploys — prevents race conditions
```

### Preview environments (MR-based)

```yaml
deploy:preview:
  stage: deploy
  needs: [build]
  environment:
    name: preview/$CI_COMMIT_REF_SLUG
    url: https://${CI_COMMIT_REF_SLUG}.preview.example.com
    on_stop: deploy:preview:stop
    auto_stop_in: 1 week
  script:
    - ./deploy.sh preview "$CI_COMMIT_REF_SLUG"
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
      when: manual
      allow_failure: true

deploy:preview:stop:
  stage: deploy
  environment:
    name: preview/$CI_COMMIT_REF_SLUG
    action: stop
  script:
    - ./teardown.sh preview "$CI_COMMIT_REF_SLUG"
  rules:
    - if: $CI_PIPELINE_SOURCE == 'merge_request_event'
      when: manual
      allow_failure: true
```

## Resource Groups

Source: <https://docs.gitlab.com/ci/resource_groups/>

Use `resource_group:` to serialize jobs that must not run concurrently (e.g., production deploys):

```yaml
deploy:production:
  resource_group: production  # only one deploy:production runs at a time
```

## Environment Approval Gates (Premium/Ultimate)

Protected environments require manual approval before deployment. Configure in:
**Settings → CI/CD → Protected environments**

This is a GitLab Premium/Ultimate feature. On Free tier, use `when: manual` instead.
