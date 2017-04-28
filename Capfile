# Load DSL and set up stages
require "capistrano/setup"

# Include default deployment tasks
require "capistrano/deploy"
require "capistrano/rails"
require "capistrano/rails/assets"
require "capistrano/rails/console"
require "capistrano/rbenv"
require "capistrano/bundler"
require "whenever/capistrano"
require "rollbar/capistrano3"

# Load custom tasks from `lib/capistrano/tasks` if you have any defined
Dir.glob("lib/capistrano/tasks/*.rake").each { |r| import r }
