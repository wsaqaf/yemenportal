class PostsFetcher::ItemSaver
  def initialize(source:, item:)
    @source = source
    @item = item
  end

  def save!
    create_post_and_attach_to_topic
  end

  private

  attr_reader :source, :item

  def create_post_and_attach_to_topic
    topic_finder_for_created_post.attach_topic!
  end

  def topic_finder_for_created_post
    PostsFetcher::TopicFinder.new(created_post)
  end

  def created_post
    PostsFetcher::PostFactory.new(source: source, item: item).create
  end
end
