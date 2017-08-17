class PostsFetcher::ItemSaver
  def initialize(source, item)
    @source = source
    @item = item
  end

  def save!
    return if post_already_exist?
    Post.transaction do
      Post.create!(post_params)
    end
  end

  private

  attr_reader :source, :item

  def post_already_exist?
    Post.find_by(link: item.link).present?
  end

  def post_params
    {
      title: item.title,
      link: item.link,
      description: item.description,
      published_at: item.published_at,
      image_url: item.image_url,
      source: source,
      topic: topic
    }
  end

  def topic
    if FeatureToggle.clustering_enabled?
      topic_with_related_posts || new_topic
    else
      new_topic
    end
  end

  def topic_with_related_posts
    RelatedPostsFinder.new(item).topic_with_related_posts_or_nil
  end

  def new_topic
    Topic.create!
  end
end
