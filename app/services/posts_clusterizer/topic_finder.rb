class PostsClusterizer::TopicFinder
  def initialize(post)
    @post = post
  end

  def attach_topic
    if topic_with_related_posts.present? && topic_does_not_contain_post_from_same_source?
      topic_attacher.attach
    else
      create_new_topic!
    end
  end

  private

  attr_reader :post

  def topic_with_related_posts
    @_topic_with_related_posts ||=
      PostsClusterizer::RelatedPostsFinder.new(post).topic_with_related_posts_or_nil
  end

  def topic_attacher
    @_topic_attacher ||=
      PostsClusterizer::TopicAttacher.new(post: post, topic: topic_with_related_posts)
  end

  def topic_does_not_contain_post_from_same_source?
    !topic_with_related_posts.sources_of_all_posts.include?(post.source)
  end

  def create_new_topic!
    Topic.create!(main_post: post)
  end
end
