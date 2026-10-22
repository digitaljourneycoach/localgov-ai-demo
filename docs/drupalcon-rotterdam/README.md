# DrupalCon Rotterdam webinar deck

A 7-minute talk for the LocalGov Drupal community on the Drupal AI workshop at DrupalCon Rotterdam, with three live demos on this site. It's styled with the Journey Coach GDS design system.

- Open the deck at https://localgov-ai-demo.ddev.site/drupalcon-rotterdam/ once `ddev start` has run. `index.html` is a presenter checklist; the talk starts at `01-title.html`.
- Keys: arrow keys move, **N** speaker notes, **F** full screen, **R** reveals the answers on the "spot the mistakes" slide.
- The slides live in `web/drupalcon-rotterdam/`. Each slide is its own HTML file, sharing `deck.css` and `deck.js`.

To change slide text, edit `build_deck.py` here and run `python3 docs/drupalcon-rotterdam/build_deck.py`. It rewrites the 12 slides and the frame of `index.html`; the checklist content in `index.html` is kept as it is.
