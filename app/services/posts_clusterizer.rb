class PostsClusterizer
  def self.clusterize
    Post.non_clustered_posts.find_each do |post|
      PostsClusterizer::TopicFinder.new(post).attach_topic
    end
  end
end
