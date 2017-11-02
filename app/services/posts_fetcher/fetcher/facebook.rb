class PostsFetcher::Fetcher::Facebook < PostsFetcher::Fetcher
  private

  def normalized_raw_items
    raw_items.map do |item|
      {
        link: item["permalink_url"],
        description: item["message"] || item["name"],
        published_at: item["created_time"].to_time,
        image_url: item["picture"]
      }
    end
  end

  def raw_items
    connection.get_connection(
      source.facebook_link,
      "posts",
      fields: %w(permalink_url message name created_time picture)
    )
  end

  def connection
    Koala::Facebook::API.new
  end
end
