desc "Fetches posts for all sources"
task rss_parser: :environment do
  Source.find_each do |source|
    PostsFetcherJob.perform_now(source.id)
  end
end
