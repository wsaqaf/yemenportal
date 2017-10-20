class PostsFetcher::TopicFinder
  def initialize(post)
    @post = post
  end

  def post_with_topic!
    return if post.invalid?
    Post.transaction do
      post.update(topic: topic)
    end
  end

  private

  attr_reader :post

  def topic
    topic_with_related_posts || new_topic
  end

  def topic_with_related_posts
    RelatedPostsFinder.new(post).topic_with_related_posts_or_nil
  end

  def new_topic
    Topic.create!(main_post: post)
  end
end
