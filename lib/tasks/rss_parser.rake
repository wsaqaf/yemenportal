require "open-uri"
require "feedjira"

desc "Fetches posts for all sources"
task rss_parser: :environment do
  Source.not_deleted.approved.find_each do |source|
    begin
      PostsFetcher.new(source).fetch!
      source.update(state: Source.state.valid)
      SourceLog.create(source: source, state: :valid)

    # Fix it and move to a separate service with better names for errors
    # Temporary solution
    rescue Errno::ENOENT, OpenURI::HTTPError
      source.update(state: Source.state.incorrect_path)
      SourceLog.create(source: source, state: :invalid)
    rescue Feedjira::NoParserAvailable
      source.update(state: Source.state.incorrect_stucture)
      SourceLog.create(source: source, state: :invalid)
    rescue
      source.update(state: Source.state.other)
      SourceLog.create(source: source, state: :invalid)
    end
  end
end
