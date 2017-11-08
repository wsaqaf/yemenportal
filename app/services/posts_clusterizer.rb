class PostsClusterizer
  def self.clusterize!
    Post.non_clustered_posts.where("posts.created_at > ?", 3.hours.ago).find_each do |post|
      PostsClusterizer::TopicFinder.new(post).attach_topic!
    end
  end
end
