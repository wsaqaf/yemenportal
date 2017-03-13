require "rss"
require "open-uri"

class PostsFetcherJob < ActiveJob::Base
  def perform(source_id)
    source = Source.find(source_id)
    open(source.link) do |rss|
      RSSParserService.fetch_items(rss, source_id).each { |item| PostCreaterService.add_post(item, source) }
    end
  end
end
