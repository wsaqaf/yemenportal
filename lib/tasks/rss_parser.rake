desc "Fetches posts for all sources"
task rss_parser: :environment do
  Source.find_each do |source|
    PostsFetcher.new(source).fetch!
    # PostsFetcherJob.perform_later(source.id)
  end
end
