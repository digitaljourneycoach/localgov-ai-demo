# LocalGov demo: bins and recycling

Example content for the "Bins, recycling and waste" section of a typical
London borough council website. It uses the standard LocalGov Drupal service
content types, so it shows off the services navigation, breadcrumbs, top
tasks and related links, and gives the AI features realistic pages to work
with.

## What it creates

```
Bins, recycling and waste                  (service landing page)
├── Bin collections                        (service sub-landing page)
│   ├── Find your bin collection day
│   ├── Report a missed bin collection
│   ├── Christmas and bank holiday collections
│   ├── Order a new or replacement bin
│   ├── Bin collections for flats
│   ├── Assisted bin collections
│   └── Clinical waste collections
├── Recycling                              (service sub-landing page)
│   ├── What goes in your recycling bin
│   ├── Food waste recycling
│   ├── Recycling batteries, electricals and textiles
│   └── Reuse and recycling centres
├── Garden waste collections
├── Book a bulky waste collection
├── Street cleaning and fly-tipping        (service sub-landing page)
│   ├── Report fly-tipping
│   ├── Report a street cleaning problem
│   └── Report graffiti
└── Business waste and recycling
```

That is 1 landing page, 3 sub-landing pages and 17 service pages.

## Usage

```bash
# Creates the content when the module is installed.
ddev drush en localgov_demo_bins -y

# Re-run after editing content/bins_and_recycling.yml. Updates the
# existing pages rather than creating duplicates.
ddev drush localgov-demo-bins:import

# Delete the pages. Uninstalling the module also deletes them.
ddev drush localgov-demo-bins:remove
```

## Editing the content

All the text is in `content/bins_and_recycling.yml`. Links written as
`node:<id>` point to another page in the file. The "start" buttons on
transactional pages (for example "Report a missed collection") link to
placeholder paths such as `/report-missed-bin`, because the demo site has no
real forms behind them.

Phone numbers use the Ofcom range reserved for drama (020 7946 0xxx), and
names and addresses are fictional.
