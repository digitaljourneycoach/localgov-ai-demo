# LocalGov AI review sidebar

Shows the suggestions from [AI Content Review](https://www.drupal.org/project/ai_content_review)
as a list in the right-hand sidebar of the node edit form. Editors can see
every suggestion while they edit, without opening the review dialog.

## Why

AI Content Review adds a "Content Review" score summary and an "Improvement
plan" to the edit form sidebar. The suggestions themselves are only listed in
its review dialog, or in its "Review suggestions" top bar panel. That panel
needs the core Navigation module, which this site does not use (it uses Gin
Toolbar). This module brings the same list into the edit form.

## What it shows

A "Review suggestions (n)" section in the sidebar (the `advanced` group, so it
sits under Content Review and Improvement plan in Gin and Claro). It contains:

- the overall score (the average of the criteria scores) and grade. The grade
  is the worst grade of any criterion, so one failing criterion is never
  hidden by others passing
- for each criterion: its score, its Pass, Warning or Fail grade, and the AI's
  explanation
- for each suggestion: the field it targets, the current (quoted) text, the
  suggested text, the rationale, and whether it is still to review, accepted
  or ignored

Click a suggestion to scroll to its field and flash it. If the quoted text is
found, it is also selected: in CKEditor through the editor's model, and in
plain inputs such as Title with a text selection. If the text cannot be found
(for example, it was in a block or listing on the page rather than a field,
or it has since been edited), the card says so.

If the content has changed since a criterion was reviewed, the section warns
that the quoted text may no longer match.

There is no Apply button. Accepting or ignoring a suggestion is still done in
the AI Review dialog. The list is read-only.

## How it works

- `src/Hook/ReviewSuggestionsSidebarHooks.php` implements
  `hook_form_node_form_alter()` and `hook_theme()` as attribute hooks.
- It reads everything through ai_content_review's own services: the review
  rule loader, the record loader (`loadLatestForSubject()`), the input hasher
  (to match records to criteria), `GradeEvaluator` thresholds and
  `RenderHelpers::gradeModifier()`/`decisionLabels()`. Nothing is stored by
  this module.
- The section carries the node's cache tags plus `review_record_list`,
  `suggestion_list` and the review rule list tags, so it updates after a new
  review, a decision or a rule change.
- `js/review-suggestions-sidebar.js` does the scroll, flash and text
  selection.
- `templates/localgov-ai-review-sidebar.html.twig` holds the markup and can
  be overridden in a theme.

## Requirements

- Drupal 11.1 or later (attribute hooks)
- AI Content Review, with a review rule that targets the node's content type
- The "view review records" permission to see the list

## Install

```
ddev drush en localgov_ai_review_sidebar
ddev drush cr
```
