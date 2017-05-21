require "rss"
require "open-uri"

class PostsFetcherJob < ActiveJob::Base
  def perform(source_id)
    source = Source.find(source_id)
    begin
      items = fetch_items(source)
    rescue Errno::ENOENT
      SourceLog.create(source: source, state: :invalid)
      source.update(state: Source.state.incorrect_path)
    rescue RSS::NotWellFormedError, RSS::NotAvailableValueError
      SourceLog.create(source: source, state: :invalid)
      source.update(state: Source.state.incorrect_stucture)
    else
      source.update(state: Source.state.valid)
      SourceLog.create(source: source, posts_count: items.length)
    end
  end

  private

  def fetch_items(source)
    items = []
    if source.source_type.rss?
      items = RSSParserService.fetch_items(open(source.link), source.id)
    elsif source.source_type.facebook?
      items = RSSParserService.fetch_facebook_items(source)
    end
    create_service = PostCreaterService.new
    items.each { |item| create_service.add_post(item, source) }
  end
end
