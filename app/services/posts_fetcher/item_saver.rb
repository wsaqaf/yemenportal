class PostsFetcher::ItemSaver
  def initialize(source, item)
    @post = PostsFetcher::PostFactory.new(source, item).create
  end

  def save!
    return if post.invalid?
    Post.transaction do
      post.update(topic: topic)
    end
  end

  private

  attr_reader :post

  def topic
    if FeatureToggle.clustering_enabled?
      topic_with_related_posts || new_topic
    else
      new_topic
    end
  end

  def topic_with_related_posts
    RelatedPostsFinder.new(post).topic_with_related_posts_or_nil
  end

  def new_topic
    Topic.create!(main_post: post)
  end
end
