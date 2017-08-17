require "rss"
require "open-uri"

desc "Fetches posts for all sources"
task rss_parser: :environment do
  Source.approved.find_each do |source|
    begin
      PostsFetcher.new(source).fetch!

    # Fix it and move to a separate service with better names for errors
    # Temporary solution
    rescue Errno::ENOENT, OpenURI::HTTPError
      source.update(state: Source.state.incorrect_path)
      SourceLog.create(source: source, state: :invalid)
    rescue RSS::NotWellFormedError, RSS::NotAvailableValueError
      source.update(state: Source.state.incorrect_sctructure)
      SourceLog.create(source: source, state: :invalid)
    rescue
      source.update(state: Source.state.other)
      SourceLog.create(source: source, state: :invalid)
    end
  end
end
