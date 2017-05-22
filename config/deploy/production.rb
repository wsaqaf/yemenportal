server "inewscloud-vip.positive-dedicated.net", port: 33015, user: "yemenportal",
  roles: [:app, :web, :db]

set :branch, "feature-add-post-clustering"

set :rails_env, 'production'
