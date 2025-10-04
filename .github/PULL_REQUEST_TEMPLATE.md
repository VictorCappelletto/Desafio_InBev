## Description

<!-- Provide a clear and concise description of what this PR does -->



## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code style update (formatting, renaming)
- [ ] Refactoring (no functional changes)
- [ ] Configuration change
- [ ] Test update

## Related Issues

<!-- Link to related issues, if any -->

Closes #
Related to #

## Checklist

### Code Quality

- [ ] Code follows SOLID principles
- [ ] Type hints are used consistently
- [ ] Functions have docstrings (Google style)
- [ ] No hardcoded credentials or secrets
- [ ] Code is formatted with `black` and `isort`

### Testing

- [ ] Unit tests added/updated
- [ ] All tests pass locally (`poetry run task test`)
- [ ] Coverage maintained or improved
- [ ] Manual testing performed (if applicable)

### Documentation

- [ ] README updated (if needed)
- [ ] Code comments added where necessary
- [ ] MkDocs updated (if applicable)

### DAGs (if applicable)

- [ ] DAG follows naming convention (`*_solid`)
- [ ] Tags are appropriate
- [ ] Logging is structured (uses `utils.logger`)
- [ ] Error handling implemented
- [ ] Configuration via environment variables
- [ ] Validated with `python dags/your_dag.py`

### Security

- [ ] No secrets in code
- [ ] Environment variables used for sensitive configs
- [ ] Placeholders used in examples/docs
- [ ] Safe `__repr__` methods (no secret exposure)

## Screenshots

<!-- If applicable, add screenshots to help explain your changes -->



## Testing Instructions

<!-- Describe how reviewers can test your changes -->

```bash
# Example commands to test
astro dev start
# Navigate to http://localhost:8080
# ...
```

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance may be affected (explain below)

<!-- If affected, explain: -->



## Deployment Notes

<!-- Any special deployment considerations? -->

- [ ] No special deployment steps needed
- [ ] Requires environment variable changes (list below)
- [ ] Requires database migration
- [ ] Requires Airflow restart

<!-- If special steps needed, list them: -->



## Additional Notes

<!-- Any other information that reviewers should know -->



---

## Automated Checks

<!-- These will be filled automatically by CI -->

- CI Status: pending
- Test Coverage: pending
- Security Scan: pending
- DAG Validation: pending

---

**Reviewer**: @victorcappelleto
**Estimated Review Time**: <!-- e.g., 15 min, 1 hour -->
