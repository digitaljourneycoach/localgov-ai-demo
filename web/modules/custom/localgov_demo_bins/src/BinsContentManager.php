<?php

declare(strict_types=1);

namespace Drupal\localgov_demo_bins;

use Drupal\Component\Serialization\Yaml;
use Drupal\Core\Entity\EntityTypeManagerInterface;
use Drupal\Core\Extension\ModuleExtensionList;
use Drupal\Core\Logger\LoggerChannelFactoryInterface;
use Drupal\Core\Logger\LoggerChannelInterface;
use Drupal\node\NodeInterface;

/**
 * Creates and removes the bins and recycling example content.
 *
 * The content lives in content/bins_and_recycling.yml. Every item gets a
 * UUID derived from its id, so importing again updates the existing nodes
 * instead of creating duplicates.
 */
class BinsContentManager {

  /**
   * Maps the item types used in the YAML file to node bundles.
   */
  protected const BUNDLES = [
    'landing' => 'localgov_services_landing',
    'sublanding' => 'localgov_services_sublanding',
    'page' => 'localgov_services_page',
  ];

  /**
   * The logger channel.
   */
  protected LoggerChannelInterface $logger;

  public function __construct(
    protected EntityTypeManagerInterface $entityTypeManager,
    protected ModuleExtensionList $moduleList,
    LoggerChannelFactoryInterface $loggerFactory,
  ) {
    $this->logger = $loggerFactory->get('localgov_demo_bins');
  }

  /**
   * Creates or updates all the example content.
   *
   * @return \Drupal\node\NodeInterface[]
   *   The saved nodes, keyed by item id.
   */
  public function import(): array {
    $items = $this->loadItems();
    $format = $this->textFormat();
    $nodes = [];

    // First pass: create every node with its text and parent, in file order
    // so parents exist before their children and get the right URL alias.
    foreach ($items as $item) {
      $node = $this->loadNode($item['id']) ?? $this->entityTypeManager->getStorage('node')->create([
        'type' => self::BUNDLES[$item['type']],
        'uuid' => $this->uuid($item['id']),
      ]);
      $node->setTitle($item['title']);
      $node->set('body', [
        'value' => trim($item['body'] ?? ''),
        'summary' => $item['summary'] ?? '',
        'format' => $format,
      ]);
      if (!empty($item['parent']) && $node->hasField('localgov_services_parent')) {
        $node->set('localgov_services_parent', ['target_id' => $nodes[$item['parent']]->id()]);
      }
      if (!empty($item['contact'])) {
        $this->setContact($node, $item['contact'], $format);
      }
      $node->setPublished();
      if ($node->hasField('moderation_state')) {
        $node->set('moderation_state', 'published');
      }
      $node->save();
      $nodes[$item['id']] = $node;
    }

    // Second pass: links between pages, now that every node has an id.
    foreach ($items as $item) {
      $node = $nodes[$item['id']];
      $this->setLinks($node, 'localgov_common_tasks', $item['top_tasks'] ?? [], $nodes);
      $this->setLinks($node, 'localgov_related_links', $item['related_links'] ?? [], $nodes);
      if ($node->hasField('localgov_destinations')) {
        $node->set('localgov_destinations', array_map(
          fn($id) => ['target_id' => $nodes[$id]->id()],
          $item['destinations'] ?? [],
        ));
      }
      if ($node->hasField('localgov_topics')) {
        $node->set('localgov_topics', $this->buildTopicLists($item['sections'] ?? [], $nodes));
      }
      $node->save();
    }

    $this->logger->notice('Imported @count bins and recycling pages.', ['@count' => count($nodes)]);
    return $nodes;
  }

  /**
   * Deletes all the example content.
   *
   * @return int
   *   The number of nodes deleted.
   */
  public function remove(): int {
    $count = 0;
    // Children first, so parents are never left with dangling references.
    foreach (array_reverse($this->loadItems()) as $item) {
      if ($node = $this->loadNode($item['id'])) {
        $node->delete();
        $count++;
      }
    }
    $this->logger->notice('Removed @count bins and recycling pages.', ['@count' => $count]);
    return $count;
  }

  /**
   * Reads the content definitions from the YAML file.
   */
  protected function loadItems(): array {
    $path = $this->moduleList->getPath('localgov_demo_bins') . '/content/bins_and_recycling.yml';
    return Yaml::decode(file_get_contents($path));
  }

  /**
   * Loads the node for an item, if it has already been imported.
   */
  protected function loadNode(string $id): ?NodeInterface {
    $nodes = $this->entityTypeManager->getStorage('node')->loadByProperties(['uuid' => $this->uuid($id)]);
    return $nodes ? reset($nodes) : NULL;
  }

  /**
   * Builds a stable UUID from an item id.
   */
  protected function uuid(string $id): string {
    $hash = md5('localgov_demo_bins:' . $id);
    return sprintf('%s-%s-4%s-a%s-%s',
      substr($hash, 0, 8),
      substr($hash, 8, 4),
      substr($hash, 13, 3),
      substr($hash, 17, 3),
      substr($hash, 20, 12),
    );
  }

  /**
   * Picks the LocalGov editor format, falling back to basic HTML.
   */
  protected function textFormat(): string {
    $storage = $this->entityTypeManager->getStorage('filter_format');
    return $storage->load('wysiwyg') ? 'wysiwyg' : 'basic_html';
  }

  /**
   * Sets the contact fields on a service landing page.
   */
  protected function setContact(NodeInterface $node, array $contact, string $format): void {
    $fields = [
      'localgov_phone' => $contact['phone'] ?? NULL,
      'localgov_email_address' => $contact['email'] ?? NULL,
      'localgov_contact_us_online' => $contact['contact_us_online'] ?? NULL,
    ];
    foreach ($fields as $field => $value) {
      if ($value !== NULL && $node->hasField($field)) {
        $node->set($field, $value);
      }
    }
    foreach (['localgov_opening_hours' => 'opening_hours', 'localgov_address' => 'address'] as $field => $key) {
      if (!empty($contact[$key]) && $node->hasField($field)) {
        $node->set($field, ['value' => trim($contact[$key]), 'format' => $format]);
      }
    }
  }

  /**
   * Sets a link field from a list of title and link pairs.
   */
  protected function setLinks(NodeInterface $node, string $field, array $links, array $nodes): void {
    if (!$node->hasField($field)) {
      return;
    }
    $node->set($field, array_map(
      fn($link) => ['uri' => $this->uri($link['link'], $nodes), 'title' => $link['title']],
      $links,
    ));
  }

  /**
   * Builds the topic list paragraphs for a service sub-landing page.
   *
   * @return \Drupal\paragraphs\ParagraphInterface[]
   *   The unsaved paragraphs, which are saved with the host node.
   */
  protected function buildTopicLists(array $sections, array $nodes): array {
    $storage = $this->entityTypeManager->getStorage('paragraph');
    $paragraphs = [];
    foreach ($sections as $section) {
      $paragraphs[] = $storage->create([
        'type' => 'topic_list_builder',
        'topic_list_header' => $section['header'],
        'topic_list_links' => array_map(
          fn($id) => ['uri' => 'entity:node/' . $nodes[$id]->id(), 'title' => $nodes[$id]->getTitle()],
          $section['links'],
        ),
      ]);
    }
    return $paragraphs;
  }

  /**
   * Turns a link from the YAML file into a link field URI.
   */
  protected function uri(string $link, array $nodes): string {
    if (str_starts_with($link, 'node:')) {
      return 'entity:node/' . $nodes[substr($link, 5)]->id();
    }
    if (str_starts_with($link, '/')) {
      return 'internal:' . $link;
    }
    return $link;
  }

}
