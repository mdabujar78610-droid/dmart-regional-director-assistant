# Changelog

All notable project updates are recorded here.

## 2026-11-12

### Fixed
- Replaced the deprecated pandas `.dt.dayofweek` accessor with `.dt.day_of_week` in the Part A cleaning and acceptance scripts.

### Validated on the baseline commit
- GitHub Actions workflow run [#43142990496](https://github.com/mdabujar78610-droid/dmart-regional-director-assistant/actions/runs/43142990496) completed successfully on commit `445006102bf12eb3c095be6bc5aa2186da65f724`.
- Part A cleaning and acceptance checks passed; the pipeline cleaned 453 raw rows to 450 rows, removed 3 exact duplicates, and regenerated the analysis reports.
- Pytest: 2 passed.
- Golden evaluation: 37 of 37 cases passed; the evaluation runner generated a GO release decision for that run.
- The workflow emitted pandas deprecation warnings in the two weekday-accessor locations. The cleanup above addresses those source locations; the cleanup branch still requires a fresh CI run before its own release status can be called validated.

### Notes
- The datasets are synthetic practice data, not actual DMart operational records.
- The baseline workflow uploaded its generated validation artifacts to the Actions run; those generated files were not automatically committed to the repository.
