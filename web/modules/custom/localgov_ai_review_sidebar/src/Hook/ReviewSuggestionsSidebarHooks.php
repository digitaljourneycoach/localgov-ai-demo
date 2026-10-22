<?php

declare(strict_types=1);

namespace Drupal\localgov_ai_review_sidebar\Hook;

use Drupal\ai_content_review\Entity\ReviewRecordInterface;
use Drupal\ai_content_review\Entity\SuggestionInterface;
use Drupal\ai_content_review\GradeEvaluator;
use Drupal\ai_content_review\InputHasherInterface;
use Drupal\ai_content_review\ReviewRecordLoaderInterface;
use Drupal\ai_content_review\ReviewRecordTypePluginManager;
use Drupal\ai_content_review\ReviewRuleLoaderInterface;
use Drupal\ai_content_review\Utils\RenderHelpersInterface;
use Drupal\Component\Utility\Html;
use Drupal\Core\Cache\Cache;
use Drupal\Core\Datetime\DateFormatterInterface;
use Drupal\Core\Entity\ContentEntityFormInterface;
use Drupal\Core\Entity\FieldableEntityInterface;
use Drupal\Core\Form\FormStateInterface;
use Drupal\Core\Hook\Attribute\Hook;
use Drupal\Core\Session\AccountInterface;
use Drupal\Core\StringTranslation\StringTranslationTrait;

/**
 * Lists AI Content Review suggestions in the node edit form sidebar.
 *
 * The ai_content_review module shows a score summary in the sidebar, but the
 * suggestions themselves only appear in its review dialog (or, on sites using
 * the Navigation module, the top bar panel). This adds a "Review suggestions"
 * section beside them that lists every suggestion from the latest review, read
 * from the module's own records rather than stored again.
 */
class ReviewSuggestionsSidebarHooks {

  use StringTranslationTrait;

  /**
   * Grading tiers from RenderHelpers::gradeModifier(), worst first.
   */
  private const TIER_ORDER = ['critical', 'warning', 'good', 'none'];

  public function __construct(
    private readonly ReviewRuleLoaderInterface $ruleLoader,
    private readonly ReviewRecordLoaderInterface $recordLoader,
    private readonly ReviewRecordTypePluginManager $recordTypePluginManager,
    private readonly InputHasherInterface $inputHasher,
    private readonly RenderHelpersInterface $renderHelpers,
    private readonly DateFormatterInterface $dateFormatter,
    private readonly AccountInterface $currentUser,
  ) {
  }

  /**
   * Implements hook_theme().
   */
  #[Hook('theme')]
  public function theme(): array {
    return [
      'localgov_ai_review_sidebar' => [
        'variables' => [
          'overall' => NULL,
          'criteria' => [],
          'suggestion_count' => 0,
        ],
      ],
    ];
  }

  /**
   * Implements hook_form_BASE_FORM_ID_alter() for node_form.
   */
  #[Hook('form_node_form_alter')]
  public function nodeFormAlter(array &$form, FormStateInterface $form_state): void {
    $formObject = $form_state->getFormObject();
    if (!$formObject instanceof ContentEntityFormInterface) {
      return;
    }

    $node = $formObject->getEntity();
    $form['#cache']['contexts'][] = 'user.permissions';
    // A new node has never been reviewed.
    if ($node->isNew() || !$this->currentUser->hasPermission('view review records')) {
      return;
    }

    $cacheTags = Cache::mergeTags(
      $node->getCacheTags(),
      $this->ruleLoader->getListCacheTags(),
      ['review_record_list', 'suggestion_list'],
    );
    $form['#cache']['tags'] = Cache::mergeTags($form['#cache']['tags'] ?? [], $cacheTags);

    $rules = $this->ruleLoader->loadForEntity($node);
    if (empty($rules)) {
      return;
    }

    $recordType = $this->recordTypePluginManager->getTypeForSubject($node);
    $records = $this->recordLoader->loadLatestForSubject($node);
    $decisionLabels = $this->renderHelpers->decisionLabels();

    $criteria = [];
    $scores = [];
    $tiers = [];
    $suggestionCount = 0;
    $undecidedCount = 0;
    $lastReviewed = NULL;

    foreach ($rules as $rule) {
      foreach ($rule->getCriteria() as $criterionDef) {
        // Records are keyed by the hash of the criterion configuration, which
        // is how the review module ties a record back to its criterion.
        $hash = $this->inputHasher->hash($criterionDef['configuration'] ?? []);
        $record = $records[$hash] ?? NULL;
        if (isset($criteria[$hash]) || $record === NULL || $record->getStatus() !== ReviewRecordInterface::STATUS_COMPLETE) {
          continue;
        }

        $score = $record->getScore() !== NULL ? (int) $record->getScore() : NULL;
        [$pass, $warn] = GradeEvaluator::thresholdsFor($criterionDef);
        $tier = $this->renderHelpers->gradeModifier($score, $pass, $warn);
        if ($score !== NULL) {
          $scores[] = $score;
          $tiers[] = $tier;
        }
        $lastReviewed = max($lastReviewed ?? 0, (int) $record->getReviewedAt());

        $suggestions = [];
        foreach ($record->getSuggestions() as $suggestion) {
          $decision = $suggestion->getDecision();
          $suggestions[] = [
            'id' => (int) $suggestion->id(),
            'target' => (string) $suggestion->getTarget(),
            'field_label' => $this->fieldLabel($node, $suggestion),
            'original_value' => $this->plainText($suggestion->getOriginalValue()),
            'suggested_value' => $this->plainText($suggestion->getSuggestedValue()),
            'rationale' => $this->plainText($suggestion->getRationale()),
            'decision' => $decision,
            'decision_label' => $decisionLabels[$decision] ?? $decision,
          ];
          $suggestionCount++;
          if ($decision === SuggestionInterface::DECISION_UNDECIDED) {
            $undecidedCount++;
          }
        }

        $label = (string) ($criterionDef['label'] ?? '');
        $criteria[$hash] = [
          'label' => $label !== '' ? $label : $record->getCriterionLabel(),
          'score' => $score,
          'tier' => $tier,
          'tier_label' => $this->tierLabel($tier),
          'explanation' => $this->plainText($record->getExplanation()),
          // Suggestions quote the content as it was when it was reviewed, so
          // warn the editor when they may no longer match the form.
          'stale' => $recordType->subjectChangedSince($record, $node),
          'suggestions' => $suggestions,
        ];
      }
    }

    $overall = NULL;
    if ($scores) {
      // The overall grade is the worst grade of any criterion, so one failing
      // criterion is never hidden by others passing.
      $tier = current(array_intersect(self::TIER_ORDER, $tiers));
      $overall = [
        'score' => (int) round(array_sum($scores) / count($scores)),
        'tier' => $tier,
        'tier_label' => $this->tierLabel($tier),
        'reviewed' => $lastReviewed ? $this->t('@ago ago', [
          '@ago' => $this->dateFormatter->formatTimeDiffSince($lastReviewed, ['granularity' => 1]),
        ]) : NULL,
      ];
    }

    $form['localgov_ai_review_sidebar'] = [
      '#type' => 'details',
      '#title' => $this->t('Review suggestions (@count)', ['@count' => $suggestionCount]),
      // Open while there is something left to look at.
      '#open' => $undecidedCount > 0,
      '#weight' => -8,
      '#attributes' => ['class' => ['lgd-ai-review-sidebar']],
      '#attached' => ['library' => ['localgov_ai_review_sidebar/sidebar']],
      '#cache' => [
        'tags' => $cacheTags,
        'contexts' => ['user.permissions'],
      ],
      'list' => [
        '#theme' => 'localgov_ai_review_sidebar',
        '#overall' => $overall,
        '#criteria' => array_values($criteria),
        '#suggestion_count' => $suggestionCount,
      ],
    ];
    if (isset($form['advanced'])) {
      $form['localgov_ai_review_sidebar']['#group'] = 'advanced';
    }
  }

  /**
   * Returns a readable name for the field a suggestion targets.
   */
  private function fieldLabel(FieldableEntityInterface $node, SuggestionInterface $suggestion): string {
    $target = (string) $suggestion->getTarget();
    if ($target !== '' && $node->hasField($target)) {
      return (string) $node->getFieldDefinition($target)->getLabel();
    }
    return $target !== '' ? $target : (string) $this->t('Page content');
  }

  /**
   * Decodes HTML entities in AI output, which quotes the stored markup.
   *
   * Twig escapes the result again, and the decoded text is what the editor
   * sees in CKEditor, so it is also what the locate script searches for.
   */
  private function plainText(?string $text): ?string {
    return $text === NULL ? NULL : Html::decodeEntities($text);
  }

  /**
   * Returns the label for a grading tier.
   */
  private function tierLabel(string $tier): string {
    return (string) match ($tier) {
      'good' => $this->t('Pass'),
      'warning' => $this->t('Warning'),
      'critical' => $this->t('Fail'),
      default => $this->t('Not graded'),
    };
  }

}
