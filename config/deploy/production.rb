server "inewscloud-vip.positive-dedicated.net", port: 33015, user: "yemenportal",
  roles: [:app, :web, :db]

set :branch, "problem-crashed-prod"

set :rails_env, 'production'
