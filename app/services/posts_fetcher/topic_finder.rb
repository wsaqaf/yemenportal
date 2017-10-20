class PostsFetcher::TopicFinder
  def initialize(post)
    @post = post
  end

  def attach_topic!
    return if post.invalid?
    Post.transaction do
      attach_or_create_new_topic
    end
  end

  private

  attr_reader :post

  def attach_or_create_new_topic
    if topic_with_related_posts.present?
      post.update(topic: topic_with_related_posts)
    else
      create_new_topic!
    end
  end

  def topic_with_related_posts
    @_topic_with_related_posts ||= RelatedPostsFinder.new(post).topic_with_related_posts_or_nil
  end

  def create_new_topic!
    Topic.create!(main_post: post)
  end
end
