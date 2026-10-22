# LocalGov Drupal AI demo

A [LocalGov Drupal](https://localgovdrupal.org/) site with the Drupal AI modules added,
built to show council web teams what AI can do on a LocalGov site today. It started as
the LocalGov version of the Drupal AI workshop at DrupalCon Rotterdam, and it is the site
used for the live demos in the LocalGov Drupal webinar about that workshop.

It shows three things:

| Demo | What a visitor or editor sees | Built with |
|---|---|---|
| **Ask the website** | Residents ask a question in their own words at `/ask` and get an answer written from the council's pages, with the source pages listed. | AI Search, AI Answers, a pgvector database |
| **Check a page** | Editors ask an AI reviewer to check a page against the house style. It scores the page and quotes every problem, and the suggestions are listed in the edit form sidebar. | AI Content Review, plus the custom `localgov_ai_review_sidebar` module |
| **Realistic content** | A full "Bins, recycling and waste" section, so the AI features have real-looking council pages to work with. | The custom `localgov_demo_bins` module |

It also contains the slide deck for the webinar, in `web/drupalcon-rotterdam/`.

This is a demo, not a product. The custom modules are small and written for this site.
Use it to try things out, and please share what you find with the LocalGov Drupal
community.

## Contents

- [What you need](#what-you-need)
- [1. Install the site](#1-install-the-site)
- [2. Connect an AI provider](#2-connect-an-ai-provider)
- [3. Add the example content](#3-add-the-example-content)
- [4. Ask the website (AI search at /ask)](#4-ask-the-website-ai-search-at-ask)
- [5. Check a page (AI Content Review)](#5-check-a-page-ai-content-review)
- [6. The webinar slide deck](#6-the-webinar-slide-deck)
- [What is in this repository](#what-is-in-this-repository)
- [Troubleshooting](#troubleshooting)
- [Starting again](#starting-again)

## What you need

- [DDEV](https://ddev.com/get-started/) with Docker (or OrbStack, Colima or Rancher
  Desktop). Everything else runs inside DDEV.
- An API key for an AI provider. The demo was built with an
  [OpenAI](https://platform.openai.com/api-keys) key. Anthropic and amazee.ai providers
  are installed too, but AI search needs an **embeddings** model, which Anthropic does
  not offer, so OpenAI or amazee.ai is the easiest choice.
- Some API credit. Indexing the site and trying the demos makes a few hundred small
  requests.

## 1. Install the site

Clone the repository and start DDEV:

```bash
git clone https://github.com/digitaljourneycoach/localgov-ai-demo.git
cd localgov-ai-demo
ddev start
ddev composer install
```

`ddev start` starts three containers: the web server, MariaDB, and a PostgreSQL database
with the [pgvector](https://github.com/pgvector/pgvector) extension, which AI search uses
to store its vectors (see [.ddev/docker-compose.postgres.yaml](.ddev/docker-compose.postgres.yaml)).
There is no `composer.lock` in this repository, so `composer install` resolves the
latest matching versions. That takes a few minutes the first time.

Install LocalGov Drupal and log in:

```bash
ddev drush site:install localgov --site-name="LocalGov AI Demo" --account-name=admin --account-pass=admin -y
ddev launch
```

The site runs at https://localgov-ai-demo.ddev.site with the `localgov_scarfolk` theme.
Log in with `admin` / `admin`, or get a one-time login link with `ddev drush user:login`.

Check that the vector database is running:

```bash
ddev exec -s postgres psql -U vectordb -d default -c "select extname from pg_extension"
```

The list should include `vector`.

## 2. Connect an AI provider

Every AI feature in the demo goes through the [AI module](https://www.drupal.org/project/ai),
which talks to AI services through provider modules. Enable the AI module, the providers
and the modules that store API keys:

```bash
ddev drush pm:install ai ai_provider_openai ai_provider_anthropic ai_provider_amazeeio key easy_encryption ai_logging -y
```

Then add your key and choose the default models:

1. Go to **Configuration › AI Setup and Configuration › Providers**
   ([/admin/config/ai/providers](https://localgov-ai-demo.ddev.site/admin/config/ai/providers))
   and set up **OpenAI**. Paste your API key when it asks for one. It is stored as a Key
   entity, encrypted by Easy Encryption, not in plain configuration.
2. Go to **AI Settings** ([/admin/config/ai/settings](https://localgov-ai-demo.ddev.site/admin/config/ai/settings))
   and choose the default models. The demo uses:

   | Operation type | Provider and model |
   |---|---|
   | Chat | OpenAI `gpt-5.2` (or any current GPT model) |
   | Chat with tools / function calling | OpenAI `gpt-5.2` |
   | Embeddings | OpenAI `text-embedding-3-small` |

3. Test it: go to **AI Setup and Configuration › AI API Explorer › Chat Generation**,
   type a question and check that you get an answer.

With AI Logging enabled, every request and response is logged at
[/admin/config/ai/logging/collection](https://localgov-ai-demo.ddev.site/admin/config/ai/logging/collection).
Turn on logging of requests and responses in its settings. It is the easiest way to see
what the AI was sent and what it answered.

Choose the providers **before** step 4: the AI search recipe reads the default chat and
embeddings models when it is applied.

[docs/01_setup.md](docs/01_setup.md) explains providers, the AI dashboard, the AI
Explorer, logging and guardrails in more detail. It was written for the workshop's
university site, so its URLs and recipe paths do not match this site, but the screens are
the same.

## 3. Add the example content

The AI features are only as good as the content they work from, so the demo needs
realistic pages.

### LocalGov Drupal's own demo content (optional)

LocalGov Drupal ships a demo content module with guides, directories, news and events.
Install it if you want the AI search to answer questions such as *How do I order a copy
of a birth certificate?*:

```bash
ddev drush pm:install localgov_demo -y
```

If Drush cannot find it, add it first with `ddev composer require drupal/localgov_demo`.

### Bins, recycling and waste

The custom module [`localgov_demo_bins`](web/modules/custom/localgov_demo_bins/) creates
a full "Bins, recycling and waste" section for a fictional London borough: 1 service
landing page, 3 sub-landing pages and 17 service pages, using the standard LocalGov
service content types.

```bash
ddev drush pm:install localgov_demo_bins -y
```

The pages are created when the module is installed. Open
[/bins-recycling-and-waste](https://localgov-ai-demo.ddev.site/bins-recycling-and-waste)
to see them, with the services navigation, top tasks and related links.

All the text is in [content/bins_and_recycling.yml](web/modules/custom/localgov_demo_bins/content/bins_and_recycling.yml).
After editing it, update the pages in place, or remove them:

```bash
ddev drush localgov-demo-bins:import   # updates the existing pages, no duplicates
ddev drush localgov-demo-bins:remove   # deletes them (uninstalling does the same)
```

Phone numbers use the Ofcom drama range and names and addresses are fictional. See the
[module README](web/modules/custom/localgov_demo_bins/README.md) for the full page list.

## 4. Ask the website (AI search at /ask)

Residents ask a question in plain words and get an answer written from the site's own
pages, with links to the pages it used. This is retrieval-augmented generation (RAG):

1. Every published page is split into chunks, and each chunk is turned into an
   embedding (a list of numbers that captures its meaning) and stored in pgvector.
2. A question is turned into an embedding too, and the closest chunks are found.
3. An AI agent writes the answer from those chunks only, and lists the source pages.

The full background is in [docs/03_ai_search.md](docs/03_ai_search.md) (written for the
workshop site) and the LocalGov differences are in
[docs/05_ai_search_lgd.md](docs/05_ai_search_lgd.md). The short version follows.

### Apply the recipe

`drupal/ai_recipe_answers` is already in `composer.json`. It brings AI Search, the
PostgreSQL vector database provider, AI Answers and AI Agents with it.

```bash
ddev drush recipe ../recipes/ai_recipe_answers
ddev drush cache:rebuild
```

The recipe creates a Search API server on the pgvector database, an index called
`content_vector` with every node bundle, and a **Content Search Agent** that answers
from the index. The vector size (1536 for `text-embedding-3-small`) is set from your
default embeddings model.

### Adjust it for LocalGov

These changes were made by hand on the demo site. See
[docs/05_ai_search_lgd.md](docs/05_ai_search_lgd.md) for the details.

1. **Published pages only.** Edit the `content_vector` index at
   **Configuration › Search and metadata › Search API**, open **Processors** and enable
   **Entity status**, so drafts and unpublished pages are never used in an answer.
2. **Reference view mode.** If the index or AI Answers settings refer to a *Card* view
   mode, use **Teaser** instead: LocalGov Drupal has no Card view mode. LocalGov already
   has a *Search index* display for every content type, so nothing else needs
   configuring.
3. **The agent.** Edit the Content Search Agent at
   **AI Setup and Configuration › Agents** and make its instructions talk about the
   council's website and services. Tell it to suggest contacting the council when the
   website has no answer, and never to ask for personal details.
4. **Permissions.** Let visitors use it:

   ```bash
   ddev drush role:perm:add anonymous 'use ai answers'
   ddev drush role:perm:add authenticated 'use ai answers'
   ```

### Index the content

The embeddings requests for a whole site can hit your provider's rate limit. When that
happens, the log shows `Request rate limit has been exceeded` and some chunks are
skipped, **although Search API still reports 100%**. On a new or low-tier OpenAI key,
index two items at a time:

```bash
ddev drush search-api:clear content_vector
until ddev drush search-api:status content_vector | grep -q '100%'; do
  ddev drush search-api:index content_vector --limit=2 --batch-size=2; sleep 12
done
ddev drush watchdog:show --type=ai_search
```

On the demo site this takes about 30 minutes and gives 426 chunks for 137 published
pages. If your key has higher limits, a plain `ddev drush search-api:index content_vector`
is fine. Either way, check the watchdog output for rate limit errors afterwards.

Test retrieval before you build the page: go to **AI Setup and Configuration ›
AI Explorer › Vector DB Explorer**, choose the `content_vector` index and search for
*missed bin*. You should see chunks from the bins pages, each with a score.

### Build the Ask page

1. Create a **Services page** called `Ask the council` with the URL alias `/ask`. (LocalGov
   has no basic page type.) A one-line introduction is enough as its body.
2. Go to **Structure › Block layout** for `localgov_scarfolk` and place these blocks in
   the **Content** region, visible only on `/ask`:
   1. **Main page content** (already there)
   2. **AI Answers: Question**, with the placeholder `Ask a question about council
      services` and suggested questions such as:
      ```
      When is my bin collected?
      How do I report a missed bin?
      What can I put in my recycling bin?
      How do I order a copy of a birth certificate?
      ```
   3. **AI Answers: Answer**, agent *Content Search Agent*, show references off
   4. **AI Answers: Sources**
3. Optionally place another **AI Answers: Question** block in **Footer first**, titled
   `Ask the council`, with the cross-page URL `/ask`, hidden on `/ask`. It lets
   visitors ask from any page.

### Fix the layout in LocalGov themes

Out of the box, the AI Answers blocks run full width in LocalGov themes instead of
sitting inside the page container, and the suggested question buttons have white text
on no background. The custom module
[`localgov_ai_answers_layout`](web/modules/custom/localgov_ai_answers_layout/) fixes
both with a small stylesheet that it attaches only to the AI Answers blocks:

```bash
ddev drush pm:install localgov_ai_answers_layout -y
ddev drush cache:rebuild
```

### Try it

Log out (or use a private window) and open
[/ask](https://localgov-ai-demo.ddev.site/ask). Try:

- *When is my bin collected?*
- *How do I report a missed bin?*
- *What can I put in my recycling bin?*
- *Can I put pizza boxes in my recycling?* (a question no page answers word for word)
- *Who won the football World Cup in 2014?* It should decline, because the answer is
  not on the website.

Each answer should have inline citations and a list of source pages. Open
[AI Logs](https://localgov-ai-demo.ddev.site/admin/config/ai/logging/collection) to
follow the request: the question, the chunks the search tool returned and the answer.
On the [AI Logging settings](https://localgov-ai-demo.ddev.site/admin/config/ai/logging/settings)
page, add `ai_agents_runner_` to the thread tag prefixes so that the agent's steps are
grouped.

Known issues:

- For an off-topic question the agent sometimes still cites low-scoring pages that it
  says are not relevant. Setting a minimum score on the RAG tool helps (see *More to
  try* in [docs/03_ai_search.md](docs/03_ai_search.md)).
- The `/ask` page itself is indexed, because it is a services page.

## 5. Check a page (AI Content Review)

[AI Content Review](https://www.drupal.org/project/ai_content_review) lets an editor ask
an AI reviewer to check a page against written criteria, such as a house style. The
reviewer gives each criterion a score and a Pass, Warning or Fail grade, quotes every
problem and suggests a correction. Editors accept or ignore each suggestion and make the
changes themselves. Reviews run only when an editor asks; never on save.

### Install

```bash
ddev drush pm:install ai_content_review ai_agents token token_entity_render -y
```

Token Entity Render provides the `[node:render:full]` token, which passes the rendered
page to the reviewer. Without it, the reviewer sees no content.

### Set up a review rule

There is no public recipe for AI Content Review yet, so the rule and its criteria are set
up by hand. [docs/04_ai_content_review.md](docs/04_ai_content_review.md) walks through
the workshop's rule in detail, including a complete house-style rubric you can adapt.

1. Go to **AI Setup and Configuration › Review Rules**
   ([/admin/config/ai/content-review/rules](https://localgov-ai-demo.ddev.site/admin/config/ai/content-review/rules))
   and add a rule for **Content** of the subtype **Service page** (and any other
   LocalGov types you want reviewed).
2. Add a criterion of the type **Agent-based criterion**, with a Content Review agent
   and a fast chat model. A slow model can run past the provider's request time limit.
3. In **Guidelines & rules**, write the rubric. Keep it to a closed list of rules the AI
   can check and quote, for example from the GOV.UK style guide: sentence case headings,
   dates as *22 October 2026*, *to* instead of a dash in ranges, link text that makes
   sense on its own, no exclamation marks or ampersands.
4. Set the scoring thresholds, for example: below 85 fails, 85 to 89 warns, 90 and above
   passes.

To let content editors use it:

```bash
ddev drush role:perm:add localgov_editor 'run reviews'
ddev drush role:perm:add localgov_editor 'view review records'
ddev drush role:perm:add localgov_editor 'view review history'
```

### Show the suggestions in the edit form

AI Content Review lists its suggestions in a **Review suggestions** panel in the core
Navigation top bar. LocalGov Drupal uses Gin Toolbar instead, so that panel never
appears. The custom module
[`localgov_ai_review_sidebar`](web/modules/custom/localgov_ai_review_sidebar/) adds the
same list to the right-hand sidebar of the node edit form:

```bash
ddev drush pm:install localgov_ai_review_sidebar -y
ddev drush cache:rebuild
```

It shows the overall score and grade, each criterion's score and explanation, and each
suggestion with the field it targets, the current text, the suggested text and the
rationale. Click a suggestion to jump to its field and select the quoted text. The list
is read-only. See the [module README](web/modules/custom/localgov_ai_review_sidebar/README.md)
for how it works.

### Try it

1. Edit one of the bins pages, for example *Report a missed bin collection*, and add a
   few deliberate mistakes: a Title Case Heading, a date such as *10/22/2026*, a range
   such as *9am-5pm*, a "click here" link and an exclamation mark. Save it.
2. Open the page's **AI Review** tab and click **Review**. After 10 to 30 seconds the
   result appears, with a score and a grade.
3. Click **Edit**. The sidebar now has **Content Review**, **Improvement plan** and
   **Review suggestions (n)**. Click a suggestion to jump to the text it is about.
4. In the review dialog, **Accept** or **Ignore** each suggestion. Accepted ones appear
   in the **Improvement plan** as a checklist.
5. Correct the text yourself, save, and click **Update** on the AI Review tab. The page
   should now pass. The **AI Review History** tab lists every review.
6. **Content › AI content review** lists every page with its result, and the bulk action
   **Queue AI review** reviews several pages at once on cron.

> **Do not click Apply.** In AI Content Review 1.0.0-alpha3, *Apply* replaces the
> **whole field** with the suggested text, which is usually a short phrase, and saves the
> page straight away. If it happens, restore the previous revision on the **Revisions**
> tab. This is issue
> [#3585854](https://git.drupalcode.org/project/ai_content_review/-/work_items/3585854).

## 6. The webinar slide deck

The deck for the LocalGov Drupal webinar on the DrupalCon Rotterdam workshop is a set of
plain HTML pages in [web/drupalcon-rotterdam/](web/drupalcon-rotterdam/), so it is
served by the site itself:

- Open https://localgov-ai-demo.ddev.site/drupalcon-rotterdam/ once `ddev start` has run.
  `index.html` is a presenter checklist; the talk starts at `01-title.html`.
- Keys: arrow keys move between slides, **N** shows speaker notes, **F** goes full
  screen, **R** reveals the answers on the "spot the mistakes" slide.
- To change the slide text, edit
  [docs/drupalcon-rotterdam/build_deck.py](docs/drupalcon-rotterdam/build_deck.py) and run
  `python3 docs/drupalcon-rotterdam/build_deck.py`. It rewrites the 12 slides and keeps
  the checklist in `index.html`.

See [docs/drupalcon-rotterdam/README.md](docs/drupalcon-rotterdam/README.md) for more.

## What is in this repository

This is the standard [LocalGov Drupal project template](https://github.com/localgovdrupal/localgov_project)
with these additions:

| Path | What it is |
|---|---|
| `composer.json` | Adds the AI module, the OpenAI, Anthropic and amazee.ai providers, AI CKEditor, AI Content Review, the AI Answers recipe, Drupal CMS AI, Easy Encryption and Token Entity Render. |
| `.ddev/docker-compose.postgres.yaml`, `.ddev/postgres/` | The PostgreSQL + pgvector service for AI search, and the `VECTOR_DB_*` environment variables the AI Answers recipe reads. |
| `web/modules/custom/localgov_demo_bins/` | Bins, recycling and waste example content. |
| `web/modules/custom/localgov_ai_review_sidebar/` | AI Content Review suggestions in the node edit sidebar. |
| `web/modules/custom/localgov_ai_answers_layout/` | Fits the AI Answers blocks to the LocalGov page width. |
| `web/drupalcon-rotterdam/`, `docs/drupalcon-rotterdam/` | The webinar slide deck and its build script. |
| `docs/` | Step-by-step guides. Steps 1 to 4 were written for the DrupalCon Rotterdam workshop's university site and explain each AI feature in depth; their commands refer to workshop recipes that are not in this repository. Step 5 covers the LocalGov version of AI search. |

The site configuration is not exported to `config/sync`, so a fresh install is set up
with the steps above rather than with `drush config:import`.

## Troubleshooting

**AI search answers "I couldn't find that" for questions it should answer.** The page
probably has no chunks because of rate limiting during indexing. Run
`ddev drush watchdog:show --type=ai_search` and look for rate limit errors, then clear
and re-index two items at a time as in step 4. Search API's 100% does not prove that
every chunk was embedded.

**The AI Answers recipe fails, or the vector size is wrong.** Set the default
*Embeddings* model in AI Settings before applying the recipe. If you change the
embeddings model later, change the vector size on the Search API server to match, then
clear and re-index.

**The postgres service is not running.** Run `ddev restart` and check
`ddev describe`. The `postgres` service should be listed.

**A review takes too long and fails.** Choose a faster model on the criterion, or set
its **Execution mode** to *Polling*.

**The Review suggestions section does not appear in the edit form.** It needs a review
rule that targets the page's content type, the *View AI review records* permission, and
at least one review of the page.

**I renamed the DDEV project and AI search stopped working.** The pgvector data lives in
a Docker volume named after the DDEV project, and DDEV snapshots only cover MariaDB. After
a rename, or after restoring a snapshot, re-index `content_vector`.

## Starting again

Take a snapshot before trying something risky, and restore it to go back:

```bash
ddev snapshot --name=before-my-change
ddev snapshot restore before-my-change
```

To start completely from scratch, run `ddev delete -O` (this deletes the databases,
including the vectors) and go back to step 1.

## Credits and licence

Built by [Digital Journey Coach](https://digitaljourneycoach.com) on top of
[LocalGov Drupal](https://localgovdrupal.org/) and the
[Drupal AI](https://www.drupal.org/project/ai) initiative. Licensed under the GNU
General Public License, version 2 or later, like Drupal itself. See [LICENSE](LICENSE).

For general LocalGov Drupal installation and development, see the
[LocalGov Drupal documentation](https://docs.localgovdrupal.org/devs/getting-started/).
