require "rss"

class RSSParserService
  def self.call
    Source.approved.find_each do |source|
      PostsFetcherJob.perform_now(source.id)
    end
  end

  def self.fetch_items(source)
    xml = HTTParty.get(source.link).body
    entries = Feedjira::Feed.parse(xml).entries
    posts = Post.source_posts(source.id)
    entries.select { |item| posts.empty? || item.published > posts.first.published_at }
  end

  def self.fetch_facebook_items(source)
    connection = Koala::Facebook::API.new
    posts = Post.source_posts(source.id)

    items = connection.get_connection(source.facebook_page, "posts", { fields: %w(link message
                                                                                  name created_time picture) })
    items.select { |item| posts.empty? || item["created_time"].to_time > posts.first.published_at }
  end
end
