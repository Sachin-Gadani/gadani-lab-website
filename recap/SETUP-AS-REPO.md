# Moving this into its own GitHub repository

This project was developed inside a branch of another repository because the
session that wrote it could not create a new GitHub repo (the GitHub App had no
repo-creation permission). The code is standalone — it has no dependency on the
repository it currently sits in.

To give it its own home:

```bash
# from a clone of the host repo, on the branch this directory lives in
cp -r recap /path/to/recap && cd /path/to/recap
rm SETUP-AS-REPO.md

git init -b main
git add .
git commit -m "Initial commit: local audio-to-executive-summary pipeline"

gh repo create Sachin-Gadani/recap --private --source=. --remote=origin --push
```

Then delete the `recap/` directory from the host repository's branch, and drop
the `- recap` line that was added to its `_config.yaml` exclude list.

If you would rather keep the git history that was made here:

```bash
git subtree split --prefix=recap -b recap-only
git clone . /path/to/recap --branch recap-only --single-branch
```
