server "server_url", user: "user_name", roles: [:app, :web, :db]

set :branch, "prod"

set :rails_env, 'production'

# Configure puma
set :puma_env, fetch(:rails_env)
set :puma_state, "#{shared_path}/tmp/pids/puma.state"
set :puma_pid, "#{shared_path}/tmp/pids/puma.pid"
set :puma_bind, "unix://#{shared_path}/tmp/sockets/puma.sock"
set :puma_threads, [2, 16]
set :puma_workers, 2
set :puma_preload_app, true