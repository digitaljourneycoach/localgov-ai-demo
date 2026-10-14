# LocalGov Drupal Composer project template

A Composer-based installer for the LocalGov Drupal distribution.

See https://www.drupal.org/project/localgov_project for more information.

This project template should provide a kickstart for managing your site
dependencies with Composer.

## Usage

For guidance on installing see:

 - [Installing LocalGov Drupal locally with composer](https://git.drupalcode.org/project/localgov#installing-localgov-drupal-locally-with-composer)
 - [Getting started, on LocalGov Drupal docs](https://docs.localgovdrupal.org/devs/getting-started/)

## Installing LocalGov Drupal locally

To install LocalGov Drupal locally for testing or development, we recommend
using ddev. See https://ddev.com/get-started/

With ddev installed, it is very quick to set up LocalGov Drupal locally for
testing, development and contribution.

```
composer create-project --no-install drupal/localgov_project:^4.0@beta MY_PROJECT
cd MY_PROJECT
ddev start
composer install
ddev drush si localgov -y
```

## composer.json and composer.lock

We expect most projects using this package will start with the composer.json in
this package, committing it to your own project repository as your own root
composer.json. One can then extend composer.json, requiring other Drupal and
composer packages to evolve your codebase as needed.

Once you have run a `composer create-project` command, it is usually desirable
to commit the composer.lock file to your project repository and use this lock
file to control the specific version of packages that you deploy to dev, test
and ultimately production hosting environments.

## Maintainers

This project is currently maintained by the following users, but do check on
https://www.drupal.org/project/localgov_project

 - Andy Broomfield: https://www.drupal.org/u/andybroomfield
 - Ekes: https://www.drupal.org/u/ekes
 - Finn Lewis: https://www.drupal.org/u/finn-lewis
 - Mark Conroy: https://www.drupal.org/u/markconroy
 - Stephen Cox: https://www.drupal.org/u/stephen-cox
 - Tony Barker: https://www.drupal.org/u/tonypaulbarker
