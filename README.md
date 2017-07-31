# YemenPortal

## Technical Debt

* CHECK AUTHORIZATION
* Change logic of fetching posts

* README
* Gem wrappers of javascript libs. Better to install it using npm.
* Code Style
  * Quotemarks in Gemfile
  * Commented code (bin/setup)

* bin/update ?

* Unnecessary ignorance in gitignore
* Don't ignore config/puma.rb. Use ENV variables to configure puma.
* Install gems to vendor/bundle
* Remove unused ActionCable
* Capistrano-db-tasks
* config/linecount.txt

* posts resources in routes
* approvement of sources in routes

* all env variables should be listed in config/secrets.yml

* mailcatcher
  * list in README
  * install in bin/setup and bin/update

* PostsFetcherJob
  * private methods receive arguments

* RSSParserService
  * class methods

* PostCreatedService
  * complicate

* TfidfService
  * complicate
  * private methods receive params

* VoteService
  * one class method

* Use policies the right way

* PostsController
  * #user_voted
  * #posts_params

* Posts::ReaderController
  * Should be PostsController#show?

* Controllers
  * Unused constants
  * A lot of params passed to cells

* Javascript
  * Big methods

* Stylesheets
  * Use BEM

* Refactor tests
