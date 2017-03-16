require "rss"
require "open-uri"

class PostsFetcherJob < ActiveJob::Base
  def perform(source_id)
    source = Source.find(source_id)
    begin
      RSSParserService.fetch_items(open(source.link), source_id)
        .each { |item| PostCreaterService.add_post(item, source) }
    rescue Errno::ENOENT, RSS::NotWellFormedError
      source.update(state: Source.state.incorrect_path)
    end
  end
end
