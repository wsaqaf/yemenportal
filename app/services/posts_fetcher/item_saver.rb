class PostsFetcher::ItemSaver
  def initialize(source:, item:)
    @source = source
    @item = item
  end

  def save!
    topic_finder.post_with_topic!
  end

  private

  attr_reader :source, :item

  def topic_finder
    @_topic_finder ||= PostsFetcher::TopicFinder.new(post)
  end

  def post
    @_post ||= PostsFetcher::PostFactory.new(source: source, item: item).create
  end
end
