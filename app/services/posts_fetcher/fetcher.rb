class PostsFetcher::Fetcher
  def self.for(source)
    if source.rss?
      PostsFetcher::Fetcher::RSS.new(source)
    elsif source.facebook?
      PostsFetcher::Fetcher::Facebook.new(source)
    end
  end

  def initialize(source)
    @source = source
  end

  def fetched_items
    normalized_raw_items.map do |item|
      PostsFetcher::FetchedItem.new(item)
    end
  end

  private

  attr_reader :source
end
