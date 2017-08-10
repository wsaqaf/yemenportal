class PostsFetcher::Fetcher::RSS < PostsFetcher::Fetcher
  private

  def normalized_raw_items
    raw_items.map do |item|
      {
        link: item.url,
        title: item.title,
        description: item.summary,
        published_at: item.published
      }
    end
  end

  def raw_items
    Feedjira::Feed.parse(raw_document).entries
  end

  def raw_document
    HTTParty.get(source.link).body
  end
end
