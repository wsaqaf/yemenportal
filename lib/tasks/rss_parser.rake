desc "Fetches posts for all sources"
task rss_parser: :environment do
  Source.find_each do |source|
    PostsFetcher.new(source).fetch!
  end
end
