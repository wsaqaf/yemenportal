require "rss"
require "open-uri"

class PostsFetcherJob < ActiveJob::Base
  def perform(source_id)
    source = Source.find(source_id)
    begin
      items = fetch_items(source)
      source.update(state: Source.state.valid)
      SourceLog.create(source: source, posts_count: items.length)
    rescue Errno::ENOENT, OpenURI::HTTPError
      save_error_info(source, Source.state.incorrect_path)
    rescue RSS::NotWellFormedError, RSS::NotAvailableValueError
      save_error_info(source, Source.state.incorrect_stucture)
    rescue
      save_error_info(source, Source.state.other)
    end
  end

  private

  def save_error_info(source, state)
    SourceLog.create(source: source, state: :invalid)
    source.update(state: state)
  end

  def fetch_items(source)
    items = []
    if source.source_type.rss?
      items = RSSParserService.fetch_items(open(source.link), source.id)
    elsif source.source_type.facebook?
      items = RSSParserService.fetch_facebook_items(source)
    end
    create_service = PostCreaterService.new(source)
    items.each { |item| create_service.add_post(item) }
    create_service.added_posts
  end
end
