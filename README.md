# UKCEH Tech for Nature website

The public website of UKCEH's automated biodiversity monitoring team: our technology, projects, stories, news, fieldwork diaries and how-to guides for partners. It brings together the old AMBER dashboard and WildSense sites, and isn't tied to any one project.

Built with [Quarto](https://quarto.org) and published on GitHub Pages: every change to `main` goes live a few minutes later.

## Adding things

| To add | How |
|---|---|
| A **story, news item or fieldwork diary** from a partner | They sign in to the [Share your story form](https://connect-apps.ceh.ac.uk/tech-for-nature-share/) with their own login (the team makes logins on the approvals page) and fill it in. The team approves it, and it's published automatically. |
| The same, written by the team | Use the form too, or add a folder by hand: see [CONTRIBUTING.md](CONTRIBUTING.md). |
| A **project** | a folder in `projects/` with an `index.qmd` (copy an existing one) |
| A **team member** or **partner** | `about/team.qmd`, `about/partners.qmd` (photos and logos in `assets/`) |
| A **how-to guide** | a `.qmd` file in `how-to/`, linked from `how-to/index.qmd` |

`how-to/upload.qmd` and `how-to/sites.qmd` are **copied automatically** from the toolkit's guides ([ceh-biomonitoring](https://github.com/NERC-CEH/ceh-biomonitoring) `docs/`) by `tools/sync_howtos.py`, at every build and every Monday. Edit them there, not here.

## The layout

```
index.qmd            home page
technology/          AMI, LepiSense, sound recorders, bat detectors, other
projects/            one folder per project
map/                 where we work (deployments.json: country totals; no UK site names)
stories/ news/ diaries/   one folder per post: index.md + its photos
how-to/              partner guides (upload.qmd, sites.qmd copied from the toolkit)
about/               about, team, partners and funders, contact
assets/              theme (UKCEH colours, Arial), logo, people's photos, partner logos
templates/post.md    a starting point for a post written by hand
tools/               sync_howtos.py
_quarto.yml          menus and settings (the site's name is here and in _variables.yml)
```

## Building it on your computer

Install [Quarto](https://quarto.org/docs/get-started/) (the ceh-biomonitoring installer includes it), then:

```bash
quarto preview          # opens the site and refreshes as you edit
quarto render           # builds it into _site/
```

## Publishing (set up once)

1. Repo **Settings → Pages → Source: GitHub Actions**. `.github/workflows/publish.yml` then builds and publishes on every push to `main`.
2. Keep **videos off the repo**: link YouTube, Vimeo or Google Drive instead. Photos should be under about 500 KB (the form shrinks them automatically).
3. **Renaming the site:** change `title` in `_quarto.yml`, `name` and `full-name` in `_variables.yml`, the site address (`site-url`), and the form's and approvals' `WEBSITE_URL`.

The form and approvals apps live in the private repo (`ceh-biomonitoring-internal/website_submissions/`).
