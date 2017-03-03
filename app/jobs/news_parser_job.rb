require "rss"
require "open-uri"

class NewsParserJob < ActiveJob::Base
  # include Sidekiq::Worker

  def perform(souce_id)
    source = Source.find(souce_id)
    open(source.link) do |rss|
      feed = RSS::Parser.parse(rss)
      feed.items.each do |item|
        Post.create(description: item.description, link: item.link, published_at: item.pubDate, source: source,
          title: item.title)
      end
    end
  end
end
