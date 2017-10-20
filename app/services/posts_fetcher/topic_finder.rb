class PostsFetcher::TopicFinder
  def initialize(post)
    @post = post
  end

  def attach_topic!
    if post.valid?
      # we create topic and post
      Post.transaction do
        attach_or_create_new_topic
      end
    end
  end

  private

  attr_reader :post

  def attach_or_create_new_topic
    if topic_with_related_posts.present? && topic_does_not_contain_post_from_same_source?
      post.update(topic: topic_with_related_posts)
    else
      create_new_topic!
    end
  end

  def topic_with_related_posts
    @_topic_with_related_posts ||= RelatedPostsFinder.new(post).topic_with_related_posts_or_nil
  end

  def topic_does_not_contain_post_from_same_source?
    !topic_with_related_posts.sources_of_all_posts.include?(post.source)
  end

  def create_new_topic!
    Topic.create!(main_post: post)
  end
end
