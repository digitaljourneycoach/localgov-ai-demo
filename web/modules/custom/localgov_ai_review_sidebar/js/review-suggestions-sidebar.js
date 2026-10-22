/**
 * @file
 * Takes the editor from a suggestion in the sidebar to the text it is about.
 *
 * Clicking a suggestion scrolls to the field it targets and flashes it. When
 * the quoted text can be found it is also selected: inside CKEditor through
 * the editor's own model, so the selection survives the editor re-rendering,
 * and in plain inputs with setSelectionRange().
 */

((Drupal, once) => {
  'use strict';

  const FLASH_CLASS = 'lgd-ai-review-flash';
  const ACTIVE_CLASS = 'is-active';

  // Characters the model tends to spell differently from the stored text.
  // One-to-one only, so normalized offsets map straight back to the source.
  const FOLDED = {
    '‘': "'",
    '’': "'",
    '“': '"',
    '”': '"',
    '–': '-',
    '—': '-',
    ' ': ' ',
  };

  /**
   * Folds quotes and dashes, lowercases and collapses whitespace.
   *
   * @param {string} raw
   *   The source text.
   *
   * @return {{text: string, map: number[]}}
   *   The normalized text, and the index in raw of each of its characters.
   */
  function normalize(raw) {
    let text = '';
    const map = [];
    let afterSpace = true;

    for (let i = 0; i < raw.length; i++) {
      const char = FOLDED[raw[i]] ?? raw[i];
      if (/\s/.test(char)) {
        if (!afterSpace) {
          text += ' ';
          map.push(i);
        }
        afterSpace = true;
      } else {
        const lower = char.toLowerCase();
        text += lower.length === 1 ? lower : char;
        map.push(i);
        afterSpace = false;
      }
    }

    return { text, map };
  }

  /**
   * Finds a quote in a string.
   *
   * @return {?{start: number, end: number}}
   *   Offsets into the raw string, end exclusive, or null when not found.
   */
  function findInString(haystack, quote) {
    const needle = normalize(quote).text.trim();
    if (!needle) {
      return null;
    }
    const page = normalize(haystack);
    const index = page.text.indexOf(needle);
    if (index === -1) {
      return null;
    }
    return {
      start: page.map[index],
      end: page.map[index + needle.length - 1] + 1,
    };
  }

  /**
   * Finds a quote in the text of a DOM subtree.
   *
   * @return {?Range}
   *   A DOM range around the first match, or null when not found.
   */
  function findInDom(root, quote) {
    const nodes = [];
    let text = '';
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      nodes.push({ node: walker.currentNode, start: text.length });
      text += walker.currentNode.data;
    }

    const match = findInString(text, quote);
    if (!match) {
      return null;
    }

    // Maps an offset in the joined text back to a text node and offset.
    const locate = (offset, isEnd) => {
      for (let i = nodes.length - 1; i >= 0; i--) {
        if (
          offset > nodes[i].start ||
          (!isEnd && offset === nodes[i].start)
        ) {
          return [nodes[i].node, offset - nodes[i].start];
        }
      }
      return [nodes[0].node, 0];
    };

    const range = document.createRange();
    range.setStart(...locate(match.start, false));
    range.setEnd(...locate(match.end, true));
    return range;
  }

  /**
   * Returns the form wrapper of a field, by its machine name.
   */
  function fieldWrapper(target) {
    if (!target) {
      return null;
    }
    const selector = `edit-${target.replace(/_/g, '-')}`;
    return (
      document.querySelector(`[data-drupal-selector="${selector}-wrapper"]`) ||
      document.querySelector(`[data-drupal-selector="${selector}"]`)
    );
  }

  /**
   * Returns the CKEditor 5 instances inside a container, or all of them.
   */
  function editorsIn(container) {
    if (!Drupal.CKEditor5Instances) {
      return [];
    }
    return [...Drupal.CKEditor5Instances.values()].filter(
      (editor) =>
        !container ||
        (editor.sourceElement && container.contains(editor.sourceElement)),
    );
  }

  /**
   * Selects a quote inside a CKEditor 5 instance.
   *
   * @return {boolean}
   *   Whether the quote was found and selected.
   */
  function selectInEditor(editor, quote) {
    const root = editor.editing.view.getDomRoot();
    const domRange = root ? findInDom(root, quote) : null;
    if (!domRange) {
      return false;
    }
    const viewRange =
      editor.editing.view.domConverter.domRangeToView(domRange);
    if (!viewRange) {
      return false;
    }
    const modelRange = editor.editing.mapper.toModelRange(viewRange);
    editor.model.change((writer) => writer.setSelection(modelRange));
    editor.editing.view.focus();
    editor.editing.view.scrollToTheSelection();
    return true;
  }

  /**
   * Selects a quote inside a text input or plain textarea.
   *
   * @return {boolean}
   *   Whether the quote was found and selected.
   */
  function selectInInput(input, quote) {
    const match = findInString(input.value, quote);
    if (!match) {
      return false;
    }
    input.focus({ preventScroll: true });
    input.setSelectionRange(match.start, match.end);
    return true;
  }

  /**
   * Looks for the quote in a container and selects it when found.
   */
  function selectQuote(container, form, quote) {
    if (!quote) {
      return false;
    }
    if (editorsIn(container).some((editor) => selectInEditor(editor, quote))) {
      return true;
    }
    const inputs = (container || form).querySelectorAll(
      'input[type="text"], textarea',
    );
    return [...inputs].some(
      (input) =>
        !input.closest('.lgd-ai-review-sidebar') &&
        input.offsetParent !== null &&
        selectInInput(input, quote),
    );
  }

  /**
   * Briefly outlines an element so the eye can find it after scrolling.
   */
  function flash(element) {
    element.classList.remove(FLASH_CLASS);
    // Restart the animation when the same field is clicked twice.
    // eslint-disable-next-line no-void
    void element.offsetWidth;
    element.classList.add(FLASH_CLASS);
    setTimeout(() => element.classList.remove(FLASH_CLASS), 2500);
  }

  /**
   * Jumps to the field and text a suggestion button refers to.
   */
  function locate(button) {
    const form = button.closest('form') || document;
    const { lgdAiReviewTarget: target, lgdAiReviewQuote: quote } =
      button.dataset;

    const list = button.closest('[data-lgd-ai-review]');
    list
      .querySelectorAll(`.${ACTIVE_CLASS}`)
      .forEach((item) => item.classList.remove(ACTIVE_CLASS));
    button.classList.add(ACTIVE_CLASS);

    const wrapper = fieldWrapper(target);
    if (wrapper) {
      wrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });
      flash(wrapper);
    }

    // Look in the target field first; a suggestion without a target, or whose
    // text has moved, may still be found elsewhere in the form.
    const found =
      selectQuote(wrapper, form, quote) ||
      (wrapper && selectQuote(null, form, quote));

    if (found && !wrapper) {
      const selected = document.activeElement;
      if (selected) {
        flash(selected.closest('.form-wrapper, .form-item') || selected);
      }
    }

    const notFound = Boolean(quote) && !found;
    button.classList.toggle('is-not-found', notFound);
    const hint = button.querySelector('.lgd-ai-review__not-found');
    if (hint) {
      hint.hidden = !notFound;
    }
    if (notFound) {
      Drupal.announce(hint ? hint.textContent : '');
    }
  }

  /**
   * Makes each listed suggestion jump to its place in the form.
   *
   * @type {Drupal~behavior}
   */
  Drupal.behaviors.lgdAiReviewSidebar = {
    attach(context) {
      once('lgd-ai-review-locate', '.lgd-ai-review__locate', context).forEach(
        (button) => button.addEventListener('click', () => locate(button)),
      );
    },
  };
})(Drupal, once);
