require "rss"
require "open-uri"

class PostsFetcherJob < ActiveJob::Base
  def perform(souce_id)
    source = Source.find(souce_id)
    open(source.link) do |rss|
      feed = RSS::Parser.parse(rss)
      posts = Post.source_posts(source.id)

      feed.items.select { |item| posts.empty? || item.pubDate > posts.first }.each do |item|
        Post.create(description: item.description, link: item.link, published_at: item.pubDate, source: source,
          title: item.title, category_id: source.category_id)
      end
    end
  end
end
