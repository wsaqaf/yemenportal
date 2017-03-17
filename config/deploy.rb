lock '3.6.1'

set :whenever_identifier, ->{ "#{fetch(:application)}_#{fetch(:stage)}" }

set :application, 'yemenportal'
set :repo_url, 'git@github.com:datarockets/yemenportal.git'
set :deploy_to, '/home/yemenportal/app'
set :ssh_options, { :forward_agent => true }

set :linked_files, %w(.env)
set :linked_dirs, %w(tmp/sockets tmp/pids log public/uploads)

set :rbenv_type, :user
set :rbenv_ruby, File.read('.ruby-version').strip

set :disallow_pushing, true
set :db_remote_clean, true
set :db_local_clean, true

set :keep_releases, 4

set :systemctl_roles, ["app"]

after "deploy:finished", "systemctl:app:restart"
