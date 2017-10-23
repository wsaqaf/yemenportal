class PostsFetcher::TopicAttacher
  def initialize(post:, topic:)
    @post = post
    @topic = topic
  end

  def attach
    if attaching_post_was_published_early?
      set_new_main_post
    else
      post.update(topic: topic)
    end
  end

  private

  attr_reader :post, :topic

  def attaching_post_was_published_early?
    topic_main_post.published_at > post.published_at
  end

  def set_new_main_post
    topic_main_post.update(topic: topic)
    topic.update(main_post: post)
  end

  def topic_main_post
    @_topic_main_post ||= topic.main_post
  end
end
