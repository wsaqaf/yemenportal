desc "Clusterizes non-clustered posts"
task posts_clustering: :environment do
  PostsClusterizer.clusterize
end
