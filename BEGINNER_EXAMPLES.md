# Beginner examples

These examples are meant for people who do not want to start by reading ontology documentation.

If you want to swap in your own data immediately:

- One numeric CSV column -> start with `profile_series(...)`.
- Wide table with one `timestamp` column and one or more numeric columns -> start with `profile_dataset(df, domain=...)`.
- Irregular long table -> rename columns to `subject`, `timestamp`, `channel`, and `value`, then call `profile_dataset(...)`.
- Editable starter script -> `examples/integrations/pandas_notebook_template.py`.

Built-in beginner examples:

- **Single-column CSV -> report** - one numeric column is enough to get started.
- **Timestamps + missingness -> why irregularity matters** - explicit time gaps change interpretation.
- **Two curves -> similarity verdict** - the smallest possible comparison workflow.
- **Inflation + search interest -> regime shift report** - beginner economics example.
- **Single sensor drift -> structural watchouts** - beginner engineering example.
- **Daily survey sentiment -> irregularity + burstiness** - beginner social-science example.

See the matching notebooks under `examples/notebooks/`.
