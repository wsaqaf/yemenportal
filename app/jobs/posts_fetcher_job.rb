require "rss"
require "open-uri"

class PostsFetcherJob < ActiveJob::Base
  def perform(source_id)
    source = Source.find(source_id)
    begin
      items = RSSParserService.fetch_items(open(source.link), source_id)
      items.each { |item| PostCreaterService.add_post(item, source) }
      SourceLog.create(source: source, posts_count: items.length) if source.state.valid?
    rescue Errno::ENOENT, RSS::NotWellFormedError
      SourceLog.create(source: source, state: :invalid)
      source.update(state: Source.state.incorrect_path)
    end
  end
end
