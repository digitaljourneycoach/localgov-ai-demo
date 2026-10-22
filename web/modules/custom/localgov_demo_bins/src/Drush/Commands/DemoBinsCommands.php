<?php

declare(strict_types=1);

namespace Drupal\localgov_demo_bins\Drush\Commands;

use Drupal\localgov_demo_bins\BinsContentManager;
use Drush\Attributes as CLI;
use Drush\Commands\AutowireTrait;
use Drush\Commands\DrushCommands;
use Symfony\Component\DependencyInjection\Attribute\Autowire;

/**
 * Drush commands for the bins and recycling example content.
 */
final class DemoBinsCommands extends DrushCommands {

  use AutowireTrait;

  public function __construct(
    #[Autowire(service: 'localgov_demo_bins.content_manager')]
    private readonly BinsContentManager $contentManager,
  ) {
    parent::__construct();
  }

  /**
   * Creates or updates the bins and recycling example content.
   */
  #[CLI\Command(name: 'localgov-demo-bins:import', aliases: ['ldb-import'])]
  #[CLI\Usage(name: 'drush localgov-demo-bins:import', description: 'Create the pages, or update them after editing content/bins_and_recycling.yml.')]
  public function import(): void {
    $nodes = $this->contentManager->import();
    $this->logger()->success(dt('Imported @count pages. The section starts at @url', [
      '@count' => count($nodes),
      '@url' => reset($nodes)->toUrl()->toString(),
    ]));
  }

  /**
   * Deletes the bins and recycling example content.
   */
  #[CLI\Command(name: 'localgov-demo-bins:remove', aliases: ['ldb-remove'])]
  public function remove(): void {
    $count = $this->contentManager->remove();
    $this->logger()->success(dt('Removed @count pages.', ['@count' => $count]));
  }

}
