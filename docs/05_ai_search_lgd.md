# Step 5: AI Search and AI Answers on the LocalGov Drupal demo

**Goal:** the same **Ask** page as in [step 3](03_ai_search.md), but on the LocalGov
Drupal demo site (`d11-localgov`): residents ask a question in their own words at
[/ask](https://d11-localgov.ddev.site/ask) and get an answer written from the council
pages, with the source pages listed.

Follow [step 3](03_ai_search.md) for how it works. This page lists only what is
different on the LGD site.

## 1. The vector database

This branch adds the PostgreSQL + pgvector service, copied from the workshop project:

- `.ddev/docker-compose.postgres.yaml`: the `postgres` service (host `postgres`,
  database `default`, user `vectordb`) and the `VECTOR_DB_*` environment variables
  that the recipe reads.
- `.ddev/postgres/init-vector.sql`: enables the `vector` extension.

```bash
ddev restart
ddev exec -s postgres psql -U vectordb -d default -c "select extname from pg_extension"
```

## 2. Modules and recipe

No `composer require` is needed: `drupal/ai_recipe_answers` is already in
`composer.json` and brings `ai_search`, `ai_vdb_provider_postgres`, `ai_answers` and
`ai_agents` with it.

```bash
ddev drush recipe ../recipes/ai_recipe_answers
ddev drush cache:rebuild
```

## 3. Differences from the workshop site

| | Workshop (Northmoor) | LGD demo |
|---|---|---|
| Default providers | amazee.ai `chat` / `embeddings` | The site's existing defaults: OpenAI `gpt-5.2` for *Chat with tools*, `text-embedding-3-small` for *Embeddings* |
| Vector size | 1024 | 1536 (set automatically by the recipe from the default embeddings model) |
| Bundles | all node bundles | all node bundles: services landing/sub-landing/page/status, guides, step by step, news, events, directories, publications, subsites |
| Published only | no filter | **Entity status** processor added to the index, so drafts and unpublished pages are never retrieved |
| Search index view mode | created by the recipe | LGD already has a *Search index* display for every bundle (from `localgov_search`), and it renders the body and main fields, so nothing to configure |
| Reference view mode | Card | **Teaser** (LGD has no Card view mode) |
| Ask page | Utility page `Ask Northmoor` | **Services page** `Ask the council` (LGD has no basic page type), alias `/ask` |
| Theme / regions | Olivero, *Content* and *Footer Top* | `localgov_scarfolk`, *Content* and *Footer first* |

### Indexing and rate limits

The OpenAI key on this site has a low request rate limit for embeddings. Indexing all
pages at once logs `Request rate limit has been exceeded` and some chunks are skipped,
although Search API reports 100%. Index a few items at a time instead:

```bash
ddev drush search-api:clear content_vector
until ddev drush search-api:status content_vector | grep -q '100%'; do
  ddev drush search-api:index content_vector --limit=2 --batch-size=2; sleep 12
done
ddev drush watchdog:show --type=ai_search
```

### The agent

The *Content Search Agent* instructions talk about the council's website and its
services instead of Northmoor University. They also tell the agent to suggest
contacting the council when the website has no answer, and never to ask for personal
details.

### Blocks

In `localgov_scarfolk`, in the **Content** region, visible only on `/ask`:

1. Main page content (weight 0)
2. AI Answers: Question, placeholder `Ask a question about council services`, with the
   suggested questions:
   ```
   When is my bin collected?
   How do I report a missed bin?
   What can I put in my recycling bin?
   How do I order a copy of a birth certificate?
   ```
3. AI Answers: Answer, agent *Content Search Agent*, show references off
4. AI Answers: Sources

In **Footer first**: AI Answers: Question titled `Ask the council`, cross-page fallback
URL `/ask`, hidden on `/ask`.

There is no council tax content on the demo site, so the council tax question from the
plan was replaced with one about certificates.

### Permissions and logging

```bash
ddev drush role:perm:add anonymous 'use ai answers'
ddev drush role:perm:add authenticated 'use ai answers'
```

`ai_agents_runner_` was added to the thread tag prefixes in
[AI Logging Settings](https://d11-localgov.ddev.site/admin/config/ai/logging/settings).

To check that no page is missing chunks, compare `total_chunks` in the `search_api_item`
table with the rows per page in `content_database_index`. To re-index a few pages, do
not just set `status = 1` in `search_api_item`: also reset `processed_chunks = 0` and
`total_chunks = NULL`, or the old chunks are deleted and nothing new is embedded.

Result on 22 October 2026: **426 chunks** for the **137 published pages**.

## Result and known issues

Tested as an anonymous visitor: *When is my bin collected?*, *How do I report a missed
bin?*, *What can I put in my recycling bin?* and *How do I order a copy of a birth
certificate?* are answered with inline citations and a list of sources. *Who won the
football world cup in 2014?* is declined.

- In `localgov_scarfolk` the suggested question buttons show no text (the theme's
  button styles), and the AI Answers blocks are full width instead of inside the page
  container. Both need a small CSS fix in the theme.
- For an off-topic question the agent sometimes still cites low-scoring pages
  (score below 0.2) that it says are not relevant. Forcing **min_score** on the RAG tool
  (see *More to try* in step 3) avoids this.
- The `/ask` page itself is indexed, because it is a services page.

## Rollback

A database snapshot was taken before these changes:

```bash
ddev snapshot restore pre-ai-search
```

The vectors are stored in PostgreSQL, not in the database snapshot. After a restore,
remove the `postgres` service files or clear its volume if you no longer need them.
