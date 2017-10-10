class PostsFetcher::Fetcher::Facebook < PostsFetcher::Fetcher
  TITLE_LENGTH_LIMIT = 100
  TITLE_WORDS_SEPARATOR = /\s/

  private

  def normalized_raw_items
    raw_items.map do |item|
      normalized_item = prepare_normalized_item(item)
      normalized_item.merge(title: normalized_item_title(normalized_item))
    end
  end

  def raw_items
    connection.get_connection(source.facebook_link, "posts", fields: ["link",
      "message", "name", "created_time", "picture"])
  end

  def connection
    Koala::Facebook::API.new
  end

  def prepare_normalized_item(item)
    {
      link: item["link"],
      description: item["message"] || item["name"],
      published_at: item["created_time"].to_time,
      image_url: item["picture"]
    }
  end

  def normalized_item_title(item)
    item[:description].truncate(TITLE_LENGTH_LIMIT, separator: TITLE_WORDS_SEPARATOR)
  end
end
