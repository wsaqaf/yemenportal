server "inewscloud-vip.positive-dedicated.net", port: 33015, user: "yemenportal",
  roles: [:app, :web, :db]

set :branch, "master"

set :rails_env, 'production'

# Configure puma
set :puma_env, fetch(:rails_env)
set :puma_state, "#{shared_path}/tmp/pids/puma.state"
set :puma_pid, "#{shared_path}/tmp/pids/puma.pid"
set :puma_bind, "unix://#{shared_path}/tmp/sockets/puma.sock"
set :puma_threads, [2, 16]
set :puma_workers, 2
set :puma_preload_app, true
