require "rss"

class RSSParserService
  def self.call
    Source.find_each do |source|
      PostsFetcherJob.perform_later(source.id)
    end
  end

  def self.fetch_items(rss, source_id)
    feed = RSS::Parser.parse(rss)
    posts = Post.source_posts(source_id)
    feed.items.select { |item| posts.empty? || item.pubDate > posts.first.published_at }
  end
end